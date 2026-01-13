import sqlite3
from flask import Flask, render_template, request, render_template_string, g

app = Flask(__name__)
DATABASE = 'database.db'

# Store comments in memory for now (Reset when server restarts)
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
        # Secure Login (Fixed yesterday)
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        user = db.execute(query, (username, password)).fetchone()

        if user:
            return dashboard(user)
        else:
            error = "Invalid Credentials"
    return render_template('login.html', error=error)

def dashboard(user):
    return render_template_string(f"""
    {{% extends "base.html" %}}
    {{% block content %}}
        <h1>Welcome, {user['username']}</h1>
        <a href="/feedback" class="btn">Go to Public Feedback</a>
        <a href="/" class="btn" style="background:#64748b;">Logout</a>
    {{% endblock %}}
    """)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        comment = request.form['comment']
        COMMENTS.append(comment)

    # 🚨 VULNERABILITY: We are manually looping and marking text as SAFE 🚨
    # This tells the browser "Trust this code", allowing scripts to run.
    comments_html = "".join([f"<div class='badge' style='display:block; text-align:left; margin:5px;'>{c}</div>" for c in COMMENTS])

    return render_template_string(f"""
    {{% extends "base.html" %}}
    {{% block content %}}
        <h1>Public Feedback</h1>
        <p>Leave a comment for the team:</p>
        <form method="post">
            <input type="text" name="comment" style="width:100%; padding:10px;" placeholder="Type here...">
            <button type="submit" class="btn" style="margin-top:10px;">Post Comment</button>
        </form>
        <hr>
        <h3>Recent Comments:</h3>
        {comments_html} <br>
        <a href="/" class="btn" style="background:#64748b;">Back to Home</a>
    {{% endblock %}}
    """)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
