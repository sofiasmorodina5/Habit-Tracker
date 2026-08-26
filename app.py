from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta, datetime
import secrets

from config import SECRET_KEY
from db import execute, query, query_one
from utils import generate_csrf_token, check_csrf
from habit import (
    get_all_habits, search_habits, get_habit_with_owner,
    add_habit, update_habit, delete_habit,
    get_habits_by_user, add_habit_category, delete_habit_categories,
    get_habit_categories, get_all_categories
)
from user import (
    get_user_by_username, get_user_by_id, create_user,
    get_total_logs, get_participating_habits
)
from log import (
    get_logs_for_habit, get_log_for_date, toggle_log,
    get_streak, get_week_log_count, get_week_dates
)
from participant import (
    get_participants, get_participant, add_participant, remove_participant
)
from comment import get_comments_by_habit, add_comment, delete_comment, get_comment_count_for_user
from note import get_notes_by_habit, add_note, delete_note

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
        if not username or len(username) < 3:
            flash("Käyttäjätunnuksen on oltava vähintään 3 merkkiä")
            return render_template("register.html", username=username)
        if not username.isalnum():
            flash("Käyttäjätunnus saa sisältää vain kirjaimia ja numeroita")
            return render_template("register.html", username=username)
        if not password or len(password) < 8:
            flash("Salasanan on oltava vähintään 8 merkkiä")
            return render_template("register.html", username=username)
        if get_user_by_username(username):
            flash("Käyttäjätunnus on jo varattu")
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
    habits = get_all_habits()
    habits = [dict(row) for row in habits]
    for h in habits:
        h["is_participant"] = bool(get_participant(h["id"], session["user_id"]))
        today = date.today().isoformat()
        h["logged_today"] = bool(get_log_for_date(h["id"], session["user_id"], today))
    return render_template("index.html", habits=habits)

@app.route("/search")
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))
    query_term = request.args.get("query", "").strip()
    if not query_term:
        return redirect(url_for("index"))
    habits = search_habits(query_term)
    habits = [dict(row) for row in habits]
    for h in habits:
        h["is_participant"] = bool(get_participant(h["id"], session["user_id"]))
        today = date.today().isoformat()
        h["logged_today"] = bool(get_log_for_date(h["id"], session["user_id"], today))
    return render_template("index.html", habits=habits, search_query=query_term)

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
    errors = []
    if not title:
        errors.append("Otsikko on pakollinen")
    elif len(title) > 100:
        errors.append("Otsikko on liian pitkä (max 100 merkkiä)")
    if description and len(description) > 500:
        errors.append("Kuvaus on liian pitkä (max 500 merkkiä)")
    if errors:
        for error in errors:
            flash(error)
        return render_template("add_habit.html", categories=categories, title=title, description=description)
    habit_id = add_habit(session["user_id"], title, description, difficulty)
    selected_categories = request.form.getlist("categories")
    for category in selected_categories:
        add_habit_category(habit_id, category)
    flash("Tapa lisätty onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/edit/<int:habit_id>", methods=["GET", "POST"])
def edit_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    habit = get_habit_with_owner(habit_id)
    if not habit or habit["user_id"] != session["user_id"]:
        flash("Et voi muokata tätä tapaa")
        return redirect(url_for("index"))
    categories = get_all_categories()
    selected = get_habit_categories(habit_id)
    if request.method == "GET":
        return render_template("edit_habit.html", habit=habit, categories=categories, selected_categories=selected)
    check_csrf()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    difficulty = request.form.get("difficulty", "neutraali")
    errors = []
    if not title:
        errors.append("Otsikko on pakollinen")
    elif len(title) > 100:
        errors.append("Otsikko on liian pitkä (max 100 merkkiä)")
    if description and len(description) > 500:
        errors.append("Kuvaus on liian pitkä (max 500 merkkiä)")
    if errors:
        for error in errors:
            flash(error)
        return render_template("edit_habit.html", habit=habit, categories=categories, selected_categories=selected)
    update_habit(habit_id, title, description, difficulty)
    delete_habit_categories(habit_id)
    selected_categories = request.form.getlist("categories")
    for category in selected_categories:
        add_habit_category(habit_id, category)
    flash("Tapa päivitetty onnistuneesti!")
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
def delete_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    delete_habit(habit_id, session["user_id"])
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
        return redirect(request.referrer or url_for("index"))
    habit = get_habit_with_owner(habit_id)
    if not habit:
        return "Tapa ei löydy", 404
    is_owner = (habit["user_id"] == session["user_id"])
    is_participant = bool(get_participant(habit_id, session["user_id"]))
    if not (is_owner or is_participant):
        return "Et voi merkitä tätä tapaa", 403
    toggle_log(habit_id, session["user_id"], log_date)
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/unlog", methods=["POST"])
def unlog_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    log_date = request.form.get("log_date", date.today().isoformat())
    toggle_log(habit_id, session["user_id"], log_date)
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/join", methods=["POST"])
def join_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    add_participant(habit_id, session["user_id"])
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/leave", methods=["POST"])
def leave_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    habit = get_habit_with_owner(habit_id)
    if habit and habit["user_id"] == session["user_id"]:
        flash("Et voi poistua omasta tavastasi")
        return redirect(request.referrer or url_for("index"))
    remove_participant(habit_id, session["user_id"])
    return redirect(request.referrer or url_for("index"))

@app.route("/habit/<int:habit_id>/note_add", methods=["POST"])
def add_note_route(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    note_text = request.form.get("note_text", "").strip()
    if not note_text:
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    add_note(habit_id, session["user_id"], note_text)
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/note_delete/<int:note_id>", methods=["POST"])
def delete_note_route(habit_id, note_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    delete_note(note_id, session["user_id"])
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/comment_add", methods=["POST"])
def add_comment_route(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    comment_text = request.form.get("comment_text", "").strip()
    if not comment_text:
        return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))
    add_comment(habit_id, session["user_id"], comment_text)
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>/comment_delete/<int:comment_id>", methods=["POST"])
def delete_comment_route(habit_id, comment_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    check_csrf()
    delete_comment(comment_id, session["user_id"])
    return redirect(request.referrer or url_for("view_habit", habit_id=habit_id))

@app.route("/habit/<int:habit_id>")
def view_habit(habit_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    week_offset = request.args.get("week_offset", 0, type=int)
    habit = get_habit_with_owner(habit_id)
    if not habit:
        return "Tapa ei löydy", 404
    today = date.today()
    target_date = today + timedelta(weeks=week_offset)
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    logged_dates = get_logs_for_habit(habit_id, session["user_id"])
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    week_count = len([d for d in logged_dates if monday <= datetime.strptime(d, "%Y-%m-%d").date() <= sunday])
    streak = get_streak(habit_id, session["user_id"])
    notes = get_notes_by_habit(habit_id)
    comments = get_comments_by_habit(habit_id)
    participants = get_participants(habit_id)
    is_owner = (habit["user_id"] == session["user_id"])
    is_participant = bool(get_participant(habit_id, session["user_id"]))
    categories = get_habit_categories(habit_id)
    difficulty = habit["difficulty"] if habit["difficulty"] else "neutraali"
    return render_template("view_habit.html",
                         habit=habit,
                         difficulty=difficulty,
                         notes=notes,
                         comments=comments,
                         participants=participants,
                         is_owner=is_owner,
                         is_participant=is_participant,
                         logged_dates=logged_dates,
                         streak=streak,
                         week_dates=week_dates,
                         week_count=week_count,
                         week_offset=week_offset,
                         monday=monday,
                         sunday=sunday,
                         categories=categories)

@app.route("/user/<username>")
def user_profile(username):
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = get_user_by_username(username)
    if not user:
        return "Käyttäjää ei löydy", 404
    own_habits = get_habits_by_user(user["id"])
    participating = get_participating_habits(user["id"])
    all_habits = list(own_habits) + list(participating)
    best_streak = 0
    for habit in all_habits:
        streak = get_streak(habit["id"], user["id"])
        if streak > best_streak:
            best_streak = streak
    total_logs = get_total_logs(user["id"])
    return render_template("profile.html",
                         profile_user=user,
                         own_habits=own_habits,
                         participating=participating,
                         total_logs=total_logs,
                         best_streak=best_streak)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

if __name__ == "__main__":
    app.run(debug=True)
