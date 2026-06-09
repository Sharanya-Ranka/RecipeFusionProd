import json
import os
import networkx as nx
import re
import logging
from src.utils.types import RecipeFusionInferenceKey
from src.utils.utils import save_to_jsonl, load_from_jsonl

# logging.basicConfig(
#     filename="response_parsing_log.log",
#     level=logging.INFO,
#     # format='%(asctime)s - %(levelname)s - %(message)s'
# )
logger = logging.getLogger(__name__)

"""
The model is expected to produce output in the following format:

Original Recipes : <RecipeA>(<CuisineA>) + <RecipeB>(<CuisineB>)

RecipeA:
<RecipeA>
<RecipeJSONA>

RecipeB:
<RecipeB>
<RecipeJSONB>

Fusion Explanation:
<Fusion Explanation>

RecipeFusion:
<RecipeFusion>
<RecipeJSONFusion>
"""

RECIPE_A = "RecipeA"
RECIPE_B = "RecipeB"
RECIPE_FUSION = "RecipeFusion"

EXPECTED_KEYS = {
    "OrigRecipeA",
    "CuisineA",
    "OrigRecipeB",
    "CuisineB",
    "Fusion_Explanation",
    # Recipe A Keys
    f"{RECIPE_A}_Title",
    f"{RECIPE_A}_JSON_str",
    f"{RECIPE_A}_parsed",
    # Recipe B Keys
    f"{RECIPE_B}_Title",
    f"{RECIPE_B}_JSON_str",
    f"{RECIPE_B}_parsed",
    # Recipe Fusion Keys
    f"{RECIPE_FUSION}_Title",
    f"{RECIPE_FUSION}_JSON_str",
    f"{RECIPE_FUSION}_parsed",
}


def apply_other_fixes(eval_str):
    return eval_str


def apply_common_fixes(eval_str):
    eval_str = re.sub(r"\*\*", "", eval_str)
    eval_str = re.sub(r"---", "", eval_str)
    # To fix JSON parsin issues for strings like "amount": 1/4,
    recipe_str_fixed = re.sub(
        r'"amount":\s*([^"]+?),',
        r'"amount": "\1",',
        eval_str,
    )

    return recipe_str_fixed


def apply_fixes(recipefusion_str):
    eval_str = apply_common_fixes(recipefusion_str)
    eval_str = apply_other_fixes(eval_str)

    return eval_str


def extract_parts(output_string):
    extracted_data = {}

    # 1. Extract the "Original Recipes" line
    # Targeted regex just for this specific single line
    orig_pattern = r"Original Recipes\s*:\s*(?P<OrigRecipeA>[^(]+)\((?P<CuisineA>[^)]+)\)\s*\+\s*(?P<OrigRecipeB>[^(]+)\((?P<CuisineB>[^)]+)\)"
    orig_match = re.search(orig_pattern, output_string, re.IGNORECASE)
    if orig_match:
        for key, value in orig_match.groupdict().items():
            extracted_data[key] = value.strip()

    # Helper function: safely extract content between headers
    def get_section(start_header: str, end_header: str = None) -> str:
        ends = rf"^{end_header}" if end_header else r"\Z"
        # Look for the start header, capture everything lazily until an end header or the end of the string
        pattern = rf"^{start_header}\s*(.*?)(?={ends})"
        match = re.search(pattern, output_string, re.DOTALL | re.MULTILINE)
        return match.group(1).strip() if match else ""

    # 2. Extract the raw text blocks for each section
    # We pass a list of potential "next headers" so the regex knows when to stop capturing
    recipe_a_block = get_section(r"RecipeA:", r"RecipeB:")
    recipe_b_block = get_section(r"RecipeB:", r"Fusion Explanation:")
    fusion_exp = get_section(r"Fusion Explanation:", r"RecipeFusion:")
    recipe_fusion_block = get_section(r"RecipeFusion:")

    if fusion_exp:
        extracted_data["Fusion_Explanation"] = fusion_exp

    # Helper function: split a recipe block into its Title and JSON components
    def parse_recipe_block(block: str, prefix: str):
        if not block:
            return
        # Safest bet: The JSON payload starts at the first '{' or '['
        json_match = re.search(r"[\{\[]", block)
        if json_match:
            split_idx = json_match.start()
            extracted_data[f"{prefix}_Title"] = block[:split_idx].strip().split("\n")[0]
            extracted_data[f"{prefix}_JSON_str"] = block[split_idx:].strip()
        else:
            # Fallback: Just split by the first newline if no brackets are found
            parts = block.split("\n", 1)
            extracted_data[f"{prefix}_Title"] = (
                parts[0].strip() if len(parts) > 0 else ""
            )
            extracted_data[f"{prefix}_JSON_str"] = (
                parts[1].strip() if len(parts) > 1 else ""
            )

    # 3. Parse out the titles and JSONs from the captured blocks
    parse_recipe_block(recipe_a_block, "RecipeA")
    parse_recipe_block(recipe_b_block, "RecipeB")
    parse_recipe_block(recipe_fusion_block, "RecipeFusion")
    # breakpoint()

    return extracted_data


def parse_recipefusion_str(recipefusion_str):
    eval_str = apply_fixes(recipefusion_str)
    extracted_data = extract_parts(eval_str)
    errors = []
    # breakpoint()
    for recipe_key in ["RecipeA", "RecipeB", "RecipeFusion"]:
        if f"{recipe_key}_JSON_str" in extracted_data:
            try:
                recipe_json_str = extracted_data[f"{recipe_key}_JSON_str"]
                recipe_json = json.loads(recipe_json_str)
                extracted_data[f"{recipe_key}_parsed"] = recipe_json
            except json.JSONDecodeError as e:
                error_str = f"JSON Parsing Error for {recipe_key}: {str(e)}"
                errors.append(error_str)

    missing_keys = EXPECTED_KEYS - extracted_data.keys()

    return dict(
        extracted_data=extracted_data,
        missing_keys=list(missing_keys),
        errors=errors,
    )


def parse_recipefusion_file(input_filepath, output_filepath):
    logger.info(f"Parsing RecipeFusion responses in file {input_filepath}")

    data = load_from_jsonl(input_filepath, context="Parsing Responses")

    erroneous_inds = []
    results = []

    for i, entry in enumerate(data):
        output_str = entry.get(
            "fixed_model_generated_response", entry["model_generated_response"]
        )

        parsing_results = parse_recipefusion_str(output_str)
        results.append({**entry, **parsing_results})

        if len(parsing_results.get("errors", [])) > 0:
            erroneous_inds.append(i)

    logger.info(f"Number of erroneous indices={len(erroneous_inds)}")
    logger.info(f"Erroneous inds = {erroneous_inds}")

    save_to_jsonl(results, output_filepath, mode="w", context="Parsing Responses")
