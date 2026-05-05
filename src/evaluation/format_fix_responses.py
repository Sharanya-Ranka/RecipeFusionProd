import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.utils.utils import save_to_jsonl, load_from_jsonl
import logging

logger = logging.getLogger(__name__)


# The strict formatting prompt, stripped of the persona/task generation instructions
FORMATTING_PROMPT_TEMPLATE = """
You are a strict data-formatting assistant. Your ONLY job is to take the provided MODEL_RESPONSE and reformat it to exactly match the TARGET_FORMAT layout and JSON_SCHEMA below.

CRITICAL CONSTRAINTS:
1. ONLY fix the formatting and JSON structure.
2. DO NOT change the actual wording, descriptions, culinary techniques, or ingredients present in the MODEL_RESPONSE.
3. DO NOT fix any factual, logical, or culinary mistakes. If a recipe makes no sense or has errors, keep them exactly as they are, but enforce the required shape.
4. You must ONLY use the information already present in the sample response. Do not generate new culinary content to fill in gaps.

---
TARGET_FORMAT Layout (Must follow this exact structure):

Original Recipes: [Dish A] ([Cuisine A]) + [Dish B] ([Cuisine B])

RecipeA:
[Dish Name]
[JSON Data]

RecipeB:
[Dish Name]
[JSON Data]

Fusion Explanation:
[Detailed paragraph explaining the fusion]

RecipeFusion:
[New Fusion Dish Name]
[JSON Data]

---
JSON_SCHEMA Requirements (for the [JSON Data] blocks):
* `description`: str.
* `ingredients`: List of objects with `name` (string), `amount` (string), and `unit` (string).
* `steps`: List of objects. Each step contains:
    * `instruction`: str
    * `action`: str
    * `inputs`: List[str]
    * `result_name`: str
    * `metadata`: A list of lists for structured metadata (e.g., `[["container", "skillet"], ["time", "5 min"]]`).

---
MODEL_RESPONSE TO FIX:
{sample_response}
"""


def fix_response_format(sample_response: str) -> str:
    """
    Takes a poorly formatted model response and asks Gemini (via LangChain)
    to fix only the format based on a strict template.
    """
    # Initialize the LangChain Gemini model.
    # Temperature 0 is ideal for strict formatting/extraction tasks.
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", temperature=0, thinking_budget=0, max_retries=2
    )

    # Create the LangChain PromptTemplate
    prompt = PromptTemplate(
        input_variables=["sample_response"], template=FORMATTING_PROMPT_TEMPLATE
    )

    # Create the chain (Prompt -> LLM)
    chain = prompt | llm

    try:
        # Invoke the chain
        response = chain.invoke({"sample_response": sample_response})
        logger.info(f"Response received\n{response}")
        logger.info(f"Response content\n{response.content.strip()}")
        return response.content.strip()
    except Exception as e:
        print(f"Error calling Gemini API via LangChain: {e}")
        return sample_response  # Fallback to original if API fails


def fix_response_format_file(
    input_filepath: str, output_filepath: str, indices_to_process: list[int]
):
    """
    Reads a JSON file, processes specific indices to fix formatting using LangChain,
    and writes the results to a new JSON file.
    """
    # 1. Load the data
    data = load_from_jsonl(input_filepath, context="Format fixing")

    # 2. Process the specified indices
    for index in indices_to_process:
        if 0 <= index < len(data):
            print(f"Processing index {index}...")
            item = data[index]

            if "model_generated_response" in item:
                original_text = item["model_generated_response"]
                fixed_text = fix_response_format(original_text)

                # Populate the new key
                data[index]["fixed_model_generated_response"] = fixed_text
                logger.info(f"Successfully processed index {index}.\n{fixed_text}")
            else:
                logger.warning(
                    f"Warning: Key 'model_generated_response' not found at index {index}."
                )
        else:
            logger.warning(
                f"Warning: Index {index} is out of bounds for the input data (length: {len(data)})."
            )

    # 3. Save the updated data
    save_to_jsonl(data, output_filepath, mode="w", context="Format fixing")
