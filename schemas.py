from marshmallow import Schema, fields

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    userId = fields.Int(load_only=True)

class PlainUserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)

class UserSchema(PlainUserSchema):
    stores = fields.Nested(PlainStoreSchema, dump_only=True, many=True)

class StoreSchema(PlainStoreSchema):
    user = fields.Nested(PlainUserSchema, dump_only=True)

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
  sellerStore = fields.Nested(PlainStoreSchema, dump_only=True)
  receiverStore = fields.Nested(PlainStoreSchema, dump_only=True)


