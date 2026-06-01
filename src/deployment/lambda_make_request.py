import os
import json
import urllib.request
import urllib.parse

# Put your Cloudflare Secret Key in your Lambda Environment Variables
CLOUDFLARE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "YOUR_SECRET_KEY")
QWEN_MODAL_URL = os.environ.get("QWEN_MODAL_URL")
LLAMA_MODAL_URL = os.environ.get("LLAMA_MODAL_URL")

# Modal authentication credentials
MODAL_TOKEN_ID = os.environ.get("MODAL_TOKEN_ID", "")
MODAL_TOKEN_SECRET = os.environ.get("MODAL_TOKEN_SECRET", "")


def build_response(status_code, body_dict):
    """Helper to return Lambda Function URL formatted response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict),
    }


def verify_turnstile(token: str) -> bool:
    """Verifies the token directly with Cloudflare's API."""
    # Safety Check: Log a warning if the key is missing from environment setup
    if not CLOUDFLARE_SECRET_KEY or CLOUDFLARE_SECRET_KEY == "YOUR_SECRET_KEY":
        print(
            "ERROR: CLOUDFLARE_SECRET_KEY environment variable is not configured correctly."
        )
        return False

    if not token:
        print("ERROR: Token parameter passed to verify_turnstile is empty.")
        return False

    try:
        verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

        # 1. Structure payload parameters cleanly
        payload_data = urllib.parse.urlencode(
            {
                "secret": CLOUDFLARE_SECRET_KEY.strip(),  # Clear accidental whitespace/newlines
                "response": token,
            }
        ).encode("utf-8")

        # 2. Add explicit Content-Type headers so Cloudflare accepts the request format
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(payload_data)),
        }

        # 3. Create request with explicit parameters
        req = urllib.request.Request(
            verify_url, data=payload_data, headers=headers, method="POST"
        )

        with urllib.request.urlopen(req) as response:
            response_text = response.read().decode("utf-8")
            result = json.loads(response_text)

            # Print the output log in CloudWatch so you can read exact reasons if validation fails
            print(f"Cloudflare complete response payload: {response_text}")

            if not result.get("success", False):
                # Turnstile returns descriptive error codes like ['invalid-input-response']
                print(
                    f"Turnstile verification denied. Error codes: {result.get('error-codes', [])}"
                )
                return False

            return True

    except urllib.error.HTTPError as e:
        # Better diagnostics: read and dump the error message body returned by Cloudflare
        error_body = e.read().decode("utf-8") if e else ""
        print(
            f"Token verification network failure: HTTP Error {e.code}: {e.reason}. Body: {error_body}"
        )
        return False
    except Exception as e:
        print(f"Unexpected token verification failure error: {str(e)}")
        return False


def lambda_handler(event, context):
    # 3. Parse incoming request body
    try:
        body = json.loads(event.get("body", "{}"))
    except (TypeError, json.JSONDecodeError):
        return build_response(400, {"error": "Malformed JSON payload received."})

    # Extract required structural parameters
    cf_token = body.get("cf_token")
    model_name = body.get("model_name")
    model_payload = body.get("model_payload", {})

    model_id = model_payload.get("model")
    messages = model_payload.get("messages")

    if model_name == "qwen4bft":
        modal_endpoint = QWEN_MODAL_URL
    elif model_name == "llama8bft":
        modal_endpoint = LLAMA_MODAL_URL
    else:
        return build_response(
            400, {"error": f"Invalid model name. '{model_name}' not recognized."}
        )

    if not modal_endpoint:
        return build_response(
            500, {"error": "Target Modal configuration missing on backend."}
        )
    if not cf_token:
        return build_response(
            400, {"error": "Missing security token: 'cf_token' is required."}
        )
    if not model_id or not messages:
        return build_response(
            400,
            {"error": "Missing required model_payload keys: 'model' and 'messages'."},
        )

    # 5. Cloudflare Turnstile Verification Interception
    is_valid_user = verify_turnstile(cf_token)
    if not is_valid_user:
        print(f"Invalid user")
        return build_response(
            403,
            {
                "error": "Security validation failed. Turnstile token invalid or expired."
            },
        )

    # 6. Re-bundle payload dynamically for forward execution
    # Forwards everything except the cf_token security wrapper
    forward_payload = {k: v for k, v in model_payload.items()}

    # 2. Bundle headers including the Modal Auth Keys
    modal_headers = {
        "Content-Type": "application/json",
        "Modal-Key": MODAL_TOKEN_ID,
        "Modal-Secret": MODAL_TOKEN_SECRET,
    }

    # 7. Dispatches asynchronous tracking request payload directly onto Modal backend
    try:
        req_data = json.dumps(forward_payload).encode("utf-8")
        req = urllib.request.Request(
            modal_endpoint, data=req_data, headers=modal_headers, method="POST"
        )
        print(f"Creating Modal Request")
        with urllib.request.urlopen(req, timeout=20) as modal_response:
            print(f"Got Modal response")
            modal_status = modal_response.status
            modal_body = json.loads(modal_response.read().decode("utf-8"))

            # Directly hand down asynchronous tracker context data block
            return build_response(modal_status, modal_body)

    except urllib.error.HTTPError as he:
        err_msg = he.read().decode("utf-8")
        print(f"Modal execution node error: Status {he.code} | Response: {err_msg}")
        return build_response(
            he.code,
            {
                "error": "Upstream error generated by inference broker.",
                "details": err_msg,
            },
        )

    except Exception as e:
        print(f"Network transport fault targeting Modal url endpoints: {str(e)}")
        return build_response(
            502, {"error": "Failed to proxy payload down to backend executor engines."}
        )
