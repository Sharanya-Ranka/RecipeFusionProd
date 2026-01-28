import hydra
import logging
from vllm import LLM, SamplingParams

logger = logging.getLogger(__name__)


def run_server(cfg):
    logger.info(f"Initializing vLLM server for model: {cfg.model.path}")

    llm = LLM(
        model=cfg.model.path,
        gpu_memory_utilization=cfg.server.gpu_memory_utilization,
        tensor_parallel_size=cfg.model.tensor_parallel_size,
    )

    sampling_params = SamplingParams(
        temperature=cfg.sampling.temperature,
        top_p=cfg.sampling.top_p,
        max_tokens=cfg.sampling.max_tokens,
    )

    return llm, sampling_params
