from marshmallow import Schema, fields, validate
from schemas.user import UserSchema

import math

class PostSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    body = fields.Str(required=True)
    category = fields.Str(required=True)
    image = fields.Str(required=False)
    tags = fields.List(fields.Str())
    status = fields.Str(required=False, validate=[
        validate.OneOf(["review", "public"])
    ])
    created_at = fields.DateTime("%Y-%m-%d %H:%M:%S")


class PostORMSchema(Schema):
    id = fields.Integer()
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    body = fields.Str(required=True)
    image = fields.Str(required=False)

    tags = fields.Method("get_tag_names")
    category = fields.Method("get_category_name")
    user = fields.Nested(UserSchema, only=("email", "name", "image"))
    created_at = fields.DateTime("%d/%m/%Y %H:%M")
    deleted_at = fields.DateTime("%d/%m/%Y %H:%M")
    read_time = fields.Method("calculate_time_read")
    status = fields.Method("get_status_name")

    def get_category_name(self, obj):
        return obj.category.name if obj.category_id else None
    
    def get_status_name(self, obj):
        return obj.status.status
    
    def calculate_time_read(self, obj):
        return "{} min".format(math.ceil(len(obj.body.split()) / 130))

    def get_tag_names(self, obj):
        return [tag.tag for tag in obj.tags]