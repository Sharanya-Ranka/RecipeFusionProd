import hydra
from omegaconf import DictConfig
from src.data_engine.loader import load_fusion_dataset
from src.data_engine.formatter import apply_chat_formatting
from src.models.packaging import merge_and_upload
from src.training.trainer import run_training
from dotenv import load_dotenv

load_dotenv()


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    breakpoint()
    merge_and_upload(cfg)


if __name__ == "__main__":
    main()
