"""Model benchmarking for commit message generation.

Runs diffs through multiple models, scores the outputs, and records results
to enable automatic model selection based on quality and cost efficiency.
"""

from __future__ import annotations

import json
import os
import subprocess  # nosec B404
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import MAX_DIFF_CHARS
from .prompts import COMMIT_SYSTEM_PROMPT, build_prompt, looks_like_commit_message

SCORES_FILE = Path(".venv") / ".model_scores.json"
BENCHMARK_STALENESS_DAYS = 30


def check_benchmark_staleness() -> Optional[str]:
    """Return a warning message if benchmark data is stale or missing."""
    has_local = SCORES_FILE.exists()
    has_default = (Path(__file__).parent / "default_scores.json").exists()

    if not has_local and not has_default:
        return "No benchmark data found. Run 'gitops benchmark' to find the best model for your workload."

    if not has_local:
        # Using package defaults — no warning needed
        return None

    try:
        scores = json.loads(SCORES_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return "Benchmark data is corrupted. Run 'gitops benchmark' to regenerate."
    if not scores:
        return None
    # Check age of most recent trial
    latest = max(s.get("timestamp", "") for s in scores)
    if latest:
        try:
            last_run = datetime.fromisoformat(latest)
            age_days = (datetime.now() - last_run).days
            if age_days > BENCHMARK_STALENESS_DAYS:
                return f"Benchmark data is {age_days} days old. Run 'gitops benchmark' to refresh (models and pricing change over time)."
        except ValueError:
            pass
    return None


def refresh_model_catalog(candidates: Optional[List[dict]] = None) -> List[dict]:
    """Query Bedrock for available models and return an updated benchmark list.

    Falls back to the candidate list if the API call fails.
    """
    candidates = candidates or BENCHMARK_MODELS
    try:
        import boto3
    except ModuleNotFoundError:
        return candidates

    try:
        client = boto3.client("bedrock")
        response = client.list_foundation_models()

        # Also get inference profiles for newer models
        profiles_response = client.list_inference_profiles()
        profile_ids = {p["inferenceProfileId"] for p in profiles_response.get("inferenceProfileSummaries", [])}
    except Exception:
        return candidates

    # Build available model set: prefer US inference profiles, fall back to direct IDs
    available_ids = set()
    for m in response.get("modelSummaries", []):
        available_ids.add(m["modelId"])
    available_ids.update(profile_ids)

    # Filter benchmark models to only those accessible
    active = []
    for model in candidates:
        if model["id"] in available_ids:
            active.append(model)
    return active if active else candidates


def _invoke_model(model: dict, prompt: str, system_prompt: str | None, max_tokens: int = 4000) -> str:
    """Invoke a model using the correct API format for its provider."""
    import boto3
    from botocore.config import Config

    config = Config(read_timeout=60, connect_timeout=10, retries={"max_attempts": 1})
    client = boto3.client("bedrock-runtime", config=config)
    provider = model.get("provider", "anthropic")

    if provider == "nova":
        body: dict = {
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.2},
        }
        if system_prompt:
            body["system"] = [{"text": system_prompt}]
        response = client.invoke_model(modelId=model["id"], body=json.dumps(body))
        payload = json.loads(response["body"].read())
        return "".join(part.get("text", "") for part in payload.get("output", {}).get("message", {}).get("content", []))

    if provider in ("mistral", "meta", "deepseek"):
        # Converse API format (works for Mistral, Meta, DeepSeek on Bedrock)
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        kwargs: dict = {
            "modelId": model["id"],
            "messages": messages,
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": 0.2},
        }
        if system_prompt:
            kwargs["system"] = [{"text": system_prompt}]
        response = client.converse(**kwargs)
        return "".join(block.get("text", "") for block in response.get("output", {}).get("message", {}).get("content", []))

    if provider == "ai21":
        body = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }
        if system_prompt:
            body["messages"].insert(0, {"role": "system", "content": system_prompt})
        response = client.invoke_model(modelId=model["id"], body=json.dumps(body))
        payload = json.loads(response["body"].read())
        choices = payload.get("choices", [])
        return choices[0].get("message", {}).get("content", "") if choices else ""

    if provider == "cohere":
        body = {
            "message": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }
        if system_prompt:
            body["preamble"] = system_prompt
        response = client.invoke_model(modelId=model["id"], body=json.dumps(body))
        payload = json.loads(response["body"].read())
        return payload.get("text", "")

    # Anthropic format (default)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }
    if system_prompt:
        body["system"] = system_prompt
    response = client.invoke_model(modelId=model["id"], body=json.dumps(body))
    payload = json.loads(response["body"].read())
    return "".join(part.get("text", "") for part in payload.get("content", []))


# Models to benchmark by tier
_TIER_MINIMAL = [
    {"id": "amazon.nova-micro-v1:0", "name": "Nova Micro", "provider": "nova", "cost_per_1k_input": 0.000035, "cost_per_1k_output": 0.00014},
    {"id": "amazon.nova-lite-v1:0", "name": "Nova Lite", "provider": "nova", "cost_per_1k_input": 0.00006, "cost_per_1k_output": 0.00024},
    {
        "id": "anthropic.claude-3-haiku-20240307-v1:0",
        "name": "Claude 3 Haiku",
        "provider": "anthropic",
        "cost_per_1k_input": 0.00025,
        "cost_per_1k_output": 0.00125,
    },
]

_TIER_QUICK = _TIER_MINIMAL + [
    {"id": "mistral.ministral-3-3b-instruct", "name": "Ministral 3B", "provider": "mistral", "cost_per_1k_input": 0.00004, "cost_per_1k_output": 0.00004},
    {"id": "mistral.ministral-3-8b-instruct", "name": "Ministral 8B", "provider": "mistral", "cost_per_1k_input": 0.0001, "cost_per_1k_output": 0.0001},
    {
        "id": "us.meta.llama4-scout-17b-instruct-v1:0",
        "name": "Llama 4 Scout 17B",
        "provider": "meta",
        "cost_per_1k_input": 0.00017,
        "cost_per_1k_output": 0.00017,
    },
]

_TIER_STANDARD = _TIER_QUICK + [
    {
        "id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "name": "Claude Haiku 4.5",
        "provider": "anthropic",
        "cost_per_1k_input": 0.001,
        "cost_per_1k_output": 0.005,
    },
    {"id": "amazon.nova-pro-v1:0", "name": "Nova Pro", "provider": "nova", "cost_per_1k_input": 0.0008, "cost_per_1k_output": 0.0032},
    {"id": "mistral.ministral-3-14b-instruct", "name": "Ministral 14B", "provider": "mistral", "cost_per_1k_input": 0.0002, "cost_per_1k_output": 0.0002},
    {
        "id": "us.meta.llama4-maverick-17b-instruct-v1:0",
        "name": "Llama 4 Maverick 17B",
        "provider": "meta",
        "cost_per_1k_input": 0.00017,
        "cost_per_1k_output": 0.00017,
    },
]

_TIER_THOROUGH = _TIER_STANDARD + [
    {
        "id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "name": "Claude Sonnet 4.5",
        "provider": "anthropic",
        "cost_per_1k_input": 0.003,
        "cost_per_1k_output": 0.015,
    },
    {"id": "us.amazon.nova-2-lite-v1:0", "name": "Nova 2 Lite", "provider": "nova", "cost_per_1k_input": 0.00006, "cost_per_1k_output": 0.00024},
    {"id": "us.meta.llama3-3-70b-instruct-v1:0", "name": "Llama 3.3 70B", "provider": "meta", "cost_per_1k_input": 0.00072, "cost_per_1k_output": 0.00072},
    {"id": "deepseek.v3.2", "name": "DeepSeek V3.2", "provider": "deepseek", "cost_per_1k_input": 0.0005, "cost_per_1k_output": 0.002},
    {"id": "mistral.magistral-small-2509", "name": "Magistral Small", "provider": "mistral", "cost_per_1k_input": 0.0005, "cost_per_1k_output": 0.002},
]

_TIER_EXHAUSTIVE = _TIER_THOROUGH + [
    {"id": "us.anthropic.claude-sonnet-4-6", "name": "Claude Sonnet 4.6", "provider": "anthropic", "cost_per_1k_input": 0.003, "cost_per_1k_output": 0.015},
    {
        "id": "us.anthropic.claude-opus-4-1-20250805-v1:0",
        "name": "Claude Opus 4.1",
        "provider": "anthropic",
        "cost_per_1k_input": 0.015,
        "cost_per_1k_output": 0.075,
    },
    {"id": "mistral.mistral-large-3-675b-instruct", "name": "Mistral Large 3", "provider": "mistral", "cost_per_1k_input": 0.002, "cost_per_1k_output": 0.006},
    {"id": "us.deepseek.r1-v1:0", "name": "DeepSeek R1", "provider": "deepseek", "cost_per_1k_input": 0.00135, "cost_per_1k_output": 0.00548},
    {"id": "mistral.devstral-2-123b", "name": "Devstral 2 123B", "provider": "mistral", "cost_per_1k_input": 0.0005, "cost_per_1k_output": 0.002},
]

BENCHMARK_TIERS = {
    "minimal": _TIER_MINIMAL,
    "quick": _TIER_QUICK,
    "standard": _TIER_STANDARD,
    "thorough": _TIER_THOROUGH,
    "exhaustive": _TIER_EXHAUSTIVE,
}
BENCHMARK_MODELS = _TIER_MINIMAL  # default for staleness check


@dataclass
class TrialResult:
    model_id: str
    model_name: str
    repo: str
    commit_hash: str
    diff_chars: int
    latency_ms: int
    output_tokens_approx: int
    format_valid: bool
    quality_score: float
    message: str
    cost_estimate: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


def _get_diff_for_commit(repo_path: str, commit_hash: str) -> tuple[str, str, List[str]]:
    """Extract diff, status, and new files for a commit."""
    result = subprocess.run(  # nosec
        ["git", "-C", repo_path, "diff", f"{commit_hash}^..{commit_hash}"],
        capture_output=True,
        text=True,
        check=False,
    )
    diff = result.stdout or ""

    # Get status
    status_result = subprocess.run(  # nosec
        ["git", "-C", repo_path, "diff", "--name-status", f"{commit_hash}^..{commit_hash}"],
        capture_output=True,
        text=True,
        check=False,
    )
    status = status_result.stdout or ""

    # Extract new files
    new_files = [line[2:] for line in status.splitlines() if line.startswith("A\t")]

    return diff, status, new_files


def _estimate_cost(model: dict, input_chars: int, output_chars: int) -> float:
    """Rough cost estimate based on char-to-token ratio (~4 chars per token)."""
    input_tokens = input_chars / 4
    output_tokens = output_chars / 4
    return input_tokens / 1000 * model["cost_per_1k_input"] + output_tokens / 1000 * model["cost_per_1k_output"]


def _score_message(message: str) -> dict:
    """Score a commit message on structural and content quality.

    Returns format_valid (bool) and quality_score (0.0-1.0).
    Evaluates: format, specificity, naturalness, and absence of bot-speak.
    """
    lines = message.strip().splitlines()
    if not lines:
        return {"format_valid": False, "quality_score": 0.0}

    subject = lines[0]
    subject_len = len(subject)

    valid = looks_like_commit_message(message)
    if not valid:
        return {"format_valid": False, "quality_score": 0.0}

    # Extract executive paragraph (lines between blank-after-subject and file sections)
    exec_lines = []
    file_section_started = False
    for ln in lines[2:]:
        stripped = ln.strip()
        if stripped.startswith(("Modified:", "New:", "Deleted:")):
            file_section_started = True
            continue
        if not file_section_started and stripped and not stripped.startswith(("-", "*", "•")):
            exec_lines.append(stripped)
    exec_para = " ".join(exec_lines).lower()
    body_lines = [ln for ln in lines[2:] if ln.strip()] if len(lines) > 2 else []

    score = 1.0

    # --- STRUCTURE ---
    # Penalize generic subjects
    generic_subjects = [
        "update staged changes",
        "update files",
        "misc changes",
        "code updates",
        "various updates",
        "changes",
        "updates",
    ]
    if subject.lower().strip() in generic_subjects:
        score -= 0.4

    if subject_len < 15:
        score -= 0.15
    if subject_len > 72:
        score -= 0.1

    # No executive paragraph at all
    if not exec_lines:
        if body_lines:
            descriptive = [ln for ln in body_lines if not ln.strip().startswith(("- ", "Modified:", "New:", "Deleted:", "src/", "docs/", "./"))]
            if not descriptive:
                score -= 0.3  # file list only
        else:
            score -= 0.2  # no body

        return {"format_valid": True, "quality_score": max(0.0, min(1.0, score))}

    # --- BOT-SPEAK PENALTY ---
    bot_phrases = [
        "this commit introduces",
        "this commit adds",
        "this commit updates",
        "this commit implements",
        "this commit includes",
        "this commit represents",
        "this pr ",
        "this pull request",
        "this change introduces",
        "the following changes",
        "here is a summary",
        "the purpose of this commit",
    ]
    bot_hits = sum(1 for p in bot_phrases if p in exec_para)
    score -= bot_hits * 0.1

    # --- CORPORATE FILLER PENALTY ---
    filler_phrases = [
        "key improvements",
        "key enhancements",
        "several enhancements",
        "several improvements",
        "comprehensive update",
        "comprehensive changes",
        "significant improvements",
        "various improvements",
        "various enhancements",
        "robust framework",
        "streamlined",
        "leveraging",
        "synergy",
        "paradigm",
        "holistic",
        "transformative",
        "strategic initiative",
        "cutting-edge",
        "best practices",
        "world-class",
    ]
    filler_hits = sum(1 for p in filler_phrases if p in exec_para)
    score -= filler_hits * 0.08

    # --- VAGUENESS PENALTY ---
    vague_phrases = [
        "code quality",
        "code improvements",
        "code enhancements",
        "code updates",
        "general improvements",
        "minor improvements",
        "updated logic",
        "improved functionality",
        "enhanced functionality",
        "better handling",
        "improved handling",
        "various fixes",
        "miscellaneous changes",
    ]
    vague_hits = sum(1 for p in vague_phrases if p in exec_para)
    score -= vague_hits * 0.1

    # --- SPECIFICITY REWARD ---
    # Reward if the exec paragraph contains specific technical terms
    # (function names, module paths, feature keywords)
    specificity_signals = 0
    # Contains something that looks like a function/class/module name
    import re

    if re.search(r'\b[a-z_]+_[a-z_]+\b', exec_para):  # snake_case identifiers
        specificity_signals += 1
    if re.search(r'\b[A-Z][a-z]+[A-Z]', " ".join(exec_lines)):  # CamelCase in original case
        specificity_signals += 1
    if re.search(r'\b(api|cli|url|json|yaml|sql|http|aws|bedrock)\b', exec_para):
        specificity_signals += 1
    # Contains a concrete action verb (not just "updated" or "improved")
    concrete_verbs = [
        "renamed",
        "added",
        "removed",
        "fixed",
        "replaced",
        "migrated",
        "split",
        "merged",
        "extracted",
        "refactored",
        "wired",
        "connected",
    ]
    if any(v in exec_para for v in concrete_verbs):
        specificity_signals += 1

    if specificity_signals >= 3:
        score += 0.1
    elif specificity_signals == 0:
        score -= 0.1

    # --- NATURALNESS ---
    # Penalize if every sentence starts the same way (repetitive structure)
    sentences = [s.strip() for s in exec_para.replace(". ", ".\n").splitlines() if s.strip()]
    if len(sentences) >= 3:
        first_words = [s.split()[0] if s.split() else "" for s in sentences]
        if len(set(first_words)) == 1:
            score -= 0.1  # all sentences start with same word

    return {"format_valid": True, "quality_score": max(0.0, min(1.0, score))}


def run_trial(repo_path: str, commit_hash: str, model: dict) -> Optional[TrialResult]:
    """Run a single model trial against a commit diff."""
    diff, status, new_files = _get_diff_for_commit(repo_path, commit_hash)
    if not diff.strip():
        return None

    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n... (diff truncated)"

    prompt = build_prompt(status, diff, new_files, is_initial_commit=False)
    input_chars = len(prompt) + len(COMMIT_SYSTEM_PROMPT or "")

    start = time.time()
    try:
        message = _invoke_model(model, prompt, COMMIT_SYSTEM_PROMPT)
    except Exception as exc:
        print(f"    ✗ {model['name']}: {exc}")
        return None
    latency_ms = int((time.time() - start) * 1000)

    score = _score_message(message)
    cost = _estimate_cost(model, input_chars, len(message))

    return TrialResult(
        model_id=model["id"],
        model_name=model["name"],
        repo=Path(repo_path).name,
        commit_hash=commit_hash[:12],
        diff_chars=len(diff),
        latency_ms=latency_ms,
        output_tokens_approx=len(message) // 4,
        format_valid=score["format_valid"],
        quality_score=score["quality_score"],
        message=message.strip(),
        cost_estimate=cost,
    )


def load_scores() -> List[dict]:
    """Load historical trial results. Falls back to package-embedded defaults."""
    if SCORES_FILE.exists():
        try:
            return json.loads(SCORES_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    # Fall back to bundled benchmark data
    default_path = Path(__file__).parent / "default_scores.json"
    if default_path.exists():
        try:
            return json.loads(default_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return []


def save_scores(scores: List[dict]) -> None:
    """Persist trial results."""
    SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCORES_FILE.write_text(json.dumps(scores, indent=2) + "\n")


def get_best_model(scores: Optional[List[dict]] = None, diff_size: Optional[int] = None) -> Optional[str]:
    """Determine the best model from recorded scores.

    If diff_size is provided, only considers trials in the same size bucket:
      small: <10,000 chars, medium: 10,000-50,000, large: >50,000
    Composite: quality_score * 0.6 + cost_efficiency * 0.3 + speed * 0.1
    """
    scores = scores if scores is not None else load_scores()
    if not scores:
        return None

    # Filter by diff size bucket if requested
    if diff_size is not None:
        bucket = _diff_bucket(diff_size)
        bucket_scores = [s for s in scores if _diff_bucket(s.get("diff_chars", 0)) == bucket]
        if bucket_scores:
            scores = bucket_scores

    # Aggregate by model
    from collections import defaultdict

    stats = defaultdict(lambda: {"quality_sum": 0.0, "total": 0, "cost_sum": 0.0, "latency_sum": 0})

    for s in scores:
        mid = s["model_id"]
        stats[mid]["total"] += 1
        # Support both old (format_valid only) and new (quality_score) data
        stats[mid]["quality_sum"] += s.get("quality_score", 1.0 if s.get("format_valid") else 0.0)
        stats[mid]["cost_sum"] += s["cost_estimate"]
        stats[mid]["latency_sum"] += s["latency_ms"]

    # Need at least 2 trials per model to rank
    eligible = {k: v for k, v in stats.items() if v["total"] >= 2}
    if not eligible:
        return None

    # Normalize metrics
    max_cost = max(v["cost_sum"] / v["total"] for v in eligible.values()) or 1
    max_latency = max(v["latency_sum"] / v["total"] for v in eligible.values()) or 1

    ranked = []
    for mid, v in eligible.items():
        quality = v["quality_sum"] / v["total"]
        avg_cost = v["cost_sum"] / v["total"]
        avg_latency = v["latency_sum"] / v["total"]
        cost_score = 1 - (avg_cost / max_cost)
        speed_score = 1 - (avg_latency / max_latency)
        composite = quality * 0.6 + cost_score * 0.3 + speed_score * 0.1
        ranked.append((mid, composite, quality, avg_cost, avg_latency))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[0][0]


def _diff_bucket(chars: int) -> str:
    """Categorize diff size into small/medium/large."""
    if chars < 10_000:
        return "small"
    if chars < 50_000:
        return "medium"
    return "large"


def print_leaderboard(scores: Optional[List[dict]] = None) -> None:
    """Print the model leaderboard from recorded scores."""
    scores = scores if scores is not None else load_scores()
    if not scores:
        print("No benchmark data recorded yet.")
        return

    from collections import defaultdict

    stats = defaultdict(lambda: {"quality_sum": 0.0, "total": 0, "cost_sum": 0.0, "latency_sum": 0, "name": ""})
    for s in scores:
        mid = s["model_id"]
        stats[mid]["total"] += 1
        stats[mid]["quality_sum"] += s.get("quality_score", 1.0 if s.get("format_valid") else 0.0)
        stats[mid]["cost_sum"] += s["cost_estimate"]
        stats[mid]["latency_sum"] += s["latency_ms"]
        stats[mid]["name"] = s.get("model_name", mid)

    print(f"\n{'Model':<28} {'Trials':>6} {'Quality':>8} {'Avg Cost':>10} {'Avg ms':>8}")
    print("-" * 66)
    for mid, v in sorted(stats.items(), key=lambda x: x[1]["quality_sum"] / max(x[1]["total"], 1), reverse=True):
        quality = v["quality_sum"] / v["total"] * 100
        avg_cost = v["cost_sum"] / v["total"]
        avg_ms = v["latency_sum"] // v["total"]
        print(f"{v['name']:<28} {v['total']:>6} {quality:>7.0f}% ${avg_cost:>8.6f} {avg_ms:>7}ms")

    best = get_best_model(scores)
    if best:
        name = stats[best]["name"]
        print(f"\n→ Recommended: {name} ({best})")


def benchmark_workflow(repos: Optional[List[str]] = None, commits_per_repo: int = 3, tier: str = "quick", workers: Optional[int] = None) -> int:
    """Run benchmark trials across repos and models with concurrent execution."""
    if not repos:
        repos = ["."]

    max_workers = workers or min(os.cpu_count() or 4, 8)
    base_models = BENCHMARK_TIERS.get(tier, _TIER_MINIMAL)

    # Gather commits
    test_cases: List[tuple[str, str]] = []
    for repo_path in repos:
        result = subprocess.run(  # nosec
            ["git", "-C", repo_path, "log", "--format=%H", f"-{commits_per_repo}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            for h in result.stdout.strip().splitlines():
                # Skip initial commits (no parent)
                check = subprocess.run(  # nosec
                    ["git", "-C", repo_path, "rev-parse", f"{h}^"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if check.returncode == 0:
                    test_cases.append((repo_path, h))

    if not test_cases:
        print("No valid commits found for benchmarking.")
        return 1

    models = refresh_model_catalog(base_models)
    total_trials = len(models) * len(test_cases)
    print(f"\nBenchmarking {len(models)} models × {len(test_cases)} commits = {total_trials} trials ({tier} tier, {max_workers} workers)\n")

    existing_scores = load_scores()
    new_results: List[TrialResult] = []

    # Build all (repo, commit, model) jobs
    jobs = [(repo_path, commit_hash, model) for repo_path, commit_hash in test_cases for model in models]

    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_trial, rp, ch, m): (rp, ch, m) for rp, ch, m in jobs}
        for future in as_completed(futures):
            rp, ch, m = futures[future]
            completed += 1
            try:
                trial_result = future.result()
            except Exception as exc:
                print(f"  [{completed}/{total_trials}] ✗ {m['name']:<24} {Path(rp).resolve().name}/{ch[:8]}: {exc}")
                continue
            if trial_result:
                new_results.append(trial_result)
                status = "✓" if trial_result.format_valid else "✗"
                print(
                    f"  [{completed}/{total_trials}] {status} {m['name']:<24} "
                    f"{trial_result.repo}/{ch[:8]}  {trial_result.latency_ms:>5}ms  "
                    f"${trial_result.cost_estimate:.6f}  ({trial_result.diff_chars:,} chars)",
                )

    if new_results:
        all_scores = existing_scores + [asdict(r) for r in new_results]
        save_scores(all_scores)
        print(f"\nRecorded {len(new_results)} new trials ({len(all_scores)} total)")
        print_leaderboard(all_scores)
        export_results_markdown(all_scores)
    else:
        print("No trials completed.")

    return 0


def export_results_markdown(scores: Optional[List[dict]] = None) -> None:
    """Write benchmark results to docs/benchmark_results.md."""
    scores = scores if scores is not None else load_scores()
    if not scores:
        return

    from collections import defaultdict

    stats = defaultdict(lambda: {"quality_sum": 0.0, "total": 0, "cost_sum": 0.0, "latency_sum": 0, "name": ""})
    for s in scores:
        mid = s["model_id"]
        stats[mid]["total"] += 1
        stats[mid]["quality_sum"] += s.get("quality_score", 1.0 if s.get("format_valid") else 0.0)
        stats[mid]["cost_sum"] += s["cost_estimate"]
        stats[mid]["latency_sum"] += s["latency_ms"]
        stats[mid]["name"] = s.get("model_name", mid)

    lines = [
        "# Model Benchmark Results",
        "",
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"Total trials: {len(scores)}",
        "",
        "## Leaderboard",
        "",
        "| Model | Trials | Quality | Avg Cost | Avg Latency |",
        "|-------|--------|---------|----------|-------------|",
    ]

    for mid, v in sorted(stats.items(), key=lambda x: x[1]["quality_sum"] / max(x[1]["total"], 1), reverse=True):
        quality = v["quality_sum"] / v["total"] * 100
        avg_cost = v["cost_sum"] / v["total"]
        avg_ms = v["latency_sum"] // v["total"]
        lines.append(f"| {v['name']} | {v['total']} | {quality:.0f}% | ${avg_cost:.6f} | {avg_ms}ms |")

    best = get_best_model(scores)
    if best and best in stats:
        lines.append(f"\n**Recommended: {stats[best]['name']}** (`{best}`)")

    lines += [
        "",
        "## Trial Details",
        "",
        "| Model | Repo | Commit | Diff Size | Valid | Latency | Cost |",
        "|-------|------|--------|-----------|-------|---------|------|",
    ]
    for s in scores:
        valid = "✓" if s["format_valid"] else "✗"
        lines.append(
            f"| {s['model_name']} | {s['repo']} | `{s['commit_hash']}` | {s['diff_chars']:,} | {valid} | {s['latency_ms']}ms | ${s['cost_estimate']:.6f} |",
        )
    lines.append("")

    out = Path("docs/benchmark_results.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"\n→ Results written to {out}")
