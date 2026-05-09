"""Interactive Bedrock model selection workflow."""

from __future__ import annotations

import json
from pathlib import Path

from .config import MODEL_ID

MODEL_CONFIG_FILE = Path(".venv") / ".bedrock_model_config.json"

# Families and their available models on Bedrock
MODEL_CATALOG: dict[str, list[dict[str, str]]] = {
    "Claude (Anthropic)": [
        {"id": "anthropic.claude-3-5-sonnet-20241022-v2:0", "name": "Claude 3.5 Sonnet v2"},
        {"id": "anthropic.claude-3-5-haiku-20241022-v1:0", "name": "Claude 3.5 Haiku"},
        {"id": "anthropic.claude-3-sonnet-20240229-v1:0", "name": "Claude 3 Sonnet"},
        {"id": "anthropic.claude-3-haiku-20240307-v1:0", "name": "Claude 3 Haiku"},
    ],
    "Llama (Meta)": [
        {"id": "meta.llama3-1-405b-instruct-v1:0", "name": "Llama 3.1 405B Instruct"},
        {"id": "meta.llama3-1-70b-instruct-v1:0", "name": "Llama 3.1 70B Instruct"},
        {"id": "meta.llama3-1-8b-instruct-v1:0", "name": "Llama 3.1 8B Instruct"},
    ],
    "Mistral": [
        {"id": "mistral.mistral-large-2407-v1:0", "name": "Mistral Large (24.07)"},
        {"id": "mistral.mixtral-8x7b-instruct-v0:1", "name": "Mixtral 8x7B Instruct"},
    ],
    "Amazon (Titan / Nova)": [
        {"id": "amazon.nova-pro-v1:0", "name": "Nova Pro"},
        {"id": "amazon.nova-lite-v1:0", "name": "Nova Lite"},
        {"id": "amazon.nova-micro-v1:0", "name": "Nova Micro"},
    ],
}


def load_model_id() -> str:
    """Return the configured model ID, falling back to the default."""
    if MODEL_CONFIG_FILE.exists():
        try:
            data = json.loads(MODEL_CONFIG_FILE.read_text())
            return data.get("model_id", MODEL_ID)
        except (json.JSONDecodeError, OSError):
            pass
    return MODEL_ID


def save_model_id(model_id: str) -> None:
    """Persist the selected model ID."""
    MODEL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODEL_CONFIG_FILE.write_text(json.dumps({"model_id": model_id}, indent=2) + "\n")


def model_workflow() -> int:
    """Interactive model selection: family → model → save."""
    current = load_model_id()
    print(f"\nCurrent model: {current}\n")

    families = list(MODEL_CATALOG.keys())
    print("Select a model family:\n")
    for i, family in enumerate(families, 1):
        print(f"  {i}) {family}")

    print()
    try:
        choice = input("Family number (or 'q' to cancel): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return 0
    if choice.lower() == "q":
        return 0
    try:
        family_idx = int(choice) - 1
        if family_idx < 0 or family_idx >= len(families):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return 1

    family = families[family_idx]
    models = MODEL_CATALOG[family]
    print(f"\n{family} models:\n")
    for i, m in enumerate(models, 1):
        print(f"  {i}) {m['name']}")
        print(f"     {m['id']}")

    print()
    try:
        choice = input("Model number (or 'q' to cancel): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return 0
    if choice.lower() == "q":
        return 0
    try:
        model_idx = int(choice) - 1
        if model_idx < 0 or model_idx >= len(models):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        return 1

    selected = models[model_idx]
    save_model_id(selected["id"])
    print(f"\n✓ Model set to: {selected['name']} ({selected['id']})")
    return 0
