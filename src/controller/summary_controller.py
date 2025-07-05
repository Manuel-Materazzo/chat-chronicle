from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from threading import Semaphore

from src.dto.enums.input_file_type import InputFileType
from src.dto.schemas.instagram_export_request_schema import InstagramExportRequestSchema
from src.dto.schemas.summary_response_schema import SummaryResponseSchema
from src.dto.schemas.whatsapp_export_request_schema import WhatsappExportRequestSchema
from src.service.ai_processor.ai_processor import AiProcessor
from src.service.ai_processor.ai_processor_factory import ai_processor_factory
from src.service.logging_service import LoggingService
from src.service.parser.parser_factory import parser_factory
from src.service.reader.reader_factory import reader_factory

blp = Blueprint("summarize", "usesummarizers", url_prefix="/summarize",
                description="Extract a daily summary from a list of messages")

app_config: dict = {}
logging_service: LoggingService = None
ai_processor: AiProcessor = None
ai_semaphore: Semaphore = None


def set_config(config: dict):
    global app_config
    global logging_service
    global ai_processor
    global ai_semaphore
    logging_service = LoggingService(config)
    app_config = config
    ai_processor = ai_processor_factory(config)
    concurrency_limit = config.get('inference-service', {}).get('concurrency-limit', 2)
    ai_semaphore = Semaphore(concurrency_limit)


def execute_summary_request(input_type: InputFileType, current_config: dict, raw_messages: any) -> dict:
    export_intermediate_steps = current_config.get('output', {}).get('export-intermediate-steps', False)

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
        chat_log = parser.get_messages(day)
        summary_state = ai_processor.get_summary_sync(chat_log)
        entry = {
            "date": day,
            "summary": str(summary_state.get('summary', '')),
        }
        if export_intermediate_steps:
            # remove summary and AI chat, and output everything else
            del summary_state["summary"]
            del summary_state["ai_chat"]
            entry["intermediate_steps"] = summary_state
        diary_entries.append(entry)

    return {
        "entries": diary_entries,
    }


@blp.route("/instagram-export")
class IEMessageResource(MethodView):
    @blp.arguments(InstagramExportRequestSchema)
    @blp.response(200, SummaryResponseSchema)
    def post(self, payload):
        """Creates a diary page from a list of messages in the Instagram Export format"""
        acquired = ai_semaphore.acquire(blocking=False)
        if not acquired:
            return jsonify({"error": "AI service busy, try again later"}), 503
        current_config = app_config.copy()
        current_config.update(payload["configs"])
        try:
            return execute_summary_request(InputFileType.INSTAGRAM_EXPORT, current_config, payload)
        finally:
            ai_semaphore.release()


@blp.route("/whatsapp-export")
class WEMessageResource(MethodView):
    @blp.arguments(WhatsappExportRequestSchema)
    @blp.response(200, SummaryResponseSchema)
    def post(self, payload):
        """Creates a diary page from a list of messages in the Whatsapp Export format"""
        acquired = ai_semaphore.acquire(blocking=False)
        if not acquired:
            return jsonify({"error": "AI service busy, try again later"}), 503
        current_config = app_config.copy()
        current_config.update(payload["configs"])
        try:
            return execute_summary_request(InputFileType.WHATSAPP_EXPORT, current_config, payload["messages"])
        finally:
            ai_semaphore.release()
