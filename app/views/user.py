from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user

from schemas.user import UserSchema, UserORMSchema
from controllers.user import UserService
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.exc import IntegrityError
from jwt_auth import required_role

user_bp = Blueprint('user', __name__, url_prefix="/api/user")

# Inizializza gli schemi
user_schema = UserSchema()
user_orm_schema = UserORMSchema()

@user_bp.route('', methods=['POST'])
def create_user():
    """Crea un nuovo utente"""
    data = request.get_json()
    
    # Validazione input
    errors = user_schema.validate(data)
    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400
    
    try:
        user = UserService.create_user(data)
        return jsonify({
            "success": True,
            "result": user_schema.dump(user)
        }), 201
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
        
    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Username or email already exists"
        }), 409
        
    except Exception as e:
        print(e)
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500

@user_bp.route('', methods=['GET'])
def get_all_users():
    """Ottieni tutti gli utenti (paginati)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        users, total = UserService.get_all_users_paginated(
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            "success": True,
            "result": user_schema.dump(users, many=True),
            "total": total,
            "page": page,
            "per_page": per_page
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to retrieve users"
        }), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Ottieni un singolo utente per ID"""
    # Se sei te stesso o un admin procedi pure
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise NotFound("User not found")
            
        return jsonify({
            "success": True,
            "result": user_orm_schema.dump(user)
        })
        
    except NotFound as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Aggiorna un utente esistente"""
    data = request.get_json()
    
    # Validazione input
    errors = user_orm_schema.validate(data)
    if errors:
        return jsonify({
            "success": False,
            "errors": errors
        }), 400
    
    try:
        updated_user = UserService.update_user(user_id, data)
        if not updated_user:
            raise NotFound("User not found")
            
        return jsonify({
            "success": True,
            "result": user_orm_schema.dump(updated_user)
        })
        
    except NotFound as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 400
        
    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Username or email already in use"
        }), 409
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to update user"
        }), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Elimina un utente"""
    try:
        deleted = UserService.delete_user(user_id)
        if not deleted:
            raise NotFound("User not found")
            
        return jsonify({
            "success": True,
            "message": "User deleted successfully"
        }), 200
        
    except NotFound as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Failed to delete user"
        }), 500

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    return user_orm_schema.dump(current_user)
