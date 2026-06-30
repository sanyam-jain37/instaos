import sqlite3

conn = sqlite3.connect("data/reels.db")

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM reels")
count = cursor.fetchone()[0]

print(f"\nTotal reels in database: {count}\n")

cursor.execute("""
SELECT id, name, folder
FROM reels
LIMIT 20
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()