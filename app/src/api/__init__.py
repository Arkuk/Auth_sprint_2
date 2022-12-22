from flask_restx import Api

from api.v1.admin_roles import api as api_admin_roles
from api.v1.admin_user_roles import api as api_admin_user_roles
from api.v1.admin_users import api as api_admin_users
from api.v1.authorized import api as api_authorized
from api.v1.not_authorized import api as api_not_authorized

api = Api(
    version="1.0",
    title="Auth",
    description="Auth for praktikum",
    doc="/api/v1/swagger",
)

api.add_namespace(api_not_authorized, path="/api/v1")
api.add_namespace(api_authorized, path="/api/v1")
api.add_namespace(api_admin_users, path="/api/v1")
api.add_namespace(api_admin_user_roles, path="/api/v1")
api.add_namespace(api_admin_roles, path="/api/v1")
