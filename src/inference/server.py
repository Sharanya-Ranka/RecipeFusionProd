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
    Runs vLLM inference on a dataset by batching, formatting, and collecting outputs.
    """
    # 1. Format the dataset using the provided context function
    # cfg.prompts should contain the system, user, and assistant templates
    formatted_dataset = apply_chat_formatting(dataset, cfg.prompts, with_assistant_message=False)

    logger.info("Formatted dataset for inference")
    
    # 2. Extract SamplingParams from config
    # Adjust the keys based on your specific configuration structure
    sampling_params = SamplingParams(
        temperature=getattr(cfg.inference.sampling, "temperature", 0.3),
        top_p=getattr(cfg.inference.sampling, "top_p", 0.95),
        max_tokens=getattr(cfg.inference.sampling, "max_tokens", 10000),
    )

    all_outputs = []
    batch_size = cfg.inference.max_num_seqs
    num_batches = np.ceil(len(formatted_dataset) / batch_size)
    
    # 3. Chunk dataset and run inference
    # formatted_dataset is a Hugging Face Dataset; we iterate in strides
    for i in range(0, len(formatted_dataset), batch_size):
        # Slice the dataset for the current chunk
        batch = formatted_dataset[i : i + batch_size]
        
        # 'batch' from a HF Dataset slice is a dict of lists: {"messages": [[...], [...]]}
        formatted_prompts = batch["messages"]

        # Run vLLM chat inference
        # use_tqdm is optional but helpful for tracking progress
        chunk_outputs = llm.chat(
            messages=formatted_prompts, 
            sampling_params=sampling_params,
            use_tqdm=True 
        )
        
        # 4. Collect all RequestOutput objects
        all_outputs.extend(chunk_outputs)

        logger.info(f"Completed inference on examples {i} to {i+batch_size} of {len(formatted_dataset)}")

    return all_outputs
    


