import json
import logging
from typing import List, Any, Dict
from src.utils.types import EvaluationKey, RecipeFusionInferenceKey
import re

logger = logging.getLogger(__name__)


def save_to_jsonl(
    data: List[Any], filepath: str, mode: str = "w", context: str = "JSONL save"
):
    """
    Saves a list of items to a JSON Lines (.jsonl) file.
    """
    try:
        # Always enforce utf-8 encoding
        with open(filepath, mode, encoding="utf-8") as f:
            for item in data:
                # Dump the individual item and append a newline
                f.write(json.dumps(item) + "\n")
    except Exception as e:
        logger.error(
            f"Failed during '{context}': Could not write to {filepath}. Error: {str(e)}"
        )


def load_from_jsonl(filepath: str, context: str = "JSONL load") -> List[Any] | None:
    """
    Loads a JSON Lines (.jsonl) file and returns a list of parsed dictionaries.
    """
    parsed_data = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # Enumerate allows us to track the line number for better error messages
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:  # Skip blank lines safely
                    parsed_data.append(json.loads(line))

        return parsed_data

    except FileNotFoundError as e:
        # Fixed the error message: this is for missing files, not bad formatting
        logger.error(f"Failed during '{context}': File not found at {filepath}.")
        return None

    except json.JSONDecodeError as e:
        # We can now pinpoint exactly which line in the JSONL file is broken
        logger.error(
            f"Failed during '{context}': Invalid JSON format in {filepath} on line {line_num}. Error: {str(e)}"
        )
        return None


def get_recipefusion_inference_key(
    id, cuisine_a, cuisine_b
) -> RecipeFusionInferenceKey:
    return RecipeFusionInferenceKey(id=id, cuisine_a=cuisine_a, cuisine_b=cuisine_b)


def get_heuristic_eval_key(
    id, cuisine_a, cuisine_b, evaluator_model, dimension
) -> EvaluationKey:
    rf_key = get_recipefusion_inference_key(id, cuisine_a, cuisine_b)

    return EvaluationKey(
        inference_key=rf_key,
        evaluation_type="heuristic",
        dimension=dimension,
        evaluator_model=evaluator_model,
    )


def get_deterministic_eval_key(id, cuisine_a, cuisine_b, dimension) -> EvaluationKey:
    rf_key = get_recipefusion_inference_key(id, cuisine_a, cuisine_b)

    return EvaluationKey(
        inference_key=rf_key,
        evaluation_type="deterministic",
        dimension=dimension,
    )


def get_heurisic_eval_keystring_from_key(key: EvaluationKey) -> str:
    return f"{key.inference_key.id}_{key.inference_key.cuisine_a}_{key.inference_key.cuisine_b}_{key.evaluator_model}_{key.dimension}"


def get_heuristic_eval_key_from_keystring(keystring: str) -> EvaluationKey:
    mo = re.match(
        r"(?P<id>.*?)_(?P<cuisinea>.*?)_(?P<cuisineb>.*?)_(?P<evaluator>.*?)_(?P<dimension>.*)",
        keystring,
    )

    if not mo:
        return None
    else:
        gd = mo.groupdict()
        return EvaluationKey(
            inference_key=get_recipefusion_inference_key(
                gd["id"], gd["cuisinea"], gd["cuisineb"]
            ),
            evaluation_type="heuristic",
            dimension=gd["dimension"],
            evaluator_model=gd["evaluator"],
        )


# --- 2. Helper: JSON Extractor ---
import json
import re
from typing import Any, Optional


def extract_json(content: str) -> Optional[Any]:
    """
    Robustly extract the largest valid JSON object or array from a string.
    Handles Markdown code blocks and mixed text.
    """
    if not content:
        return None

    # 1. Strip Markdown Code Blocks (```json ... ```)
    # This regex looks for ``` optionally followed by 'json',
    # capturing the content inside, with DOTALL handling newlines.
    match = re.search(r"```(?:json)?\s*(.*?)```", content, re.DOTALL)
    if match:
        content = match.group(1)

    # 2. Find the starting positions of { and [
    start_brace = content.find("{")
    start_bracket = content.find("[")

    # If neither exists, it's not JSON
    if start_brace == -1 and start_bracket == -1:
        return None

    # 3. Determine the outer bounds based on which appears first
    # We prioritize the first occurring character to capture the main block
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start = start_brace
        end = content.rfind("}") + 1
    else:
        start = start_bracket
        end = content.rfind("]") + 1

    # Validation: Ensure we actually found a start and an end
    if start == -1 or end == 0:
        return None

    # 4. Extract and Parse
    json_str = content[start:end]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Optional: Add error logging here if needed
        return None


def fill_prompt_template(template: str, variables: dict):
    """Function to fill in a prompt template with given variables, written within {{}}"""
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        template = template.replace(placeholder, str(value))
    return template
