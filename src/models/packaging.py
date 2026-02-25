import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

# Initialize logging to track the merge progress
logger = logging.getLogger(__name__)


def merge_and_upload(cfg):
    # 1. Load Base Model (High Precision)
    base_model = AutoModelForCausalLM.from_pretrained(
        cfg.model.repo_id,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    # 2. Load Adapters
    model = PeftModel.from_pretrained(base_model, cfg.merging.adapter_repo_id)

    # 3. Merge
    merged_model = model.merge_and_unload()

    logger.info("Merging completed successfully.")

    # 4. Push to Hub
    logger.info(f"Uploading merged model to: {cfg.merging.merged_repo_id}")
    merged_model.push_to_hub(cfg.merging.merged_repo_id, max_shard_size="2GB")
    logger.info(f"Uploading tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.repo_id)
    tokenizer.push_to_hub(cfg.merging.merged_repo_id)
    logger.info("Upload finished.")
