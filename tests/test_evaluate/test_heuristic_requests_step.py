import json
import pytest
from unittest.mock import patch
from omegaconf import OmegaConf

# Adjust the import path to match your structure
from main_evaluate import eval_step_heuristic_requests


# We mock the sendRequests function directly where it is imported/used in main_evaluate
@patch("main_evaluate.sendRequests")
def test_eval_step_heuristic_requests(
    mock_send_requests, dummy_parsed_data_dir, caplog
):

    # 1. Setup the Mock Config
    # We define two fake evaluators to test both the OpenAI and Gemini formatting branches
    cfg = OmegaConf.create(
        {
            "evaluation": {
                "folder_path": str(dummy_parsed_data_dir),
                "filenames": ["test_data"],
                "suffixes": {"parse": "_parsed"},
                "create_requests": True,
                "send_requests": True,
                "evaluator_models": [
                    {"name": "gpt-eval", "provider": "openai", "model": "gpt-4o-mini"},
                    {
                        "name": "gemini-eval",
                        "provider": "google",
                        "model": "gemini-2.5-flash",
                    },
                ],
            }
        }
    )

    # 2. Execute the Step
    eval_step_heuristic_requests(cfg)

    # 3. Assertions: File Creation (State)
    openai_output_path = dummy_parsed_data_dir / "test_data_evalreq_gpt-eval.json"
    gemini_output_path = dummy_parsed_data_dir / "test_data_evalreq_gemini-eval.json"

    assert openai_output_path.exists(), "Failed to create OpenAI batch requests file."
    assert gemini_output_path.exists(), "Failed to create Gemini batch requests file."

    # Verify the contents of the OpenAI file (Should be JSONL format, 3 requests per item)
    with open(openai_output_path, "r", encoding="utf-8") as f:
        openai_lines = f.readlines()

    assert (
        len(openai_lines) == 3
    ), "Expected 3 heuristic requests (Creativity, Realism, Viability)."

    # Parse one line to ensure it structured correctly for OpenAI
    first_openai_request = json.loads(openai_lines[0])
    assert first_openai_request["method"] == "POST"
    assert first_openai_request["body"]["model"] == "gpt-4o-mini"
    assert "test_data" in first_openai_request["custom_id"]

    # 4. Assertions: Network Call Interception (Behavior)
    # The sendRequests function should have been called exactly twice (once per evaluator)
    assert (
        mock_send_requests.call_count == 2
    ), "sendRequests was not called the expected number of times."

    # We can inspect the arguments of the first call to ensure it passed the right file and model config
    first_call_args = mock_send_requests.call_args_list[0][0]
    assert "test_data_evalreq_gpt-eval.json" in first_call_args[0]
    assert (
        first_call_args[1].provider == "openai"
    )  # OmegaConf allows dot-notation access
