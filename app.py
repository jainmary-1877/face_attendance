from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from config import db_config
from werkzeug.security import generate_password_hash, check_password_hash
from config import secret_key
import csv

app = Flask(__name__)
app.secret_key = secret_key

db = mysql.connector.connect(**db_config)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email=request.form['email']

        cursor.execute("INSERT INTO teachers (username, password,email) VALUES (%s, %s,%s)", (username, password,email))
        db.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
       

        cursor.execute("SELECT password FROM teachers WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[0], password):
            session['username'] = username
            return redirect(url_for('attendance'))  # Later redirect to dashboard
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/attendance')
def attendance():
    if 'username' not in session:
        return redirect(url_for('login'))

    attendance_list = []
    try:
        with open('Attendance.csv', 'r') as file:
            reader = csv.reader(file)
            attendance_list = list(reader)
    except FileNotFoundError:
        attendance_list = []

    return render_template('attendance.html', attendance=attendance_list)
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session
    return redirect(url_for('home'))  # Redirect to home/index.html

if __name__ == '__main__':
    app.run(debug=True)
