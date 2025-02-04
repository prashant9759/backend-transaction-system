from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError


from db import db
from tables import ProductModel
from schemas import ProductSchema

blp = Blueprint("products", __name__, description="Operations on Products")

@blp.route("/api/product")
class ProductCreation(MethodView):
  @blp.response(200,ProductSchema(many=True))
  def get(self):
    products = ProductModel.query.all()
    return products

  @blp.arguments(ProductSchema)
  @blp.response(201,ProductSchema)
  def post(self,productData):
    product = ProductModel(**productData)

    try:
      db.session.add(product)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(
        500,
        message=str(e)
      )
    return product


@blp.route("/api/product/<int:product_id>")
class Store(MethodView):
  @blp.response(200,ProductSchema)
  def get(self,product_id):
    product = ProductModel.query.get(product_id)
    return product

  @blp.arguments(ProductSchema)
  @blp.response(200,ProductSchema)
  def put(self,productData,product_id):
    product = ProductModel.query.get(product_id)
    if not product:
      product = ProductModel(**productData, id=product_id)

      try:
        db.session.add(product)
        db.session.commit()
      except SQLAlchemyError as e:
        abort(
          500,
          message=str(e)
        )

    else:
      product.name = productData["name"]
      product.price = productData["price"]
      db.session.commit()

    return product

  def delete(self,product_id):
    product = ProductModel.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Product deleted"}) 
