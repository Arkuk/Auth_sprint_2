from flask_restx import fields

role_schema_create = {
    "name": fields.String(
        required=True,
        pattern=r"^(?=.{4,32}$)(?![.-])(?!.*[.]{2})[a-zA-Z0-9.-]+(?<![.])$",
    ),
}

role_schema_response = {
    "id": fields.String(required=True),
    "name": fields.String(required=True),
}

role_schema_expect = {
    "id": fields.String(required=True),
}
