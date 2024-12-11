from flask import Blueprint, request, redirect, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import db,getusername,safe_query,jwt
from flask import jsonify
from flask import jsonify
from flask_jwt_extended import create_access_token,get_jwt_identity,set_access_cookies,unset_jwt_cookies,create_access_token,create_refresh_token,jwt_required, verify_jwt_in_request
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

bp = Blueprint('auth', __name__)

@csrf.exempt
@bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        verify_jwt_in_request()
        username=get_jwt_identity()  
        return redirect('/')
    except Exception:
        pass
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        if not (username and password and email):
            return jsonify(
                {"message":"all fields are required!"}
            )
        user_exist=safe_query('select * from users where username = ?',username)
        if user_exist:
            return jsonify({
                "message":"user already exists"
            })
        hashed_password = generate_password_hash(password)
        safe_query('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', username, email, hashed_password)
        return jsonify({
            "message":"user created succsessfully"
        }),200
    

@csrf.exempt
@bp.route('/login', methods=['POST', 'GET'])
def login():
    try:
        
        verify_jwt_in_request() 
        user_id = get_jwt_identity()  
        return redirect('/')  

    except Exception as e:
        
        pass
    



    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.execute('SELECT * FROM users WHERE username = ?', username)
        user = user[0] if user else None
        
        
        if user and check_password_hash(user['password'], password):
            ident=str(user['id'])
            access_token = create_access_token(identity=ident)
            refresh_token = create_refresh_token(identity=ident)


            response = jsonify({"msg": "login successful"})
            set_access_cookies(response, access_token)
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True)
            return response
        return jsonify({
            "msg":"invalid login credentials"
        })

    return render_template('login.html')
        
        
@bp.route('/logout')
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@bp.route('/delete')
def deleteaccount():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete-account':
            username = getusername(session.get('user_id'))
            try:
                db.execute('delete from posts where username=?',username)
                db.execute('delete from likes where author = ?',username)
                db.execute('delete from comments where username= ?', username)
                db.execute('delete from users where username= ?', username)
            except Exception:
                return "error",404

            return jsonify({
                "message":"user deleted"
            }),200
    elif request.method == 'GET':
        return render_template('deleteacc.html',)



@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    response = jsonify({"msg": "Access token refreshed successfully"})
    set_access_cookies(response, new_access_token)
    return response