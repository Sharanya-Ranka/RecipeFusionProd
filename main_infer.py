import hydra
from omegaconf import DictConfig

# from src.inference.server import get_vllm, run_vllm
from src.data_engine.loader import load_fusion_dataset
from src.utils.types import RecipeFusionInferenceKey
from src.utils.utils import save_to_jsonl
from dotenv import load_dotenv
import os
import logging
import json
import mock

logger = logging.getLogger(__name__)
load_dotenv()


def save_to_file(cfg, raw_data, inference_outputs):
    # 2. Prepare the data for saving
    combined_results = []

    # We zip the original dataset rows with the vLLM output objects
    for sample, output in zip(raw_data, inference_outputs):
        # Extract the text from the first completion choice
        generated_text = output.outputs[0].text
        inf_key = RecipeFusionInferenceKey(
            id=cfg.inference.inference_name,
            cuisine_a=sample["cuisine_a"],
            cuisine_b=sample["cuisine_b"],
        )

        # Create a combined dictionary
        result_entry = {
            "key": inf_key.model_dump(),
            "model_generated_response": generated_text,
        }
        combined_results.append(result_entry)

    output_path = os.path.join(
        cfg.inference.inference_folderpath,
        f"{cfg.inference.inference_name}{cfg.inference.inference_suffix}.jsonl",
    )

    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    save_to_jsonl(
        combined_results, output_path, mode="w", context="Saving Inference Responses"
    )

    logger.info(f"Successfully saved {len(combined_results)} results to {output_path}")


def temp():
    with open(
        r"D:\Sharanya Personal\RecipeResearchProd\data\testing\test_inference.json", "r"
    ) as fp:
        inf_op = json.load(fp)[2:]

    inference_outputs = [mock.MagicMock() for _ in range(len(inf_op))]
    for i in range(len(inf_op)):
        inference_outputs[i].outputs[0].text = inf_op[i]["model_generated_response"]

    return inference_outputs


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    raw_data = load_fusion_dataset(cfg.data, split="test", shuffle=False).select(
        range(2)
    )
    # vllm_inst = get_vllm(cfg)
    inference_outputs = temp()  # run_vllm(cfg, vllm_inst, raw_data)  # temp()  #
    # breakpoint()
    save_to_file(cfg, raw_data, inference_outputs)


if __name__ == "__main__":
    main()
