import json
import pytest
import logging
from omegaconf import OmegaConf
from pathlib import Path

# Assuming your main code is in a module named main_evaluate
from main_evaluate import eval_step_parse

# --- 2. The Test ---


def test_eval_step_parse(dummy_data_dir, caplog):
    """Tests the parsing step, ensuring valid data parses and invalid data logs errors."""

    # Capture INFO level logs and above
    caplog.set_level(logging.INFO)

    # Mock the Hydra DictConfig using OmegaConf
    cfg = OmegaConf.create(
        {
            "evaluation": {
                "folder_path": str(dummy_data_dir),
                "filenames": ["test_data"],
                "suffixes": {"format_fixed": "_format_fixed", "parse": "_parsed"},
            }
        }
    )

    # Execute the function
    eval_step_parse(cfg)

    # --- 3. Assertions ---

    output_filepath = dummy_data_dir / "test_data_parsed.json"

    # 1. File Creation
    assert output_filepath.exists(), "The parsed output file was not created."

    with open(output_filepath, "r", encoding="utf-8") as f:
        parsed_results = json.load(f)

    assert (
        len(parsed_results) == 2
    ), "Output should contain both valid and invalid records."

    valid_record = parsed_results[0]
    invalid_record = parsed_results[1]

    # 2. Valid Data Assertions
    assert (
        "RecipeA_parsed" in valid_record["extracted_data"]
    ), "Failed to parse valid Recipe A JSON."
    assert (
        valid_record["extracted_data"]["RecipeA_parsed"]["description"]
        == "A classic pasta."
    )
    assert (
        len(valid_record.get("errors", [])) == 0
    ), "Valid record should not have parsing errors."

    # 3. Invalid Data Assertions (Error Extraction)
    assert (
        len(invalid_record.get("errors", [])) > 0
    ), "Invalid record did not register a JSON parsing error."
    assert any(
        "JSON Parsing Error" in err for err in invalid_record["errors"]
    ), "Did not catch JSONDecodeError."

    # 4. Logging Assertions
    log_messages = [record.message for record in caplog.records]
    assert "Starting step: parse" in log_messages
    assert "Completed step: parse" in log_messages
    assert any(
        "Erroneous inds = [1]" in msg for msg in log_messages
    ), "Did not log the correct erroneous index."
