from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, set_access_cookies, current_user, set_refresh_cookies, unset_jwt_cookies, get_jwt
from schemas.token import UserAuthSchema #,  UpdateUserSchema
from models.token import Token
from controllers.auth import AuthService


from config import Config


auth_bp = Blueprint('auth', __name__, url_prefix="/api/token")

auth_schema = UserAuthSchema()

@auth_bp.route("/", methods=["OPTIONS"])
def options():
    return '', 204


@auth_bp.route("/", methods=["POST"])
def create_token():
    data = request.get_json()

    errors = auth_schema.validate(data)
    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400
    
    print(data)

    try:
        token = AuthService.createToken(data)
        resp = jsonify({"login" : True})
        set_access_cookies(resp, token["access_token"], max_age=Config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        set_refresh_cookies(resp, token["refresh_token"], max_age=Config.JWT_REFRESH_TOKEN_EXPIRES.total_seconds())
        return resp, 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400
        

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def regenerate_acc_token():
    jwt = get_jwt()

    if AuthService.checkRevokedToken(jwt["jti"]):
        return jsonify(success=False, message="Refresh token revoked."), 400
    
    refresh_token = AuthService.findToken(jwt["jti"])

    token = AuthService.createAccessToken(refresh_token.user)
    
    resp = jsonify({"refreshed" : True})
    set_access_cookies(resp, token, max_age=Config.JWT_ACCESS_TOKEN_EXPIRES.seconds)

    return resp, 200


@auth_bp.route("/", methods=["DELETE"])
@jwt_required()
def revoke_token():
    resp = jsonify({"logout": True})
    AuthService.logout(current_user)
    return resp, 200
    