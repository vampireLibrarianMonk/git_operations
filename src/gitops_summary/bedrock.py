"""AWS Bedrock client utilities."""

import json

from .config import MODEL_ID, MAX_TOKENS_COMMIT

def call_bedrock(prompt: str, max_tokens: int = MAX_TOKENS_COMMIT) -> str:
    import boto3

    client = boto3.client("bedrock-runtime")
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }
    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    return "".join(part.get("text", "") for part in payload.get("content", []))

