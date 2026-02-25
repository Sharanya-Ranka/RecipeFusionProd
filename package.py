import hydra
from omegaconf import DictConfig
import logging
from src.models.packaging import merge_and_upload

# Initialize logging to track the merge progress
logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    logger.info("--- Starting Model Packaging & Merging Process ---")

    merge_and_upload(cfg)


if __name__ == "__main__":
    main()
