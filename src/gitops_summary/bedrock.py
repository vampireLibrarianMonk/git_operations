"""AWS Bedrock client utilities."""

from __future__ import annotations

import json

from .config import MAX_TOKENS_COMMIT, MODEL_ID


def call_bedrock(prompt: str, max_tokens: int = MAX_TOKENS_COMMIT) -> str:
    """Backward-compatible Bedrock helper used by existing workflows."""

    return invoke_bedrock_text(prompt, max_tokens=max_tokens)


def invoke_bedrock_text(
    prompt: str,
    *,
    system_prompt: str | None = None,
    max_tokens: int = MAX_TOKENS_COMMIT,
    model_id: str | None = None,
    temperature: float = 0.2,
) -> str:
    """Invoke Bedrock with a plain-text prompt and return concatenated text content."""

    try:
        import boto3
    except ModuleNotFoundError as exc:
        if exc.name == "boto3":
            raise RuntimeError(
                "boto3 is required for Bedrock-backed generation but is not installed in the current Python environment. "
                "Install dependencies with 'pip install -e .' or run the CLI from the project's virtualenv."
            ) from exc
        raise

    client = boto3.client("bedrock-runtime")
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            },
        ],
    }
    if system_prompt:
        body["system"] = system_prompt

    response = client.invoke_model(
        modelId=model_id or MODEL_ID,
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    return "".join(part.get("text", "") for part in payload.get("content", []))
