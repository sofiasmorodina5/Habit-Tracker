import sqlite3

DATABASE = "database.db"

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def query(sql, params=None):
    params = params if params is not None else []
    db = get_db()
    result = db.execute(sql, params).fetchall()
    db.close()
    return result

def query_one(sql, params=None):
    params = params if params is not None else []
    db = get_db()
    result = db.execute(sql, params).fetchone()
    db.close()
    return result

def execute(sql, params=None):
    params = params if params is not None else []
    db = get_db()
    result = db.execute(sql, params)
    db.commit()
    last_id = result.lastrowid
    db.close()
    return last_id
