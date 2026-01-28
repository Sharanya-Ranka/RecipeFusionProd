import json
import logging
from datasets import load_dataset, Dataset

logger = logging.getLogger(__name__)

# System message for the assistant
system_message = """You are a Fusion Chef. You follow a 4-step process: 1. Generate a classic recipe for Cuisine A. 2. Generate a classic recipe for Cuisine B. 3. Identify a Fusion Strategy and Explanation. 4. Create the final Fusion Recipe."""

# User prompt that combines the user query and the schema
user_prompt_template = """Create a fusion of {cuisine1} and {cuisine2}"""

assistant_response_template = """
Original Recipes : {dishA}({cuisine1}) + {dishB}({cuisine2})

RecipeA:
{dishA}
{instructions_dsl_A}

RecipeB:
{dishB}
{instructions_dsl_B}

Fusion Strategy:
{fusion_strategy}

Fusion Explanation:
{fusion_explanation}

RecipeFusion:
{dishfusion}
{instructions_dsl_fusion}
"""


def get_compressed_json_str(data):
    try:
        if isinstance(data, str):
            data_json = json.loads(data)
        else:
            data_json = data
        return json.dumps(data_json, indent=None, separators=(",", ":"))
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        return "{}"


def create_conversation(sample, templates):
    try:
        fillers = dict(
            cuisine1=sample["recipe_a"]["cuisine"],
            cuisine2=sample["recipe_b"]["cuisine"],
            dishA=sample["recipe_a"]["title"],
            dishB=sample["recipe_b"]["title"],
            dishfusion=sample["fusion_dish_name"],
            instructions_dsl_A=get_compressed_json_str(
                sample["recipe_a"]["recipe_json_str"]
            ),
            instructions_dsl_B=get_compressed_json_str(
                sample["recipe_b"]["recipe_json_str"]
            ),
            instructions_dsl_fusion=get_compressed_json_str(sample["fusion_recipe"]),
            fusion_strategy=sample["fusion_strategy"],
            fusion_explanation=sample["fusion_explanation"],
        )
        system_message = templates["system_message"]
        user_prompt = templates["user_prompt_template"].format(**fillers)
        assistant_response = templates["assistant_response_template"].format(**fillers)

        return {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_response},
            ]
        }
    except KeyError as e:
        logger.error(f"Missing key in sample data: {e}")
        return {"messages": []}


def apply_chat_formatting(dataset: Dataset, templates) -> Dataset:
    logger.info("Applying chat formatting to the dataset...")
    # Convert dataset to OAI messages
    formatted_dataset = dataset.map(
        create_conversation,
        fn_kwargs={"templates": templates},
        batched=False,
        remove_columns=dataset.column_names,  # Standard practice to keep the repo clean
    )

    return formatted_dataset
