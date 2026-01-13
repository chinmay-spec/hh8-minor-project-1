import sqlite3
from flask import Flask, render_template, request, render_template_string, g

app = Flask(__name__)
DATABASE = 'database.db'

# Store comments in memory
COMMENTS = []

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
        
        # ✅ SECURE LOGIN (Parameterized Queries)
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        user = db.execute(query, (username, password)).fetchone()

        if user:
            return dashboard(user)
        else:
            error = "Invalid Credentials"
    
    return render_template('login.html', error=error)

def dashboard(user):
    # Determine Badge Color
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
    
    # ✅ SECURE FEEDBACK: Pass list to template
    # Jinja2 will automatically "escape" dangerous scripts
    
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
