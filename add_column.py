import sqlite3

def add_google_id_column():
    conn = sqlite3.connect('diabeticare.db')
    cursor = conn.cursor()
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'google_id' not in columns:
        print("Adding google_id column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN google_id VARCHAR(100)")
        # SQLite doesn't support ADD CONSTRAINT UNIQUE in ALTER TABLE directly,
        # but the column itself is fine. The ORM enforces uniqueness partially, or we can create an index.
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_google_id ON users(google_id)")
        conn.commit()
        print("Column and index added successfully.")
    else:
        print("Column google_id already exists.")
    conn.close()

if __name__ == '__main__':
    add_google_id_column()
