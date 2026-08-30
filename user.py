from db import query, query_one, execute

def get_user_by_username(username):
    return query_one(
        "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
        (username,)
    )

def get_user_by_id(user_id):
    return query_one(
        "SELECT id, username, password_hash, created_at FROM users WHERE id = ?",
        (user_id,)
    )

def create_user(username, password_hash):
    return execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )

def get_total_logs(user_id):
    row = query_one(
        "SELECT COUNT(*) as count FROM habit_logs WHERE user_id = ?",
        (user_id,)
    )
    return row["count"] if row else 0

def get_participating_habits(user_id):
    return query("""
        SELECT habits.id, habits.user_id, habits.title, habits.description,
               habits.difficulty, habits.created_at, users.username as owner_username
        FROM habit_participants
        JOIN habits ON habit_participants.habit_id = habits.id
        JOIN users ON habits.user_id = users.id
        WHERE habit_participants.user_id = ?
        ORDER BY habit_participants.joined_at DESC
    """, (user_id,))
