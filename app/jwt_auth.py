from flask_jwt_extended import JWTManager, verify_jwt_in_request,unset_jwt_cookies, current_user, unset_access_cookies
from flask import jsonify, redirect, make_response

from functools import wraps

from models.user import User
from controllers.auth import AuthService

from flask import request

jwt = JWTManager()

def required_role(roles=["user", "admin"]):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            if current_user.role.role in roles:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Accesso non consentito"), 403

        return decorator
    
    return wrapper

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    resp = make_response({"Unauthorized": 1})
    return resp, 400

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    resp = make_response({"Unauthorized": 1})
    unset_jwt_cookies(resp)
    return resp, 400

@jwt.expired_token_loader
def expired_token_callback(_, jwt):
    resp = make_response({"Unauthorized": 1})
    unset_access_cookies(resp)
    return resp, 400

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=int(identity)).one_or_none()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Callback per verificare se il token è revocato"""
    jti = jwt_payload["jti"]
    return AuthService.is_token_revoked(jti) or( "refresh_token" in jwt_payload and  AuthService.is_token_revoked(jwt_payload["refresh_token"]))
