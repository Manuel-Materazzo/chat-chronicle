from marshmallow import fields, Schema

from src.dto.schemas.summary_schema import SummarySchema


class SummaryResponseSchema(Schema):
    entries = fields.List(fields.Nested(SummarySchema), required=True)
