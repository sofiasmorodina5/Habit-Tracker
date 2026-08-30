from db import query, query_one, execute

def get_notes_by_habit(habit_id):
    return query("""
        SELECT habit_notes.id, habit_notes.habit_id, habit_notes.user_id,
               habit_notes.note_text, habit_notes.created_at, users.username
        FROM habit_notes
        JOIN users ON habit_notes.user_id = users.id
        WHERE habit_notes.habit_id = ?
        ORDER BY habit_notes.created_at DESC
    """, (habit_id,))

def add_note(habit_id, user_id, note_text):
    execute(
        "INSERT INTO habit_notes (habit_id, user_id, note_text) VALUES (?, ?, ?)",
        (habit_id, user_id, note_text)
    )

def delete_note(note_id, user_id):
    execute(
        "DELETE FROM habit_notes WHERE id = ? AND user_id = ?",
        (note_id, user_id)
    )
