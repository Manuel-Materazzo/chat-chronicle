from marshmallow import Schema, fields


class WhatsappExportMessageSchema(Schema):
    sender_name = fields.String(required=True)
    timestamp = fields.String(required=True)
    content = fields.String(required=True)
