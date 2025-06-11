from marshmallow import fields, Schema


class WhatsappExportRequestSchema(Schema):
    configs = fields.Dict(keys=fields.Str())
    messages = fields.List(fields.Str(), required=True)
