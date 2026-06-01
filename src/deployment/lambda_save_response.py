import json
import boto3
import os
import logging

# # Set up the logger
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# Initialize the S3 client outside the handler to reuse connection across warm invocations
s3 = boto3.client("s3")

# Best practice: pass your bucket name via an environment variable
BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


def lambda_handler(event, context):
    try:
        # 1. Parse the incoming body from the Baseten webhook
        # (API Gateway / Function URLs wrap the payload in an 'event["body"]' string)
        if "body" in event:
            payload = json.loads(event["body"])
        else:
            payload = event  # Direct invocation fallback

        # 2. Extract uniquely identifying information for the file name
        request_id = payload.get("request_id", "unknown_request")
        status = payload.get("status", "unknown_status")
        file_key = f"baseten-inference/{status}/{request_id}.json"

        # 3. Convert payload back to a clean JSON string to save it
        file_content = json.dumps(payload, indent=2)

        # 4. Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=file_content,
            ContentType="application/json",
        )

        print(f"Successfully saved {file_key} to S3 bucket {BUCKET_NAME}")

        # 5. Always return a 200 OK rapidly to Baseten
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"status": "success", "message": "Inference saved to S3"}
            ),
        }

    except Exception as e:
        print(f"Error handling webhook: {str(e)}")
        # Even if your internal storage fails, you usually want to give a clean response
        # or handle retry logic depending on your system's design
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "error", "message": str(e)}),
        }
