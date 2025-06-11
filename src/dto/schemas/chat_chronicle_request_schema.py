from marshmallow import fields, Schema

from src.dto.schemas.message_schema import MessageSchema


class ChatChronicleRequestSchema(Schema):
    configs = fields.Dict(keys=fields.Str())
    messages = fields.List(fields.Nested(MessageSchema), required=True)
