from flask import Blueprint, request, redirect, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils import db,getusername,safe_query,jwt,create_tokens
from flask import jsonify
from flask_jwt_extended import decode_token,create_access_token,get_jwt_identity,set_access_cookies,unset_jwt_cookies,create_access_token,create_refresh_token,jwt_required, verify_jwt_in_request,get_jwt
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta,datetime

import uuid

csrf = CSRFProtect()

bp = Blueprint('auth', __name__)

#we should add the session ids, on the login and etc ... 



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
@bp.route("/password",methods=["PATCH"])
@jwt_required()
def resset_password():
    idenity=get_jwt_identity()
    print(f"idenity={idenity}")

    provided_oldpassword=request.json.get("old_password")
    new_password=request.json.get("new_password")

    old_password_hashed=safe_query("select password from users where id = ?  ",idenity)
    



    if old_password_hashed and check_password_hash(old_password_hashed[0]["password"],provided_oldpassword):

        sessions = db.execute("SELECT jti, refresh_jti, refresh_expire,access_expire FROM sessions WHERE user_id = ?", idenity)
        print(sessions)
        for session in sessions:
            access_jti = session["jti"]
            refresh_jti = session["refresh_jti"]
            expires = session["access_expire"] 
            refresh_expire=session["refresh_expire"]
        
            safe_query("INSERT INTO blacklistedtokens (jti,token_type ,expires_at) VALUES (?, ?,?)", access_jti,"access", expires)
            safe_query("INSERT INTO blacklistedtokens (jti,token_type ,expires_at) VALUES (?, ?,?)", refresh_jti,"refresh" ,refresh_expire)
        if sessions:
            safe_query("delete from sessions where user_id = ? ",idenity)
            safe_query("update users set password = ? where id= ? ",generate_password_hash(new_password),idenity)
        return jsonify({"msg":"password updated pls log in again"})















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
            return create_tokens(ident,jsonify({"msg":"login successfull"}))
        
        return jsonify({
            "msg":"invalid login credentials"
        })

    return render_template('login.html')
        
        
@bp.route('/logout')
@jwt_required()
def logout():
    jwtpayload = get_jwt()
    access_jti = jwtpayload["jti"]
    expires_at=jwtpayload["exp"]

    user_id=get_jwt_identity()
    session=safe_query("select * from sessions where user_id = ? and jti = ? ",user_id,access_jti)

    if session: 
        
        refresh_exp = session[0]["refresh_expire"]
        refresh_jti = session[0]["refresh_jti"]
        safe_query("INSERT INTO blacklistedtokens (jti, token_type,expires_at) VALUES (?, ?,?)", refresh_jti, "refresh",str(refresh_exp))
        safe_query("INSERT INTO blacklistedtokens (jti, token_type,expires_at) VALUES (?, ?,?)", access_jti, "access",str(expires_at))
        safe_query("delete from sessions where jti = ? ", access_jti)
        
    
    response = jsonify({"msg": "Successfully logged out"})
    unset_jwt_cookies(response)
    response.set_cookie("refresh_token", "", expires=0)
    return response



@bp.route('/delete')
@jwt_required()
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


from flask_jwt_extended import get_jti

@bp.route('/refresh', methods=['GET', 'POST'])
@jwt_required(refresh=True)
def refresh():
    ident=get_jwt_identity()
    old_refresh_jti =get_jwt().get("jti")

    old_access_jti=safe_query("select jti from sessions where refresh_jti = ?",old_refresh_jti)[0].get("jti")
    refresh_exp = safe_query("SELECT refresh_expire FROM sessions WHERE refresh_jti = ?",  old_refresh_jti)[0].get("refresh_expire")
    db.execute("insert into blacklistedtokens (jti,token_type,expires_at) VALUES (?,?,?)",old_refresh_jti,"refresh_token",refresh_exp) 
    db.execute("insert into blacklistedtokens (jti,token_type,expires_at) VALUES (?,?,?)", old_access_jti,"access_token",refresh_exp) 
    safe_query("delete from sessions where refresh_jti=?",old_refresh_jti)
    return create_tokens(ident,jsonify({"msg":"token refreshed"}))


