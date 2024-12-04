import sqlite3
import hashlib, uuid

# conn = sqlite3.connect('users.db')
# cursor = conn.cursor()

# # Create a table to store user information
# # cursor.execute('''
# #     CREATE TABLE IF NOT EXISTS users (
# #         id INTEGER PRIMARY KEY AUTOINCREMENT,
# #         username TEXT NOT NULL,
# #         cabin TEXT NOT NULL,
# #         email TEXT NOT NULL,
# #         password TEXT NOT NULL,
# #         phone TEXT NOT NULL,
# #         status TEXT NOT NULL,
# #         timings TEXT,
# #         device TEXT,
#           public_id TEXT
# #     )
# # ''')

# username = input("Enter your username: ")
# email = input("Enter your email: ")
# password = input("Enter your password: ")
# phone = input("Enter your phone: ")
# cabin = input("Enter your cabin: ")
# status = input("Enter your status: ")
# timings = input("Enter your timings: ")
# device = input("Enter your device MAC: ")
# public_id = str(uuid.uuid4())

# hashed_password = hashlib.sha256(password.encode()).hexdigest()
# cursor.execute(
#             """
#             INSERT INTO users (username, email, password, phone, cabin, status, timings, device, public_id)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#         """,
#             (username, email, hashed_password, phone, cabin, status, timings, device, public_id),
#         )

# conn.commit()
# conn.close()

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
# search_word = "b"
# print(search_word)
# if search_word == '':
#     query = "SELECT username, email, phone, cabin, status, timings from users ORDER BY username ASC"
#     cursor.execute(query)
#     faculty = cursor.fetchall()
#     print(faculty)
# else:    
#     cursor.execute("SELECT username, email, phone, cabin, status, timings FROM users WHERE username LIKE ? COLLATE NOCASE", ('%' + search_word + '%',))
#     numrows = int(cursor.rowcount)
#     faculty = cursor.fetchall()
#     print(faculty)
#     print(numrows)
# add a column to the table
cursor.execute("ALTER TABLE users ADD COLUMN IDS text")
# cursor.execute("ALTER TABLE users ADD COLUMN public_id text")
# drop column id, 
# cursor.execute("ALTER TABLE users DROP COLUMN uuid")
#rename column
# cursor.execute("ALTER TABLE users RENAME COLUMN old_id TO id")
conn.commit()
conn.close()
