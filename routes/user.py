from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask import jsonify, render_template, redirect, url_for, flash
from forms import RegisterForm
from hash import bcrypt

from db import db
from tables import UserModel
from schemas import UserSchema

blp = Blueprint("users", __name__, description="Operations on users")

def register_user(userData):
    if len(userData["password"]) < 6:
      abort(400, message="Password must be at least 6 characters long.")
    old_password = userData["password"]
    userData.pop("password")
    user = UserModel(**userData,_password=bcrypt.generate_password_hash(old_password))
    # user.password = userData["password"]
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "UNIQUE constraint failed: User.email" in str(e):
            abort(400, message="Email already exists.")
        elif "UNIQUE constraint failed: User.name" in str(e):
            abort(400, message="Name already exists.")
        else:
            abort(400, message="Integrity error occurred.")
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, message="An error occurred while processing the request.")
    return user


@blp.route("/api/user")
class UserCreation(MethodView):
  @blp.response(200,UserSchema(many=True))
  def get(self):
    users = UserModel.query.all()
    for user in users:
      print(user)
    return users

  @blp.arguments(UserSchema)
  @blp.response(201, UserSchema)
  def post(self, userData):
    user = register_user(userData)
    return user, 201


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




@blp.route("/user/register", endpoint="register_page")
class UserRegistration(MethodView):
    def get(self):
        form = RegisterForm()
        return render_template('register.html', form=form)

    def post(self):
      form = RegisterForm()
      if form.validate_on_submit():
          userData = {
          "name": form.name.data,
          "email": form.email.data,
          "password": form.password1.data  # Ensure you hash the password before storing it
        }
          try:
              user = register_user(userData)
              return redirect(url_for('market_page'))
          except IntegrityError as e:
              db.session.rollback()
              if "UNIQUE constraint failed: User.email" in str(e):
                  form.email.errors.append("Email already exists.")
              elif "UNIQUE constraint failed: User.name" in str(e):
                  form.name.errors.append("Name already exists.")
              else:
                  form.errors.append("Integrity error occurred.")
          except SQLAlchemyError as e:
              db.session.rollback()
              form.errors.append("An error occurred while processing the request.")
          print(userData) 
          user = register_user(userData)
          return redirect(url_for("market_page"))

      if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}')
      return render_template('register.html', form=form)


    
      