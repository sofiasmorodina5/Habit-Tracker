from db import query, query_one, execute

def get_participants(habit_id):
    return query("""
        SELECT users.id, users.username
        FROM habit_participants
        JOIN users ON habit_participants.user_id = users.id
        WHERE habit_participants.habit_id = ?
    """, (habit_id,))

def get_participant(habit_id, user_id):
    return query_one(
        "SELECT id, habit_id, user_id, joined_at FROM habit_participants "
        "WHERE habit_id = ? AND user_id = ?",
        (habit_id, user_id)
    )

def add_participant(habit_id, user_id):
    execute(
        "INSERT INTO habit_participants (habit_id, user_id) VALUES (?, ?)",
        (habit_id, user_id)
    )

def remove_participant(habit_id, user_id):
    execute(
        "DELETE FROM habit_participants WHERE habit_id = ? AND user_id = ?",
        (habit_id, user_id)
    )
