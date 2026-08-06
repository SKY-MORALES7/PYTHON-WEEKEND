import sqlite3

conn = sqlite3.connect('db.sqlite3')
try:
    conn.execute("ALTER TABLE core_event ADD COLUMN sponsors_title VARCHAR(255) DEFAULT ''")
    print("Column added.")
except Exception as e:
    print(f"Error (maybe column exists): {e}")

try:
    conn.execute("ALTER TABLE core_event ADD COLUMN schedule_title VARCHAR(255) DEFAULT ''")
    print("Column schedule_title added.")
except Exception as e:
    print(f"Error (maybe column exists): {e}")

conn.commit()
conn.close()
