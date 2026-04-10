"""PlantUML discovery and rendering helpers."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path


SUPPORTED_OUTPUT_FORMATS = ("png", "svg", "txt")
PLANTUML_VERSION = "1.2024.8"
PLANTUML_JAR_URL = f"https://github.com/plantuml/plantuml/releases/download/v{PLANTUML_VERSION}/plantuml-{PLANTUML_VERSION}.jar"
JAR_SEARCH_PATHS = (
    "/usr/local/lib/plantuml.jar",
    "/opt/plantuml.jar",
    "/tmp/plantuml.jar",
)


def find_plantuml_command() -> list[str] | None:
    """Find a usable PlantUML command or jar invocation."""

    command = shutil.which("plantuml")
    if command:
        return [command]

    for candidate in _candidate_jar_paths():
        if candidate and Path(candidate).is_file():
            return ["java", "-jar", candidate]

    return None


def render_diagram(input_path: str | Path, output_format: str = "png", output_dir: str | Path | None = None) -> Path:
    """Render a single PlantUML file."""

    if output_format not in SUPPORTED_OUTPUT_FORMATS:
        valid = ", ".join(SUPPORTED_OUTPUT_FORMATS)
        raise ValueError(f"Unsupported PlantUML output format '{output_format}'. Valid formats: {valid}")

    base_command = find_plantuml_command()
    if not base_command:
        raise RuntimeError(_install_instructions())

    source_path = Path(input_path)
    if not source_path.exists():
        raise RuntimeError(f"PlantUML source file not found: {source_path}")

    command = [*base_command, f"-t{output_format}"]
    destination_dir = source_path.parent
    if output_dir is not None:
        destination_dir = Path(output_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        command.extend(["-o", str(destination_dir.resolve())])

    command.append(str(source_path.resolve()))
    env = _build_headless_env()

    result = subprocess.run(command, capture_output=True, text=True, env=env, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip() or "unknown PlantUML error"
        raise RuntimeError(f"PlantUML rendering failed for {source_path.name}: {stderr}")

    return destination_dir / f"{source_path.stem}.{output_format}"


def render_directory(directory: str | Path, output_format: str = "png") -> list[Path]:
    """Render all .puml files in a directory."""

    root = Path(directory)
    outputs: list[Path] = []
    for source_path in sorted(root.glob("*.puml")):
        outputs.append(render_diagram(source_path, output_format=output_format))
    return outputs


def _build_headless_env() -> dict[str, str]:
    env = dict(os.environ)
    current = env.get("JAVA_TOOL_OPTIONS", "").strip()
    required = "-Djava.awt.headless=true"
    if required not in current:
        env["JAVA_TOOL_OPTIONS"] = f"{required} {current}".strip()
    return env


def _install_instructions() -> str:
    windows_temp = os.path.join(os.getenv("TEMP", "%TEMP%"), "plantuml.jar")
    return (
        "PlantUML was not found. The easiest setup is Java + the PlantUML jar; no apt/yum PlantUML package is required, "
        "and for component/activity/entity-style diagrams Graphviz is not required.\n\n"
        "This CLI already forces headless mode by setting JAVA_TOOL_OPTIONS=-Djava.awt.headless=true when it renders, "
        "so once Java and the jar are available you can rerun the command.\n\n"
        "Quick setup options:\n"
        "- Put the jar at /tmp/plantuml.jar, /usr/local/lib/plantuml.jar, or /opt/plantuml.jar\n"
        "- Or set PLANTUML_JAR to the jar location\n"
        "- Jar download URL: "
        f"{PLANTUML_JAR_URL}\n\n"
        "Ubuntu/Debian:\n"
        "  sudo apt-get install -y default-jre-headless wget\n"
        f"  wget -O /tmp/plantuml.jar \"{PLANTUML_JAR_URL}\"\n"
        "  export PLANTUML_JAR=/tmp/plantuml.jar\n"
        "  JAVA_TOOL_OPTIONS=\"-Djava.awt.headless=true\" java -jar /tmp/plantuml.jar -version\n\n"
        "Amazon Linux 2:\n"
        "  sudo yum install -y java-17-amazon-corretto-headless wget\n"
        f"  wget -O /tmp/plantuml.jar \"{PLANTUML_JAR_URL}\"\n"
        "  export PLANTUML_JAR=/tmp/plantuml.jar\n"
        "  JAVA_TOOL_OPTIONS=\"-Djava.awt.headless=true\" java -jar /tmp/plantuml.jar -version\n\n"
        "Windows (PowerShell):\n"
        "  winget install EclipseAdoptium.Temurin.17.JRE\n"
        f"  Invoke-WebRequest -OutFile $env:TEMP\\plantuml.jar -Uri \"{PLANTUML_JAR_URL}\"\n"
        f"  $env:PLANTUML_JAR = \"{windows_temp}\"\n"
        f"  [Environment]::SetEnvironmentVariable('PLANTUML_JAR', '{windows_temp}', 'User')\n"
        "  $env:JAVA_TOOL_OPTIONS = '-Djava.awt.headless=true'\n"
        "  java -jar $env:TEMP\\plantuml.jar -version\n\n"
        "Manual render example:\n"
        "  JAVA_TOOL_OPTIONS=\"-Djava.awt.headless=true\" java -jar /tmp/plantuml.jar -tpng docs/diagrams/architecture.puml"
    )


def _candidate_jar_paths() -> list[str]:
    """Return candidate PlantUML jar locations in priority order."""

    candidates: list[str] = []

    env_jar = os.getenv("PLANTUML_JAR")
    if env_jar:
        candidates.append(env_jar)

    candidates.extend(JAR_SEARCH_PATHS)
    candidates.append(str(Path.home() / ".local" / "lib" / "plantuml.jar"))
    candidates.append(str(Path.cwd() / "plantuml.jar"))
    candidates.append(str(Path.cwd() / ".tools" / "plantuml.jar"))

    temp_dir = os.getenv("TEMP") or os.getenv("TMP")
    if temp_dir:
        candidates.append(str(Path(temp_dir) / "plantuml.jar"))

    if platform.system().lower().startswith("win"):
        local_app_data = os.getenv("LOCALAPPDATA")
        if local_app_data:
            candidates.append(str(Path(local_app_data) / "plantuml" / "plantuml.jar"))

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        if candidate and candidate not in seen:
            deduped.append(candidate)
            seen.add(candidate)
    return deduped