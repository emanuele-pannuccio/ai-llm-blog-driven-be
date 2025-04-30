from marshmallow import Schema, fields, validate, EXCLUDE


class UserAuthSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        load_only=True
    )