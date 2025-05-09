from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError
from jwt_auth import required_role

from controllers.category import CategoryService
from schemas.category import CategorySchema, CategoryCreateSchema

category_bp = Blueprint('categories', __name__, url_prefix="/api/category")
create_schema = CategoryCreateSchema()
output_schema = CategorySchema()

@category_bp.route('', methods=["OPTIONS"])
def options():
    return '', 204

@category_bp.route('', methods=['POST'])
def create_category():
    try:
        data = create_schema.load(request.json)
        category = CategoryService.create_category(**data)
        return jsonify(success=True, result=output_schema.dump(category)), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
@category_bp.route('/<int:category_id>', methods=['GET'])
@jwt_required(optional=True)
def get_category(category_id):
    try:
        category = CategoryService.get_category(category_id)
        return jsonify(success=True, result=output_schema.dump(category)), 200
    except NoResultFound:
        return jsonify({'error': 'Categoria non trovata'}), 404

@category_bp.route('', methods=['GET'])
@jwt_required(optional=True)
def list_categories():
    try:
        data = request.get_json()
    except:
        data = {}

    categories, total_pages, page, total_count = CategoryService.list_categories(**data, admin=current_user and current_user.role.role == "admin")

    

    obj = output_schema.dump(categories, many=True)

    return jsonify(result=obj, total_pages=total_pages, page=page, total_count=total_count), 200

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    try:
        category = CategoryService.delete_category(category_id)
        if category:
            return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500