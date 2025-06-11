from flask.views import MethodView
from flask_smorest import Blueprint

from src.dto.summary_request_schema import SummaryRequestSchema

blp = Blueprint("summarize", "usesummarizers", url_prefix="/summarize",
                description="Extract a daily summary from a list of messages")


@blp.route("/chat-chronicle")
class MessageResource(MethodView):
    @blp.arguments(SummaryRequestSchema)
    @blp.response(200, SummaryRequestSchema)
    def post(self, message_data):
        """Creates a diary page from a list of messages in the standard ChatChronicle format"""
        return message_data


@blp.route("/instagram-export")
class MessageResource(MethodView):
    @blp.arguments(SummaryRequestSchema)
    @blp.response(200, SummaryRequestSchema)
    def post(self, message_data):
        """Creates a diary page from a list of messages in the Instagram Export format"""
        return message_data


@blp.route("/whatsapp-export")
class MessageResource(MethodView):
    @blp.arguments(SummaryRequestSchema)
    @blp.response(200, SummaryRequestSchema)
    def post(self, message_data):
        """Creates a diary page from a list of messages in the Whatsapp Export format"""
        return message_data



