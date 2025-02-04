from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

class StoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    userId = fields.Int(required=True)

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    unit = fields.Str(required=True)
    price = fields.Float(required=True)

class PlainTransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    receiverStoreId = fields.Int(load_only=True)
    sellerStoreId = fields.Int(load_only=True)
    amount = fields.Float(required=True)
    timestamp = fields.DateTime(required=True)

class ProductTransactionSchema(Schema):
    productId = fields.Int(load_only=True)
    transactionId = fields.Int(load_only=True)
    quantity = fields.Float(required=True)
    product = fields.Nested(ProductSchema, dump_only=True)


class TransactionSchema(PlainTransactionSchema):
  products = fields.List(fields.Int(), load_only=True)
  quantities = fields.List(fields.Float(), required=True)
  productDetails = fields.List(fields.Nested(ProductTransactionSchema), dump_only=True)
  sellerStore = fields.Nested(StoreSchema, dump_only=True)
  receiverStore = fields.Nested(StoreSchema, dump_only=True)


