from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from flask import request
from db import db
from tables import TransactionModel, ProductTransactionModel, StoreModel, ProductModel, UserModel
from schemas import TransactionSchema
from datetime import datetime

blp = Blueprint("transactions", __name__, description="Operations on transactions")



def validate_required_fields(data, required_fields):
    if not data:
        abort(400, message="Request data is missing.")
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        abort(400, message=f"Request must contain the following fields: {', '.join(missing_fields)}")



def validate_date_format(date_str, field_name):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        abort(400, message=f"{field_name} format must be 'YYYY-MM-DD'.")


def get_store_ids(user_id):
    try:
        # Find all store IDs corresponding to the userId
        store_ids = [store.id for store in StoreModel.query.filter_by(userId=user_id).all()]
        return store_ids
    except SQLAlchemyError as e:
        abort(500, message=f"An error occurred while retrieving store IDs: {str(e)}")


def get_transactions(store_ids, start_date, end_date):
    
        try:

            # Find all transactions where either receiverStoreId or sellerStoreId is in store_ids
            transactions = TransactionModel.query.filter(
                (TransactionModel.receiverStoreId.in_(store_ids) | TransactionModel.sellerStoreId.in_(store_ids)),
                TransactionModel.date.between(start_date, end_date)
            ).all()

            # Serialize the transactions
            transaction_schema = TransactionSchema(many=True)
            response = transaction_schema.dump(transactions)

            return transactions

        except SQLAlchemyError as e:
            abort(500, message=f"An error occurred while retrieving transactions: {str(e)}")

@blp.route("/api/transaction")
class TransactionCreation(MethodView):
    @blp.arguments(TransactionSchema)
    @blp.response(201, TransactionSchema)
    def post(self, transaction_data):
        try:
            # Check if 'products' and 'quantities' lists have the same length
            if len(transaction_data["products"]) != len(transaction_data["quantities"]):
                abort(400, message="'products' and 'quantities' lists must have the same length.")

            # Validate receiverStoreId and sellerStoreId
            receiver_store = StoreModel.query.get(transaction_data["receiverStoreId"])
            seller_store = StoreModel.query.get(transaction_data["sellerStoreId"])
            if not receiver_store:
                abort(400, message="Receiver store does not exist.")
            if not seller_store:
                abort(400, message="Seller store does not exist.")

            # Validate products
            product_ids = transaction_data["products"]
            existing_products = ProductModel.query.filter(ProductModel.id.in_(product_ids)).all()
            if len(existing_products) != len(product_ids):
                abort(400, message="One or more products do not exist.")

            # Create a new transaction
            new_transaction = TransactionModel(
                receiverStoreId=transaction_data["receiverStoreId"],
                sellerStoreId=transaction_data["sellerStoreId"],
                amount=transaction_data["amount"],
                date=transaction_data["timestamp"]
            )
            db.session.add(new_transaction)
            db.session.flush()  # Flush to get the transaction ID

            # Add products to the transaction and store quantities
            product_transactions = []
            for product_id, quantity in zip(transaction_data["products"], transaction_data["quantities"]):
                new_product_transaction = ProductTransactionModel(
                    productId=product_id,
                    transactionId=new_transaction.id,
                    quantity=quantity
                )
                db.session.add(new_product_transaction)
                product_transactions.append(new_product_transaction)

            db.session.commit()

            return new_transaction

        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"An error occurred while processing the transaction: {str(e)}")



@blp.route("/api/transactions/user")
class RetrieveTransactions(MethodView):
    @blp.response(200, TransactionSchema(many=True))
    def post(self):
        data = request.json

        # Validate required fields
        validate_required_fields(data, ["userId", "startDate", "endDate"])

        user_id = data["userId"]
        start_date_str = data["startDate"]
        end_date_str = data["endDate"]

        # Validate date format
        start_date = validate_date_format(start_date_str, "startDate")
        end_date = validate_date_format(end_date_str, "endDate")

        # Validate user existence
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message="User not found.")

        # Get store IDs corresponding to the user
        store_ids = get_store_ids(user_id)

        # Get transactions
        transactions = get_transactions(store_ids, start_date, end_date)

        return transactions, 200



@blp.route("/api/transactions/store")
class RetrieveStoreTransactions(MethodView):
    @blp.response(200, TransactionSchema(many=True))
    def post(self):
        data = request.json

        # Validate required fields
        validate_required_fields(data, ["storeId", "startDate", "endDate"])

        store_id = data["storeId"]
        start_date_str = data["startDate"]
        end_date_str = data["endDate"]

        # Validate date format
        start_date = validate_date_format(start_date_str, "startDate")
        end_date = validate_date_format(end_date_str, "endDate")

        # Validate store existence
        store = StoreModel.query.get(store_id)
        if not store:
            abort(404, message="Store not found.")

        # Get transactions
        transactions = get_transactions([store_id], start_date, end_date)

        return transactions, 200