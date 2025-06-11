from marshmallow import Schema, fields


class InstagramExportMessageSchema(Schema):
    sender_name = fields.String(required=True)
    timestamp_ms = fields.Integer(required=True)
    content = fields.String(required=False)

    call_duration = fields.Integer(required=False)
    reactions = fields.List(fields.Raw(), required=False)
    share = fields.Dict(required=False)

    videos = fields.List(fields.Raw(), required=False)
    audio_files = fields.List(fields.Raw(), required=False)
    photos = fields.List(fields.Raw(), required=False)

    is_geoblocked_for_viewer = fields.Boolean(required=False)
    is_unsent_image_by_messenger_kid_parent = fields.Boolean(required=False)
