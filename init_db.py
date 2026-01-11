import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql', 'w') as f:
    f.write('DROP TABLE IF EXISTS users; CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, secret TEXT, salary TEXT);')

with connection:
    connection.execute("DROP TABLE IF EXISTS users")
    # Added 'username' and 'password' columns
    connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, secret TEXT, salary TEXT)")
    
    # Admin User (The target)
    connection.execute("INSERT INTO users (username, password, role, secret, salary) VALUES ('admin', 'Sup3rS3cr3tP@ssw0rd', 'admin', 'FLAG{SQL_INJECTION_MASTER}', '$120,000')")
    
    # Guest User
    connection.execute("INSERT INTO users (username, password, role, secret, salary) VALUES ('guest', 'guest123', 'user', 'No secrets here', '$0')")

connection.commit()
connection.close()
print("Database updated with Passwords!")
