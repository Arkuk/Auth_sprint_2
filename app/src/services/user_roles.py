from flask_restx import abort
from flask_restx._http import HTTPStatus

from db.postgres import db
from models.user_role import user_role


class UserRoles:
    def get_user_roles(self, user_id):
        """Получить список ролей конкретного пользователя"""
        query = user_role.select().where(user_role.c.user_id == user_id)
        roles_id = db.session.execute(query).all()
        return roles_id

    def assign_role(self, user_id, body: dict):
        """Присвоение роли конкретному пользователю"""
        role_id = body["role_id"]
        role_query = (
            user_role.select()
            .with_only_columns()
            .where(user_role.c.role_id == role_id and user_role.c.user_id == user_id)
        )
        role = db.session.execute(role_query).all()
        if not role:
            add_role_query = user_role.insert().values(user_id=user_id, role_id=role_id)
            db.session.execute(add_role_query)
            db.session.commit()
            return HTTPStatus.CREATED
        else:
            abort(HTTPStatus.CONFLICT, "Role is already assigned")

    def discard_role(self, user_id, body: dict):
        """Удаление роли у пользователя"""
        role_id = body["role_id"]
        role = (
            user_role.select()
            .with_only_columns([user_role.c.id])
            .where(user_role.c.role_id == role_id and user_role.c.user_id == user_id)
        )
        role = db.session.execute(role).first()
        if role:
            """.first(), на случай нештатной ситуации, когда у пользователя bможет оказаться несколько одинаковых ролей"""
            delete_role = user_role.delete().where(user_role.c.id == role[0])
            db.session.execute(delete_role)
            db.session.commit()
            return HTTPStatus.OK
        else:
            abort(HTTPStatus.CONFLICT, "No role to delete")


user_roles = UserRoles()
