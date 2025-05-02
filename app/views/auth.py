from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, set_access_cookies, current_user, set_refresh_cookies, unset_jwt_cookies, get_jwt
from schemas.token import UserAuthSchema #,  UpdateUserSchema
from models.token import Token
from controllers.auth import AuthService


from config import Config
from flask import make_response


auth_bp = Blueprint('auth', __name__, url_prefix="/api/token")

auth_schema = UserAuthSchema()

@auth_bp.route("", methods=["OPTIONS"])
def options():
    return '', 204


@auth_bp.route("", methods=["POST"])
def create_token():
    data = request.get_json()

    errors = auth_schema.validate(data)
    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400
    
    try:
        resp = make_response({"ok": "authenticated"}, 201)
        token = AuthService.createToken(data)
        set_access_cookies(resp, token["access_token"])
        set_refresh_cookies(resp, token["refresh_token"])
        return resp
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400
        
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def regenerate_acc_token():
    jwt_payload = get_jwt()

    try:
        token = AuthService.refresh_from_token(jwt_payload)
        resp = make_response({"ok": "authenticated"}, 201)
        set_access_cookies(resp, token["access_token"])
        return resp
    except ValueError as e:
        return jsonify({"msg": str(e)}), 401


@auth_bp.route("", methods=["DELETE"])
@jwt_required()
def revoke_token():
    resp = jsonify({"logout": True})
    jwt_payload = get_jwt()
    
    AuthService.logout_tokens(jwt_payload)

    # unset_jwt_cookies(resp)
    return resp, 200
    