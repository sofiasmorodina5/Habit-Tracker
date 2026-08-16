from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
import secrets
import os

from db import (
    get_db, get_user_by_username, get_habit, get_all_categories,
    get_habit_categories, get_streak, get_week_dates, get_week_log_count
)

app = Flask(__name__)
app.secret_key = os.urandom(24)

def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]

def check_csrf():
    if request.method == "POST":
        token = request.form.get("csrf_token")
        if not token or token != session.get("csrf_token"):
            abort(403, "CSRF-tarkistus epäonnistui")

app.jinja_env.globals["csrf_token"] = generate_csrf_token
app.jinja_env.globals["date"] = date

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        check_csrf()
        username = request.form["username"].strip()
        password = request.form["password"]
        if not username or not password:
            flash("Käyttäjätunnus ja salasana ovat pakollisia")
            return render_template("register.html")
        if get_user_by_username(username):
            flash("Käyttäjätunnus on jo varattu")
            return render_template("register.html")
        password_hash = generate_password_hash(password)
        db = get_db()
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        db.commit()
        db.close()
        flash("Rekisteröityminen onnistui! Voit nyt kirjautua sisään.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_csrf()
        username = request.form["username"]
        password = request.form["password"]
        user = get_user_by_username(username)
        if not user:
            flash("Käyttäjätunnusta ei löydy. Rekisteröidy ensin.")
            return render_template("login.html")
        if not check_password_hash(user["password_hash"], password):
            flash("Virheellinen salasana")
            return render_template("login.html")
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["csrf_token"] = secrets.token_hex(16)
        flash("Kirjautuminen onnistui!")
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Olet kirjautunut ulos.")
    return redirect(url_for("login"))

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
    db.close()
    return render_template("index.html", habits=habits)

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
    db.close()
    return render_template("index.html", habits=habits, search_query=query)

@app.route("/add", methods=["GET", "POST"])
def add_habit():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        categories = get_all_categories()
        return render_template("add_habit.html", categories=categories)
    check_csrf()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title:
        flash("Otsikko on pakollinen")
        return render_template("add_habit.html", categories=get_all_categories())
    if len(title) > 100:
        flash("Otsikko on liian pitkä (max 100 merkkiä)")
        return render_template("add_habit.html", categories=get_all_categories())
    if len(description) > 500:
        flash("Kuvaus on liian pitkä (max 500 merkkiä)")
        return render_template("add_habit.html", categories=get_all_categories())
    db = get_db()
    cursor = db.execute(
        "INSERT INTO habits (user_id, title, description) VALUES (?, ?, ?)",
        (session["user_id"], title, description)
    )
    habit_id = cursor.lastrowid
    categories = request.form.getlist("categories")
    for category in categories:
        db.execute(
            "INSERT INTO habit_categories (habit_id, category_name) VALUES (?, ?)",
            (habit_id, category)
        )
    db.commit()
    db.close()
    flash("Tapa lisätty onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    habit = db.execute(
        "SELECT * FROM habits WHERE id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    ).fetchone()
    if not habit:
        db.close()
        flash("Et voi muokata tätä tapaa")
        return redirect(url_for("index"))
    all_categories = get_all_categories()
    selected = get_habit_categories(habit_id)
    if request.method == "GET":
        db.close()
        return render_template("edit_habit.html", habit=habit, categories=all_categories, selected_categories=selected)
    check_csrf()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title:
        flash("Otsikko on pakollinen")
        db.close()
        return render_template("edit_habit.html", habit=habit, categories=all_categories, selected_categories=selected)
    db.execute(
        "UPDATE habits SET title = ?, description = ? WHERE id = ?",
        (title, description, habit_id)
    )
    db.execute("DELETE FROM habit_categories WHERE habit_id = ?", (habit_id,))
    categories = request.form.getlist("categories")
    for category in categories:
        db.execute(
            "INSERT INTO habit_categories (habit_id, category_name) VALUES (?, ?)",
            (habit_id, category)
        )
    db.commit()
    db.close()
    flash("Tapa päivitetty onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    db = get_db()
    db.execute(
        "DELETE FROM habits WHERE id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    )
    db.commit()
    db.close()
    flash("Tapa poistettu onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/habit/<int:habit_id>/log", methods=["POST"])
def log_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
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
    existing = db.execute(
        "SELECT * FROM habit_logs WHERE habit_id = ? AND user_id = ? AND log_date = ?",
        (habit_id, session["user_id"], log_date)
    ).fetchone()
    if existing:
        db.execute(
            "DELETE FROM habit_logs WHERE habit_id = ? AND user_id = ? AND log_date = ?",
            (habit_id, session["user_id"], log_date)
        )
    else:
        db.execute(
            "INSERT INTO habit_logs (habit_id, user_id, log_date) VALUES (?, ?, ?)",
            (habit_id, session["user_id"], log_date)
        )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/join", methods=["POST"])
def join_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
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
    check_csrf()
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

@app.route("/habit/<int:habit_id>/note_add", methods=["POST"])
def add_note(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    note_text = request.form.get("note_text", "").strip()
    if not note_text:
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    db = get_db()
    db.execute(
        "INSERT INTO habit_notes (habit_id, user_id, note_text) VALUES (?, ?, ?)",
        (habit_id, session["user_id"], note_text)
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/note_delete/<int:note_id>", methods=["POST"])
def delete_note(habit_id, note_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    db = get_db()
    db.execute(
        "DELETE FROM habit_notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/comment_add", methods=["POST"])
def add_comment(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    comment_text = request.form.get("comment_text", "").strip()
    if not comment_text:
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    db = get_db()
    db.execute(
        "INSERT INTO habit_comments (habit_id, user_id, comment_text) VALUES (?, ?, ?)",
        (habit_id, session["user_id"], comment_text)
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/comment_delete/<int:comment_id>", methods=["POST"])
def delete_comment(habit_id, comment_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    db = get_db()
    db.execute(
        "DELETE FROM habit_comments WHERE id = ? AND user_id = ?",
        (comment_id, session["user_id"])
    )
    db.commit()
    db.close()
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

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
    comments = db.execute("""
        SELECT habit_comments.*, users.username
        FROM habit_comments
        JOIN users ON habit_comments.user_id = users.id
        WHERE habit_comments.habit_id = ?
        ORDER BY habit_comments.created_at DESC
    """, (habit_id,)).fetchall()
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
    today_iso = date.today().isoformat()
    categories = db.execute(
        "SELECT category_name FROM habit_categories WHERE habit_id = ?",
        (habit_id,)
    ).fetchall()
    category_list = [c["category_name"] for c in categories]
    db.close()
    return render_template("view_habit.html",
                         habit=habit,
                         notes=notes,
                         comments=comments,
                         participants=participants,
                         is_owner=is_owner,
                         is_participant=bool(is_participant),
                         logged_dates=logged_dates,
                         streak=streak,
                         week_dates=week_dates,
                         week_count=week_count,
                         today_iso=today_iso,
                         categories=category_list)

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
                         best_streak=best_streak)

if __name__ == "__main__":
    app.run(debug=True)
