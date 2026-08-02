from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta, datetime
import os

app = Flask(__name__)
app.secret_key = "salainen-avain"

def get_db():
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row
    return db

def get_user_by_id(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user

def get_habit(habit_id):
    db = get_db()
    habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    db.close()
    return habit

def user_can_edit_habit(habit_id, user_id):
    habit = get_habit(habit_id)
    if not habit:
        return False
    return habit["user_id"] == user_id

def get_user_settings(user_id):
    db = get_db()
    settings = db.execute(
        "SELECT background_color FROM user_settings WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    db.close()
    if settings:
        return settings["background_color"]
    return "#ffffff"

def set_user_settings(user_id, background_color):
    db = get_db()
    db.execute(
        "INSERT INTO user_settings (user_id, background_color) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET background_color = ?",
        (user_id, background_color, background_color)
    )
    db.commit()
    db.close()

def get_streak(habit_id, user_id):
    db = get_db()
    logs = db.execute(
        "SELECT log_date FROM habit_logs WHERE habit_id = ? AND user_id = ? ORDER BY log_date DESC",
        (habit_id, user_id)
    ).fetchall()
    db.close()
    if not logs:
        return 0
    dates = [datetime.strptime(log["log_date"], "%Y-%m-%d").date() for log in logs]
    streak = 0
    current_date = date.today()
    if current_date not in dates:
        current_date = current_date - timedelta(days=1)
    while current_date in dates:
        streak += 1
        current_date = current_date - timedelta(days=1)
    return streak

def get_week_dates():
    today = date.today()
    # Maanantaista sunnuntaihin
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=i) for i in range(7)]

def get_week_log_count(habit_id, user_id):
    """Laskee montako kertaa tällä viikolla (ma-su) on suoritettu."""
    db = get_db()
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    logs = db.execute(
        "SELECT COUNT(*) as count FROM habit_logs "
        "WHERE habit_id = ? AND user_id = ? AND log_date BETWEEN ? AND ?",
        (habit_id, user_id, monday.isoformat(), sunday.isoformat())
    ).fetchone()
    db.close()
    return logs["count"] if logs else 0

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form["username"]
    password = request.form["password"]
    password_hash = generate_password_hash(password)
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        db.commit()
    except sqlite3.IntegrityError:
        return "Käyttäjätunnus on jo varattu"
    finally:
        db.close()
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    if not user or not check_password_hash(user["password_hash"], password):
        return "Virheellinen käyttäjätunnus tai salasana"
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["background_color"] = get_user_settings(user["id"])
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        current_color = session.get("background_color", "#ffffff")
        return render_template("settings.html", current_color=current_color)
    color = request.form.get("background_color", "#ffffff")
    set_user_settings(session["user_id"], color)
    session["background_color"] = color
    return redirect(url_for("settings"))

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    habits = db.execute("""
        SELECT habits.*, users.username as owner_username,
               (SELECT COUNT(*) FROM habit_participants WHERE habit_id = habits.id) as participant_count
        FROM habits
        JOIN users ON habits.user_id = users.id
        ORDER BY habits.created_at DESC
    """).fetchall()
    habits = [dict(row) for row in habits]
    for h in habits:
        participant = db.execute(
            "SELECT * FROM habit_participants WHERE habit_id = ? AND user_id = ?",
            (h["id"], session["user_id"])
        ).fetchone()
        h["is_participant"] = bool(participant)
        today = date.today().isoformat()
        log = db.execute(
            "SELECT * FROM habit_logs WHERE habit_id = ? AND user_id = ? AND log_date = ?",
            (h["id"], session["user_id"], today)
        ).fetchone()
        h["logged_today"] = bool(log)
        # Viikon suoritusmäärä
        week_count = get_week_log_count(h["id"], session["user_id"])
        h["week_count"] = week_count
        h["target_per_week"] = h.get("target_per_week", 0)
    db.close()
    return render_template("index.html", habits=habits, bg_color=session.get("background_color", "#ffffff"))

@app.route("/search")
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))
    query = request.args.get("query", "").strip()
    if not query:
        return redirect(url_for("index"))
    db = get_db()
    search_term = f"%{query}%"
    habits = db.execute("""
        SELECT habits.*, users.username as owner_username,
               (SELECT COUNT(*) FROM habit_participants WHERE habit_id = habits.id) as participant_count
        FROM habits
        JOIN users ON habits.user_id = users.id
        WHERE habits.title LIKE ? OR habits.description LIKE ?
        ORDER BY habits.created_at DESC
    """, (search_term, search_term)).fetchall()
    habits = [dict(row) for row in habits]
    for h in habits:
        participant = db.execute(
            "SELECT * FROM habit_participants WHERE habit_id = ? AND user_id = ?",
            (h["id"], session["user_id"])
        ).fetchone()
        h["is_participant"] = bool(participant)
        today = date.today().isoformat()
        log = db.execute(
            "SELECT * FROM habit_logs WHERE habit_id = ? AND user_id = ? AND log_date = ?",
            (h["id"], session["user_id"], today)
        ).fetchone()
        h["logged_today"] = bool(log)
        week_count = get_week_log_count(h["id"], session["user_id"])
        h["week_count"] = week_count
        h["target_per_week"] = h.get("target_per_week", 0)
    db.close()
    return render_template("index.html", habits=habits, search_query=query, bg_color=session.get("background_color", "#ffffff"))

@app.route("/add", methods=["GET", "POST"])
def add_habit():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("add_habit.html", bg_color=session.get("background_color", "#ffffff"))
    title = request.form["title"]
    description = request.form.get("description", "")
    target_per_week = int(request.form.get("target_per_week", 0))
    db = get_db()
    cursor = db.execute(
        "INSERT INTO habits (user_id, title, description, target_per_week) VALUES (?, ?, ?, ?)",
        (session["user_id"], title, description, target_per_week)
    )
    habit_id = cursor.lastrowid
    weekdays = request.form.getlist("weekday")
    for day in weekdays:
        db.execute(
            "INSERT INTO habit_categories (habit_id, category_name, category_value) "
            "VALUES (?, 'weekday', ?)",
            (habit_id, day)
        )
    frequency = request.form.get("frequency")
    if frequency:
        db.execute(
            "INSERT INTO habit_categories (habit_id, category_name, category_value) "
            "VALUES (?, 'frequency', ?)",
            (habit_id, frequency)
        )
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if not user_can_edit_habit(habit_id, session["user_id"]):
        return "Et voi muokata tätä tapaa", 403
    db = get_db()
    habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    categories = db.execute(
        "SELECT * FROM habit_categories WHERE habit_id = ?", (habit_id,)
    ).fetchall()
    if request.method == "GET":
        db.close()
        return render_template("edit_habit.html", habit=habit, categories=categories, bg_color=session.get("background_color", "#ffffff"))
    title = request.form["title"]
    description = request.form.get("description", "")
    target_per_week = int(request.form.get("target_per_week", 0))
    db.execute(
        "UPDATE habits SET title = ?, description = ?, target_per_week = ? WHERE id = ?",
        (title, description, target_per_week, habit_id)
    )
    db.execute("DELETE FROM habit_categories WHERE habit_id = ?", (habit_id,))
    weekdays = request.form.getlist("weekday")
    for day in weekdays:
        db.execute(
            "INSERT INTO habit_categories (habit_id, category_name, category_value) "
            "VALUES (?, 'weekday', ?)",
            (habit_id, day)
        )
    frequency = request.form.get("frequency")
    if frequency:
        db.execute(
            "INSERT INTO habit_categories (habit_id, category_name, category_value) "
            "VALUES (?, 'frequency', ?)",
            (habit_id, frequency)
        )
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if not user_can_edit_habit(habit_id, session["user_id"]):
        abort(403)
    db = get_db()
    db.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))

# --- SUORITUSMERKINNÄT ---
@app.route("/habit/<int:habit_id>/log", methods=["POST"])
def log_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    log_date = request.form.get("log_date", date.today().isoformat())
    db = get_db()
    habit = db.execute("SELECT user_id FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if not habit:
        db.close()
        return "Tapa ei löydy", 404
    is_owner = (habit["user_id"] == session["user_id"])
    is_participant = db.execute(
        "SELECT * FROM habit_participants WHERE habit_id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    ).fetchone()
    if not (is_owner or is_participant):
        db.close()
        return "Et voi merkitä tätä tapaa", 403
    db.execute(
        "INSERT INTO habit_logs (habit_id, user_id, log_date, completed) "
        "VALUES (?, ?, ?, 1) ON CONFLICT(habit_id, user_id, log_date) "
        "DO UPDATE SET completed = 1",
        (habit_id, session["user_id"], log_date)
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/unlog", methods=["POST"])
def unlog_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    log_date = request.form.get("log_date", date.today().isoformat())
    db = get_db()
    db.execute(
        "DELETE FROM habit_logs WHERE habit_id = ? AND user_id = ? AND log_date = ?",
        (habit_id, session["user_id"], log_date)
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("index"))

# --- MUISTIINPANOT ---
@app.route("/habit/<int:habit_id>/note_add", methods=["POST"])
def add_note(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    note_text = request.form.get("note_text", "").strip()
    if not note_text:
        return redirect(url_for("view_habit", habit_id=habit_id))
    db = get_db()
    db.execute(
        "INSERT INTO habit_notes (habit_id, user_id, note_text) VALUES (?, ?, ?)",
        (habit_id, session["user_id"], note_text)
    )
    db.commit()
    db.close()
    return redirect(url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/note_delete/<int:note_id>", methods=["POST"])
def delete_note(habit_id, note_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    note = db.execute(
        "SELECT * FROM habit_notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    ).fetchone()
    if note:
        db.execute("DELETE FROM habit_notes WHERE id = ?", (note_id,))
        db.commit()
    db.close()
    return redirect(url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/join", methods=["POST"])
def join_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    existing = db.execute(
        "SELECT * FROM habit_participants WHERE habit_id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    ).fetchone()
    if not existing:
        db.execute(
            "INSERT INTO habit_participants (habit_id, user_id) VALUES (?, ?)",
            (habit_id, session["user_id"])
        )
        db.commit()
    db.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/leave", methods=["POST"])
def leave_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    habit = db.execute("SELECT user_id FROM habits WHERE id = ?", (habit_id,)).fetchone()
    if habit and habit["user_id"] == session["user_id"]:
        db.close()
        return "Et voi poistua omasta tavastasi", 403
    db.execute(
        "DELETE FROM habit_participants WHERE habit_id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>")
def view_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    habit = db.execute("""
        SELECT habits.*, users.username as owner_username
        FROM habits
        JOIN users ON habits.user_id = users.id
        WHERE habits.id = ?
    """, (habit_id,)).fetchone()
    if not habit:
        db.close()
        return "Tapa ei löydy", 404

    notes = db.execute(
        "SELECT * FROM habit_notes WHERE habit_id = ? ORDER BY created_at DESC",
        (habit_id,)
    ).fetchall()

    participants = db.execute("""
        SELECT users.id, users.username
        FROM habit_participants
        JOIN users ON habit_participants.user_id = users.id
        WHERE habit_participants.habit_id = ?
    """, (habit_id,)).fetchall()

    is_owner = (habit["user_id"] == session["user_id"])
    is_participant = db.execute(
        "SELECT * FROM habit_participants WHERE habit_id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    ).fetchone()

    logs = db.execute(
        "SELECT log_date FROM habit_logs WHERE habit_id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    ).fetchall()
    logged_dates = [log["log_date"] for log in logs]

    streak = get_streak(habit_id, session["user_id"])
    week_dates = get_week_dates()
    week_count = get_week_log_count(habit_id, session["user_id"])
    target = habit["target_per_week"] if habit["target_per_week"] else 0
    today_iso = date.today().isoformat()

    db.close()
    return render_template("view_habit.html",
                         habit=habit,
                         notes=notes,
                         participants=participants,
                         is_owner=is_owner,
                         is_participant=bool(is_participant),
                         logged_dates=logged_dates,
                         streak=streak,
                         week_dates=week_dates,
                         week_count=week_count,
                         target=target,
                         today_iso=today_iso,
                         bg_color=session.get("background_color", "#ffffff"))

@app.route("/user/<username>")
def user_profile(username):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        db.close()
        return "Käyttäjää ei löydy", 404
    habits = db.execute("""
        SELECT habits.*,
               (SELECT COUNT(*) FROM habit_logs WHERE habit_id = habits.id) as log_count,
               (SELECT COUNT(*) FROM habit_participants WHERE habit_id = habits.id) as participant_count
        FROM habits
        WHERE habits.user_id = ?
        ORDER BY habits.created_at DESC
    """, (user["id"],)).fetchall()
    total_logs = db.execute(
        "SELECT COUNT(*) as count FROM habit_logs WHERE user_id = ?",
        (user["id"],)
    ).fetchone()["count"]
    best_streak = 0
    for habit in habits:
        streak = get_streak(habit["id"], user["id"])
        if streak > best_streak:
            best_streak = streak
    db.close()
    return render_template("profile.html",
                         profile_user=user,
                         habits=habits,
                         total_logs=total_logs,
                         best_streak=best_streak,
                         bg_color=session.get("background_color", "#ffffff"))

if __name__ == "__main__":
    app.run(debug=True)
