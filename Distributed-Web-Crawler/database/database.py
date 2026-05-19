import sqlite3

# Connect database
conn = sqlite3.connect("crawler.db")

# Create cursor
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    title TEXT,
    content TEXT
)
""")

conn.commit()

print("Database Ready")