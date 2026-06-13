from database import get_db_connection

# Connect database
conn = get_db_connection()
cursor = conn.cursor()

# Fetch all rows
cursor.execute("SELECT * FROM pages")
rows = cursor.fetchall()

# Print rows
for row in rows:
    print(row)

conn.close()