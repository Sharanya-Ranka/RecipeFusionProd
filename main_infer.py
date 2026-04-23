import hydra
from omegaconf import DictConfig
from src.inference.server import get_vllm, run_vllm
from src.data_engine.loader import load_fusion_dataset
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)
load_dotenv()


def save_to_file(cfg, raw_data, inference_outputs):
    # 2. Prepare the data for saving
    combined_results = []

    # We zip the original dataset rows with the vLLM output objects
    for sample, output in zip(raw_data, inference_outputs):
        # Extract the text from the first completion choice
        generated_text = output.outputs[0].text

        # Create a combined dictionary
        result_entry = {
            **sample,  # Include all original fields (cuisine_a, cuisine_b, etc.)
            "model_generated_response": generated_text,
            # "prompt_token_ids": output.prompt_token_ids,
            # "output_token_ids": output.outputs[0].token_ids
        }
        combined_results.append(result_entry)

    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(cfg.inference.inference_output_path), exist_ok=True)

    # 4. Write to JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined_results, f, indent=4, ensure_ascii=False)

    logger.info(f"Successfully saved {len(combined_results)} results to {output_path}")


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    raw_data = load_fusion_dataset(cfg.data, split="test", shuffle=False).select(range(5))
    vllm_inst = get_vllm(cfg)
    inference_outputs = run_vllm(cfg, vllm_inst, raw_data)
    save_to_file(cfg, raw_data, inference_outputs)


if __name__ == "__main__":
    main()
