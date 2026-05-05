# tests/test_evaluate/test_format_fix_step.py
import json
import pytest
from unittest.mock import patch
from omegaconf import OmegaConf

# Adjust import based on your exact structure
from main_evaluate import eval_step_format_fix


# Note: The patch path MUST match exactly how it is imported in the code running it.
# main_evaluate imports from src.evaluation.format_fix_responses.
@patch("src.evaluation.format_fix_responses.fix_response_format")
def test_eval_step_format_fix(mock_fix_format, dummy_data_dir, caplog):

    # 1. Setup the Mock Behavior
    # When the code tries to call the LangChain Gemini function, it will
    # hit this mock instead and instantly return this string.
    mock_fix_format.return_value = "PERFECTLY FIXED JSON FORMAT"

    # 2. Mock the Hydra Config
    cfg = OmegaConf.create(
        {
            "evaluation": {
                "folder_path": str(dummy_data_dir),
                "filenames": ["test_data"],
                # Zip expects a list for each filename. We are telling it to fix index 1.
                "format_fix_indices": [[1]],
                "suffixes": {"format_fixed": "_format_fixed"},
            }
        }
    )

    # 3. Run the Function
    eval_step_format_fix(cfg)

    # 4. Assertions
    output_filepath = dummy_data_dir / "test_data_format_fixed.json"

    # Check that the file was created
    assert output_filepath.exists(), "Format fixed file was not created."

    with open(output_filepath, "r", encoding="utf-8") as f:
        fixed_data = json.load(f)

    # Check that index 1 got the fixed key, and the mock was injected successfully
    assert "fixed_model_generated_response" in fixed_data[1]
    assert (
        fixed_data[1]["fixed_model_generated_response"] == "PERFECTLY FIXED JSON FORMAT"
    )

    # Verify that index 0 (which we didn't specify in format_fix_indices) was untouched
    assert "fixed_model_generated_response" not in fixed_data[0]
