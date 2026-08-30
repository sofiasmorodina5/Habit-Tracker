from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
import secrets

from db import query, query_one, execute
from config import SECRET_KEY
from utils import generate_csrf_token, check_csrf

from user import (
    get_user_by_username, get_user_by_id, create_user,
    get_total_logs, get_participating_habits
)
from habit import (
    get_all_habits, get_habit_count, search_habits, get_search_count,
    get_habit_with_owner,
    add_habit, update_habit, delete_habit,
    get_habits_by_user, add_habit_category, delete_habit_categories,
    get_habit_categories, get_all_categories, PAGE_SIZE
)
from log import (
    get_logs_for_habit, get_log_for_date, toggle_log,
    get_streak, get_week_log_count, get_week_dates
)
from participant import (
    get_participants, get_participant, add_participant, remove_participant
)
from comment import get_comments_by_habit, add_comment, delete_comment
from note import get_notes_by_habit, add_note, delete_note

def validate_habit(title, description, difficulty):
    errors = []
    if not title or not title.strip():
        errors.append("Otsikko on pakollinen")
    elif len(title) > 30:
        errors.append("Otsikko voi olla enintään 30 merkkiä pitkä")
    if description and len(description) > 30:
        errors.append("Kuvaus voi olla enintään 30 merkkiä pitkä")
    if difficulty not in ["helppo", "neutraali", "vaativa"]:
        errors.append("Virheellinen vaikeustaso")
    return errors

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.jinja_env.globals["csrf_token"] = generate_csrf_token
app.jinja_env.globals["date"] = date

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        errors = []
        username_valid = True
        password_valid = True

        if not username or len(username) < 3:
            errors.append("Käyttäjätunnuksen on oltava vähintään 3 merkkiä")
            username_valid = False
        elif len(username) > 30:
            errors.append("Käyttäjätunnus voi olla enintään 30 merkkiä")
            username_valid = False
        if not username.isalnum():
            errors.append("Käyttäjätunnus saa sisältää vain kirjaimia ja numeroita")
            username_valid = False
        if get_user_by_username(username):
            errors.append("Käyttäjätunnus on jo varattu")
            username_valid = False

        if not password or len(password) < 8:
            errors.append("Salasanan on oltava vähintään 8 merkkiä")
            password_valid = False
        elif len(password) > 30:
            errors.append("Salasana voi olla enintään 30 merkkiä")
            password_valid = False

        if errors:
            if not username_valid:
                username = ""
            for error in errors:
                flash(error)
            return render_template("register.html", username=username)

        password_hash = generate_password_hash(password)
        create_user(username, password_hash)
        flash("Rekisteröityminen onnistui! Voit nyt kirjautua sisään.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "")
        password = request.form.get("password", "")
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
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    total_habits = get_habit_count()
    total_pages = max(1, -(-total_habits // PAGE_SIZE))
    if page > total_pages:
        page = total_pages
    habits = get_all_habits(page)
    habits = [dict(row) for row in habits]
    for h in habits:
        participant = query_one(
            "SELECT id, habit_id, user_id, joined_at FROM habit_participants "
            "WHERE habit_id = ? AND user_id = ?",
            (h["id"], session["user_id"])
        )
        h["is_participant"] = bool(participant)
        today = date.today().isoformat()
        log = query_one(
            "SELECT id, habit_id, user_id, log_date FROM habit_logs "
            "WHERE habit_id = ? AND user_id = ? AND log_date = ?",
            (h["id"], session["user_id"], today)
        )
        h["logged_today"] = bool(log)
    return render_template("index.html", habits=habits, page=page, total_pages=total_pages)

@app.route("/search")
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("index"))
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    total_habits = get_search_count(query_term)
    total_pages = max(1, -(-total_habits // PAGE_SIZE))
    if page > total_pages:
        page = total_pages
    habits = search_habits(query_term, page)
    habits = [dict(row) for row in habits]
    for h in habits:
        participant = query_one(
            "SELECT id, habit_id, user_id, joined_at FROM habit_participants "
            "WHERE habit_id = ? AND user_id = ?",
            (h["id"], session["user_id"])
        )
        h["is_participant"] = bool(participant)
        today = date.today().isoformat()
        log = query_one(
            "SELECT id, habit_id, user_id, log_date FROM habit_logs "
            "WHERE habit_id = ? AND user_id = ? AND log_date = ?",
            (h["id"], session["user_id"], today)
        )
        h["logged_today"] = bool(log)
    return render_template(
        "index.html", habits=habits, search_query=query_term,
        page=page, total_pages=total_pages
    )

@app.route("/add", methods=["GET", "POST"])
def add_habit():
    if "user_id" not in session:
        return redirect(url_for("login"))
    categories = get_all_categories()
    if request.method == "GET":
        return render_template("add_habit.html", categories=categories)
    check_csrf()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    difficulty = request.form.get("difficulty", "neutraali")

    errors = validate_habit(title, description, difficulty)
    if errors:
        for error in errors:
            flash(error)
        return render_template(
            "add_habit.html",
            categories=categories,
            title=title,
            description=description
        )

    habit_id = execute(
        "INSERT INTO habits (user_id, title, description, difficulty) VALUES (?, ?, ?, ?)",
        (session["user_id"], title, description, difficulty)
    )
    selected_categories = request.form.getlist("categories")
    for category in selected_categories:
        execute(
            "INSERT INTO habit_categories (habit_id, category_name) VALUES (?, ?)",
            (habit_id, category)
        )
    flash("Tapa lisätty onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    habit = query_one(
        "SELECT id, user_id, title, description, difficulty, created_at "
        "FROM habits WHERE id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    )
    if not habit:
        flash("Et voi muokata tätä tapaa")
        return redirect(url_for("index"))
    categories = get_all_categories()
    selected = get_habit_categories(habit_id)
    if request.method == "GET":
        return render_template(
            "edit_habit.html",
            habit=habit,
            categories=categories,
            selected_categories=selected
        )
    check_csrf()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    difficulty = request.form.get("difficulty", "neutraali")

    errors = validate_habit(title, description, difficulty)
    if errors:
        for error in errors:
            flash(error)
        return render_template(
            "edit_habit.html",
            habit=habit,
            categories=categories,
            selected_categories=selected
        )

    execute(
        "UPDATE habits SET title = ?, description = ?, difficulty = ? WHERE id = ?",
        (title, description, difficulty, habit_id)
    )
    execute("DELETE FROM habit_categories WHERE habit_id = ?", (habit_id,))
    selected_categories = request.form.getlist("categories")
    for category in selected_categories:
        execute(
            "INSERT INTO habit_categories (habit_id, category_name) VALUES (?, ?)",
            (habit_id, category)
        )
    flash("Tapa päivitetty onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    execute(
        "DELETE FROM habits WHERE id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    )
    flash("Tapa poistettu onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/habit/<int:habit_id>/log", methods=["POST"])
def log_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    log_date = request.form.get("log_date", date.today().isoformat())
    if log_date > date.today().isoformat():
        flash("Et voi merkitä tulevia päiviä suoritetuiksi")
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    habit = get_habit_with_owner(habit_id)
    if not habit:
        flash("Tapa ei löydy")
        return redirect(request.referrer or url_for("index"))
    is_owner = (habit["user_id"] == session["user_id"])
    is_participant = bool(get_participant(habit_id, session["user_id"]))
    if not (is_owner or is_participant):
        flash("Et voi merkitä tätä tapaa. Osallistu ensin painamalla 'Osallistu'-nappia.")
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    toggle_log(habit_id, session["user_id"], log_date)
    flash("Suoritus merkattu!")
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/unlog", methods=["POST"])
def unlog_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    log_date = request.form.get("log_date", date.today().isoformat())
    execute(
        "DELETE FROM habit_logs WHERE habit_id = ? AND user_id = ? AND log_date = ?",
        (habit_id, session["user_id"], log_date)
    )
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/join", methods=["POST"])
def join_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    existing = query_one(
        "SELECT id, habit_id, user_id, joined_at FROM habit_participants "
        "WHERE habit_id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    )
    if not existing:
        execute(
            "INSERT INTO habit_participants (habit_id, user_id) VALUES (?, ?)",
            (habit_id, session["user_id"])
        )
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/leave", methods=["POST"])
def leave_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    habit = query_one("SELECT user_id FROM habits WHERE id = ?", (habit_id,))
    if habit and habit["user_id"] == session["user_id"]:
        flash("Et voi poistua omasta tavastasi")
        return redirect(request.referrer or url_for("index"))
    execute(
        "DELETE FROM habit_participants WHERE habit_id = ? AND user_id = ?",
        (habit_id, session["user_id"])
    )
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/note_add", methods=["POST"])
def add_note(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    note_text = request.form.get("note_text", "").strip()
    if not note_text:
        flash("Muistiinpano ei voi olla tyhjä")
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    if len(note_text) > 30:
        flash("Muistiinpano voi olla enintään 30 merkkiä pitkä")
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    execute(
        "INSERT INTO habit_notes (habit_id, user_id, note_text) VALUES (?, ?, ?)",
        (habit_id, session["user_id"], note_text)
    )
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/note_delete/<int:note_id>", methods=["POST"])
def delete_note(habit_id, note_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    execute(
        "DELETE FROM habit_notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"])
    )
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/comment_add", methods=["POST"])
def add_comment(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    comment_text = request.form.get("comment_text", "").strip()
    if not comment_text:
        flash("Kommentti ei voi olla tyhjä")
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    if len(comment_text) > 30:
        flash("Kommentti voi olla enintään 30 merkkiä pitkä")
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    execute(
        "INSERT INTO habit_comments (habit_id, user_id, comment_text) VALUES (?, ?, ?)",
        (habit_id, session["user_id"], comment_text)
    )
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/comment_delete/<int:comment_id>", methods=["POST"])
def delete_comment(habit_id, comment_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    execute(
        "DELETE FROM habit_comments WHERE id = ? AND user_id = ?",
        (comment_id, session["user_id"])
    )
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>")
def view_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    week_offset = request.args.get("week_offset", 0, type=int)
    habit = get_habit_with_owner(habit_id)
    if not habit:
        flash("Tapa ei löydy")
        return redirect(url_for("index"))
    notes = get_notes_by_habit(habit_id)
    comments = get_comments_by_habit(habit_id)
    participants = get_participants(habit_id)
    is_owner = (habit["user_id"] == session["user_id"])
    is_participant = bool(get_participant(habit_id, session["user_id"]))
    logged_dates = get_logs_for_habit(habit_id, session["user_id"])
    streak = get_streak(habit_id, session["user_id"])

    week_dates = get_week_dates(week_offset)
    monday = week_dates[0]
    sunday = week_dates[6]

    week_count = get_week_log_count(habit_id, session["user_id"])
    today_iso = date.today().isoformat()
    categories = get_habit_categories(habit_id)

    return render_template("view_habit.html",
                         habit=habit,
                         notes=notes,
                         comments=comments,
                         participants=participants,
                         is_owner=is_owner,
                         is_participant=is_participant,
                         logged_dates=logged_dates,
                         streak=streak,
                         week_dates=week_dates,
                         week_count=week_count,
                         today_iso=today_iso,
                         categories=categories,
                         week_offset=week_offset,
                         monday=monday,
                         sunday=sunday)

@app.route("/user/<username>")
def user_profile(username):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = query_one(
        "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
        (username,)
    )
    if not user:
        return "Käyttäjää ei löydy", 404

    own_habits = query("""
        SELECT habits.id, habits.user_id, habits.title, habits.description,
               habits.difficulty, habits.created_at,
               (SELECT COUNT(*) FROM habit_logs WHERE habit_id = habits.id) as log_count,
               (SELECT COUNT(*) FROM habit_participants
                WHERE habit_id = habits.id) as participant_count
        FROM habits
        WHERE habits.user_id = ?
        ORDER BY habits.created_at DESC
    """, (user["id"],))

    participating = query("""
        SELECT habits.id, habits.user_id, habits.title, habits.description,
               habits.difficulty, habits.created_at, users.username as owner_username
        FROM habit_participants
        JOIN habits ON habit_participants.habit_id = habits.id
        JOIN users ON habits.user_id = users.id
        WHERE habit_participants.user_id = ?
        ORDER BY habit_participants.joined_at DESC
    """, (user["id"],))

    all_habits = list(own_habits) + list(participating)

    best_streak = 0
    for habit in all_habits:
        streak = get_streak(habit["id"], user["id"])
        if streak > best_streak:
            best_streak = streak

    total_logs = query_one(
        "SELECT COUNT(*) as count FROM habit_logs WHERE user_id = ?",
        (user["id"],)
    )
    total_logs = total_logs["count"] if total_logs else 0

    return render_template("profile.html",
                         profile_user=user,
                         own_habits=own_habits,
                         participating=participating,
                         total_logs=total_logs,
                         best_streak=best_streak)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", title="Sivua ei löytynyt",
                            message="Etsimääsi sivua ei ole olemassa, palaa etusivulle."), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template(
        "error.html", title="Toiminto estetty",
        message="Sinulla ei ole oikeutta tehdä tätä toimintoa, palaa etusivulle."
    ), 403
