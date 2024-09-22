from flask import Blueprint, request, session, current_app
from connectors.mysql_connector import connection
from models.users import Users

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from datetime import timedelta


from flask_login import login_user, logout_user, login_required, current_user

from cerberus import Validator
from validation.users_insert import users_insert_schema
import os
from flasgger import swag_from
users_routes = Blueprint("users_routes", __name__)

@users_routes.route("/users", methods=["POST"])
def register_users():
    
    v = Validator(users_insert_schema)
    request_body = {
        "username" : request.form["username"],
        "email" : request.form["email"],
        "password_hash" : request.form["password_hash"]
    }
    
    if not v.validate(request_body):
        return {"error": v.errors}, 409
    
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        NewUser = Users(
            username=request.form["username"],
            email=request.form["email"],
        )

        NewUser.set_password(request.form["password_hash"])

        s.add(NewUser)
        s.commit()
    except Exception as e:
        s.rollback()
        return { "message": "Fail to Register", "error":str(e)}, 500
    finally:
        s.close()
    return { "message": "Register Success" }, 200

@users_routes.route('/users/login', methods=['POST'])
def check_login():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        email = request.form['email']
        users = s.query(Users).filter(Users.email == email).first()

        if users is None:
            return { "message": "User not found" }, 403
        
        if not users.check_password(request.form['password_hash']):
            return { "message": "Invalid password" }, 403
        
        # Lakukan login pengguna dan atur durasi sesi
        login_user(users, remember=True, duration=timedelta(hours=1))
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(hours=1)

        # Ambil ID sesi
        session_id = request.cookies.get('session')

        return {
            "session_id": session_id,
            "message": "Login Success"
        }, 200

    except Exception as e:
        s.rollback()
        return { "message": "Failed to login", "error": str(e) }, 500
    finally:
        s.close()

@users_routes.route("/users/list", methods=['GET'])
@login_required
def list_users():

    Session = sessionmaker(connection)
    s = Session()

    try:
        users_query = select(Users)
        result = s.execute(users_query)
        users = []

        for row in result.scalars():
            if row.id != current_user.id:
                users.append({
                    "id": row.id,
                    "username": row.username,
                    "email": row.email
                })

        return {
            'users': users,
            'message' : "This list all user without you , " + current_user.username
        }

    except Exception as e:
        print(e)
        return { 'message': "Unexpected Error", "error":str(e) }, 500
    
@users_routes.route("/users/me", methods=['GET'])
@login_required
def users_profile():

    Session = sessionmaker(connection)
    s = Session()

    try:
        # Ambil data pengguna hanya untuk current_user
        user = s.query(Users).filter(Users.id == current_user.id).first()

        if not user:
            return { 'message': "User not found" }, 404

        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'message': "Halo , this is your profile " + current_user.username
        }

    except Exception as e:
        print(e)
        return { 'message': "Unexpected Error", "error": str(e) }, 500


@users_routes.route('/users/me/<id>', methods=['PUT'])
@login_required
def users_update(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        users = s.query(Users).filter(Users.id == id).first()
        if not users:
            return { "message": "User not found" }, 404

        # Pastikan hanya current_user yang dapat menghapus akunnya sendiri
        if current_user.id != users.id:
            return { "message": "Unauthorized: You are not authorized to uptade this user" }, 403

        users.username = request.form['username']
        users.email = request.form['email']

        s.commit()
    except Exception as e:
        s.rollback()
        return { "message": "Fail to Update", "error":str(e)}, 500
    finally:
        s.close()
    return { 'message': 'Success update user data'}, 200


@users_routes.route('/users/<id>', methods=['DELETE'])
@login_required
def users_delete(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        users = s.query(Users).filter(Users.id == id).first()

        if not users:
            return { "message": "User not found" }, 404

        # Pastikan hanya current_user yang dapat menghapus akunnya sendiri
        if current_user.id != users.id:
            return { "message": "Unauthorized: You are not authorized to delete this user" }, 403

        s.delete(users)
        s.commit()
    except Exception as e:
        s.rollback()
        return { "message": "Fail to Delete", "error": str(e) }, 500
    finally:
        s.close()

    return { 'message': 'Success delete Users data'}, 200


@users_routes.route('/logout', methods=['POST'])
@login_required
def user_logout():
    try:
        logout_user()
        return {"message": "Success logout"}, 200
    except Exception as e:
        return {"message": "Failed to logout", "error": str(e)}, 500

@users_routes.route('/check_session', methods=['GET'])
def check_session():
    try:
        if current_user.is_authenticated:
            return {"message": "Session active"}, 200
        else:
            return {"message": "No active session"}, 401
    except Exception as e:
        return {"error": str(e)}, 500
