import sqlite3
from flask import Flask, render_template_string, request, g

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

@app.route('/')
def home():
    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
        <div class="badge badge-blue">Secure System v2.0</div>
        <h1>Employee Portal</h1>
        <p>Access centralized employee records securely.</p>
        <div style="margin-top: 20px;">
            <a href="/profile?user_id=2" class="btn">Login as Guest</a>
        </div>
    {% endblock %}
    """)

@app.route('/profile')
def profile():
    user_id = request.args.get('user_id')
    
    # Connect to Real DB
    db = get_db()
    # Vulnerable SQL Logic (Simulated for this specific IDOR level)
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if user:
        # If Admin, show red badge
        if user['role'] == 'admin':
            badge_color = "#ef4444" # Red
            badge_text = "ADMIN ACCESS"
            secret_display = f"<div style='background:#fee2e2; color:#b91c1c; padding:10px; border-radius:5px; margin-top:15px; font-weight:bold;'>⚠️ SECRET: {user['secret']}</div>"
        else:
            badge_color = "#3b82f6" # Blue
            badge_text = "Standard User"
            secret_display = ""

        return render_template_string(f"""
        {{% extends "base.html" %}}
        {{% block content %}}
            <div class="badge" style="background:{badge_color}; color:white">{badge_text}</div>
            <h1>{user['name']}</h1>
            <p>Role: {user['role']}</p>
            <p>Salary: {user['salary']}</p>
            {secret_display}
            <a href="/" class="btn" style="background:#64748b; margin-top:20px;">Logout</a>
        {{% endblock %}}
        """)
    
    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
        <h1>User Not Found</h1>
        <a href="/" class="btn">Go Back</a>
    {% endblock %}
    """)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
