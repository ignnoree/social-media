from flask import Blueprint, request, render_template, session, redirect
from flask import jsonify
import jwt
from app.utils import getusername, ifpost_contents,home_query,db,safe_query,FLASK_JWT_SECRET_KEY2,get_user_id,create_post,post_comments,delete_comment,delete_post,like,edit_post
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies, create_access_token
from app import cache

bp = Blueprint('home', __name__)





@bp.route('/whoami')
@jwt_required()
def whoami():
    username = get_jwt_identity()
    return username



@bp.route('/', methods=['POST', 'GET'])
@jwt_required()
def home():
    user_id = get_jwt_identity()
    print(f'useriddddddddfadfaf{user_id}')
    username=getusername(user_id)  #(username) 
    print(f'usernamedfadfaf{username}')
    if not username:
        return redirect('/login')
    
    print(f'user is = {user_id}')

    if request.method == 'POST':
        ALLOWED_ACTIONS = {'create_post','post_comment','delete_comment','delete_post','like_post'}
        action = request.form.get('action')
        if action not in ALLOWED_ACTIONS:
            return "invalid action",404
        else:
            if action=='create_post':
                return create_post(username)
            elif action=='post_comments':
                return post_comments(username)
            elif action=='delete_comment':
                return delete_comment(username)
            elif action =='delete_post':
                return delete_post(username)
            elif action =='like_post':
                return like(username)
    elif request.method=='PUT':
        return edit_post       

    user_id=str(user_id)

    limit = int(request.args.get('limit', 10))  
    offset = int(request.args.get('offset', 0))
    

    result = safe_query(home_query,user_id,user_id,user_id,user_id,user_id,limit,offset)
    
    posts_with_comments = {}
    liked_data = safe_query(
        'SELECT post_id, COUNT(*) AS like_count FROM likes GROUP BY post_id')

    likes_count = {}
    for i in liked_data:
        likes_count[i['post_id']] = i['like_count']
    for i in result:
        post_id = i['post_id']
        if post_id not in posts_with_comments:
            posts_with_comments[post_id] = {
                'id': post_id,
                'username': i['posts_author'],
                'content': i['posts_content'],
                'created_at': i['post_created_at'],
                'comments': [],
                'liked_count': likes_count.get(post_id, 0)

            }
        if i['comment_id']:
            posts_with_comments[post_id]['comments'].append({
                'comment_id': i['comment_id'],
                'comment_author': i['comment_author'],
                'comment_content': i['comment']
            })

    final_result={"posts":posts_with_comments}           
    
    return jsonify({"posts":posts_with_comments})



@bp.route('/explore',methods=['POST', 'GET'])
def explore():
    if request.method=='POST':
        pass
    
    profiles=safe_query('select username from users')

    return jsonify({"profiles":profiles})


