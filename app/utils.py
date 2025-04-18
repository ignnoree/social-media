from flask import  request,jsonify

from cs50 import SQL
from sqlite3 import DatabaseError
from flask_jwt_extended import JWTManager
import uuid
from datetime import datetime,timedelta
from flask_jwt_extended import decode_token,create_access_token,get_jwt_identity,set_access_cookies,unset_jwt_cookies,create_access_token,create_refresh_token,jwt_required, verify_jwt_in_request,get_jwt


jwt=JWTManager()


def create_tokens(ident,response):
    access_expire = timedelta(hours=1)

    refresh_expire=timedelta(days=30)
    access_expire_db= datetime.now() + access_expire
    refresh_expire_db=datetime.now()+refresh_expire
    session_id=str(uuid.uuid4())
    access_jti=str(uuid.uuid4())
    refresh_jti=str(uuid.uuid4())

    access_token = create_access_token(identity=ident,additional_claims={"jti":access_jti,"session_id":session_id},expires_delta=access_expire)
    refresh_token = create_refresh_token(identity=ident, additional_claims={"jti":refresh_jti,"session_id":session_id},expires_delta=refresh_expire)


    expires = datetime.now() + timedelta(days=30)
    set_access_cookies(response, access_token)
    response.set_cookie('refresh_token_cookie', refresh_token, httponly=True, secure=True,expires=expires)
    safe_query('''
        INSERT INTO sessions (id,user_id, accesstoken, refreshtoken, ip, useragent, jti, refresh_jti,access_expire,refresh_expire)
        VALUES (?, ?, ?, ?, ?, ?, ?,?,?,?)''',session_id,
        ident, access_token, refresh_token,
        request.remote_addr, request.headers.get('User-Agent'),
        access_jti, refresh_jti,str(access_expire_db),str(refresh_expire_db)
        
    )
    return response
    
    

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    
    jti = jwt_payload["jti"]
  
    token = safe_query("select * from blacklistedtokens where jti = ?", jti)
    
    if token:
        return True
    return False

db = SQL('sqlite:///D:/Downloads/projects/socialmedia/social-media/app/mydatabase.db')


FLASK_JWT_SECRET_KEY2='examlekeyhere'

def getusername(user_id):
    user = db.execute('SELECT username FROM users WHERE id = ?', user_id)
    return user[0]['username'] if user else None


def create_post(username):
    content=request.json.get('content')
    if content:
        safe_query('insert into posts(content,username) VALUES (?,?)',content,username)
        return jsonify({"message":"Post created successfully"}),201
    else : 
        return jsonify({"error":"content required"}),400


def post_comments(username):
    comment_content=request.json.get('comment_content')
    post_id=request.json.get('post_id')
    
    if comment_content and post_id:
        safe_query('insert into comments(post_id,content,username) VALUES (?,?,?)',post_id,comment_content,username)
        return jsonify({"message":"comment posted successfully"}),201
    else :
        return jsonify({"error":"content and post_id"}),400
    

def delete_comment(username):
    commentid=request.json.get('comment_id')
    if commentid and username:
        safe_query('delete from comments where id = ? and username = ?',commentid,username)
        return jsonify({"message":"comment deleted"}),201
    else :
        return jsonify({"error":"commentid and usrname required !"})





def delete_post(username):
    post_id=request.json.get('post_id')
    if post_id:
        safe_query('DELETE FROM posts WHERE id = ? AND username = ?', post_id, username)
        return jsonify({"message":"post deleted successfully"}),201
    else:
        return jsonify({"error":"post_id required"}),401


def like(username):
    post_id=request.json.get('post_id')
    existing_likes=db.execute('select * from likes where author = ? and post_id=?',username,post_id)
    if post_id:
        if not existing_likes : 
            safe_query('insert into likes (author,post_id) values (?,?)',username,post_id)
            return jsonify({"message":"post liked"}),201
            
        else:
            safe_query('delete from likes where post_id = ? and author = ?',post_id,username)
            return jsonify({"message":"like removed"}),201
        

def edit_post(username,postid,postcontent):
    safe_query('update posts set content = ? where id = ? and username = ?',postcontent,postid,username)
    return jsonify({
        "msg":"comment updated"
    })
def delete_post(username,post_id):
    safe_query('delete from posts where id = and username = ?',post_id,username)










def ifpost_contents(username, action):
    if action=='create_post':
        content=request.json.get('content')
        if content:
            safe_query('insert into posts(content,username) VALUES (?,?)',content,username)
            return jsonify({"message":"Post created successfully"}),201
        else : 
            return jsonify({"error":"content required"}),400
        

    elif action=='post_comment':
        comment_content=request.json.get('comment_content')
        post_id=request.json.get('post_id')
        
        if comment_content and post_id:
            safe_query('insert into comments(post_id,content,username) VALUES (?,?,?)',post_id,comment_content,username)
            return jsonify({"message":"comment posted successfully"}),201
        else :
            return jsonify({"error":"content and post_id"}),400

    elif action=='delete_comment':
        commentid=request.json.get('comment_id')
        if commentid and username:
            safe_query('delete from comments where id = ? and username = ?',commentid,username)
            return jsonify({"message":"comment deleted"}),201
        else :
            return jsonify({"error":"commentid and usrname required !"})

    elif action=='delete_post':
        post_id=request.json.get('post_id')
        if post_id:
            safe_query('DELETE FROM posts WHERE id = ? AND username = ?', post_id, username)
            return jsonify({"message":"post deleted successfully"}),201
        else:
            return jsonify({"error":"post_id required"})

    elif action =='like_post' :
        post_id=request.json.get('post_id')
        existing_likes=db.execute('select * from likes where author = ? and post_id=?',username,post_id)
        if post_id:
            if not existing_likes : 
                safe_query('insert into likes (author,post_id) values (?,?)',username,post_id)
                return jsonify({"message":"post liked"}),201
                
            else:
                safe_query('delete from likes where post_id = ? and author = ?',post_id,username)
                return jsonify({"message":"like removed"}),201
            
    elif request.method == 'PUT':
        #username=get_jwt_identity() 
        new_postid=request.json.get('post_id')
        postcontent=request.json.get('edited_content')
        db.execute('update posts set content = ? where id = ?',postcontent,new_postid)
    
    
profile_query='''SELECT posts.id AS post_id, 
       posts.username AS post_author, 
       posts.content AS post_content, 
       posts.created_at AS post_created_at, 
       comments.id AS comment_id, 
       comments.content AS comment_content, 
       comments.username AS comment_author   
FROM posts
LEFT JOIN comments ON posts.id = comments.post_id
WHERE posts.username = ?
ORDER BY posts.created_at DESC'''
 

home_query2='''
SELECT 
    posts.id AS post_id,
    posts.username AS posts_author,
    posts.content AS posts_content,
    posts.created_at AS post_created_at,
    comments.id AS comment_id,
    comments.username AS comment_author,
    comments.content AS comment
FROM posts
LEFT JOIN comments ON posts.id = comments.post_id
INNER JOIN users ON posts.username = users.username
INNER JOIN followers ON users.id = followers.followed_id
WHERE followers.follower_id = ?
ORDER BY posts.created_at DESC
LIMIT ? OFFSET ?
;'''







home_query = '''
SELECT 
    posts.id AS post_id,
    posts.username AS posts_author,
    posts.content AS posts_content,
    posts.created_at AS post_created_at,
    comments.id AS comment_id,
    comments.username AS comment_author,
    comments.content AS comment
FROM posts
LEFT JOIN comments ON posts.id = comments.post_id
INNER JOIN users ON posts.username = users.username
INNER JOIN followers ON users.id = followers.followed_id
WHERE followers.follower_id = ?
  AND posts.username NOT IN (
      SELECT blocked_id FROM blocked_users WHERE user_id = ?
      UNION
      SELECT user_id FROM blocked_users WHERE user_id = ?
  )
  AND (comments.username IS NULL OR comments.username NOT IN (
      SELECT blocked_id FROM blocked_users WHERE user_id = ?
      UNION
      SELECT user_id FROM blocked_users WHERE user_id = ?
  ))
ORDER BY posts.created_at DESC
LIMIT ? OFFSET ?
;'''














comments_query = '''
SELECT comments.id AS comment_id,
       comments.username AS comment_author,
       comments.content AS comment_content,
       comments.post_id
FROM comments
WHERE comments.post_id IN (
    SELECT posts.id
    FROM posts
    INNER JOIN followers ON posts.username = followers.followed_id
    WHERE followers.follower_id = ?
    ORDER BY posts.created_at DESC
    LIMIT 20 OFFSET ?
)
ORDER BY comments.created_at ASC
'''


own_profile_query='''SELECT posts.id AS post_id, 
       posts.username AS post_author, 
       posts.content AS post_content, 
       posts.created_at AS post_created_at, 
       comments.id AS comment_id, 
       comments.content AS comment_content, 
       comments.username AS comment_author   
FROM posts
LEFT JOIN comments ON posts.id = comments.post_id
WHERE posts.username = ?
ORDER BY posts.created_at DESC'''




def safe_query(query,*params):
    try:
        return db.execute(query,*params)
    except DatabaseError as e:
        
         return "database error!",404

def get_user_id(username):
    userid= safe_query('select id from users where username = ? ',username)
    return userid[0]['id']
    
