from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError


from db import db
from tables import StoreModel, UserModel
from schemas import StoreSchema

blp = Blueprint("stores", __name__, description="Operations on Stores")

@blp.route("/api/store")
class StoreCreation(MethodView):
  @blp.response(200,StoreSchema(many=True))
  def get(self):
    stores = StoreModel.query.all()
    return stores

  @blp.arguments(StoreSchema)
  @blp.response(201,StoreSchema)
  def post(self,storeData):
    user = UserModel.query.get(storeData["userId"])
    if not user:
      abort(
        404,
        message="User not found"
      )
    store = StoreModel(**storeData)

    try:
      db.session.add(store)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(
        500,
        message=str(e)
      )
    return store


@blp.route("/api/store/<int:store_id>")
class Store(MethodView):
  @blp.response(200,StoreSchema)
  def get(self,store_id):
    store = StoreModel.query.get(store_id)
    return store

  @blp.arguments(StoreSchema)
  @blp.response(200,StoreSchema)
  def put(self,storeData,store_id):
    user = UserModel.query.get(storeData["userId"])
    if not user:
      abort(
        404,
        message="User not found"
      )
    store = StoreModel.query.get(store_id)
    if not store:
      store = StoreModel(**storeData, id=store_id)

      try:
        db.session.add(store)
        db.session.commit()
      except SQLAlchemyError as e:
        abort(
          500,
          message=str(e)
        )

    else:
      if store.userId != storeData["userId"]:
        abort(
          403,
          message="You are not allowed to change the user of the store"
        )
      store.name = storeData["name"]
      db.session.commit()

    return store

  def delete(self,store_id):
    store = StoreModel.query.get_or_404(store_id)
    db.session.delete(store)
    db.session.commit()
    return jsonify({"message":"Store deleted"}) 
