from marshmallow import Schema, fields, validate

from schemas.post import PostORMSchema, PostSchema

class TagSchema(Schema):
    id = fields.Int(dump_only=True)
    tag = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    posts = fields.List(fields.Nested(PostORMSchema))

# class TagCreateSchema(Schema):
#     """
#     Schema per la creazione di nuovi tag
#     """
#     tag = fields.Str(
#         required=True,
#         validate=[
#             validate.Length(min=2, max=50),
#             validate.Regexp(
#                 r'^[a-zA-Z0-9_\-]+$',
#                 error="Tag can only contain letters, numbers, underscores and hyphens"
#             )
#         ]
#     )

# class TagUpdateSchema(Schema):
#     """
#     Schema per l'aggiornamento dei tag
#     """
#     tag = fields.Str(
#         validate=[
#             validate.Length(min=2, max=50),
#             validate.Regexp(
#                 r'^[a-zA-Z0-9_\-]+$',
#                 error="Tag can only contain letters, numbers, underscores and hyphens"
#             )
#         ]
#     )