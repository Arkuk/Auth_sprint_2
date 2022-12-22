from flask_restx import fields

responses_tokens = {
    "access_token": fields.String(required=True),
    "refresh_token": fields.String(required=True),
}
