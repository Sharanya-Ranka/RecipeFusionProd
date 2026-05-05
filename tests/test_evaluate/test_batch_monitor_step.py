import os
import pytest
from unittest.mock import patch, MagicMock
from omegaconf import OmegaConf

# Adjust import based on your exact structure
from main_evaluate import eval_step_batch_monitor


# Patch the functions directly where they are imported/used in main_evaluate.
# Note: The order of decorators determines the order of the arguments!
# The closest patch to the function goes first in the argument list.
@patch("main_evaluate.saveBatchResultsGemini")
@patch("main_evaluate.saveBatchResultsOpenAI")
@patch("main_evaluate.monitorBatch")
def test_eval_step_batch_monitor(
    mock_monitor, mock_save_openai, mock_save_gemini, tmp_path, caplog
):

    # 1. Setup the Mock Behavior using a side_effect function
    # This allows `monitorBatch` to return different fake status objects
    # depending on the batch_id it is asked to check.
    def mock_monitor_responses(batch_id, batch_type):
        mock_batch_info = MagicMock()

        if batch_id == "batch_openai_success":
            mock_batch_info.status = "completed"
            mock_batch_info.output_file_id = "openai_file_123"

        elif batch_id == "batch_gemini_success":
            # Gemini has nested attributes: status.name and dest.file_name
            # MagicMock handles nested attributes perfectly without extra setup.
            mock_batch_info.status.name = "JOB_STATE_SUCCEEDED"
            mock_batch_info.dest.file_name = "gemini_file_456"

        elif batch_id == "batch_pending":
            # A batch that hasn't finished yet
            mock_batch_info.status = "in_progress"

        return mock_batch_info

    # Attach the custom logic to the mock
    mock_monitor.side_effect = mock_monitor_responses

    # 2. Mock the Hydra Config
    # We provide three batches to test all branches of your if/else logic
    cfg = OmegaConf.create(
        {
            "evaluation": {
                "folder_path": str(tmp_path),
                "batch_info": [
                    ["batch_openai_success", "openai", "recipe_openai"],
                    ["batch_gemini_success", "google", "recipe_gemini"],
                    ["batch_pending", "openai", "recipe_pending"],
                ],
            }
        }
    )

    # 3. Execute the Function
    eval_step_batch_monitor(cfg)

    # 4. Assertions

    # Ensure monitor was called exactly 3 times (once for each batch in config)
    assert mock_monitor.call_count == 3

    # Verify OpenAI saving logic was triggered correctly
    expected_openai_path = os.path.join(str(tmp_path), "recipe_openai_evalres.json")
    mock_save_openai.assert_called_once_with("openai_file_123", expected_openai_path)

    # Verify Gemini saving logic was triggered correctly
    expected_gemini_path = os.path.join(str(tmp_path), "recipe_gemini_evalres.json")
    mock_save_gemini.assert_called_once_with("gemini_file_456", expected_gemini_path)

    # Verify the "pending" branch logged the correct message without trying to save
    log_messages = [record.message for record in caplog.records]
    assert "Batches did not complete. Check logs for status" in log_messages
