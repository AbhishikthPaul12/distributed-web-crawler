import sqlite3

# Connect database
conn = sqlite3.connect("crawler.db")

cursor = conn.cursor()

# Fetch all rows
cursor.execute("SELECT * FROM pages")

rows = cursor.fetchall()

# Print rows
for row in rows:
    print(row)

conn.close()