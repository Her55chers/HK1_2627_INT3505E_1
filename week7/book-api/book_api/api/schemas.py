from marshmallow import EXCLUDE, Schema, fields, validate


# ─── Book ───
class BookOut(Schema):
    id = fields.Int()
    isbn = fields.Str()
    title = fields.Str()
    author = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()


class BookIn(Schema):
    isbn = fields.Str(required=True, validate=validate.Length(min=3, max=32))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    author = fields.Str(allow_none=True, validate=validate.Length(max=255))
    price_cents = fields.Int(required=True, validate=validate.Range(min=0))
    qty_in_stock = fields.Int(load_default=0, validate=validate.Range(min=0))


class BookPatch(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=255))
    author = fields.Str(allow_none=True, validate=validate.Length(max=255))
    price_cents = fields.Int(validate=validate.Range(min=0))
    qty_in_stock = fields.Int(validate=validate.Range(min=0))


class ReserveIn(Schema):
    qty = fields.Int(required=True, validate=validate.Range(min=1))


class PageArgs(Schema):
    class Meta:
        unknown = EXCLUDE

    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    size = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


# ─── Order ───
class OrderItemIn(Schema):
    book_id = fields.Int(required=True)
    qty = fields.Int(required=True, validate=validate.Range(min=1))


class OrderIn(Schema):
    customer_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    items = fields.List(fields.Nested(OrderItemIn), required=True,
                        validate=validate.Length(min=1))


class OrderItemOut(Schema):
    book_id = fields.Int()
    book_title = fields.Function(lambda item: item.book.title)
    qty = fields.Int()
    unit_price_cents = fields.Int()


class OrderOut(Schema):
    id = fields.Int()
    customer_name = fields.Str()
    total_cents = fields.Int()
    items = fields.List(fields.Nested(OrderItemOut))
