from flask import Flask, request, redirect, render_template,session,flash,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from cs50 import SQL


db = SQL('sqlite:///mydatabase.db')

def getusername(user_id):
    user = db.execute('SELECT username FROM users WHERE id = ?', user_id)
    return user[0]['username'] if user else None

def ifpost_contents(username, action):
    if action=='create_post':
        content=request.form.get('content')
        db.execute('insert into posts(content,username) VALUES (?,?)',content,username)
        

    elif action=='post_comment':
        
        comment_content=request.form.get('comment_content')
        post_id=request.form.get('post_id')
        
        if comment_content and post_id:
            db.execute('insert into comments(post_id,content,username) VALUES (?,?,?)',post_id,comment_content,username)

    elif action=='delete_comment':
        commentid=request.form.get('comment_id')
        if commentid and username:
            db.execute('delete from comments where id = ? and username = ?',commentid,username)

    elif action=='delete_post':
        post_id=request.form.get('post_id')
        if post_id:
            db.execute('DELETE FROM posts WHERE id = ? AND username = ?', post_id, username)

    elif action =='like_post' :
        post_id=request.form.get('post_id')
        existing_likes=db.execute('select * from likes where author = ? and post_id=?',username,post_id)
        if not existing_likes : 
            db.execute('insert into likes (author,post_id) values (?,?)',username,post_id)
            
        else:
            db.execute('delete from likes where post_id = ? and author = ?',post_id,username)
            
    elif request.method == 'PUT':
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
 

home_query='''
select posts.id as post_id,
posts.username as posts_author,
posts.content as posts_content,
posts.created_at as post_created_at,
comments.id as comment_id,
comments.username as comment_author,
comments.content as comment
FROM posts 
left join comments on posts.id = comments.post_id
inner join users on posts.username = users.username
inner join followers on users.id=followers.followed_id
where followers.follower_id= ?
ORDER BY 
    posts.created_at DESC;
'''