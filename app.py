from flask import Flask, render_template
from flask_smorest import Api


from db import db
from hash import bcrypt

from routes.user import blp as  UserBlueprint
from routes.store import blp as StoreBlueprint
from routes.product import blp as ProductBlueprint
from routes.transaction import blp as TransactionBlueprint

from tables import *

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "Stores REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SECRET_KEY"] ="3e7fa6f5a6ba9143faca1463"
app.config["DEBUG"] = True

db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
  db.create_all()

api = Api(app)

@app.route("/")
@app.route("/home")
def home_page():
  return render_template("home.html")

@app.route("/market")
def market_page():
    items = [
        {'id': 1, 'name': 'Phone', 'barcode': '893212299897', 'price': 500},
        {'id': 2, 'name': 'Laptop', 'barcode': '123985473165', 'price': 900},
        {'id': 3, 'name': 'Keyboard', 'barcode': '231985128446', 'price': 150}
    ]
    return render_template('market.html', items=items)

api.register_blueprint(UserBlueprint)
api.register_blueprint(StoreBlueprint)
api.register_blueprint(ProductBlueprint)
api.register_blueprint(TransactionBlueprint)

if __name__ == "__main__":
    app.run(debug=True)  # Ensure the app runs in debug mode
