from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    # This HTML uses the new CSS classes we created
    return render_template_string("""
    {% extends "base.html" %}
    {% block content %}
        <div class="badge badge-blue">Internal Tool v1.0</div>
        <h1>Employee Portal</h1>
        <p>Welcome to the secure internal network. Please verify your identity to access sensitive documents.</p>
        <a href="#" class="btn">Authenticating...</a>
    {% endblock %}
    """)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
