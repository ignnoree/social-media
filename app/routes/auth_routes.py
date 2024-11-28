from flask import Blueprint, request, redirect, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import db,getusername

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        if not (username and password and email):
            return render_template('register.html', message='ALL FIELDS ARE REQUIRED!')
        hashed_password = generate_password_hash(password)
        db.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', username, email, hashed_password)
        return redirect('/login')
    return render_template('register.html')

@bp.route('/login', methods=['POST', 'GET'])
def login():
    if 'user_id' in session:
        return redirect('/')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.execute('SELECT * FROM users WHERE username = ?', username)
        user = user[0] if user else None
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login successful!')
            return redirect('/')
        return render_template('login.html', message='Invalid login credentials')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/register')


@bp.route('/delete')
def deleteaccount():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete-account':
            username = getusername(session.get('user_id'))
            db.execute('delete from posts where username=?',username)
            db.execute('delete from likes where author = ?',username)
            db.execute('delete from comments where username= ?', username)
            db.execute('delete from users where username= ?', username)

            return redirect('')
    elif request.method == 'GET':
        return render_template('deleteacc.html',)
