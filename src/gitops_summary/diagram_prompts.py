"""Prompt builders and metadata for AI-generated PlantUML diagrams."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DiagramTypeSpec:
    """Definition for a supported diagram type."""

    name: str
    description: str
    instruction: str
    default: bool = False
    required_signals: tuple[str, ...] = ()
    optional_signals: tuple[str, ...] = ()
    supports_best_effort: bool = True
    insufficient_context_message: str = "Limited repository context was found for this diagram type."


DIAGRAM_TYPE_SPECS: dict[str, DiagramTypeSpec] = {
    "architecture": DiagramTypeSpec(
        name="architecture",
        description="High-level system architecture across apps, services, storage, and external systems.",
        instruction=(
            "Generate a PlantUML architecture/component diagram that shows the main system pieces, "
            "their responsibilities, and how they connect. Include application layers, storage systems, "
            "external services, and user-facing entry points when evidence exists."
        ),
        default=True,
        optional_signals=("api", "frontend", "database", "worker", "docker", "cloud", "cli", "search"),
        insufficient_context_message="Repo structure does not strongly identify major runtime components, so architecture output may be partial.",
    ),
    "containers": DiagramTypeSpec(
        name="containers",
        description="Container/service topology such as Docker Compose services and dependencies.",
        instruction=(
            "Generate a PlantUML diagram that focuses on runtime services or containers. Show service names, ports, "
            "major dependencies, and supporting infrastructure only when the repository clearly indicates them."
        ),
        default=True,
        required_signals=("docker",),
        optional_signals=("compose", "worker", "api", "frontend", "database"),
        insufficient_context_message="Container orchestration files were limited or absent, so the containers diagram may omit services or be skipped.",
    ),
    "data_model": DiagramTypeSpec(
        name="data_model",
        description="Entity relationship or schema-focused view of persistent data structures.",
        instruction=(
            "Generate a PlantUML entity-relationship diagram for the repository's data model. Include entities/tables, "
            "important columns or fields, primary/foreign keys, and relationships only when the schema is reasonably supported by the repo context."
        ),
        default=True,
        required_signals=("database",),
        optional_signals=("orm", "migrations", "sql", "models"),
        insufficient_context_message="The repository did not expose enough schema evidence to confidently map a full data model.",
    ),
    "ingestion": DiagramTypeSpec(
        name="ingestion",
        description="Activity/flow view for document or data ingestion pipelines.",
        instruction=(
            "Generate a PlantUML activity diagram showing the main ingestion or intake flow for data entering the system. "
            "Include validation, transformation, storage, indexing, and error branches when those are visible in the repo context."
        ),
        default=True,
        optional_signals=("api", "worker", "database", "search", "storage"),
        insufficient_context_message="No strong ingestion pipeline evidence was found, so the flow may be generalized.",
    ),
    "search_ask": DiagramTypeSpec(
        name="search_ask",
        description="Flow for search and question-answer style user interactions.",
        instruction=(
            "Generate a PlantUML activity or flow diagram for the repo's search-and-answer workflow. Show retrieval, ranking, context assembly, model calls, and response rendering when those behaviors are supported by the repo context."
        ),
        default=True,
        optional_signals=("search", "bedrock", "ai", "api", "database"),
        insufficient_context_message="Search and question-answer behavior was only partially visible in the repository context.",
    ),
    "sequence": DiagramTypeSpec(
        name="sequence",
        description="Interaction sequence for a primary user or system workflow.",
        instruction=(
            "Generate a PlantUML sequence diagram for the repository's main workflow. Show actors and participating systems in order, using only interactions that can be reasonably inferred from the codebase context."
        ),
        optional_signals=("api", "cli", "frontend", "worker", "bedrock"),
        insufficient_context_message="The repo shows only limited end-to-end workflow evidence, so sequence coverage may be incomplete.",
    ),
    "component": DiagramTypeSpec(
        name="component",
        description="Module/component-level structure of the application itself.",
        instruction=(
            "Generate a PlantUML component diagram showing major modules, packages, or services inside the application. Focus on code-level structure and dependencies between major components."
        ),
        optional_signals=("python", "api", "cli", "worker", "frontend"),
        insufficient_context_message="Only partial application-structure evidence was available, so component grouping may be broad.",
    ),
    "deployment": DiagramTypeSpec(
        name="deployment",
        description="Deployment/runtime topology across hosts, services, and external dependencies.",
        instruction=(
            "Generate a PlantUML deployment-style diagram for the runtime environment. Show hosts, services, infrastructure boundaries, and external providers only where the repo clearly indicates deployment topology."
        ),
        required_signals=("docker",),
        optional_signals=("kubernetes", "cloud", "terraform", "frontend", "api", "database"),
        insufficient_context_message="Deployment topology evidence was weak, so any deployment diagram should be treated as best effort.",
    ),
    "class": DiagramTypeSpec(
        name="class",
        description="Class-oriented structural view for object-heavy repositories.",
        instruction=(
            "Generate a PlantUML class diagram only if the repository context clearly shows meaningful classes and relationships. Prefer a smaller trustworthy diagram over a speculative one."
        ),
        required_signals=("classes",),
        optional_signals=("python", "models", "orm"),
        insufficient_context_message="The repository does not expose enough class relationship detail for a trustworthy class diagram.",
    ),
    "state": DiagramTypeSpec(
        name="state",
        description="State machine or lifecycle transitions for domain objects or workflows.",
        instruction=(
            "Generate a PlantUML state diagram only if the repository context shows meaningful statuses, transitions, or lifecycle states. Keep the diagram scoped to one coherent workflow."
        ),
        required_signals=("stateful",),
        optional_signals=("workflow", "api", "database"),
        insufficient_context_message="State transitions were not explicit enough to confidently derive a full state diagram.",
    ),
    "use_case": DiagramTypeSpec(
        name="use_case",
        description="User-facing capabilities and actor interactions.",
        instruction=(
            "Generate a PlantUML use-case diagram showing the main actors and user-visible capabilities supported by the repository. Use only capabilities supported by the README, CLI interface, or code organization."
        ),
        optional_signals=("cli", "api", "frontend", "readme"),
        insufficient_context_message="User-facing capabilities were only partially documented, so the use-case view may be incomplete.",
    ),
    "activity": DiagramTypeSpec(
        name="activity",
        description="Generic activity/flow diagram for a notable process in the codebase.",
        instruction=(
            "Generate a PlantUML activity diagram for one meaningful process in the repository. Prefer a concrete workflow such as ingestion, summarization, synchronization, or reporting if evidence exists."
        ),
        optional_signals=("workflow", "api", "worker", "cli"),
        insufficient_context_message="The repository did not expose one dominant process, so the activity diagram may be generalized.",
    ),
}

SUPPORTED_DIAGRAM_TYPES = tuple(DIAGRAM_TYPE_SPECS.keys())
DEFAULT_DIAGRAM_TYPES = tuple(name for name, spec in DIAGRAM_TYPE_SPECS.items() if spec.default)


def get_supported_diagram_types() -> list[str]:
    """Return all supported diagram type names."""

    return list(SUPPORTED_DIAGRAM_TYPES)


def get_default_diagram_types() -> list[str]:
    """Return the default diagram types for generation."""

    return list(DEFAULT_DIAGRAM_TYPES)


def get_diagram_type_spec(diagram_type: str) -> DiagramTypeSpec:
    """Return metadata for a diagram type or raise ValueError."""

    if diagram_type not in DIAGRAM_TYPE_SPECS:
        valid = ", ".join(get_supported_diagram_types())
        raise ValueError(f"Unsupported diagram type '{diagram_type}'. Valid types: {valid}")
    return DIAGRAM_TYPE_SPECS[diagram_type]


def get_diagram_style_rules() -> str:
    """Return shared styling instructions derived from existing diagrams."""

    return (
        "Style requirements:\n"
        "- Use !theme plain.\n"
        "- Prefer clean, readable labels and a short descriptive title.\n"
        "- Keep diagrams simple and version-control friendly.\n"
        "- Use PlantUML primitives that fit the diagram type (actor, package, component, database, cloud, entity, start/stop, if/else).\n"
        "- Do not add decorative noise, legends, or speculative details.\n"
        "- Match the plain visual style already used in docs/diagrams."
    )


def get_diagram_system_prompt() -> str:
    """Return the system prompt for diagram generation."""

    return (
        "You are a software architect generating PlantUML from repository context. "
        "Return ONLY PlantUML source code. Do not include markdown fences, prose, notes to the user, or explanations. "
        "Always include @startuml and @enduml. Always include !theme plain near the top. "
        "Never invent implementation details that are not supported by the provided repository context. "
        "If evidence is weak, reduce scope and keep the diagram conservative rather than speculative."
    )


def build_diagram_prompt(context: dict[str, Any], diagram_type: str) -> str:
    """Build the user prompt for a specific diagram type."""

    spec = get_diagram_type_spec(diagram_type)
    parts = [
        f"Diagram type: {spec.name}",
        spec.instruction,
        get_diagram_style_rules(),
        "Use only information supported by the repository context below.",
    ]

    readme = context.get("readme", "")
    if readme:
        parts.append(f"README excerpt:\n{readme}")

    top_level = context.get("top_level_entries", [])
    if top_level:
        parts.append("Top-level repo entries:\n" + "\n".join(f"- {entry}" for entry in top_level))

    file_tree = context.get("file_tree", "")
    if file_tree:
        parts.append(f"Filtered file tree:\n{file_tree}")

    configs = context.get("configs", {})
    if configs:
        rendered_configs = []
        for name, content in configs.items():
            rendered_configs.append(f"{name}:\n{content}")
        parts.append("Key config snippets:\n" + "\n\n".join(rendered_configs))

    git_log = context.get("git_log", "")
    if git_log:
        parts.append(f"Recent git log:\n{git_log}")

    detected_signals = context.get("signals", [])
    if detected_signals:
        parts.append("Detected architectural signals:\n" + ", ".join(detected_signals))

    return "\n\n".join(parts)


def format_supported_diagram_types() -> str:
    """Return a human-readable summary of supported diagram types."""

    lines = []
    for name in get_supported_diagram_types():
        spec = get_diagram_type_spec(name)
        suffix = " [default]" if spec.default else ""
        lines.append(f"- {name}{suffix}: {spec.description}")
    return "\n".join(lines)


def sanitize_plantuml_response(text: str, diagram_name: str | None = None) -> str:
    """Extract and normalize PlantUML content from a model response."""

    cleaned = text.strip()
    cleaned = cleaned.replace("```plantuml", "```").replace("```puml", "```")

    if "```" in cleaned:
        segments = [segment.strip() for segment in cleaned.split("```") if segment.strip()]
        plantuml_segment = next((segment for segment in segments if "@startuml" in segment or "@enduml" in segment), None)
        if plantuml_segment:
            cleaned = plantuml_segment
        elif segments:
            cleaned = segments[0]

    if "@startuml" in cleaned and "@enduml" in cleaned:
        start = cleaned.index("@startuml")
        end = cleaned.rindex("@enduml") + len("@enduml")
        cleaned = cleaned[start:end].strip()
    else:
        name_suffix = f" {diagram_name}" if diagram_name else ""
        cleaned = cleaned.strip("` \n")
        cleaned = f"@startuml{name_suffix}\n{cleaned}\n@enduml"

    lines = [line.rstrip() for line in cleaned.splitlines()]
    normalized_lines: list[str] = []
    inserted_theme = False

    for index, line in enumerate(lines):
        normalized_lines.append(line)
        if index == 0 and line.startswith("@startuml"):
            has_theme = any(existing.strip() == "!theme plain" for existing in lines[1:6])
            if not has_theme:
                normalized_lines.append("!theme plain")
                inserted_theme = True

    if not inserted_theme and not any(line.strip() == "!theme plain" for line in normalized_lines):
        normalized_lines.insert(1 if normalized_lines and normalized_lines[0].startswith("@startuml") else 0, "!theme plain")

    return "\n".join(normalized_lines).strip() + "\n"