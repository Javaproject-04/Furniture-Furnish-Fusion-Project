import sqlite3

conn = sqlite3.connect("furnishfusion.db")
cursor = conn.cursor()

# show tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

print("\n--- USERS ---")
cursor.execute("SELECT * FROM users")
for row in cursor.fetchall():
    print(row)

print("\n--- PRODUCTS ---")
cursor.execute("SELECT * FROM products")
for row in cursor.fetchall():
    print(row)

print("\n--- ORDERS ---")
cursor.execute("SELECT * FROM orders")
for row in cursor.fetchall():
    print(row)

conn.close()
