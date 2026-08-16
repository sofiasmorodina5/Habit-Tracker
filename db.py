import sqlite3
from datetime import date, timedelta, datetime

def get_db():
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row
    return db

def get_user_by_username(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return user

def get_habit(habit_id):
    db = get_db()
    habit = db.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
    db.close()
    return habit

def get_all_categories():
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    db.close()
    return categories

def get_habit_categories(habit_id):
    db = get_db()
    categories = db.execute(
        "SELECT category_name FROM habit_categories WHERE habit_id = ?",
        (habit_id,)
    ).fetchall()
    db.close()
    return [c["category_name"] for c in categories]

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
    monday = today - timedelta(days=today.weekday())
    return [monday + timedelta(days=i) for i in range(7)]

def get_week_log_count(habit_id, user_id):
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
