from app.utils import safe_query,getusername
from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required,get_jwt_identity
from .setting_routes import bp
import logging


@bp.route("/sessions",methods=["GET"])
@jwt_required()
def sessions():
    idenity=get_jwt_identity()
    res=safe_query("select id,created_at , ip,useragent from sessions where user_id = ? ",idenity)
    
    return res



@bp.route("/sessions",methods=["POST"])
@jwt_required()
def manage_sessions():
    target_session_id=request.json.get("session_id")
    data=safe_query("select jti,refresh_jti,access_expire,refresh_expire from sessions where id=?",target_session_id)
    print(data)
    if data:
        data=data[0]
        print(data)
        jti,refresh_jti,access_expire,refresh_expire=data["jti"],data["refresh_jti"],data["access_expire"],data["refresh_expire"]
        safe_query("insert into blacklistedtokens (jti,token_type,expires_at)VALUES(?,?,?)",jti,"access_token",access_expire)
        safe_query("insert into blacklistedtokens (jti,token_type,expires_at)VALUES(?,?,?)",refresh_jti,"refresh_token",refresh_expire)
        return jsonify({"msg":"session is removed"})
    return jsonify({"msg":"session doenst exists"})
