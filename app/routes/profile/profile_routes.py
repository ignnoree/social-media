from flask import Blueprint, request, render_template, session, redirect,jsonify
from app.utils import ifpost_contents,home_query,profile_query,db,post_comments,delete_comment,like,edit_post,safe_query,own_profile_query,delete_post
from flask_jwt_extended import jwt_required,get_jwt_identity
bp = Blueprint('profile', __name__)
from app import cache

def follow(user_id,followed_id):
    existing_follows=db.execute('select * from followers where follower_id = ? and followed_id=?',user_id,followed_id)
    if existing_follows:
        db.execute('delete from followers where follower_id = ? and followed_id = ? ',user_id,followed_id)
    else:
        db.execute('insert into followers (follower_id,followed_id) VALUES (?,?) ',user_id,followed_id)



def blockcheck(selfuser,blockeduser):
    return bool(safe_query('select * from blocked_users where user_id = ? and blocked_id = ?',selfuser,blockeduser))







@bp.route('/profile/<userprofile>', methods=['POST', 'GET'])
@jwt_required()
def profile(userprofile):
    
    profile_user = safe_query('SELECT * FROM users WHERE username = ?', userprofile)
    profile_user = profile_user[0] if profile_user else None
    user_profile_id=profile_user['id']
    user_id=get_jwt_identity()
    username=safe_query('select username from users where id=?',user_id)
    is_blocked=blockcheck(user_id,user_profile_id)
    if is_blocked:
        return jsonify({"message":"user is blocked"})


    if username==userprofile:
            if request.method == 'POST':
                data=request.get_json()
                action = data.get('action')
                post_id=data.get('post_id')

                if action=='post_comments':
                    return post_comments(username)
                elif action=='delete_comment':
                    return delete_comment(username)
                elif action=='like_post':
                    return like(username)
                elif action=='delete_post':
                    return delete_post(username,post_id)
                elif action=='edit_post':
                    new_content=data.get('new_content')
                    return edit_post(username,post_id,new_content)
            elif request.method == 'GET':
                followers=safe_query('select count(*)from followers where follower_id = ?',user_profile_id)
                followers_count=followers[0]['count(*)']if followers else 0
                followings=safe_query('select count(*)from followers where followed_id = ?',user_profile_id)
                followings_count=followings[0]['count(*)'] if followings else 0
                user_profile_id = profile_user['id']
                is_following = bool(safe_query('SELECT * FROM followers WHERE follower_id = ? AND followed_id = ?', user_id, user_profile_id))

            #cache_key = f"profile_data:{userprofile}" 
            #cached_profile = cache.get(cache_key)                                                        
            #if cached_profile:
                #return (cached_profile)
            #ache.set(cache_key,alldata(own_profile_query,userprofile,followers_count,followings_count,is_following), timeout=120)
            return alldata(profile_query,userprofile,followers_count,followings_count,is_following)


    if request.method == 'POST':
        action = request.form.get('action')
        if action=='FOLLOW':
            return follow(user_id,user_profile_id)
        elif action=='post_comments':
            return post_comments(username)
        elif action=='delete_comment':
            return delete_comment(username)
        elif action=='like_post':
            return like(username)
        
    

    elif request.method == 'GET':
        followers=safe_query('select count(*)from followers where follower_id = ?',user_profile_id)
        followers_count=followers[0]['count(*)']if followers else 0
        followings=safe_query('select count(*)from followers where followed_id = ?',user_profile_id)
        followings_count=followings[0]['count(*)'] if followings else 0
        is_following = bool(safe_query('SELECT * FROM followers WHERE follower_id = ? AND followed_id = ?', user_id, user_profile_id))
        return alldata(own_profile_query,userprofile,followers_count,followings_count,is_following,is_blocked)
        


















def alldata(query,userprofile,followers_count,followings_count,is_following,is_blocked):
    result = safe_query(query, userprofile)
    posts_with_comments = {}
    liked_data = safe_query(
        'SELECT post_id, COUNT(*) AS like_count FROM likes GROUP BY post_id')

    likes_count = {}
    for i in liked_data:
        likes_count[i['post_id']] = i['like_count']
    for i in result:
        post_id = i['post_id']
        print(f'this is {post_id}')
        if post_id not in posts_with_comments:
            posts_with_comments[post_id] = {
                'id': post_id,
                'username': i['post_author'],
                'content': i['post_content'],
                'created_at': i['post_created_at'],
                'comments': [],
                'liked_count': likes_count.get(post_id, 0)

            }
        if i['comment_id']:
            posts_with_comments[post_id]['comments'].append({
                'comment_id': i['comment_id'],
                'comment_author': i['comment_author'],
                'comment_content': i['comment_content']
            })
        

    return jsonify({
    "profile": userprofile,
    "followers_count": followers_count,
    "followings_count": followings_count,
    "follow_status": is_following,
    "posts": posts_with_comments,
    "block_status":is_blocked
})
        

        