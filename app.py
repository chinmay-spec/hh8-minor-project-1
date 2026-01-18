import sqlite3
import time
from flask import Flask, render_template, request, render_template_string, g, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_signing_cookies' 
DATABASE = 'database.db'
COMMENTS = []

# Security: Rate Limiting Storage
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
    # Security: Session Hijacking Prevention (IP Binding Check)
    if 'user_id' in session:
        if session.get('ip') == request.remote_addr:
            return redirect(url_for('dashboard_route'))
        else:
            session.clear() 

    error = None
    ip = request.remote_addr
    current_time = time.time()

    # Security: Brute Force Protection (Rate Limiting)
    if ip in failed_logins:
        attempts = failed_logins[ip]['attempts']
        ban_time = failed_logins[ip]['ban_time']
        if attempts >= 3:
            if current_time < ban_time:
                remaining = int(ban_time - current_time)
                # 🛑 THIS IS THE RED SCREEN FOR TEST 3
                return render_template_string(f"<h1 style='color:red; text-align:center; font-family:sans-serif;'>🚫 ACCESS DENIED: Too many attempts. Wait {remaining}s</h1>")
            else:
                failed_logins[ip] = {'attempts': 0, 'ban_time': 0}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        # Security: Parameterized Queries (Prevents SQL Injection for TEST 1)
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()

        if user:
            if ip in failed_logins: failed_logins.pop(ip)
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['ip'] = request.remote_addr 
            
            return redirect(url_for('dashboard_route'))
        else:
            if ip not in failed_logins: failed_logins[ip] = {'attempts': 0, 'ban_time': 0}
            failed_logins[ip]['attempts'] += 1
            if failed_logins[ip]['attempts'] >= 3:
                failed_logins[ip]['ban_time'] = current_time + 60
                error = "⛔ ACCOUNT LOCKED: Excessive login attempts."
            else:
                error = "Invalid Credentials"
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('ip') != request.remote_addr:
        session.clear()
        return "<h1>⛔ Security Alert: Session Hijacking Attempt Detected.</h1>"

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    return dashboard_view(user)

def dashboard_view(user):
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
        <a href="/feedback" class="btn" style="margin-top:20px;">Public Feedback</a>
        <a href="/logout" class="btn" style="background:#64748b; margin-top:20px;">Logout</a>
    {{% endblock %}}
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        COMMENTS.append(request.form['comment'])
    
    # Security: Jinja2 Auto-Escaping (Prevents XSS for TEST 2)
    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
        <h1>Public Feedback</h1>
        <form method="post"><input name="comment" placeholder="Type here..." style="width:100%; padding:10px;"><button class="btn" style="margin-top:10px;">Post</button></form>
        <hr>
        {% for c in comments %}
            <div class='badge' style='display:block; text-align:left; margin:5px; background:#e2e8f0; color:#1e293b;'>{{ c }}</div>
        {% endfor %}
        <br><a href="/dashboard" class="btn" style="background:#64748b;">Back</a>
    {% endblock %}
    """, comments=COMMENTS)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
