import sqlite3
import time
from flask import Flask, render_template, request, render_template_string, g, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_signing_cookies' # Required for session management
DATABASE = 'database.db'
COMMENTS = []

# Rate Limiting Dictionary
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
    # 🛡️ DEFENSE: If already logged in, check IP before showing dashboard
    if 'user_id' in session:
        if session.get('ip') == request.remote_addr:
            return redirect(url_for('dashboard_route'))
        else:
            session.clear() # Invalid IP? Kick them out!

    error = None
    ip = request.remote_addr
    current_time = time.time()

    # Rate Limiting Logic (Day 6)
    if ip in failed_logins:
        attempts = failed_logins[ip]['attempts']
        ban_time = failed_logins[ip]['ban_time']
        if attempts >= 3:
            if current_time < ban_time:
                remaining = int(ban_time - current_time)
                return render_template_string(f"<h1 style='color:red; text-align:center;'>🚫 BANNED: Wait {remaining}s</h1>")
            else:
                failed_logins[ip] = {'attempts': 0, 'ban_time': 0}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        # Secure Login (Day 4)
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()

        if user:
            if ip in failed_logins: failed_logins.pop(ip)
            
            # ✅ SESSION BINDING: Save User ID AND their IP Address
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['ip'] = request.remote_addr # <-- The Lock 🔒
            
            return redirect(url_for('dashboard_route'))
        else:
            if ip not in failed_logins: failed_logins[ip] = {'attempts': 0, 'ban_time': 0}
            failed_logins[ip]['attempts'] += 1
            if failed_logins[ip]['attempts'] >= 3:
                failed_logins[ip]['ban_time'] = current_time + 60
                error = "⛔ ACCOUNT LOCKED"
            else:
                error = "Invalid Credentials"
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard_route():
    # 🛡️ DEFENSE: Check if user is logged in AND IP matches
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('ip') != request.remote_addr:
        session.clear()
        return "<h1>⛔ Session Hijacking Detected! IP Address Mismatch.</h1>"

    # Fetch fresh user data
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
        <a href="/logout" class="btn" style="background:#64748b; margin-top:20px;">Logout</a>
    {{% endblock %}}
    """)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    # ... (Same secure feedback code as Day 5) ...
    if request.method == 'POST':
        COMMENTS.append(request.form['comment'])
    
    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
        <h1>Public Feedback</h1>
        <form method="post"><input name="comment"><button>Post</button></form>
        {% for c in comments %}<div>{{ c }}</div>{% endfor %}
        <a href="/dashboard">Back</a>
    {% endblock %}
    """, comments=COMMENTS)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
