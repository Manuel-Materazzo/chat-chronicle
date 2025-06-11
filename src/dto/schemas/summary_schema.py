from marshmallow import fields, Schema


class SummarySchema(Schema):
    date = fields.String(required=True)
    summary = fields.String(required=True)
    chat = fields.String(required=False)
