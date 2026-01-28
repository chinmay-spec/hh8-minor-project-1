import sqlite3
import time
import datetime
from flask import Flask, render_template, request, render_template_string, g, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_signing_cookies' 
DATABASE = 'database.db'
COMMENTS = []
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
    if 'user_id' in session:
        if session.get('ip') == request.remote_addr:
            return redirect(url_for('dashboard_route'))
        else:
            session.clear() 

    error = None
    ip = request.remote_addr
    current_time = time.time()

    if ip in failed_logins:
        attempts = failed_logins[ip]['attempts']
        ban_time = failed_logins[ip]['ban_time']
        if attempts >= 3:
            if current_time < ban_time:
                remaining = int(ban_time - current_time)
                return render_template_string(f"""
                {{% extends "base.html" %}}
                {{% block content %}}
                    <div style="text-align:center;">
                        <h1 style='color:#ef4444; font-size:40px;'>🚫</h1>
                        <h2 style='color:#ef4444;'>Access Denied</h2>
                        <p>Too many failed attempts.<br>Please wait <b style="color:#1e293b">{remaining}s</b>.</p>
                    </div>
                {{% endblock %}}
                """)
            else:
                failed_logins[ip] = {'attempts': 0, 'ban_time': 0}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
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
                error = "Account Locked (Security Policy)"
            else:
                error = "Invalid Credentials"
    
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard_route():
    if 'user_id' not in session: return redirect(url_for('login'))
    if session.get('ip') != request.remote_addr:
        session.clear()
        return "<h1>⛔ Security Alert: Session Hijacking Attempt Detected.</h1>"

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    return dashboard_view(user)

def dashboard_view(user):
    # Fake premium data for aesthetics
    today = datetime.date.today().strftime("%B %d, %Y")
    
    if user['role'] == 'admin':
        badge_style = "background:#fee2e2; color:#b91c1c;"
        badge_text = "ADMINISTRATOR"
        secret_box = f"""
        <div style='background:#fef2f2; border:1px solid #fee2e2; padding:15px; border-radius:12px; margin-top:20px;'>
            <p style='color:#b91c1c; font-weight:bold; margin:0; font-size:12px;'>🔐 TOP SECRET CLEARANCE</p>
            <p style='color:#7f1d1d; margin-top:5px; font-family:monospace;'>{user['secret']}</p>
        </div>"""
    else:
        badge_style = "background:#dbeafe; color:#1e40af;"
        badge_text = "STANDARD ACCOUNT"
        secret_box = ""

    return render_template_string(f"""
    {{% extends "base.html" %}}
    {{% block content %}}
        <div style="text-align:center; margin-bottom:20px;">
            <div class="badge" style="{badge_style}">{badge_text}</div>
            <h1>Good evening, {user['username']}</h1>
            <p>Welcome back to the SecurePortal.</p>
        </div>

        <div style="background:rgba(255,255,255,0.6); padding:20px; border-radius:16px; margin-bottom:20px;">
            <div class="card-row"><span class="label">User ID</span><span class="value">#{user['id']}</span></div>
            <div class="card-row"><span class="label">Role</span><span class="value" style="text-transform:capitalize">{user['role']}</span></div>
            <div class="card-row"><span class="label">Status</span><span class="value" style="color:#10b981;">● Active</span></div>
            <div class="card-row"><span class="label">Last Login</span><span class="value">{today}</span></div>
            <div class="card-row"><span class="label">Salary Tier</span><span class="value">{user['salary']}</span></div>
        </div>

        {secret_box}

        <br>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
            <a href="/profile?user_id={user['id']}" class="btn" style="background:#f59e0b;">⚠️ Vulnerability Demo</a>
            <a href="/feedback" class="btn" style="background:#6366f1;">Feedback Hub</a>
        </div>
        <a href="/logout" class="btn" style="background:#cbd5e1; color:#475569; margin-top:10px;">Sign Out</a>
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
    
    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
        <div style="text-align:center;">
            <h1>Community Feedback</h1>
            <p>Share your thoughts securely.</p>
        </div>
        
        <form method="post" style="margin-top:20px;">
            <input name="comment" placeholder="Write a comment..." required>
            <button class="btn">Post Comment</button>
        </form>

        <div style="margin-top:30px;">
            <h3 style="font-size:14px; color:#94a3b8; text-transform:uppercase; margin-bottom:15px;">Recent Activity</h3>
            {% for c in comments %}
                <div style='background:white; padding:15px; border-radius:12px; margin-bottom:10px; box-shadow:0 2px 10px rgba(0,0,0,0.03); animation: floatUp 0.5s ease forwards;'>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:24px; height:24px; background:#e0e7ff; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:10px; color:#6366f1; font-weight:bold;">U</div>
                        <span style="color:#1e293b; font-size:14px;">{{ c }}</span>
                    </div>
                </div>
            {% endfor %}
        </div>
        <br>
        <a href="/dashboard" class="btn" style="background:transparent; color:#64748b; border:1px solid #cbd5e1;">&larr; Back to Dashboard</a>
    {% endblock %}
    """, comments=COMMENTS)

@app.route('/profile')
def profile():
    target_id = request.args.get('user_id')
    if not target_id: return redirect(url_for('dashboard_route'))

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()

    if user:
        return render_template_string("""
        {% extends "base.html" %}
        {% block content %}
            <div style="border-left: 4px solid #f59e0b; padding-left: 20px; margin-bottom: 20px;">
                <h2 style="color:#b45309; font-size:16px;">⚠️ VULNERABILITY DEMO (IDOR)</h2>
                <p style="font-size:13px;">You are viewing Profile ID: <b>{{ target_id }}</b>. Change the URL ID to see others.</p>
            </div>

            <div style="text-align:center; margin-bottom:20px;">
                <div style="width:80px; height:80px; background:#e0e7ff; color:#6366f1; font-size:32px; font-weight:bold; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 15px auto;">
                    {{ user['username'][0].upper() }}
                </div>
                <h1>{{ user['username'] }}</h1>
                <p>{{ user['role'] }} at SecureCorp</p>
            </div>

            <div style="background:white; padding:20px; border-radius:16px;">
                <div class="card-row"><span class="label">Employee ID</span><span class="value">#{{ user['id'] }}</span></div>
                <div class="card-row"><span class="label">Salary</span><span class="value">{{ user['salary'] }}</span></div>
                <div class="card-row"><span class="label">Clearance</span><span class="value">{{ user['role'] }}</span></div>
                <div class="card-row"><span class="label">Secret</span><span class="value" style="font-family:monospace; color:#ef4444;">{{ user['secret'] }}</span></div>
            </div>

            <br>
            <a href="/dashboard" class="btn" style="background:#cbd5e1; color:#475569;">Back to Safety</a>
        {% endblock %}
        """, target_id=target_id, user=user)
    else:
        return "User not found"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
