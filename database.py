import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            full_name TEXT,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(user_id, full_name, username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, full_name, username)
        VALUES (?, ?, ?)
    ''', (user_id, full_name, username))
    conn.commit()
    conn.close()

def user_exists(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
