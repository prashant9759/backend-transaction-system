from flask import Flask
from flask_smorest import Api

from db import db

from routes.user import blp as  UserBlueprint
from routes.store import blp as StoreBlueprint
from routes.product import blp as ProductBlueprint
from routes.transaction import blp as TransactionBlueprint

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Stores REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

db.init_app(app)

with app.app_context():
  db.create_all()

api = Api(app)

api.register_blueprint(UserBlueprint)
api.register_blueprint(StoreBlueprint)
api.register_blueprint(ProductBlueprint)
api.register_blueprint(TransactionBlueprint)
