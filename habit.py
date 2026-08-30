from db import query, query_one, execute

def get_all_habits():
    return query("""
        SELECT habits.id, habits.user_id, habits.title, habits.description,
               habits.difficulty, habits.created_at, users.username as owner_username,
               (SELECT COUNT(*) FROM habit_participants
                WHERE habit_id = habits.id) as participant_count
        FROM habits
        JOIN users ON habits.user_id = users.id
        ORDER BY habits.created_at DESC
    """)

def search_habits(query_term):
    search = f"%{query_term}%"
    return query("""
        SELECT DISTINCT habits.id, habits.user_id, habits.title, habits.description,
               habits.difficulty, habits.created_at, users.username as owner_username,
               (SELECT COUNT(*) FROM habit_participants
                WHERE habit_id = habits.id) as participant_count
        FROM habits
        JOIN users ON habits.user_id = users.id
        LEFT JOIN habit_categories ON habits.id = habit_categories.habit_id
        WHERE habits.title LIKE ?
           OR habits.description LIKE ?
           OR habit_categories.category_name LIKE ?
        ORDER BY habits.created_at DESC
    """, (search, search, search))

def get_habit_with_owner(habit_id):
    return query_one("""
        SELECT habits.id, habits.user_id, habits.title, habits.description,
               habits.difficulty, habits.created_at, users.username as owner_username
        FROM habits
        JOIN users ON habits.user_id = users.id
        WHERE habits.id = ?
    """, (habit_id,))

def get_habit_by_id(habit_id):
    return query_one(
        "SELECT id, user_id, title, description, difficulty, created_at "
        "FROM habits WHERE id = ?",
        (habit_id,)
    )

def add_habit(user_id, title, description, difficulty):
    return execute(
        "INSERT INTO habits (user_id, title, description, difficulty) VALUES (?, ?, ?, ?)",
        (user_id, title, description, difficulty)
    )

def update_habit(habit_id, title, description, difficulty):
    execute(
        "UPDATE habits SET title = ?, description = ?, difficulty = ? WHERE id = ?",
        (title, description, difficulty, habit_id)
    )

def delete_habit(habit_id, user_id):
    execute(
        "DELETE FROM habits WHERE id = ? AND user_id = ?",
        (habit_id, user_id)
    )

def get_habits_by_user(user_id):
    return query("""
        SELECT habits.id, habits.user_id, habits.title, habits.description,
               habits.difficulty, habits.created_at,
               (SELECT COUNT(*) FROM habit_logs WHERE habit_id = habits.id) as log_count,
               (SELECT COUNT(*) FROM habit_participants
                WHERE habit_id = habits.id) as participant_count
        FROM habits
        WHERE habits.user_id = ?
        ORDER BY habits.created_at DESC
    """, (user_id,))

def add_habit_category(habit_id, category_name):
    execute(
        "INSERT INTO habit_categories (habit_id, category_name) VALUES (?, ?)",
        (habit_id, category_name)
    )

def delete_habit_categories(habit_id):
    execute("DELETE FROM habit_categories WHERE habit_id = ?", (habit_id,))

def get_habit_categories(habit_id):
    rows = query(
        "SELECT category_name FROM habit_categories WHERE habit_id = ?",
        (habit_id,)
    )
    return [row["category_name"] for row in rows]

def get_all_categories():
    return query("SELECT id, name FROM categories ORDER BY name")
