from datetime import date, timedelta, datetime

from db import query, query_one, execute

def get_logs_for_habit(habit_id, user_id):
    rows = query(
        "SELECT log_date FROM habit_logs WHERE habit_id = ? AND user_id = ?",
        (habit_id, user_id)
    )
    return [row["log_date"] for row in rows]

def get_log_for_date(habit_id, user_id, log_date):
    return query_one(
        "SELECT id, habit_id, user_id, log_date FROM habit_logs "
        "WHERE habit_id = ? AND user_id = ? AND log_date = ?",
        (habit_id, user_id, log_date)
    )

def toggle_log(habit_id, user_id, log_date):
    existing = get_log_for_date(habit_id, user_id, log_date)
    if existing:
        execute(
            "DELETE FROM habit_logs WHERE habit_id = ? AND user_id = ? AND log_date = ?",
            (habit_id, user_id, log_date)
        )
        return False
    execute(
        "INSERT INTO habit_logs (habit_id, user_id, log_date) VALUES (?, ?, ?)",
        (habit_id, user_id, log_date)
    )
    return True

def get_streak(habit_id, user_id):
    logs = query(
        "SELECT log_date FROM habit_logs "
        "WHERE habit_id = ? AND user_id = ? ORDER BY log_date DESC",
        (habit_id, user_id)
    )
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

def get_week_log_count(habit_id, user_id):
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    row = query_one(
        "SELECT COUNT(*) as count FROM habit_logs "
        "WHERE habit_id = ? AND user_id = ? AND log_date BETWEEN ? AND ?",
        (habit_id, user_id, monday.isoformat(), sunday.isoformat())
    )
    return row["count"] if row else 0

def get_week_dates(week_offset=0):
    today = date.today()
    target_date = today + timedelta(weeks=week_offset)
    monday = target_date - timedelta(days=target_date.weekday())
    return [monday + timedelta(days=i) for i in range(7)]
