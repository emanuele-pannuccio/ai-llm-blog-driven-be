from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from controllers.tag import TagService
from schemas.tag import TagSchema
from marshmallow import ValidationError

tag_bp = Blueprint('tag_bp', __name__, url_prefix='/api/tag')
tag_schema = TagSchema()


@tag_bp.route('', methods=["OPTIONS"])
def options():
    return '', 204

@tag_bp.route('', methods=['GET'])
def get_all_tags():
    try:
        data = request.get_json()
    except:
        data = {}
    tags = TagService.get_all_tags(**data)
    return jsonify(success=True, result=tag_schema.dump(tags, many=True)), 200

@tag_bp.route('/<int:tag_id>', methods=['GET'])
def get_tag(tag_id):
    tag = TagService.get_tag_by_id(tag_id)
    if not tag:
        return jsonify({'message': 'Tag not found'}), 404
    return jsonify(success=True, result=tag_schema.dump(tag)), 200

@tag_bp.route('', methods=['POST'])
# @required_role(["admin", "editor"])
# @jwt_required()
def create_tag():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400

    try:
        data = tag_schema.load(json_data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    tag = TagService.create_tag(data)
    if not tag:
        return jsonify({'message': 'Tag already exists or invalid data'}), 400

    return jsonify(tag_schema.dump(tag)), 201

@tag_bp.route('/<int:tag_id>', methods=['DELETE'])
# @jwt_required()
def delete_tag(tag_id):
    success = TagService.delete_tag(tag_id)
    if not success:
        return jsonify({'message': 'Tag not found'}), 404
    return jsonify({'message': 'Tag deleted successfully'}), 200
