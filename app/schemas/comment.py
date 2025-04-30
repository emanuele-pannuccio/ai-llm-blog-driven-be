from marshmallow import Schema, fields, validate

class CommentSchema(Schema):
    comment = fields.Str()


class CommentORMSchema(Schema):
    id = fields.Integer()
    comment = fields.Str()
    deleted_at = fields.DateTime(allow_none=True)