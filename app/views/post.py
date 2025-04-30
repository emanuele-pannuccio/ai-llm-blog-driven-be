from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user, verify_jwt_in_request
from controllers.post import PostService
from schemas.post import PostORMSchema, PostSchema #, PostUpdateSchema
from jwt_auth import required_role
 
post_bp = Blueprint('post', __name__, url_prefix='/api/post')

post_orm_schema = PostORMSchema()
post_schema = PostSchema()

@post_bp.route('/', methods=['GET'])
@jwt_required(optional=True)
def get_all_posts():
    """Ottieni tutti i post attivi"""
    
    try:
        data = request.get_json()
    except:
        data = {}

    if not current_user or current_user.role.role != "admin":
        for k in ["show_all"]:
            if k in data.keys(): del data[k]
    
    if data.get("include_deleted", None): g.bypass_filter=True

    try:
        posts, total_pages, page, total_count = PostService.get_all_posts(**data)
        return jsonify(result=post_orm_schema.dump(posts, many=True), total_pages=total_pages, page=page, total_count=total_count), 200
    except Exception as e:
        return jsonify(success=False, message=str(e))

@post_bp.route('/<int:post_id>', methods=['GET'])
@jwt_required(optional=True)
def get_post(post_id):
    """Ottieni un post specifico"""
    post = PostService.get_post_by_id(post_id, admin=current_user and current_user.role.role == "admin")
    if not post:
        return jsonify({"message": "Post not found"}), 404
    return jsonify(post_orm_schema.dump(post)), 200

@post_bp.route('/', methods=['POST'])
@required_role(["admin"])
def create_post():
    data = request.get_json()
    errors = post_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    data["publisher_id"] = current_user.id

    if not "status" in data.keys():
        data["status"] = "review"

    try:
        post = PostService.create_post(data)
        
        return jsonify(post_orm_schema.dump(post)), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

@post_bp.route("/", methods=["OPTIONS"])
def options():
    return '', 204

@post_bp.route('/<int:post_id>', methods=['PUT'])
@required_role(["admin"])
def update_post(post_id):
    """Aggiorna un post esistente"""
    post = PostService.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    data = request.get_json()
    errors = post_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    try:
        data['user'] = current_user.id
        updated_post = PostService.update_post(post_id, data)
        return jsonify(post_orm_schema.dump(updated_post)), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

@post_bp.route('/<int:post_id>', methods=['DELETE'])
@required_role(["admin"])
def delete_post(post_id):
    """Elimina logicamente un post"""
    post = PostService.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    if PostService.soft_delete_post(post_id):
        return jsonify({"message": "Post deleted successfully"}), 200
    return jsonify({"message": "Failed to delete post"}), 500

@post_bp.route('/<int:post_id>/restore', methods=['PUT'])
@required_role(["admin"])
def restore_post(post_id):
    """Ripristina un post cancellato logicamente"""
    post = PostService.get_post_by_id(post_id, include_deleted=True)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    if PostService.restore_post(post_id):
        return jsonify({"message": "Post restored successfully"}), 200
    return jsonify({"message": "Failed to restore post"}), 500