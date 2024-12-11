from flask import Blueprint, request,jsonify
from app.utils import db
from flask_jwt_extended import get_jwt_identity,jwt_required
from app.utils import safe_query,getusername
from flask_wtf.csrf import CSRFProtect
from app import cache
bp = Blueprint('setting', __name__,url_prefix='/setting')

def edit_bio(username,bio):
    safe_query('insert into users (bio) values (?) where username = ? ',bio,username)




@bp.route('/edit', methods=['POST', 'GET'])
@jwt_required()
def setting():
    user_id=get_jwt_identity()
    username=getusername(user_id)
    if request.method=='POST':
        data=request.get_json()
        action=data.get('action') 

        if action == 'edit_bio':
            bio=data.get('bio')
            return update_profile_field('bio', bio, user_id)
        
        elif action=='edit_gender':
            gender=data.get('gender')
            
            return  update_profile_field('gender', gender, user_id)
            

    
    profile_user=safe_query('select * from users where id = ?',user_id)[0]
    
    user_profile={
        "bio":profile_user['bio'],
        "gender":profile_user['gender']
    }
    cache_key = f"profile_data:{user_id}" 
    cached_profile = cache.get(cache_key)                                                        
    if cached_profile:
        print(f'we are inside cache: {type(cached_profile)}')  # Check the type of cached_profile
        print(cached_profile)
        return (cached_profile)
    cache.set(cache_key,user_profile, timeout=120)
    return user_profile
        







def update_profile_field(field, value, user_id):
    ALLOWED_FIELDS = ['bio', 'gender'] 
    if field not in ALLOWED_FIELDS:
        return jsonify({"msg": "Invalid field!"}), 400  

    
    query = f'UPDATE users SET {field} = ? WHERE id = ?'
    result = safe_query(query,value, user_id)
    
    if result == "database error!":
        return jsonify({"msg": "Database error!"}), 500
    
    cache_key = f"profile_data:{user_id}"
    cache.delete(cache_key)
    return jsonify({"msg": f"{field.capitalize()} updated successfully"}), 200