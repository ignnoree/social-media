from flask import Blueprint, request, render_template, session, redirect
from app.utils import db
bp = Blueprint('direct', __name__)

bp.route('/direct/<receiver_username>', methods=['GET'])
def direct(receiver_username):
    pass