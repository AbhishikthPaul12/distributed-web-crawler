import os
import sqlite3

# Define database path relative to this file to avoid working directory issues
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "crawler.db")

def get_db_connection():
    """Returns a SQLite connection to the crawler database."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initializes the database schema and performs migrations if needed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table already exists and check its schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='pages'")
    row = cursor.fetchone()
    
    if row:
        sql = row[0]
        # Check if "UNIQUE" is present in the URL column definition
        if "UNIQUE" not in sql.upper():
            print("Migrating pages table to add UNIQUE constraint on url...")
            try:
                cursor.execute("BEGIN TRANSACTION;")
                # Rename the old table
                cursor.execute("ALTER TABLE pages RENAME TO pages_old")
                
                # Create new table with UNIQUE constraint
                cursor.execute("""
                CREATE TABLE pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    content TEXT
                )
                """)
                
                # Copy data from pages_old to pages, deduplicating by url
                cursor.execute("""
                INSERT OR IGNORE INTO pages (id, url, title, content)
                SELECT id, url, title, content FROM pages_old GROUP BY url
                """)
                
                # Drop old table
                cursor.execute("DROP TABLE pages_old")
                conn.commit()
                print("Migration completed successfully.")
            except Exception as e:
                conn.rollback()
                print("Migration failed, rolling back. Error:", e)
        else:
            pass # Table 'pages' already has UNIQUE constraint
    else:
        # Table does not exist, create it from scratch
        print("Creating 'pages' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            content TEXT
        )
        """)
        conn.commit()
        print("Table created successfully.")
    
    conn.close()

def save_page(url, title, content):
    """Saves a page's crawled data, ignoring duplicates."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO pages (url, title, content)
        VALUES (?, ?, ?)
        """, (url, title, content))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def fetch_all_pages():
    """Fetches all pages from the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, content FROM pages")
        return cursor.fetchall()
    finally:
        conn.close()

# Auto-initialize database on import
init_db()