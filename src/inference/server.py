import hydra
import logging
from vllm import LLM, SamplingParams
from datasets import load_dataset, Dataset
from src.data_engine.formatter import apply_chat_formatting
import numpy as np

logger = logging.getLogger(__name__)


def get_vllm(cfg):
    logger.info(f"Initializing vLLM server for model: {cfg.inference.hf_model_id}")

    llm = LLM(
        model=cfg.inference.hf_model_id,
        gpu_memory_utilization=cfg.inference.gpu_memory_utilization,
        max_num_seqs=cfg.inference.max_num_seqs,
        max_model_len=cfg.inference.sampling.max_tokens,
        trust_remote_code=True,
        quantization="bitsandbytes",
    )

    return llm

def run_vllm(cfg, llm: LLM, dataset: Dataset):
    """
    Runs vLLM inference on the entire dataset at once, leveraging 
    vLLM's internal continuous batching and scheduling.
    """
    # 1. Format the dataset
    formatted_dataset = apply_chat_formatting(dataset, cfg.prompts, with_assistant_message=False)
    logger.info(f"Formatted dataset for inference. Total samples: {len(formatted_dataset)}")
    
    # 2. Extract SamplingParams from config
    sampling_params = SamplingParams(
        temperature=getattr(cfg.inference.sampling, "temperature", 0.3),
        top_p=getattr(cfg.inference.sampling, "top_p", 0.95),
        max_tokens=getattr(cfg.inference.sampling, "max_tokens", 10000),
    )

    # 3. Extract all formatted messages at once
    # For a HF Dataset, formatted_dataset[:] returns a dict of lists
    all_formatted_prompts = formatted_dataset["messages"]

    # 4. Run vLLM chat inference on the full list
    # vLLM will respect the max_num_seqs set during initialization 
    # and handle the queue internally.
    logger.info("Starting global inference session...")
    all_outputs = llm.chat(
        messages=all_formatted_prompts, 
        sampling_params=sampling_params,
        use_tqdm=True 
    )
    
    logger.info(f"Completed inference on all {len(all_outputs)} examples.")

    return all_outputs
    


