import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import logging

logger = logging.getLogger(__name__)


def inject_chat_generation_tags(tokenizer):
    """Safely injects generation tags for assistant-only loss training."""
    current_template = tokenizer.chat_template
    if not current_template:
        logger.warning("Tokenizer has no chat_template. Skipping injection.")
        return tokenizer

    old_snippet = "{{- '<|im_start|>' + message.role + '\\n' + content }}"
    new_snippet = "{{- '<|im_start|>' + message.role + '\\n' }}{% generation %}{{ content }}{% endgeneration %}"

    if old_snippet in current_template:
        tokenizer.chat_template = current_template.replace(old_snippet, new_snippet)
        logger.info("Successfully injected {% generation %} tags into the template.")
    else:
        logger.error(
            "Could not find expected snippet in chat_template. Injection failed."
        )

    return tokenizer


def build_model_and_tokenizer(model_cfg):
    """Initialize model with quantization and hardware awareness."""

    # 1. Setup Quantization
    q_cfg = model_cfg.quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=q_cfg.load_in_4bit,
        bnb_4bit_use_double_quant=q_cfg.bnb_4bit_use_double_quant,
        bnb_4bit_quant_type=q_cfg.bnb_4bit_quant_type,
        bnb_4bit_compute_dtype=torch.float16,  # Map string from config to torch type
    )

    # 2. Load Model
    model = AutoModelForCausalLM.from_pretrained(
        model_cfg.repo_id,
        quantization_config=bnb_config,
        device_map="auto",
        attn_implementation=model_cfg.attn_implementation,
    )

    # 3. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_cfg.repo_id)

    # Apply the injection based on the Hydra config flag
    if model_cfg.get("inject_generation_tags", False):
        tokenizer = inject_chat_generation_tags(tokenizer)

    return model, tokenizer
