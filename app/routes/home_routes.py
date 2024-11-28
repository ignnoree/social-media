from flask import Blueprint, request, render_template, session, redirect

from app.utils import getusername, ifpost_contents,home_query,db

bp = Blueprint('home', __name__)

@bp.route('/', methods=['POST', 'GET'])
def home():
    user = session.get('user_id')
    if not user:
        return redirect('/register')
    username = getusername(user)

    if request.method == 'POST':

        action = request.form.get('action')

        if username:
            ifpost_contents(username, action)
        return redirect('/')

    result = db.execute(home_query,user)
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
    

    return render_template('home.html', posts=posts_with_comments, username=username)



@bp.route('/explore',methods=['POST', 'GET'])
def explore():
    if request.method=='POST':
        pass
    
    profiles=db.execute('select username from users')

    return render_template('explore.html',profiles=profiles)