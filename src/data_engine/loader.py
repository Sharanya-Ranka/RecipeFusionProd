from datasets import load_dataset
import logging

logger = logging.getLogger(__name__)


def load_fusion_dataset(repo_id: str, split: str = "train", seed: int = 43):
    """Production wrapper for loading and shuffling datasets."""
    logger.info(f"Loading dataset from {repo_id}...")
    try:
        dataset = load_dataset(repo_id, split=split)
        # We shuffle here to ensure reproducibility via the seed
        dataset = dataset.shuffle(seed=seed)
        logger.info(f"Successfully loaded {len(dataset)} samples.")
        return dataset
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise
