import json
import pytest

# --- 1. Dummy Data Setup ---

VALID_RESPONSE = """Original Recipes : Pasta(Italian) + Tacos(Mexican)

RecipeA:
Pasta Recipe
{"description": "A classic pasta.", "ingredients": []}

RecipeB:
Taco Recipe
{"description": "A classic taco.", "ingredients": []}

Fusion Explanation:
A lovely blend of Italy and Mexico.

RecipeFusion:
Mexi-Pasta
{"description": "Spicy pasta.", "ingredients": []}
"""

# Invalid: Missing brackets in RecipeA, broken JSON in RecipeFusion
INVALID_RESPONSE = """Original Recipes : Curry(Indian) + Pho(Vietnamese)

RecipeA:
Curry Recipe
{"description": "A classic curry. 6"", "ingredients": []}

RecipeB:
Pho Recipe
{"description": "A classic pho.", "ingredients": []}

Fusion Explanation:
A soupy curry.

RecipeFusion:
Curry Pho
{"description": "Spicy broth", "ingredients": [}
"""


@pytest.fixture
def dummy_data_dir(tmp_path):
    """Creates a temporary directory with dummy input data."""
    data = [
        {"id": "valid_1", "model_generated_response": VALID_RESPONSE},
        {"id": "invalid_1", "model_generated_response": INVALID_RESPONSE},
    ]

    file_path = tmp_path / "test_data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    return tmp_path


@pytest.fixture
def dummy_parsed_data_dir(tmp_path):
    """
    Creates a fake JSON file mimicking the exact nested output
    expected by createAndSaveBatchRequests.
    """
    data = [
        {
            "cuisine_a": "Italian",
            "cuisine_b": "Mexican",
            "Fusion_Explanation": "A spicy pasta blend.",
            "RecipeFusion_JSON_parsed": {"description": "A delicious Mexi-Pasta"},
        }
    ]

    # Notice the suffix matches what the config will look for
    file_path = tmp_path / "test_data_parsed.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    return tmp_path
