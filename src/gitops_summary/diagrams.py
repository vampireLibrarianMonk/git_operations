"""Diagram generation and rendering workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .bedrock import invoke_bedrock_text
from .config import MAX_TOKENS_DIAGRAM
from .diagram_prompts import (
    DiagramTypeSpec,
    build_diagram_prompt,
    format_supported_diagram_types,
    get_default_diagram_types,
    get_diagram_system_prompt,
    get_diagram_type_spec,
    get_supported_diagram_types,
    sanitize_plantuml_response,
)
from .plantuml import render_diagram
from .repo_context import collect_repo_context


@dataclass
class DiagramAssessment:
    """Assessment of whether a diagram can be produced confidently."""

    status: str
    confidence: str
    warnings: list[str] = field(default_factory=list)


def diagrams_workflow(args) -> int:
    """Entry point for the diagrams CLI workflow."""

    if getattr(args, "list_types", False):
        print("Supported diagram types:")
        print(format_supported_diagram_types())
        return 0

    return generate_diagrams(
        repo_path=args.repo,
        output_dir=args.output,
        diagram_types=args.diagram_types,
        output_format=args.output_format,
        model_id=args.model,
        render_only=args.render_only,
    )


def generate_diagrams(
    repo_path: str = ".",
    output_dir: str = "docs/diagrams",
    diagram_types: list[str] | None = None,
    output_format: str = "png",
    model_id: str | None = None,
    render_only: bool = False,
) -> int:
    """Generate or render PlantUML diagrams for a repository."""

    requested_types = _normalize_diagram_types(diagram_types)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    if render_only:
        return _render_existing_diagrams(output_root, requested_types, output_format)

    print(f"[diagrams] Analyzing repository context from {repo_path}...")
    try:
        context = collect_repo_context(repo_path)
    except Exception as exc:
        print(f"[diagrams] Failed to collect repository context: {exc}")
        return 1

    system_prompt = get_diagram_system_prompt()
    generated = 0
    had_errors = False

    for diagram_type in requested_types:
        spec = get_diagram_type_spec(diagram_type)
        assessment = assess_diagram_feasibility(context, spec)

        if assessment.status == "skip":
            print(f"[diagrams] Skipped {diagram_type}: {assessment.warnings[0] if assessment.warnings else 'insufficient context'}")
            continue

        confidence_note = f"confidence={assessment.confidence}"
        if assessment.status == "best_effort":
            print(f"[diagrams] Generating {diagram_type} ({confidence_note}, best effort)...")
        else:
            print(f"[diagrams] Generating {diagram_type} ({confidence_note})...")

        for warning in assessment.warnings:
            print(f"[diagrams] Note for {diagram_type}: {warning}")

        prompt = build_diagram_prompt(context, diagram_type)
        puml_path = output_root / f"{diagram_type}.puml"

        try:
            response = invoke_bedrock_text(
                prompt,
                system_prompt=system_prompt,
                max_tokens=MAX_TOKENS_DIAGRAM,
                model_id=model_id,
            )
            puml_text = sanitize_plantuml_response(response, diagram_name=diagram_type)
            puml_path.write_text(puml_text, encoding="utf-8")
        except Exception as exc:
            had_errors = True
            print(f"[diagrams] Failed to generate {diagram_type}: {exc}")
            continue

        generated += 1

        try:
            rendered_path = render_diagram(puml_path, output_format=output_format)
        except Exception as exc:
            had_errors = True
            print(f"[diagrams] Generated {diagram_type} source: {puml_path}")
            print(f"[diagrams] Rendering failed for {diagram_type}: {exc}")
            continue

        if assessment.status == "best_effort":
            print(f"[diagrams] Generated {diagram_type} (best effort): {puml_path} -> {rendered_path}")
        else:
            print(f"[diagrams] Generated {diagram_type}: {puml_path} -> {rendered_path}")

    if generated == 0:
        return 1 if had_errors else 0
    return 1 if had_errors else 0


def assess_diagram_feasibility(context: dict, spec: DiagramTypeSpec) -> DiagramAssessment:
    """Assess whether a diagram type has enough repo evidence to generate."""

    signals = set(context.get("signals", []))
    has_generic_context = bool(context.get("readme") or context.get("file_tree"))

    required_hits = [signal for signal in spec.required_signals if signal in signals]
    optional_hits = [signal for signal in spec.optional_signals if signal in signals]

    if spec.required_signals and len(required_hits) == len(spec.required_signals):
        confidence = "high" if optional_hits else "medium"
        return DiagramAssessment(status="generate", confidence=confidence)

    if spec.required_signals and required_hits:
        return DiagramAssessment(
            status="best_effort" if spec.supports_best_effort else "skip",
            confidence="medium",
            warnings=[spec.insufficient_context_message],
        )

    if not spec.required_signals and optional_hits:
        confidence = "high" if len(optional_hits) >= 2 else "medium"
        return DiagramAssessment(status="generate", confidence=confidence)

    if optional_hits and spec.supports_best_effort:
        return DiagramAssessment(status="best_effort", confidence="low", warnings=[spec.insufficient_context_message])

    if spec.supports_best_effort and has_generic_context and spec.name in {"architecture", "component", "sequence", "use_case", "activity", "ingestion"}:
        return DiagramAssessment(status="best_effort", confidence="low", warnings=[spec.insufficient_context_message])

    return DiagramAssessment(status="skip", confidence="low", warnings=[spec.insufficient_context_message])


def _normalize_diagram_types(diagram_types: list[str] | None) -> list[str]:
    normalized = diagram_types or get_default_diagram_types()
    valid = set(get_supported_diagram_types())
    ordered: list[str] = []

    for diagram_type in normalized:
        if diagram_type not in valid:
            supported = ", ".join(get_supported_diagram_types())
            raise ValueError(f"Unsupported diagram type '{diagram_type}'. Supported types: {supported}")
        if diagram_type not in ordered:
            ordered.append(diagram_type)

    return ordered


def _render_existing_diagrams(output_root: Path, requested_types: list[str], output_format: str) -> int:
    rendered = 0
    had_errors = False

    for diagram_type in requested_types:
        source_path = output_root / f"{diagram_type}.puml"
        if not source_path.exists():
            print(f"[diagrams] Skipped {diagram_type}: no PlantUML source found at {source_path}")
            continue

        try:
            rendered_path = render_diagram(source_path, output_format=output_format)
        except Exception as exc:
            had_errors = True
            print(f"[diagrams] Failed to render {diagram_type}: {exc}")
            continue

        rendered += 1
        print(f"[diagrams] Rendered {diagram_type}: {rendered_path}")

    if rendered == 0:
        return 1 if had_errors else 0
    return 1 if had_errors else 0