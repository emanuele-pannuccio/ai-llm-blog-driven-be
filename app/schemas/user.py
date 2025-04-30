from marshmallow import Schema, fields, validate, EXCLUDE

class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=50),
            validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', error="Minimum eight characters, at least one letter, one number and one special character")
        ],
        load_only=True
    )
    name = fields.Str(required=True, validate=validate.Length(min=1))
    image = fields.Url()


class UserORMSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    
    email = fields.Email()
    password = fields.Str(
        validate=[
            validate.Length(min=8, max=50),
            validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', error="Minimum eight characters, at least one letter, one number and one special character")
        ],
        load_only=True
    )
    name = fields.Str(validate=validate.Length(min=1))
    image = fields.Str(validate=[
        validate.Regexp(r'^(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&=]*)', error="Image URL not valid")
    ])

    role = fields.Method('get_role')

    def get_role(self, obj):
        return obj.role.role
