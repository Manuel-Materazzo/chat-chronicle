from src.dto.enums.summarization_strategy import SummarizationStrategy
from src.service.ai_processor.ai_processor import AiProcessor
from src.service.ai_processor.linear_ai_processor import LinearAiProcessor
from src.service.ai_processor.map_reduce_ai_processor import MapReduceAiProcessor


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

    if strategy == SummarizationStrategy.MAP_REDUCE:
        return _get_map_reduce_processor(config, api_key, base_url, timeout, concurrency_limit)

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


def _get_map_reduce_processor(config: dict, api_key, base_url, timeout, concurrency_limit):
    token_per_chunk = config.get('summarization', {}).get('map-reduce-strategy', {}).get('token-per-chunk', 4000)
    # Map agent settings
    map_configs = config.get('summarization', {}).get('map-reduce-strategy', {}).get('map-agent', {})
    map_max_tokens = map_configs.get('max-tokens', 2000)
    map_model_name = map_configs.get('model-name', 'gemma-3-4b-it-qat')
    map_temperature = map_configs.get('temperature', 0.2)
    map_top_p = map_configs.get('top-p', 0.7)
    map_system_prompt = map_configs.get('system-prompt', '')
    map_user_prompt = map_configs.get('user-prompt', '')

    # Reduce agent settings
    reduce_configs = config.get('summarization', {}).get('map-reduce-strategy', {}).get('reduce-agent', {})
    reduce_max_tokens = reduce_configs.get('max-tokens', 2000)
    reduce_model_name = reduce_configs.get('model-name', 'gemma-3-4b-it-qat')
    reduce_temperature = reduce_configs.get('temperature', 0.4)
    reduce_top_p = reduce_configs.get('top-p', 0.7)
    reduce_system_prompt = reduce_configs.get('system-prompt', '')
    reduce_user_prompt = reduce_configs.get('user-prompt', '')

    return MapReduceAiProcessor(map_system_prompt, map_user_prompt, map_model_name, map_temperature, map_max_tokens,
                                map_top_p, reduce_system_prompt, reduce_user_prompt, reduce_model_name,
                                reduce_temperature, reduce_max_tokens, reduce_top_p, token_per_chunk, api_key, base_url,
                                timeout, concurrency_limit)
