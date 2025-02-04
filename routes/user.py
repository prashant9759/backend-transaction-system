from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify


from db import db
from tables import UserModel
from schemas import UserSchema

blp = Blueprint("users", __name__, description="Operations on users")

@blp.route("/api/user")
class UserCreation(MethodView):
  @blp.response(200,UserSchema(many=True))
  def get(self):
    users = UserModel.query.all()
    for user in users:
      print(user)
    return users

  @blp.arguments(UserSchema)
  @blp.response(201,UserSchema)
  def post(self,userData):
    user = UserModel(**userData)

    try:
      db.session.add(user)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(
        500,
        message=str(e)
      )
    return user


@blp.route("/api/user/<int:user_id>")
class User(MethodView):
  @blp.response(200,UserSchema)
  def get(self,user_id):
    user = UserModel.query.get_or_404(user_id)
    return user

  @blp.arguments(UserSchema)
  @blp.response(200,UserSchema)
  def put(self,userData,user_id):
    user = UserModel.query.get(user_id)
    if not user:
      user = UserModel(**userData, id=user_id)

      try:
        db.session.add(user)
        db.session.commit()
      except SQLAlchemyError as e:
        abort(
          500,
          message=str(e)
        )

    else:
      user.name = userData["name"]
      db.session.commit()

    return user
