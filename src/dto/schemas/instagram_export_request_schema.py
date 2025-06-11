from marshmallow import fields, Schema

from src.dto.schemas.instagram_export_message_schema import InstagramExportMessageSchema


class InstagramExportRequestSchema(Schema):
    configs = fields.Dict(keys=fields.Str())
    messages = fields.List(fields.Nested(InstagramExportMessageSchema), required=True)
