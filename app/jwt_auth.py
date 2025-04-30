from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt, current_user
from flask import jsonify

from functools import wraps

from models.user import User


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