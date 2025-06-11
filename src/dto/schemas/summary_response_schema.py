from marshmallow import fields, Schema


class SummaryResponseSchema(Schema):
    date = fields.String(required=True)
    summary = fields.String(required=True)
    chat = fields.String(required=False)
