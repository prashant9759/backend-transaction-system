from db import db
from hash import bcrypt

class UserModel(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    stores = db.relationship("StoreModel", back_populates="user")
    _password = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plainPassword):
        self._password = bcrypt.generate_password_hash(plainPassword)

class StoreModel(db.Model):
    __tablename__ = "Store"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('User.id'))

    # Relationships
    user = db.relationship("UserModel", back_populates="stores")
    receivedTransactions = db.relationship("TransactionModel", foreign_keys="[TransactionModel.receiverStoreId]", back_populates="receiverStore")
    soldTransactions = db.relationship("TransactionModel", foreign_keys="[TransactionModel.sellerStoreId]", back_populates="sellerStore")

class ProductModel(db.Model):
    __tablename__ = "Product"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(80), nullable=False)

    # Relationships
    productTransactions = db.relationship("ProductTransactionModel", back_populates="product")

class TransactionModel(db.Model):
    __tablename__ = "Transaction"

    id = db.Column(db.Integer, primary_key=True)
    receiverStoreId = db.Column(db.Integer, db.ForeignKey('Store.id'))
    sellerStoreId = db.Column(db.Integer, db.ForeignKey('Store.id'))
    amount = db.Column(db.Float, unique=False, nullable=False)
    date = db.Column(db.DateTime, unique=False, nullable=False)

    # Relationships
    receiverStore = db.relationship("StoreModel", foreign_keys=[receiverStoreId], back_populates="receivedTransactions")
    sellerStore = db.relationship("StoreModel", foreign_keys=[sellerStoreId], back_populates="soldTransactions")
    productDetails = db.relationship("ProductTransactionModel", back_populates="transaction", cascade="all, delete-orphan")

class ProductTransactionModel(db.Model):
    __tablename__ = "ProductTransaction"

    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer, db.ForeignKey('Product.id'))
    transactionId = db.Column(db.Integer, db.ForeignKey('Transaction.id'))
    quantity = db.Column(db.Float, unique=False, nullable=False)

    # Relationships
    product = db.relationship("ProductModel", back_populates="productTransactions")
    transaction = db.relationship("TransactionModel", back_populates="productDetails")