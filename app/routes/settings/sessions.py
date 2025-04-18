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
