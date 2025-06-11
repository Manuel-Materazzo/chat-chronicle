from flask.views import MethodView
from flask_smorest import Blueprint

from src.dto.enums.input_file_type import InputFileType
from src.dto.schemas.chat_chronicle_request_schema import ChatChronicleRequestSchema
from src.dto.schemas.instagram_export_request_schema import InstagramExportRequestSchema
from src.dto.schemas.summary_response_schema import SummaryResponseSchema
from src.service.ai_service import AiService
from src.service.logging_service import LoggingService
from src.service.parser.parser_factory import parser_factory
from src.service.reader.reader_factory import reader_factory

blp = Blueprint("summarize", "usesummarizers", url_prefix="/summarize",
                description="Extract a daily summary from a list of messages")

app_config: dict = {}
logging_service: LoggingService = None
ai_service: AiService = None


def set_config(config: dict):
    global app_config
    global logging_service
    global ai_service
    logging_service = LoggingService(config)
    app_config = config
    ai_service = AiService(config)


def execute_summary_request(input_type: InputFileType, current_config: dict, raw_messages: any) -> dict:
    export_chat = current_config.get('output', {}).get('export-chat-log', False)

    # instantiate services
    reader = reader_factory(input_type, current_config)
    parser = parser_factory(input_type, current_config)

    # standardize, parse, and sort messages
    standardized_messages = reader.standardize_messages(raw_messages)
    parser.parse(standardized_messages)
    parser.sort_bucket()

    day_list = parser.get_available_days()

    diary_entries = []

    for day in day_list:
        chat_log = parser.get_chat_log(day)
        summary = ai_service.get_summary_sync(chat_log)
        entry = {
            "date": day,
            "summary": str(summary),
        }
        if export_chat:
            entry["chat"] = chat_log
        diary_entries.append(entry)

    return {
        "entries": diary_entries,
    }


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
