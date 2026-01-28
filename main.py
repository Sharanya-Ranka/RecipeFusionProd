import hydra
from omegaconf import DictConfig
from src.data_engine.loader import load_fusion_dataset
from src.data_engine.formatter import apply_chat_formatting
from src.models.factory import build_model_and_tokenizer
from src.training.trainer import run_training
from dotenv import load_dotenv

load_dotenv()


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    # breakpoint()
    # 1. Load and Format Data
    raw_data = load_fusion_dataset(cfg.data)
    formatted_data = apply_chat_formatting(raw_data, cfg.prompts)

    # breakpoint()
    # 2. Build the Model and Tokenizer
    model, tokenizer = build_model_and_tokenizer(cfg.model)

    # 3. Run the Training Pipeline
    run_training(cfg, model, tokenizer, formatted_data)


if __name__ == "__main__":
    main()
