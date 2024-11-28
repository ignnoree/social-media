from flask import Blueprint, request, render_template, session, redirect
from app.utils import getusername, ifpost_contents,home_query,profile_query,db

bp = Blueprint('profile', __name__)


@bp.route('/profile/<username>', methods=['POST', 'GET'])
def profile(username):
    profile_user = db.execute('SELECT * FROM users WHERE username = ?', username)
    profile_user = profile_user[0] if profile_user else None
    user_id=session.get('user_id')
    followed_id=profile_user['id']
    if request.method == 'POST':
        action = request.form.get('action')
        

        if action=='FOLLOW':
            existing_follows=db.execute('select * from followers where follower_id = ? and followed_id=?',user_id,followed_id)
            if existing_follows:
                db.execute('delete from followers where follower_id = ? and followed_id = ? ',user_id,followed_id)
            else:
                db.execute('insert into followers (follower_id,followed_id) VALUES (?,?) ',user_id,followed_id)

        ifpost_contents(username, action)
        return redirect(f'{username}')
        

    elif request.method == 'GET':
        followers=db.execute('select count(*)from followers where follower_id = ?',followed_id)
        followers_count=followers[0]['count(*)']if followers else 0
        print(f'11111{followers_count}')
        followings=db.execute('select count(*)from followers where followed_id = ?',followed_id)
        followings_count=followings[0]['count(*)'] if followings else 0
        followed_id = profile_user['id']
        is_following = bool(db.execute('SELECT * FROM followers WHERE follower_id = ? AND followed_id = ?', user_id, followed_id))
        result = db.execute(profile_query, username)
        posts_with_comments = {}
        liked_data = db.execute(
            'SELECT post_id, COUNT(*) AS like_count FROM likes GROUP BY post_id')

        likes_count = {}
        for i in liked_data:
            likes_count[i['post_id']] = i['like_count']
        for i in result:
            post_id = i['post_id']
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

        return render_template('profile.html', posts_with_comments=posts_with_comments, username=username,profile_user=profile_user,is_following=is_following,followers_count=followers_count,followings_count=followings_count)
