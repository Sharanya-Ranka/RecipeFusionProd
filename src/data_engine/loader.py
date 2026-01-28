from datasets import load_dataset
import logging

logger = logging.getLogger(__name__)


def load_fusion_dataset(data_cfg, seed: int = 42):
    """Production wrapper for loading and shuffling datasets."""
    logger.info(f"Loading dataset from {data_cfg.repo_id}...")
    try:
        dataset = load_dataset(data_cfg.repo_id, split=data_cfg.split)
        # We shuffle here to ensure reproducibility via the seed
        dataset = dataset.shuffle(seed=seed)
        # train_test_dataset = dataset.train_test_split(test_size=data_cfg.test_size)
        logger.info(f"Successfully loaded {len(dataset)} samples.")
        return dataset
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise
