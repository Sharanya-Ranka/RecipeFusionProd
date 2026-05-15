import os
import json
import pandas as pd
import re
import logging
from src.utils.utils import (
    save_to_jsonl,
    load_from_jsonl,
    get_heuristic_eval_key_from_keystring,
)
from src.utils.types import Evaluation

# logging.basicConfig(filename="heuristic_eval_summarizer.log", level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_info(eval_json):
    # Some batch formats might use 'custom_id' instead of 'key'
    keystring = eval_json.get("key", eval_json.get("custom_id", ""))

    key = get_heuristic_eval_key_from_keystring(keystring)
    evaluator = key.evaluator_model

    evaluation = Evaluation(key=key)
    score = -1
    rationale = "None"

    if eval_json.get("error", None) is not None:
        logger.info(f"Error in {eval_json}")
        evaluation.values = dict(
            score=score,
            rationale="RequestError",
        )

        return evaluation

    evaluation_str = ""
    if "gpt" in evaluator.lower():
        try:
            # Traverse the GPT output array. We iterate to find the 'message'
            # type specifically to avoid grabbing the 'reasoning' block.
            outputs = eval_json["response"]["body"]["output"]
        except Exception as e:
            logger.info(f"Information from {eval_json} couldnt be extracted")

        for out in outputs:
            if out.get("type") == "message":
                evaluation_str = out["content"][0]["text"]
                break

    elif "gemini" in evaluator.lower():
        try:
            # Traverse the Gemini output structure
            evaluation_str = eval_json["response"]["candidates"][0]["content"]["parts"][
                0
            ]["text"]
        except Exception as e:
            logger.info(f"Information from {eval_json} couldnt be extracted")

    # print(f"evaluation_str={evaluation_str}")

    # Clean up potential markdown formatting (e.g., ```json ... ```)
    evaluation_str = re.sub(
        r"^```(json)?|```$", "", evaluation_str.strip(), flags=re.IGNORECASE
    ).strip()

    # Parse the resulting string to extract the score
    try:
        parsed_eval = json.loads(evaluation_str)
        score = parsed_eval.get("score", 0)
        rationale = parsed_eval.get("rationale", None)
    except json.JSONDecodeError as e:
        info_mo = re.search(
            r'"rationale"\s*:(.*?)"score":\s*(\d)',
            evaluation_str,
            re.MULTILINE | re.DOTALL,
        )
        if info_mo:
            score = int(info_mo.group(2))
            rationale = info_mo.group(1).strip(" \n,")
        else:
            score = -1
            rationale = "JSONDecodeError"
            logger.info(f"Information from {eval_json} JSON Decode error")

    evaluation.values = dict(score=score, rationale=rationale)

    return evaluation


def extract_heuristic_evaluations(filepath):
    json_lines = []

    json_lines = load_from_jsonl(filepath, context="Heuristic Evaluations")
    data = [extract_info(line) for line in json_lines]

    return data


if __name__ == "__main__":
    # Hardcoded paths
    FOLDER_PATH = r"D:\Sharanya Personal\RecipeResearch\Results"
    INPUT_FILES = [
        "llama8bft_evalres_gemini25flash.jsonl",
        "qwen4bbase_evalres_gemini25flash.jsonl",
        "qwen4bft_evalres_gemini25flash.jsonl",
        "llama8bbase_evalres_gemini25flash.jsonl",
        "llama8bft_evalres_gpt5mini.jsonl",
        "llama8bbase_evalres_gpt5mini.jsonl",
        "qwen4bft_evalres_gpt5mini.jsonl",
        "qwen4bbase_evalres_gpt5mini.jsonl",
        "residual_evalres_gpt5mini.jsonl",
        "residual_evalres_gemini25flash.jsonl",
        "chatgpt5mini_evalres_gpt5mini.jsonl",
        "chatgpt5mini_evalres_gemini25flash.jsonl",
    ]

    all_data = []

    for file in INPUT_FILES:
        all_data.extend(extract_heuristic_evaluations(os.path.join(FOLDER_PATH, file)))

    df = pd.DataFrame(all_data)
    df.to_csv("analysis.csv")

    breakpoint()
