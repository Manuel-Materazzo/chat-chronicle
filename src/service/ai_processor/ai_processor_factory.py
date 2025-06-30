from src.dto.enums.summarization_strategy import SummarizationStrategy
from src.service.ai_processor.ai_processor import AiProcessor
from src.service.ai_processor.linear_ai_processor import LinearAiProcessor


def ai_processor_factory(config: dict) -> AiProcessor:
    """
    Instantiates the ai_processor for the provided processing tipe and returns it.
    :param config: Dictionary containing the configuration of the application.
    :return:
    """
    # get configs
    strategy = config.get('summarization', {}).get('strategy', SummarizationStrategy.MAP_REDUCE)
    api_key = config.get('inference-service', {}).get('api-key', '')
    base_url = config.get('inference-service', {}).get('endpoint', 'http://127.0.0.1:1234/v1')
    concurrency_limit = config.get('inference-service', {}).get('concurrency-limit', 1)
    timeout = config.get('inference-service', {}).get('timeout', 600)

    if strategy == SummarizationStrategy.LINEAR:
        return _get_linear_processor(config, api_key, base_url, timeout, concurrency_limit)

    strategies = [e for e in SummarizationStrategy]
    message = f"AI summarization Strategy not supported, please choose one of the following: {strategies}"
    raise ValueError(message)


def _get_linear_processor(config: dict, api_key, base_url, timeout, concurrency_limit) -> LinearAiProcessor:
    linear_configs = config.get('summarization', {}).get('linear-strategy', {})
    max_tokens = linear_configs.get('max-tokens', 2000)
    model_name = linear_configs.get('model-name', 'gemma-3-4b-it-qat')
    temperature = linear_configs.get('temperature', 0.4)
    top_p = linear_configs.get('top-p', 0.7)
    system_prompt = linear_configs.get('system-prompt', '')
    user_prompt = linear_configs.get('user-prompt', '')
    return LinearAiProcessor(system_prompt, user_prompt, model_name, temperature, max_tokens, top_p, api_key,
                             base_url, timeout, concurrency_limit)

