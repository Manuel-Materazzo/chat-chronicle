from marshmallow import fields, Schema


class MessageSchema(Schema):
    sender_name = fields.String(required=True)
    timestamp = fields.DateTime(required=True)
    content = fields.String(required=True)
