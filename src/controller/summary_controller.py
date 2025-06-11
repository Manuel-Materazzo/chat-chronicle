from flask.views import MethodView
from flask_smorest import Blueprint
from src.dto.schemas.chat_chronicle_request_schema import ChatChronicleRequestSchema
from src.dto.schemas.summary_response_schema import SummaryResponseSchema
from src.service.logging_service import LoggingService
from src.service.reader.instagram_export_json_reader import InstagramExportJsonReader

blp = Blueprint("summarize", "usesummarizers", url_prefix="/summarize",
                description="Extract a daily summary from a list of messages")


@blp.route("/chat-chronicle")
class CCMessageResource(MethodView):
    @blp.arguments(ChatChronicleRequestSchema)
    @blp.response(200, SummaryResponseSchema)
    def post(self, payload):
        """Creates a diary page from a list of messages in the standard ChatChronicle format"""
        return payload


@blp.route("/instagram-export")
class IEMessageResource(MethodView):
    @blp.arguments(ChatChronicleRequestSchema)
    @blp.response(200, SummaryResponseSchema)
    def post(self, payload):
        """Creates a diary page from a list of messages in the Instagram Export format"""
        return message_data


@blp.route("/whatsapp-export")
class WEMessageResource(MethodView):
    @blp.arguments(ChatChronicleRequestSchema)
    @blp.response(200, SummaryResponseSchema)
    def post(self, payload):
        """Creates a diary page from a list of messages in the Whatsapp Export format"""
        return payload
