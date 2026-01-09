# Authentication Bypass Demo (Minor Project 1)

## Project Description
This project is a demonstration of a logical flaw in web authentication known as **Insecure Direct Object Reference (IDOR)**. It shows how an attacker can access administrative accounts simply by manipulating URL parameters (Authentication Bypass).

## Tools Used
* **Python:** Core programming language.
* **Flask:** Web framework for the server.
* **Browser:** To manipulate the URL.

## How to Run the Project
1.  Install Python.
2.  Install Flask: `pip install flask`
3.  Run the app: `python app.py`
4.  Open your browser and go to `http://127.0.0.1:5000`.

## How to Test the Vulnerability
1.  Click the link on the homepage to log in as a "Guest".
2.  Observe the URL: `http://127.0.0.1:5000/profile?user_id=2`
3.  **The Exploit:** Change the `user_id=2` in the URL bar to `user_id=1`.
4.  Press Enter. You will now see the Admin Panel and the secret flag.

## What I Learned
I learned that relying solely on client-side input (like URL parameters) for identification is dangerous. Secure applications must use **Server-Side Validation** and Session Management to ensure the user requesting the data is authorized to see it.
