import sqlite3
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from db import DATABASE


USER_COUNT = 1000
HABIT_COUNT = 10**5
LOGS_PER_HABIT = 10
LOG_COUNT = HABIT_COUNT * LOGS_PER_HABIT
PARTICIPANTS_PER_HABIT = 2
TEST_PASSWORD = "salasana123"
DIFFICULTIES = ("helppo", "neutraali", "vaativa")
BASE_DATE = date(2026, 1, 1)


def clear_database(db):
    db.execute("DELETE FROM habit_logs")
    db.execute("DELETE FROM habit_participants")
    db.execute("DELETE FROM habit_comments")
    db.execute("DELETE FROM habit_notes")
    db.execute("DELETE FROM habit_categories")
    db.execute("DELETE FROM habits")
    db.execute("DELETE FROM users")


def user_rows(password_hash):
    for user_id in range(1, USER_COUNT + 1):
        yield "test_user_" + str(user_id), password_hash


def habit_rows():
    for habit_id in range(1, HABIT_COUNT + 1):
        user_id = (habit_id - 1) % USER_COUNT + 1
        difficulty = DIFFICULTIES[(habit_id - 1) % 3]
        yield (
            user_id,
            "Testitapa " + str(habit_id),
            "Suuren tietomäärän testitapa " + str(habit_id),
            difficulty
        )


def participant_rows():
    for habit_id in range(1, HABIT_COUNT + 1):
        owner_index = (habit_id - 1) % USER_COUNT
        for offset in range(1, PARTICIPANTS_PER_HABIT + 1):
            participant_index = (owner_index + offset) % USER_COUNT
            yield habit_id, participant_index + 1


def log_rows():
    for habit_id in range(1, HABIT_COUNT + 1):
        owner_user_id = (habit_id - 1) % USER_COUNT + 1
        for day_offset in range(LOGS_PER_HABIT):
            log_date = BASE_DATE + timedelta(days=day_offset)
            yield habit_id, owner_user_id, log_date.isoformat()


def main():
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")

    try:
        clear_database(db)

        print("Creating users...")
        password_hash = generate_password_hash(TEST_PASSWORD)
        db.executemany(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            user_rows(password_hash)
        )

        print("Creating habits...")
        db.executemany(
            """INSERT INTO habits (user_id, title, description, difficulty)
               VALUES (?, ?, ?, ?)""",
            habit_rows()
        )

        print("Adding participants...")
        db.executemany(
            "INSERT INTO habit_participants (habit_id, user_id) VALUES (?, ?)",
            participant_rows()
        )

        print("Adding habit logs...")
        db.executemany(
            "INSERT INTO habit_logs (habit_id, user_id, log_date) VALUES (?, ?, ?)",
            log_rows()
        )

        db.commit()
    finally:
        db.close()

    print("Test data created.")
    print("Test account: test_user_1 / " + TEST_PASSWORD)


if __name__ == "__main__":
    main()
