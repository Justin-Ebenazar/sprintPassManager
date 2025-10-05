from flask import Flask, redirect, render_template, request, session, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os
import webview
import threading
import signal
import time

app = Flask(__name__)
app.secret_key = "a3f1c9d8e2b4f6ajustin7c1d2e3f4a5b6c7d8"

def derive_key(user_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(user_password.encode()))

def database_connection():
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            app_name TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT,
            number TEXT,
            encrypted_password TEXT NOT NULL,
            salt BLOB NOT NULL,
            icon_filename TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) on delete cascade
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def login():
    database_connection()
    return render_template('login_page.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.get_json().get('username')
    input_password = request.get_json().get('password')
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    if result is None or not check_password_hash(result[0], input_password):
        return jsonify({"status": "failure","message": "Invalid credentials","category": "password-error"})
    session['user'] = username
    session['pass'] = input_password
    return jsonify({"status": "success","redirect": "/homepage"})

@app.route('/register', methods=['POST'])
def sign_up():
    username = request.form.get('username')
    password = generate_password_hash(request.form.get('password'))
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("Username already exists. Please choose a different one.", "message")
    conn.close()
    return redirect('/')

@app.route('/homepage')
def homepage():
    if not session.get('user'):
        return redirect('/')
    app_credentials = []
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (session['user'],))
    user_id = cursor.fetchone()[0]
    cursor.execute('SELECT id, app_name, username, email, number, encrypted_password, salt, icon_filename FROM credentials WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    for row in rows:
        cred_id, app_name, username, email, number, encrypted_password, salt, icon_filename = row
        key = derive_key(session['pass'], salt)
        fernet = Fernet(key)
        decrypted_password = fernet.decrypt(encrypted_password).decode()
        app_credentials.append({
            'id': cred_id,
            'app_name': app_name,
            'username': username,
            'email': email,
            'phone': number,
            'password': decrypted_password,
            'icon_filename': icon_filename or 'default.png'
        })
    conn.close()
    return render_template('homepage.html', credential=app_credentials)

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('pass', None)
    return redirect('/')

@app.route('/change_master_password', methods=['POST'] )
def change_master_password():
    data = request.get_json()
    old_password = data.get('current_password')
    new_password = data.get('new_password')
    if not session.get('user') or not old_password or not new_password:
        return jsonify({"status": "failure", "message": "Missing data"})
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (session['user'],))
    result = cursor.fetchone()
    if result is None or not check_password_hash(result[0], old_password):
        conn.close()
        return jsonify({"status": "failure", "message": "Old password incorrect"})
    hashed_new_password = generate_password_hash(new_password)
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_new_password, session['user']))
    conn.commit()
    conn.close()
    session['pass'] = new_password
    return jsonify({"status": "success", "message": "Password updated"})

@app.route('/add', methods=['POST'])
def add_credential():
    if not session.get('user') or not session.get('pass'):
        return redirect('/')
    app_name = request.form.get('app_name')
    username = request.form.get('username')
    email = request.form.get('email')
    number = request.form.get('phone')
    raw_password = request.form.get('password')
    icon_filename = request.form.get('icon_filename') or 'default.png'
    salt = os.urandom(16)
    key = derive_key(session['pass'], salt)
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(raw_password.encode())
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (session['user'],))
    user_id = cursor.fetchone()[0]
    cursor.execute('''
        INSERT INTO credentials (user_id, app_name, username, email, number, encrypted_password, salt, icon_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, app_name, username, email, number, encrypted_password, salt, icon_filename))
    conn.commit()
    conn.close()
    # flash("Credential added successfully!", "success")
    return redirect('/homepage')

@app.route('/update', methods=['POST'])
def update_credential():
    if not session.get('user') or not session.get('pass'):
        return redirect('/')
    cred_id = request.form.get('id')
    app_name = request.form.get('app_name')
    username = request.form.get('username')
    email = request.form.get('email')
    number = request.form.get('phone')
    raw_password = request.form.get('password')
    icon_filename = request.form.get('icon_filename') or 'default.png'
    salt = os.urandom(16)
    key = derive_key(session['pass'], salt)
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(raw_password.encode())
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE credentials
        SET app_name = ?, username = ?, email = ?, number = ?, encrypted_password = ?, salt = ?, icon_filename = ?
        WHERE id = ?
    ''', (app_name, username, email, number, encrypted_password, salt, icon_filename, cred_id))
    conn.commit()
    conn.close()
    # flash("Credential updated successfully!", "success")
    return redirect('/homepage')

@app.route('/delete', methods=['POST'])
def delete_credential():
    if not session.get('user'):
        return redirect('/')
    cred_id = request.form.get('id')
    conn = sqlite3.connect('password_manager.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM credentials WHERE id = ?', (cred_id,))
    conn.commit()
    conn.close()
    # flash("Credential deleted successfully!", "success")
    return redirect('/homepage')

@app.route('/delete_account', methods = ['POST'])
def delete_account():
    print(request.get_json().get('password'))
    if(not session.get('user') or request.get_json().get('password') != session.get('pass')):
        return jsonify({"status": "failure","message": "Password thappu"})
    conn = sqlite3.connect('password_manager.db')
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (session['user'],))
    conn.commit()
    conn.close()
    session.pop('user', None)
    session.pop('pass', None)
    return jsonify({"status": "success","redirect": "/"})
    
# def start_flask():
#     app.run(debug=False, use_reloader=False)

# if __name__ == '__main__':
#     threading.Thread(target=start_flask, daemon=True).start()
#     time.sleep(1)  # Give Flask time to start

#     window = webview.create_window("Password Manager", "http://127.0.0.1:5000")

#     def on_closed():
#         print("Window closed. Exiting...")
#         sys.exit(0)

#     webview.start(on_closed, gui='qt')

app.run(debug=True)
