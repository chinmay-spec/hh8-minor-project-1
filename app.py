import sqlite3
import time
from flask import Flask, render_template, request, render_template_string, g

app = Flask(__name__)
DATABASE = 'database.db'
COMMENTS = []

# 🛡️ RATE LIMITING STORAGE (Server-Side Validation)
failed_logins = {}

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
    ip = request.remote_addr
    current_time = time.time()

    # 1. Check if IP is banned
    if ip in failed_logins:
        attempts = failed_logins[ip]['attempts']
        ban_time = failed_logins[ip]['ban_time']

        if attempts >= 3:
            if current_time < ban_time:
                remaining = int(ban_time - current_time)
                return render_template_string(f"""
                <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
                    <h1 style="color:red;">🚫 ACCESS DENIED 🚫</h1>
                    <p>Too many failed attempts.</p>
                    <p>Please wait <b>{remaining} seconds</b>.</p>
                </div>
                """)
            else:
                # Reset after ban is over
                failed_logins[ip] = {'attempts': 0, 'ban_time': 0}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        user = db.execute(query, (username, password)).fetchone()

        if user:
            # Success: Reset counter
            if ip in failed_logins:
                failed_logins.pop(ip)
            return dashboard(user)
        else:
            # Failure: Increment counter
            if ip not in failed_logins:
                failed_logins[ip] = {'attempts': 0, 'ban_time': 0}

            failed_logins[ip]['attempts'] += 1

            if failed_logins[ip]['attempts'] >= 3:
                failed_logins[ip]['ban_time'] = current_time + 60 # Ban for 60s
                error = "⛔ ACCOUNT LOCKED: Too many attempts"
            else:
                left = 3 - failed_logins[ip]['attempts']
                error = f"Invalid Credentials. {left} attempts remaining."

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
        {secret_display}
        <br>
        <a href="/feedback" class="btn" style="margin-top:20px;">Go to Public Feedback</a>
        <a href="/" class="btn" style="background:#64748b; margin-top:20px;">Logout</a>
    {{% endblock %}}
    """)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        comment = request.form['comment']
        COMMENTS.append(comment)

    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
        <h1>Public Feedback</h1>
        <p>Leave a comment for the team:</p>
        <form method="post">
            <input type="text" name="comment" style="width:100%; padding:10px;" placeholder="Type here...">
            <button type="submit" class="btn" style="margin-top:10px;">Post Comment</button>
        </form>
        <hr>
        <h3>Recent Comments:</h3>
        {% for c in comments %}
            <div class='badge' style='display:block; text-align:left; margin:5px; background:#e2e8f0; color:#1e293b;'>
                {{ c }} 
            </div>
        {% endfor %}
        <br>
        <a href="/" class="btn" style="background:#64748b;">Back to Home</a>
    {% endblock %}
    """, comments=COMMENTS)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
