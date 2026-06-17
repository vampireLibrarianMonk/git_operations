"""AWS Bedrock client utilities."""

from __future__ import annotations

import json

from .config import MAX_TOKENS_COMMIT
from .model import load_model_id


def call_bedrock(
    prompt: str,
    max_tokens: int = MAX_TOKENS_COMMIT,
    system_prompt: str | None = None,
) -> str:
    """Backward-compatible Bedrock helper used by existing workflows.

    Automatically selects the best model for the prompt size if benchmark data exists.
    """
    from .benchmark import get_best_model, load_scores

    scores = load_scores()
    model_id = None
    if scores:
        model_id = get_best_model(scores, diff_size=len(prompt))

    return invoke_bedrock_text(prompt, max_tokens=max_tokens, system_prompt=system_prompt, model_id=model_id)


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

    resolved_model = model_id or load_model_id()
    client = boto3.client("bedrock-runtime")

    # Nova models use their own format
    if "nova" in resolved_model:
        body: dict = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
        }
        if system_prompt:
            body["system"] = [{"text": system_prompt}]
        response = client.invoke_model(modelId=resolved_model, body=json.dumps(body))
        payload = json.loads(response["body"].read())
        return "".join(
            part.get("text", "")
            for part in payload.get("output", {}).get("message", {}).get("content", [])
        )

    # Meta, Mistral, DeepSeek — use the Converse API
    if any(x in resolved_model for x in ("meta.", "mistral.", "deepseek.")):
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        kwargs: dict = {
            "modelId": resolved_model,
            "messages": messages,
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
        }
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]
        response = client.converse(**kwargs)
        return "".join(
            block.get("text", "")
            for block in response.get("output", {}).get("message", {}).get("content", [])
        )

    # Anthropic format (default)
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
        modelId=resolved_model,
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read())
    return "".join(part.get("text", "") for part in payload.get("content", []))
