import json
import os
import re
from openai import OpenAI

from google import genai
from google.genai import types

from src.evaluation.llm_evaluations_prompts import (
    CULINARY_CREATIVITY_PROMPT,
    CAUSAL_REALISM_PROMPT,
    CULINARY_VIABILITY_PROMPT,
)
import logging
from src.utils.utils import (
    save_to_jsonl,
    load_from_jsonl,
    get_heuristic_eval_key,
    get_heurisic_eval_keystring_from_key,
)
from src.utils.types import EvaluationKey, RecipeFusionInferenceKey

logger = logging.getLogger(__name__)


def createOpenAIBatchRequest(
    custom_id, model_name, developer_prompt, user_prompt, **kwargs
):
    request = {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": model_name,
            **kwargs,
            # "reasoning": {"effort": "low"},
            # "max_output_tokens": 2000,
            "input": [
                {
                    "role": "developer",
                    "content": developer_prompt,
                },
                {"role": "user", "content": user_prompt},
            ],
        },
    }

    return request


def createGeminiBatchRequest(
    custom_id, model_name, developer_prompt, user_prompt, **kwargs
):
    request = {
        "key": custom_id,
        "request": {
            "system_instruction": {"parts": [{"text": developer_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                **kwargs
                # "thinking_config": {"include_thoughts": False, "thinking_budget": 0}
            },
        },
    }

    return request
    # Similarly for CAUSAL_REALISM_PROMPT, CULINARY_VIABILITY_PROMPT


def createAndSaveBatchRequests(
    input_filepath, output_filepath, evaluator_model, partial_id
):
    requests = []

    datapoints = load_from_jsonl(input_filepath, context="Heuristic Requests Batched")

    for dp in datapoints:
        key: RecipeFusionInferenceKey = RecipeFusionInferenceKey(**dp["key"])
        cuisine_a = key.cuisine_a
        cuisine_b = key.cuisine_b

        fusion_explain = dp["Fusion_Explanation"]
        fusion_recipe = json.dumps(dp["RecipeFusion_JSON_parsed"])

        output_to_eval = f"# LLM Response to Evaluate\n\nCuisines: {cuisine_a} + {cuisine_b}\n\nFusion Explanation:\n{fusion_explain}\n\nFusion Recipe={fusion_recipe}"
        partial_key = get_heuristic_eval_key(
            partial_id, cuisine_a, cuisine_b, evaluator_model, "np dimension"
        )
        provider = evaluator_model.provider
        model = evaluator_model.model

        if provider == "openai":
            # 1. Culinary Creativity Request
            partial_key.dimension = "culinarycreativity"
            requests.append(
                createOpenAIBatchRequest(
                    get_heurisic_eval_keystring_from_key(partial_key),
                    model,
                    developer_prompt=CULINARY_CREATIVITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 2. Causal Realism Request
            partial_key.dimension = "causalrealism"
            requests.append(
                createOpenAIBatchRequest(
                    get_heurisic_eval_keystring_from_key(partial_key),
                    model,
                    developer_prompt=CAUSAL_REALISM_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 3. Culinary Viability Request
            partial_key.dimension = "culinaryviability"
            requests.append(
                createOpenAIBatchRequest(
                    get_heurisic_eval_keystring_from_key(partial_key),
                    model,
                    developer_prompt=CULINARY_VIABILITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )

        elif provider == "google":
            # 1. Culinary Creativity Request
            partial_key.dimension = "culinarycreativity"
            requests.append(
                createGeminiBatchRequest(
                    get_heurisic_eval_keystring_from_key(partial_key),
                    model,
                    developer_prompt=CULINARY_CREATIVITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 2. Causal Realism Request
            partial_key.dimension = "causalrealism"
            requests.append(
                createGeminiBatchRequest(
                    get_heurisic_eval_keystring_from_key(partial_key),
                    model,
                    developer_prompt=CAUSAL_REALISM_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 3. Culinary Viability Request
            partial_key.dimension = "culinaryviability"
            requests.append(
                createGeminiBatchRequest(
                    get_heurisic_eval_keystring_from_key(partial_key),
                    model,
                    developer_prompt=CULINARY_VIABILITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )

    save_to_jsonl(
        requests, output_filepath, mode="w", context="Heuristic Requests Batched"
    )

    return output_filepath


def createAndSaveTeacherBatchRequests(
    datapoints, model_name, partial_id, output_filepath
):
    requests = []

    for dp in datapoints:
        cuisine_a = dp["cuisine_a"]
        cuisine_b = dp["cuisine_b"]

        fusion_explain = dp["request_data"]["fusion_result_json"]["fusion_explanation"]
        fusion_recipe = json.dumps(
            dp["request_data"]["fusion_result_json"]["recipe_fusion_json"]
        )

        # breakpoint()

        output_to_eval = f"# LLM Response to Evaluate\n\nCuisines: {cuisine_a} + {cuisine_b}\n\nFusion Explanation:\n{fusion_explain}\n\nFusion Recipe={fusion_recipe}"
        partial_id2 = f"{partial_id}_{cuisine_a}_{cuisine_b}"

        if model_name == "gpt-5-mini":
            # 1. Culinary Creativity Request
            requests.append(
                createOpenAIBatchRequest(
                    f"{partial_id2}_culinary_creativity",
                    model_name,
                    developer_prompt=CULINARY_CREATIVITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 2. Causal Realism Request
            requests.append(
                createOpenAIBatchRequest(
                    f"{partial_id2}_causal_realism",
                    model_name,
                    developer_prompt=CAUSAL_REALISM_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 3. Culinary Viability Request
            requests.append(
                createOpenAIBatchRequest(
                    f"{partial_id2}_culinary_viability",
                    model_name,
                    developer_prompt=CULINARY_VIABILITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )

        elif model_name == "gemini-2.5-flash":
            # 1. Culinary Creativity Request
            requests.append(
                createGeminiBatchRequest(
                    f"{partial_id2}_culinary_creativity",
                    model_name,
                    developer_prompt=CULINARY_CREATIVITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 2. Causal Realism Request
            requests.append(
                createGeminiBatchRequest(
                    f"{partial_id2}_causal_realism",
                    model_name,
                    developer_prompt=CAUSAL_REALISM_PROMPT,
                    user_prompt=output_to_eval,
                )
            )
            # 3. Culinary Viability Request
            requests.append(
                createGeminiBatchRequest(
                    f"{partial_id2}_culinary_viability",
                    model_name,
                    developer_prompt=CULINARY_VIABILITY_PROMPT,
                    user_prompt=output_to_eval,
                )
            )

    # breakpoint()
    # Save requests in a JSONL file (1 line per request) in output_filepath
    with open(output_filepath, "w", encoding="utf-8") as f:
        for request in requests:
            f.write(json.dumps(request) + "\n")

    return output_filepath


def sendRequestsOpenAI(requests_file):
    client = OpenAI()

    batch_input_file = client.files.create(
        file=open(requests_file, "rb"), purpose="batch"
    )

    logger.info(f"batch input file: {batch_input_file}")

    batch_input_file_id = batch_input_file.id
    response = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={"description": "recipe fusion batch job"},
    )
    logger.info(f"batch creation response: {response}")

    return response


def sendRequestsGemini(requests_file, model_name, display_name):
    client = genai.Client()
    # Upload the file to the File API
    uploaded_file = client.files.upload(
        file=requests_file,
        config=types.UploadFileConfig(display_name=display_name, mime_type="jsonl"),
    )

    logger.info(f"Uploaded file: {uploaded_file.name}")

    file_batch_job = client.batches.create(
        model=model_name,
        src=uploaded_file.name,
        config={
            "display_name": display_name,
        },
    )

    logger.info(f"Created batch job: {file_batch_job.name}")


def sendRequests(requests_file, evaluator_model):
    if evaluator_model.provider == "openai":
        sendRequestsOpenAI(requests_file)
    elif evaluator_model.provider == "google":
        sendRequestsGemini(requests_file, evaluator_model.model, "recipefusion_job")


def monitorBatchGemini(batch_id):
    client = genai.Client()
    batch_status = None  # Initialize to ensure return safety

    try:
        logger.info(f"Polling status for job: {batch_id}")
        batch_status = client.batches.get(name=batch_id)

        logger.info(f"Batch Status for batch={batch_id}\n{batch_status}")
    except Exception as e:
        logger.error(
            f"Couldn't retrieve Gemini batch status for batch={batch_id}\n{str(e)}"
        )

    return batch_status


def list_batches():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    batches = client.batches.list()
    logger.info(batches)


def monitorBatchOpenAI(batch_id):
    client = OpenAI()
    try:
        batch_status = client.batches.retrieve(batch_id)
        logger.info(f"Batch Status for batch={batch_id}\n{batch_status}")
    except Exception as e:
        logger.error(
            f"Couldn't retrieve Openai batch status for batch={batch_id}\n{str(e)}"
        )
    return batch_status


def monitorBatch(batch_id, batch_type):
    batch_res = None
    if batch_type == "openai":
        batch_res = monitorBatchOpenAI(batch_id)
    elif batch_type == "google":
        batch_res = monitorBatchGemini(batch_id)
    return batch_res


def saveBatchResultsOpenAI(file_id, output_filepath):
    client = OpenAI()
    file_response = client.files.content(file_id)
    # breakpoint()
    # logger.info(file_response.text)

    with open(output_filepath, "w", encoding="utf-8") as f:
        for response in file_response.text.split("\n"):
            f.write(response + "\n")

    return output_filepath


def saveBatchResultsGemini(file_id, output_filepath):
    client = genai.Client()
    file_content = client.files.download(file=file_id)
    # Process file_content (bytes) as needed
    file_content_decoded = file_content.decode("utf-8")

    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(file_content_decoded)
