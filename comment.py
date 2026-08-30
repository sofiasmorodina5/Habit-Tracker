from db import query, execute

def get_comments_by_habit(habit_id):
    return query("""
        SELECT habit_comments.id, habit_comments.habit_id, habit_comments.user_id,
               habit_comments.comment_text, habit_comments.created_at, users.username
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
