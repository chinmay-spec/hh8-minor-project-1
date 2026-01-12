import sqlite3
from flask import Flask, render_template, request, render_template_string, g

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()

        # ✅ SECURE CODE ✅
        # We use '?' placeholders. The Database library handles the safety.
        # No more f-strings!
        query = "SELECT * FROM users WHERE username = ? AND password = ?"

        # We pass the data as a separate tuple (username, password)
        user = db.execute(query, (username, password)).fetchone()

        if user:
            return dashboard(user)
        else:
            error = "Invalid Credentials"

    return render_template('login.html', error=error)

def dashboard(user):
    if user['role'] == 'admin':
        badge_color = "#ef4444"
        badge_text = "ADMIN ACCESS"
        secret_display = f"<div style='background:#fee2e2; color:#b91c1c; padding:10px; border-radius:5px; margin-top:15px; font-weight:bold;'>⚠️ SECRET: {user['secret']}</div>"
    else:
        badge_color = "#3b82f6"
        badge_text = "Standard User"
        secret_display = ""

    return render_template_string(f"""
    {{% extends "base.html" %}}
    {{% block content %}}
        <div class="badge" style="background:{badge_color}; color:white">{badge_text}</div>
        <h1>Welcome, {user['username']}</h1>
        <p>Role: {user['role']}</p>
        <p>Salary: {user['salary']}</p>
        {secret_display}
        <a href="/" class="btn" style="background:#64748b; margin-top:20px;">Logout</a>
    {{% endblock %}}
    """)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
