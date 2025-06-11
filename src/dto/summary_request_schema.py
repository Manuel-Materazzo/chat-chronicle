from marshmallow import fields, Schema

from src.dto.message_schema import MessageSchema


class SummaryRequestSchema(Schema):
    messages = fields.List(fields.Nested(MessageSchema), required=True)
