import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql', 'w') as f:
    f.write('DROP TABLE IF EXISTS users; CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, role TEXT, secret TEXT, salary TEXT);')

with connection:
    connection.execute("DROP TABLE IF EXISTS users")
    connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, role TEXT, secret TEXT, salary TEXT)")

    # Insert the data (Admin and Guest)
    connection.execute("INSERT INTO users (id, name, role, secret, salary) VALUES (1, 'Administrator', 'admin', 'FLAG{SQL_IS_AWESOME}', '$120,000')")
    connection.execute("INSERT INTO users (id, name, role, secret, salary) VALUES (2, 'Guest User', 'user', 'No secrets here', '$0')")

connection.commit()
connection.close()

print("Database initialized successfully!")
