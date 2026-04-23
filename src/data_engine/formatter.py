import json
import logging
from datasets import load_dataset, Dataset

logger = logging.getLogger(__name__)


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


def create_conversation(sample, templates, with_assistant_message=True):
    try:
        fillers = dict(
            CUISINE_A=sample.get("cuisine_a", "Unknown Cuisine A"),
            CUISINE_B=sample.get("cuisine_b", "Unknown Cuisine B"),
            raw_response=sample.get("raw_response", {}),
        )

        system_message = templates["system_message"]
        user_prompt = templates["user_prompt_template"].format(**fillers)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ]

        if with_assistant_message:
            assistant_response = templates["assistant_response_template"].format(
                **fillers
            )
            messages.append({"role": "assistant", "content": assistant_response})

        return {"messages": messages}
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
