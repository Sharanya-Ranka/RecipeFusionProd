import logging
from trl import SFTConfig, SFTTrainer
from peft import LoraConfig, get_peft_model
import torch

logger = logging.getLogger(__name__)


def setup_peft(model, lora_cfg):
    """Configures LoRA adapters based on Hydra settings."""
    logger.info("Initializing PEFT/LoRA configuration...")
    peft_config = LoraConfig(
        r=lora_cfg.r,
        lora_alpha=lora_cfg.alpha,
        lora_dropout=lora_cfg.dropout,
        bias="none",
        target_modules="all-linear",
        task_type="CAUSAL_LM",
    )
    return get_peft_model(model, peft_config)


def run_training(cfg, model, tokenizer, train_dataset):
    """Configures SFTConfig and executes the SFTTrainer."""

    # 1. Initialize PEFT
    model = setup_peft(model, cfg.model.lora)

    # 2. Configure SFT Training Arguments
    # We map Hydra config values directly to SFTConfig parameters
    sft_args = SFTConfig(
        output_dir=cfg.paths.output_dir,
        max_length=cfg.training.max_length,
        packing=cfg.training.packing,
        max_steps=cfg.training.max_steps,
        per_device_train_batch_size=cfg.training.batch_size,
        gradient_accumulation_steps=cfg.training.grad_accum,
        gradient_checkpointing=True,
        learning_rate=cfg.training.learning_rate,
        optim=cfg.training.optimizer,
        logging_steps=cfg.training.logging_steps,
        save_strategy="steps",
        save_steps=cfg.training.save_steps,
        fp16=False,
        bf16=True,
        assistant_only_loss=cfg.training.assistant_only_loss,
        lr_scheduler_type="cosine",
        warmup_ratio=cfg.training.warmup_ratio,
        push_to_hub=cfg.training.get("push_to_hub", True),
        report_to="tensorboard",
        dataset_kwargs={
            "add_special_tokens": False,
            "append_concat_token": True,
        },
    )

    # 3. Create Trainer Object
    logger.info("Starting SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=train_dataset,
        processing_class=tokenizer,
    )

    # 4. Execute Training
    trainer.train()

    # 5. Final Save
    trainer.save_model()
    logger.info(f"Model saved to {cfg.paths.output_dir}")
