from flask_restx import fields

user_roles_schema = {
    "role_id": fields.String(required=True),
    "created": fields.DateTime(required=True),
}
