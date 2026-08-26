from db import query, query_one, execute

def get_comments_by_habit(habit_id):
    return query("""
        SELECT habit_comments.*, users.username
        FROM habit_comments
        JOIN users ON habit_comments.user_id = users.id
        WHERE habit_comments.habit_id = ?
        ORDER BY habit_comments.created_at DESC
    """, (habit_id,))

def add_comment(habit_id, user_id, comment_text):
    execute(
        "INSERT INTO habit_comments (habit_id, user_id, comment_text) VALUES (?, ?, ?)",
        (habit_id, user_id, comment_text)
    )

def delete_comment(comment_id, user_id):
    execute(
        "DELETE FROM habit_comments WHERE id = ? AND user_id = ?",
        (comment_id, user_id)
    )

def get_comment_count_for_user(user_id):
    row = query_one(
        "SELECT COUNT(*) as count FROM habit_comments "
        "JOIN habits ON habit_comments.habit_id = habits.id "
        "WHERE habits.user_id = ?",
        (user_id,)
    )
    return row["count"] if row else 0
