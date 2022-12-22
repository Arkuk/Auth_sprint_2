from flask_restx import fields

user_schema_register = {
    # username is 4-32 characters long
    # password https://regex101.com/r/dT8sD6/1
    "username": fields.String(
        required=True,
        pattern=r"^(?=.{4,32}$)(?![.-])(?!.*[.]{2})[a-zA-Z0-9.-]+(?<![.])$",
    ),
    "password1": fields.String(
        required=True,
        pattern=r"(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}",
    ),
    "password2": fields.String(
        required=True,
        pattern=r"(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}",
    ),
}

user_schema_login = {
    "username": fields.String(required=True),
    "password": fields.String(required=True),
}

user_schema_response = {
    "id": fields.String(required=True),
    "username": fields.String(required=True),
}

user_schema_long_response = {
    "id": fields.String(required=True),
    "username": fields.String(required=True),
    "created": fields.DateTime(required=True),
}

login_history_schema = {
    "id": fields.String(required=True),
    "user_agent": fields.String(required=True),
    "created": fields.DateTime(required=True),
}

change_password_schema = {
    "old_password": fields.String(required=True),
    "new_password1": fields.String(
        required=True,
        pattern=r"(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}",
    ),
    "new_password2": fields.String(
        required=True,
        pattern=r"(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,}",
    ),
}
