DROP TABLE IF EXISTS habit_logs;
DROP TABLE IF EXISTS habit_participants;
DROP TABLE IF EXISTS habit_comments;
DROP TABLE IF EXISTS habit_notes;
DROP TABLE IF EXISTS habit_categories;
DROP TABLE IF EXISTS habits;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO categories (name) VALUES 
    ('urheilu'), 
    ('hyvinvointi'), 
    ('terveys'), 
    ('oppiminen'), 
    ('työ'), 
    ('harrastus');

CREATE TABLE habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    difficulty TEXT DEFAULT 'neutraali',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE habit_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
    FOREIGN KEY (category_name) REFERENCES categories (name)
);

CREATE TABLE habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    UNIQUE(habit_id, user_id, log_date),
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE habit_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(habit_id, user_id),
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE habit_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE habit_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE INDEX idx_habits_user_id ON habits (user_id);
CREATE INDEX idx_habit_logs_user_id ON habit_logs (user_id);
CREATE INDEX idx_habit_participants_user_id ON habit_participants (user_id);
