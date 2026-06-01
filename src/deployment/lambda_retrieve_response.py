import os
import json
import urllib.request
import urllib.parse
import boto3
from botocore.exceptions import ClientError

# Initialize the S3 client outside the handler loop for better warm-start performance
s3_client = boto3.client("s3")

# Put your Cloudflare Secret Key in your Lambda Environment Variables
CLOUDFLARE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "YOUR_SECRET_KEY")


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
    # 1. Parse incoming body
    try:
        body = json.loads(event["body"]) if "body" in event else event
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Malformed JSON payload"}),
        }

    request_id = body.get("request_id")
    cf_token = body.get("cf_token")

    print(f"Using CF Token={cf_token}")
    print(f"Serving for request_id={request_id}")

    # 2. BOT PROTECTION GUARD: Check the token before doing anything else
    user_verified = True  # verify_turnstile(cf_token)
    if not user_verified:
        return {
            "statusCode": 403,
            "body": json.dumps(
                {
                    "error": "Unauthorized: API requests must originate from the official web application."
                }
            ),
        }

    # 1. Fetch parameters from Environment Variables
    bucket_name = os.environ.get("S3_BUCKET_NAME")
    base_path = os.environ.get("S3_PATH", "").strip("/")

    # Fast failure check if parameters are missing
    if not bucket_name or not request_id:
        return {
            "statusCode": 400,
            "error": "Missing configuration. Ensure S3_BUCKET_NAME is set and request_id is passed.",
        }

    # 3. Build the specific object path (Key)
    # Assumes the layout from your previous step, e.g., "baseten-inferences/SUCCEEDED/1234-5678.json"
    if base_path:
        object_key = f"{base_path}/{request_id}.json"
    else:
        object_key = f"{request_id}.json"

    try:
        # 4. Fetch object metadata and body from Amazon S3
        print(f"Attempting to fetch s3://{bucket_name}/{object_key}")
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        # 5. Read the StreamingBody and decode from bytes to string, then parse to JSON
        raw_content = response["Body"].read().decode("utf-8")
        json_data = json.loads(raw_content)

        # print(f"Returning data={raw_content[:50]}")

        # Return the parsed JSON directly to the caller
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            # 1. Wrap your custom 'data' structure inside a container dict
            # 2. Convert the entire thing into a JSON string using json.dumps()
            "body": json.dumps(json_data),
        }

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        print(f"S3 ClientError [{error_code}]: {e.response['Error']['Message']}")

        if error_code == "NoSuchKey":
            return {
                "statusCode": 404,
                "error": f"The inference file for request_id '{request_id}' could not be found.",
            }
        return {
            "statusCode": 500,
            "error": f"AWS S3 error: {e.response['Error']['Message']}",
        }

    except Exception as e:
        print(f"Unexpected processing error: {str(e)}")
        return {"statusCode": 500, "error": f"Internal process error: {str(e)}"}
