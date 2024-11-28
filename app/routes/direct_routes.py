from flask import Blueprint, request, render_template, session, redirect
from app.utils import getusername, ifpost_contents,home_query,db
bp = Blueprint('direct', __name__)

bp.route('/direct/<receiver_username>', methods=['GET'])
def direct(receiver_username):
    if 'user_id' not in session:
        return redirect('/login')
    
    sender_id = session['user_id']
    receiver = db.execute('SELECT id, username FROM users WHERE username = ?', receiver_username)
    receiver = receiver[0] if receiver else None

    if not receiver:
        return "User not found", 404

    receiver_id = receiver['id']
    messages = db.execute('''
        SELECT 
    messages.content, 
    messages.timestamp, 
    (SELECT username FROM users WHERE users.id = messages.sender_id) AS sender_username, -- Sender's username
    (SELECT username FROM users WHERE users.id = messages.receiver_id) AS receiver_username -- Receiver's username
FROM messages
WHERE 
    (messages.sender_id = ? AND messages.receiver_id = ?) -- Messages from sender to receiver
    OR 
    (messages.sender_id = ? AND messages.receiver_id = ?) -- Messages from receiver to sender
ORDER BY messages.timestamp ASC;
    ''', sender_id, receiver_id, receiver_id, sender_id)

    return render_template('direct.html', messages=messages, receiver=receiver)