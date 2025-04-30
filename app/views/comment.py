from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from controllers.comment import CommentService
from schemas.comment import CommentORMSchema, CommentSchema #, PostUpdateSchema
from jwt_auth import required_role
 
comment_bp = Blueprint('comment', __name__, url_prefix='/api/post/<int:post_id>/comment')

comment_orm_schema = CommentORMSchema()
comment_schema = CommentSchema()

@comment_bp.route('/', methods=['GET'])
def get_all_comment(post_id):
    try:
        data = request.get_json()
        if "include_deleted" in data.keys() and not type(data["include_deleted"]) is bool:
            return jsonify({
                "success": False,
                "errors": {
                    "include_deleted" : "Must be a bool"
                }
            }), 400
    except:
        data = {}
    """Ottieni tutti i post attivi"""

    try:
        comments = CommentService.get_all_comment(post_id, **data)
        return jsonify(comment_orm_schema.dump(comments, many=True)), 200
    except Exception as e:
        return jsonify(success=False, errors={
            "message" : str(e)
        }), 400
    
@comment_bp.route('/<int:comment_id>', methods=['GET'])
def get_comment(post_id, comment_id):
    """Ottieni un post specifico"""
    comment = CommentService.get_comment_by_id(post_id, comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    return jsonify(comment_orm_schema.dump(comment)), 200

@comment_bp.route('/', methods=['POST'])
def create_comment(post_id):
    """Crea un nuovo post"""
    data = request.get_json()
    errors = comment_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    data["user_id"] = 1 # current_user.id
    data["post_id"] = post_id

    try:
        post = CommentService.create_comment(data)
        
        return jsonify(comment_orm_schema.dump(post)), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    
@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    """Ottieni un post specifico"""
    comment = CommentService.get_comment_by_id(post_id, comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404
    
    if CommentService.soft_delete_post(comment_id):
        return jsonify({"message": "Post deleted successfully"}), 200
    return jsonify({"message": "Failed to delete post"}), 500