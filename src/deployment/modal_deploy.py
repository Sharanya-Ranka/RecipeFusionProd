import modal

MINUTES = 60
N_GPU = 1

# MODEL_ID = "HuggingfaceSharanya/qwen_4b_merged"
# MODEL_REVISION = "b9076b0613bcf3dc4ccbc8a817c88933aa3c700c"
# MODEL_NAME = "qwen4bft"


MODEL_ID = "HuggingfaceSharanya/llama_8b_merged"
MODEL_REVISION = "a145b26e48be1768183c1f6c3ca4325a867939a0"
MODEL_NAME = "llama8bft"


LOADING_TIMEOUT = 10 * MINUTES
LOADING_RETRY_INTERVAL = 15  # seconds
HEALTH_CHECK_RETRIES = LOADING_TIMEOUT // LOADING_RETRY_INTERVAL
REQUEST_TIMEOUT = 5 * MINUTES
LOADING_AND_SERVING_TIMEOUT = LOADING_TIMEOUT + REQUEST_TIMEOUT
MAX_MODEL_LEN = 12288
MAX_TOKENS_REQUEST = MAX_MODEL_LEN - 2048


hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)

vllm_image = modal.Image.from_registry(
    "nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12"
).uv_pip_install("vllm==0.21.0", "boto3", "httpx", "fastapi[standard]")

aws_secret = modal.Secret.from_name("my-aws-s3-credentials")
app = modal.App(f"recipefusion-{MODEL_NAME}")


# =====================================================================
# FUNCTION 1: PRIVATE WORKER WITH CONTINUOUS BATCHING ENABLED
# =====================================================================
@app.function(
    image=vllm_image,
    gpu=f"L4:{N_GPU}",
    scaledown_window=5 * MINUTES,
    timeout=LOADING_AND_SERVING_TIMEOUT,
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
    secrets=[aws_secret],
)
@modal.concurrent(max_inputs=100)
async def run_vllm_inference_and_upload(request_id: str, payload_dict: dict):
    import os
    import subprocess
    import json
    import httpx
    import boto3
    import asyncio
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("vllm_worker_plus_s3")

    INTERNAL_VLLM_PORT = 8001

    # --- Safe Background Server Boot Engine ---
    # We use a global-style check to ensure we don't try to start vLLM twice
    # if multiple concurrent inputs hit the container at the same time.
    if not hasattr(run_vllm_inference_and_upload, "vllm_process"):
        cmd = [
            "vllm",
            "serve",
            MODEL_ID,
            "--revision",
            MODEL_REVISION,
            "--served-model-name",
            MODEL_ID,
            "--host",
            "127.0.0.1",
            "--port",
            str(INTERNAL_VLLM_PORT),
            "--uvicorn-log-level=info",
            "--max-model-len",
            str(MAX_MODEL_LEN),
            "--enable-prefix-caching",
        ]
        logger.info("Starting vLLM background process inside container...")
        run_vllm_inference_and_upload.vllm_process = subprocess.Popen(cmd)

    vllm_ready = False
    # --- Async Health Check Loop ---
    health_url = f"http://127.0.0.1:{INTERNAL_VLLM_PORT}/health"
    async with httpx.AsyncClient(timeout=LOADING_TIMEOUT) as client:
        for _ in range(
            HEALTH_CHECK_RETRIES
        ):  # Try for up to 5 minutes (30 attempts with 10s sleep) to check if vLLM is ready
            try:
                r = await client.get(health_url)
                if r.status_code == 200:
                    vllm_ready = True
                    break
            except Exception:
                pass

            await asyncio.sleep(
                LOADING_RETRY_INTERVAL
            )  # Yields control so other requests can enter the container

        if not vllm_ready:
            raise RuntimeError("vLLM failed to start within the expected time.")

        # --- Hit local vLLM (Asynchronously!) ---
        # Because we use 'await', multiple requests hitting this container
        # will pile up inside vLLM concurrently, triggering continuous batching.

        vllm_url = f"http://127.0.0.1:{INTERNAL_VLLM_PORT}/v1/chat/completions"
        logger.info(f"[{request_id}] Forwarding request to vLLM batching loop...")
        response = await client.post(vllm_url, json=payload_dict)

    if response.status_code != 200:
        raise Exception(f"vLLM error: {response.text}")

    vllm_result = response.json()
    generated_text = vllm_result["choices"][0]["message"]["content"]

    # --- Handle Structural Storage Save ---
    s3_data = {
        "request_id": request_id,
        "input_structure": payload_dict,
        "output_text": generated_text,
        "raw_vllm_metrics": vllm_result.get("usage", {}),
    }

    BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
    file_key = os.environ["AWS_S3_FOLDER_PATH"] + f"/{request_id}.json"

    def upload_to_s3():
        s3_client = boto3.client("s3")
        # Has retry logic builtin (standard mode)
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=json.dumps(s3_data, indent=2),
            ContentType="application/json",
        )

    await asyncio.to_thread(upload_to_s3)
    logger.info(f"[{request_id}] Successfully archived generation payload to S3.")


# 1. Ultra-Lightweight Image for your public API Gateway (Sub-second cold start)
gateway_image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "fastapi[standard]", "pydantic"
)


# =====================================================================
# FUNCTION 2: LIGHTWEIGHT PUBLIC API GATEWAY (Stays unchanged)
# =====================================================================
@app.function(image=gateway_image, scaledown_window=1 * MINUTES)
@modal.asgi_app()
def serve():
    import uuid
    from fastapi import FastAPI
    from pydantic import BaseModel
    from typing import List, Optional

    class ChatMessage(BaseModel):
        role: str
        content: str

    class OpenAICompletionRequest(BaseModel):
        model: str
        messages: List[ChatMessage]
        temperature: Optional[float] = 0.7
        max_tokens: Optional[int] = MAX_TOKENS_REQUEST

    web_app = FastAPI(title="Async Distributed S3 Gateway")

    @web_app.post("/async_inference")
    async def intercept_chat_completion(request_data: OpenAICompletionRequest):
        execution_id = f"req-{uuid.uuid4()}"

        # Drops the job payload into the execution pool and unblocks instantly
        run_vllm_inference_and_upload.spawn(execution_id, request_data.model_dump())

        return {
            "id": execution_id,
            "object": "chat.completion.async",
            "status": "queued",
            "expected_s3_key": f"{execution_id}.json",
        }

    return web_app
