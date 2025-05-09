from marshmallow import Schema, fields, validate

from schemas.post import PostORMSchema

class CategoryCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    image = fields.String(required=True, validate=validate.Length(min=1))

class CategorySchema(Schema):
    id = fields.Integer()
    name = fields.String()
    posts = fields.List(fields.Nested(PostORMSchema))
