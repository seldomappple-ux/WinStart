from __future__ import annotations

import copy
import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from importlib import resources
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from . import __version__

KNOWN_ADAPTERS = {"copilot", "cursor", "claude", "gemini", "opencode"}
KNOWN_PROJECT_TYPES = {"governance", "embedded"}
SYNC_STRATEGIES = {"incremental", "full", "manual"}
DOC_MODES = {"zh", "en", "bilingual"}
ACTIVE_PROGRESS_STATUSES = {"draft", "promotable"}
ALL_PROGRESS_STATUSES = ACTIVE_PROGRESS_STATUSES | {"upstreamed"}
FRONTMATTER_DELIMITER = "---"
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
EMBEDDED_REQUIRED_DOCS = (
    "README.md",
    "docs/DEVELOPMENT_PLAN.md",
    "docs/DELTA_DECISIONS.md",
    "docs/PROTOCOL_SPEC.md",
    "docs/HARDWARE_BRINGUP.md",
    "docs/NEXT_ITERATION_BASELINE.md",
    "docs/VALIDATION_PLAN.md",
    "docs/schema/protocol.schema.json",
)
EMBEDDED_README_LINKS = (
    "docs/DEVELOPMENT_PLAN.md",
    "docs/DELTA_DECISIONS.md",
    "docs/PROTOCOL_SPEC.md",
    "docs/HARDWARE_BRINGUP.md",
    "docs/NEXT_ITERATION_BASELINE.md",
    "docs/VALIDATION_PLAN.md",
)


class GovernanceError(RuntimeError):
    """Raised when the governance workflow detects an invalid project state."""


@dataclass(frozen=True)
class ReleaseManifest:
    repo: str
    version: str
    published_at: str


@dataclass(frozen=True)
class ProgressEntry:
    path: Path
    page_id: str
    entry_date: str
    title: str
    status: str
    related_commit_message: str
    related_commit_hash: str
    upstream_reference: str
    keywords: list[str]
    body: str


@dataclass(frozen=True)
class ArchitectureDecision:
    decision_id: str
    title: str
    status: str
    summary: str


RESOURCE_ROOT = resources.files("vibe_governance").joinpath("resources")
TEMPLATE_ROOT = Path(str(RESOURCE_ROOT.joinpath("templates")))
SCAFFOLD_ROOT = Path(str(RESOURCE_ROOT.joinpath("scaffold")))
ENVIRONMENT = Environment(
    loader=FileSystemLoader(str(TEMPLATE_ROOT)),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def _resource_text(relative_path: str) -> str:
    return RESOURCE_ROOT.joinpath(relative_path).read_text(encoding="utf-8")


def _load_resource_yaml(relative_path: str) -> dict[str, Any]:
    return yaml.safe_load(_resource_text(relative_path))


def _load_yaml_file(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        if default is None:
            raise GovernanceError(f"Missing required file: {path}")
        return copy.deepcopy(default)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or copy.deepcopy(default) or {}


def _write_yaml_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _load_release_manifest() -> ReleaseManifest:
    data = _load_resource_yaml("release-manifest.yaml")
    return ReleaseManifest(
        repo=str(data["repo"]),
        version=str(data["version"]),
        published_at=str(data["published_at"]),
    )


def _load_catalog() -> dict[str, Any]:
    return _load_resource_yaml("rule-catalog.yaml")


def _read_scaffold(relative_path: str) -> str:
    return SCAFFOLD_ROOT.joinpath(relative_path).read_text(encoding="utf-8")


def _profile_path(target: Path) -> Path:
    return target / ".agents" / "profile.yaml"


def _rules_path(target: Path) -> Path:
    return target / ".agents" / "RULES.md"


def _overrides_path(target: Path) -> Path:
    return target / ".agents" / "overrides" / "rules.yaml"


def _decisions_path(target: Path) -> Path:
    return target / ".agents" / "architecture-decisions.yaml"


def _progress_index_path(target: Path) -> Path:
    return target / ".agents" / "PROGRESS.md"


def _progress_entries_dir(target: Path) -> Path:
    return target / ".agents" / "progress" / "entries"


def _progress_archived_dir(target: Path) -> Path:
    return target / ".agents" / "progress" / "archived"


def _entry_template_path(target: Path) -> Path:
    return target / ".agents" / "progress" / "ENTRY_TEMPLATE.md"


def _managed_dir(target: Path) -> Path:
    return target / ".agents" / ".managed"


def _snapshot_path(target: Path) -> Path:
    return _managed_dir(target) / "upstream-rule-catalog.yaml"


def _manifest_path(target: Path) -> Path:
    return _managed_dir(target) / "generated-manifest.yaml"


def _load_profile(target: Path) -> dict[str, Any]:
    return _load_yaml_file(_profile_path(target))


def _next_cleanup_version(project_version: str, iteration_window: int = 2) -> str:
    if not SEMVER_PATTERN.fullmatch(project_version):
        return project_version
    major, minor, _patch = (int(part) for part in project_version.split("."))
    return f"{major}.{minor + iteration_window}.0"


def _apply_scaffold_tokens(content: str, manifest: ReleaseManifest, project_version: str) -> str:
    return (
        content.replace("__UPSTREAM_REPO__", manifest.repo)
        .replace("__UPSTREAM_VERSION__", manifest.version)
        .replace("__PROJECT_VERSION__", project_version)
        .replace("__NEXT_CLEANUP_VERSION__", _next_cleanup_version(project_version))
    )


def _embedded_profile_defaults() -> dict[str, Any]:
    return {
        "communication_mode": "decide-before-development",
        "concurrency_model": "async",
        "module_layout": {
            "c_dir": "src",
            "h_dir": "lib",
            "paired_module_files": True,
        },
        "hardware": {
            "baud_rate": 115200,
            "wifi_band": "2.4GHz",
            "ip_strategy": "decide-before-development",
            "pin_map": "document-in-docs/HARDWARE_BRINGUP.md",
            "onboard_led": "document-in-docs/HARDWARE_BRINGUP.md",
            "flashing_interface": "document-in-docs/HARDWARE_BRINGUP.md",
            "threshold_calibration": "document-in-docs/HARDWARE_BRINGUP.md",
        },
    }


def _markdown_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith(f"{FRONTMATTER_DELIMITER}\n"):
        return {}
    _, rest = text.split(f"{FRONTMATTER_DELIMITER}\n", 1)
    marker = f"\n{FRONTMATTER_DELIMITER}\n"
    if marker not in rest:
        return {}
    metadata_text, _ = rest.split(marker, 1)
    return yaml.safe_load(metadata_text) or {}


def _load_overrides(target: Path) -> list[dict[str, Any]]:
    data = _load_yaml_file(_overrides_path(target), default={"overrides": []})
    overrides = data.get("overrides", [])
    if not isinstance(overrides, list):
        raise GovernanceError("`.agents/overrides/rules.yaml` must define an `overrides` list.")
    return overrides


def _load_decisions(target: Path) -> list[ArchitectureDecision]:
    data = _load_yaml_file(_decisions_path(target), default={"decisions": []})
    decisions: list[ArchitectureDecision] = []
    for raw in data.get("decisions", []):
        decisions.append(
            ArchitectureDecision(
                decision_id=str(raw["id"]),
                title=str(raw["title"]),
                status=str(raw["status"]),
                summary=str(raw["summary"]),
            )
        )
    return decisions


def _validate_profile(profile: dict[str, Any], catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_fields = {
        "project_type",
        "project_version",
        "project_lang",
        "comment_lang",
        "doc_mode",
        "agent_adapters",
        "upstream",
        "override_whitelist",
        "mcp",
    }
    missing = sorted(required_fields - set(profile))
    if missing:
        errors.append(f"Missing profile fields: {', '.join(missing)}")

    project_type = str(profile.get("project_type", "")).strip()
    if project_type not in KNOWN_PROJECT_TYPES:
        errors.append("`project_type` must be one of: embedded, governance")

    project_version = str(profile.get("project_version", "")).strip()
    if not project_version:
        errors.append("`project_version` is required.")
    elif not SEMVER_PATTERN.fullmatch(project_version):
        errors.append("`project_version` must use `major.minor.patch` format, for example `1.0.0`.")

    adapters = profile.get("agent_adapters", [])
    if not isinstance(adapters, list):
        errors.append("`agent_adapters` must be a list.")
    else:
        unknown_adapters = sorted(set(adapters) - KNOWN_ADAPTERS)
        if unknown_adapters:
            errors.append(f"Unknown adapters: {', '.join(unknown_adapters)}")

    upstream = profile.get("upstream", {})
    if not isinstance(upstream, dict):
        errors.append("`upstream` must be a mapping.")
    else:
        for field in ("repo", "version", "sync_strategy"):
            if field not in upstream or not str(upstream[field]).strip():
                errors.append(f"`upstream.{field}` is required.")
        if upstream.get("sync_strategy") not in SYNC_STRATEGIES:
            errors.append(
                "`upstream.sync_strategy` must be one of: "
                + ", ".join(sorted(SYNC_STRATEGIES))
            )

    doc_mode = str(profile.get("doc_mode", "")).strip()
    if doc_mode not in DOC_MODES:
        errors.append("`doc_mode` must be one of: bilingual, en, zh")

    whitelist = profile.get("override_whitelist", [])
    if not isinstance(whitelist, list):
        errors.append("`override_whitelist` must be a list.")
    else:
        rule_ids = {rule["rule_id"] for rule in catalog["rules"]}
        unknown_whitelist = [item for item in whitelist if item not in rule_ids]
        if unknown_whitelist:
            errors.append(
                "Unknown override_whitelist rules: " + ", ".join(sorted(unknown_whitelist))
            )

    mcp = profile.get("mcp", {})
    if not isinstance(mcp, dict):
        errors.append("`mcp` must be a mapping.")
    else:
        for field in ("enabled", "config_path", "allowed_tools"):
            if field not in mcp:
                errors.append(f"`mcp.{field}` is required.")
        if "enabled" in mcp and not isinstance(mcp["enabled"], bool):
            errors.append("`mcp.enabled` must be true or false.")
        if "allowed_tools" in mcp and not isinstance(mcp["allowed_tools"], list):
            errors.append("`mcp.allowed_tools` must be a list.")

    if project_type == "embedded":
        embedded = profile.get("embedded")
        if not isinstance(embedded, dict):
            errors.append("`embedded` is required when `project_type` is `embedded`.")
            return errors

        for field in ("communication_mode", "concurrency_model", "module_layout", "hardware"):
            if field not in embedded:
                errors.append(f"`embedded.{field}` is required.")

        module_layout = embedded.get("module_layout", {})
        if not isinstance(module_layout, dict):
            errors.append("`embedded.module_layout` must be a mapping.")
        else:
            for field in ("c_dir", "h_dir", "paired_module_files"):
                if field not in module_layout:
                    errors.append(f"`embedded.module_layout.{field}` is required.")
            if "paired_module_files" in module_layout and not isinstance(
                module_layout["paired_module_files"], bool
            ):
                errors.append("`embedded.module_layout.paired_module_files` must be true or false.")

        hardware = embedded.get("hardware", {})
        if not isinstance(hardware, dict):
            errors.append("`embedded.hardware` must be a mapping.")
        else:
            for field in (
                "baud_rate",
                "wifi_band",
                "ip_strategy",
                "pin_map",
                "onboard_led",
                "flashing_interface",
                "threshold_calibration",
            ):
                if field not in hardware:
                    errors.append(f"`embedded.hardware.{field}` is required.")

    return errors


def _validate_overrides(
    profile: dict[str, Any],
    catalog: dict[str, Any],
    overrides: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    whitelist = set(profile.get("override_whitelist", []))
    rules_by_id = {rule["rule_id"]: rule for rule in catalog["rules"]}
    seen: set[tuple[str, tuple[str, ...]]] = set()

    for override in overrides:
        rule_id = str(override.get("rule_id", "")).strip()
        if not rule_id:
            errors.append("Override entries must define `rule_id`.")
            continue
        if rule_id not in rules_by_id:
            errors.append(f"Override references unknown rule `{rule_id}`.")
            continue
        rule = rules_by_id[rule_id]
        if rule_id not in whitelist:
            errors.append(f"Override for `{rule_id}` is not allowed by `override_whitelist`.")
        if bool(rule.get("immutable")):
            errors.append(f"Override for `{rule_id}` is forbidden because the rule is immutable.")
        body = str(override.get("body", "")).strip()
        if not body:
            errors.append(f"Override for `{rule_id}` must define a non-empty `body`.")
        adapters = override.get("adapters", rule.get("adapters", []))
        if not isinstance(adapters, list):
            errors.append(f"Override for `{rule_id}` must use a list for `adapters`.")
            continue
        adapter_set = tuple(sorted(str(item) for item in adapters))
        if set(adapter_set) - KNOWN_ADAPTERS:
            unknown = sorted(set(adapter_set) - KNOWN_ADAPTERS)
            errors.append(f"Override for `{rule_id}` references unknown adapters: {', '.join(unknown)}")
        invalid_targets = sorted(set(adapter_set) - set(rule.get("adapters", [])))
        if invalid_targets:
            errors.append(
                f"Override for `{rule_id}` cannot target adapters outside the source rule: "
                + ", ".join(invalid_targets)
            )
        key = (rule_id, adapter_set)
        if key in seen:
            errors.append(
                f"Duplicate override detected for `{rule_id}` and adapters `{', '.join(adapter_set)}`."
            )
        seen.add(key)

    return errors


def _load_entry(entry_path: Path) -> ProgressEntry:
    text = entry_path.read_text(encoding="utf-8")
    if not text.startswith(f"{FRONTMATTER_DELIMITER}\n"):
        raise GovernanceError(f"Progress entry lacks YAML front matter: {entry_path}")
    _, rest = text.split(f"{FRONTMATTER_DELIMITER}\n", 1)
    metadata_text, body = rest.split(f"\n{FRONTMATTER_DELIMITER}\n", 1)
    metadata = yaml.safe_load(metadata_text) or {}
    required_fields = ("page_id", "date", "title", "status", "related_commit_message")
    missing = [field for field in required_fields if not metadata.get(field)]
    if missing:
        raise GovernanceError(
            f"Progress entry {entry_path} is missing required fields: {', '.join(missing)}"
        )
    status = str(metadata["status"])
    if status not in ALL_PROGRESS_STATUSES:
        raise GovernanceError(f"Invalid progress status `{status}` in {entry_path}")
    date.fromisoformat(str(metadata["date"]))
    keywords = metadata.get("keywords", [])
    if not isinstance(keywords, list):
        raise GovernanceError(f"`keywords` must be a list in {entry_path}")

    return ProgressEntry(
        path=entry_path,
        page_id=str(metadata["page_id"]),
        entry_date=str(metadata["date"]),
        title=str(metadata["title"]),
        status=status,
        related_commit_message=str(metadata["related_commit_message"]),
        related_commit_hash=str(metadata.get("related_commit_hash", "")),
        upstream_reference=str(metadata.get("upstream_reference", "")),
        keywords=[str(item) for item in keywords],
        body=body.strip(),
    )


def _serialize_entry(entry: ProgressEntry) -> str:
    metadata = {
        "page_id": entry.page_id,
        "date": entry.entry_date,
        "title": entry.title,
        "status": entry.status,
        "related_commit_message": entry.related_commit_message,
        "related_commit_hash": entry.related_commit_hash,
        "upstream_reference": entry.upstream_reference,
        "keywords": entry.keywords,
    }
    metadata_text = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True).strip()
    return (
        f"{FRONTMATTER_DELIMITER}\n"
        f"{metadata_text}\n"
        f"{FRONTMATTER_DELIMITER}\n"
        f"{entry.body.strip()}\n"
    )


def _load_entries(target: Path) -> list[ProgressEntry]:
    entries: list[ProgressEntry] = []
    for base in (_progress_entries_dir(target), _progress_archived_dir(target)):
        if not base.exists():
            continue
        for entry_path in sorted(base.rglob("*.md")):
            if entry_path.name in {"ENTRY_TEMPLATE.md", "README_中文.md"}:
                continue
            entries.append(_load_entry(entry_path))
    entries.sort(key=lambda item: (item.entry_date, item.page_id), reverse=True)
    return entries


def _validate_embedded_docs(target: Path, profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    project_version = str(profile["project_version"]).strip()

    for relative_path in EMBEDDED_REQUIRED_DOCS:
        path = target / relative_path
        if not path.exists():
            errors.append(f"Embedded project is missing required file: {path}")

    readme_path = target / "README.md"
    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        for link in EMBEDDED_README_LINKS:
            if link not in readme_text:
                errors.append(f"Embedded README must link to `{link}`.")

    validation_plan = target / "docs" / "VALIDATION_PLAN.md"
    if validation_plan.exists():
        validation_text = validation_plan.read_text(encoding="utf-8")
        for phase in ("## M0", "## M1", "## M2", "## M3"):
            if phase not in validation_text:
                errors.append(f"`docs/VALIDATION_PLAN.md` must include `{phase}`.")

    docs_with_iteration_headers = (
        target / "docs" / "DELTA_DECISIONS.md",
        target / "docs" / "NEXT_ITERATION_BASELINE.md",
    )
    for path in docs_with_iteration_headers:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in ("current_iteration:", "current_repo_version:"):
            if marker not in text:
                errors.append(f"`{path}` must include `{marker}`.")

    versioned_markdown_paths = (
        target / "docs" / "PROTOCOL_SPEC.md",
        target / "docs" / "VALIDATION_PLAN.md",
    )
    for path in versioned_markdown_paths:
        if not path.exists():
            continue
        metadata = _markdown_frontmatter(path)
        if str(metadata.get("project_version", "")).strip() != project_version:
            errors.append(f"`{path}` must declare `project_version: {project_version}` in front matter.")

    schema_path = target / "docs" / "schema" / "protocol.schema.json"
    if schema_path.exists():
        schema_data = yaml.safe_load(schema_path.read_text(encoding="utf-8")) or {}
        if str(schema_data.get("project_version", "")).strip() != project_version:
            errors.append(f"`{schema_path}` must define `project_version: {project_version}`.")

    # UTF-8 encoding validation
    critical_files = [
        target / ".agents" / "profile.yaml",
        target / ".agents" / "RULES.md",
        target / "README.md",
        target / "docs" / "PROTOCOL_SPEC.md",
        target / "docs" / "VALIDATION_PLAN.md",
    ]
    for path in critical_files:
        if not path.exists():
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"File is not valid UTF-8: {path}")

    return errors


def _relative_to_target(target: Path, path: Path) -> str:
    return path.resolve().relative_to(target.resolve()).as_posix()


def _metadata_comment(manifest: ReleaseManifest, checksum: str) -> str:
    return (
        "<!--\n"
        f"managed-by: vibe-governance {__version__}\n"
        f"upstream-repo: {manifest.repo}\n"
        f"upstream-version: {manifest.version}\n"
        f"upstream-published-at: {manifest.published_at}\n"
        f"checksum-sha256: {checksum}\n"
        "managed-note-en: DO NOT EDIT DIRECTLY. Regenerate with `vibe-governance render`.\n"
        "managed-note-zh: 请勿直接编辑此文件, 请运行 `vibe-governance render` 重新生成.\n"
        "-->\n"
    )


def _wrap_managed_content(raw_content: str, manifest: ReleaseManifest) -> tuple[str, str]:
    body = raw_content.rstrip() + "\n"
    checksum = hashlib.sha256(body.encode("utf-8")).hexdigest()
    metadata = _metadata_comment(manifest, checksum)
    if body.startswith("---\n"):
        closing = body.find("\n---\n", 4)
        if closing != -1:
            insert_at = closing + len("\n---\n")
            body = body[:insert_at] + metadata + body[insert_at:]
            return body, checksum
    return metadata + body, checksum


def _managed_targets(profile: dict[str, Any]) -> list[tuple[Path, str, str]]:
    targets: list[tuple[Path, str, str]] = [
        (Path("AGENTS.md"), "AGENTS.md.j2", "root"),
        (_progress_index_path(Path(".")), "PROGRESS.md", "progress"),
    ]

    adapters = set(profile["agent_adapters"])
    if "copilot" in adapters:
        targets.append((Path(".github/copilot-instructions.md"), "copilot-instructions.md.j2", "copilot"))
        targets.append(
            (
                Path(".github/instructions/project-governance.instructions.md"),
                "github-instructions.md.j2",
                "copilot",
            )
        )
    if "cursor" in adapters:
        targets.append((Path(".cursor/rules/governance.mdc"), "cursor-governance.mdc.j2", "cursor"))
    if "claude" in adapters:
        targets.append((Path("CLAUDE.md"), "CLAUDE.md.j2", "claude"))
    if "gemini" in adapters:
        targets.append((Path("GEMINI.md"), "GEMINI.md.j2", "gemini"))
    if "opencode" in adapters:
        targets.append((Path(".opencode/AGENTS.md"), "opencode-AGENTS.md.j2", "opencode"))
    return targets


def _effective_rule_for_adapter(
    rule: dict[str, Any],
    adapter: str,
    profile: dict[str, Any],
    overrides: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if adapter not in set(rule.get("adapters", [])):
        return None
    if bool(rule.get("requires_mcp")) and not profile["mcp"]["enabled"]:
        return None

    effective = copy.deepcopy(rule)
    for override in overrides:
        if override["rule_id"] != rule["rule_id"]:
            continue
        target_adapters = set(override.get("adapters", rule.get("adapters", [])))
        if adapter in target_adapters:
            effective["body"] = str(override["body"]).strip()
    return effective


def _rules_for_adapter(
    adapter: str,
    catalog: dict[str, Any],
    profile: dict[str, Any],
    overrides: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    for rule in sorted(catalog["rules"], key=lambda item: (int(item["priority"]), item["rule_id"])):
        effective = _effective_rule_for_adapter(rule, adapter, profile, overrides)
        if effective is not None:
            rules.append(effective)
    return rules


def _render_progress_markdown(
    target: Path,
    manifest: ReleaseManifest,
    profile: dict[str, Any],
    decisions: list[ArchitectureDecision],
    entries: list[ProgressEntry],
) -> tuple[str, str]:
    active_entries = [
        {
            "page_id": entry.page_id,
            "entry_date": entry.entry_date,
            "title": entry.title,
            "status": entry.status,
            "relative_path": _relative_to_target(target, entry.path),
            "related_commit_message": entry.related_commit_message,
        }
        for entry in entries
        if entry.status in ACTIVE_PROGRESS_STATUSES
    ][:10]
    template = ENVIRONMENT.get_template("PROGRESS.md.j2")
    body = template.render(
        profile=profile,
        target=str(target),
        active_entries=active_entries,
        decisions=decisions,
        archive_dir=".agents/progress/archived/",
        entries_dir=".agents/progress/entries/",
    )
    return _wrap_managed_content(body, manifest)


def _render_template(
    template_name: str,
    adapter: str,
    manifest: ReleaseManifest,
    target: Path,
    profile: dict[str, Any],
    catalog: dict[str, Any],
    overrides: list[dict[str, Any]],
) -> tuple[str, str]:
    template = ENVIRONMENT.get_template(template_name)
    sources = [
        ".agents/profile.yaml",
        ".agents/RULES.md",
        ".agents/overrides/rules.yaml",
        ".agents/architecture-decisions.yaml",
        ".agents/progress/entries/",
    ]
    body = template.render(
        manifest=manifest,
        profile=profile,
        rules=_rules_for_adapter(adapter, catalog, profile, overrides),
        known_sources=sources,
        target=str(target),
        is_bilingual=profile.get("doc_mode") == "bilingual",
    )
    return _wrap_managed_content(body, manifest)


def _expected_managed_outputs(target: Path) -> tuple[dict[str, str], dict[str, str]]:
    manifest = _load_release_manifest()
    catalog = _load_catalog()
    profile = _load_profile(target)
    overrides = _load_overrides(target)
    decisions = _load_decisions(target)
    entries = _load_entries(target)

    outputs: dict[str, str] = {}
    checksums: dict[str, str] = {}
    for rel_path, template_name, adapter in _managed_targets(profile):
        if adapter == "progress":
            content, checksum = _render_progress_markdown(target, manifest, profile, decisions, entries)
            actual_path = _progress_index_path(target)
        else:
            content, checksum = _render_template(
                template_name=template_name,
                adapter=adapter,
                manifest=manifest,
                target=target,
                profile=profile,
                catalog=catalog,
                overrides=overrides,
            )
            actual_path = target / rel_path
        outputs[str(actual_path.resolve())] = content
        checksums[str(actual_path.resolve())] = checksum
    return outputs, checksums


def init_project(
    target: Path,
    project_type: str = "governance",
    project_version: str | None = None,
) -> list[str]:
    manifest = _load_release_manifest()
    created: list[str] = []
    target.mkdir(parents=True, exist_ok=True)

    if project_type not in KNOWN_PROJECT_TYPES:
        raise GovernanceError(f"Unsupported project_type `{project_type}`. Expected one of: embedded, governance.")

    resolved_project_version = (project_version or manifest.version).strip()
    if not SEMVER_PATTERN.fullmatch(resolved_project_version):
        raise GovernanceError(
            "`project_version` must use `major.minor.patch` format, for example `1.0.0`."
        )

    directories = [
        target / ".agents",
        target / ".agents" / "overrides",
        _progress_entries_dir(target) / str(date.today().year),
        _progress_archived_dir(target) / str(date.today().year),
        _managed_dir(target),
    ]
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(str(directory))

    scaffold_files = {
        _profile_path(target): "profile.yaml",
        _rules_path(target): "RULES.md",
        target / ".agents" / "README_中文.md": "agents/README_中文.md",
        _overrides_path(target): "overrides/rules.yaml",
        target / ".agents" / "overrides" / "README_中文.md": "agents/overrides/README_中文.md",
        _decisions_path(target): "architecture-decisions.yaml",
        target / ".agents" / "progress" / "README_中文.md": "agents/progress/README_中文.md",
        target / ".agents" / "progress" / "entries" / "README_中文.md": "agents/progress/entries/README_中文.md",
        _entry_template_path(target): "progress/ENTRY_TEMPLATE.md",
        target / ".gitmessage": ".gitmessage",
    }
    for destination, source_name in scaffold_files.items():
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            content = _apply_scaffold_tokens(
                _read_scaffold(source_name),
                manifest,
                resolved_project_version,
            )
            if source_name == "profile.yaml":
                profile_data = yaml.safe_load(content) or {}
                profile_data["project_type"] = project_type
                profile_data["project_version"] = resolved_project_version
                if project_type == "embedded":
                    profile_data["embedded"] = _embedded_profile_defaults()
                destination.write_text(
                    yaml.safe_dump(profile_data, sort_keys=False, allow_unicode=True),
                    encoding="utf-8",
                )
            else:
                destination.write_text(content, encoding="utf-8")
            created.append(str(destination))

    if project_type == "embedded":
        embedded_scaffold_files = {
            target / "README.md": "embedded/README.md",
            target / "docs" / "README_中文.md": "embedded/docs/README_中文.md",
            target / "docs" / "DEVELOPMENT_PLAN.md": "embedded/docs/DEVELOPMENT_PLAN.md",
            target / "docs" / "DELTA_DECISIONS.md": "embedded/docs/DELTA_DECISIONS.md",
            target / "docs" / "PROTOCOL_SPEC.md": "embedded/docs/PROTOCOL_SPEC.md",
            target / "docs" / "HARDWARE_BRINGUP.md": "embedded/docs/HARDWARE_BRINGUP.md",
            target / "docs" / "NEXT_ITERATION_BASELINE.md": "embedded/docs/NEXT_ITERATION_BASELINE.md",
            target / "docs" / "VALIDATION_PLAN.md": "embedded/docs/VALIDATION_PLAN.md",
            target / "docs" / "schema" / "README_中文.md": "embedded/docs/schema/README_中文.md",
            target / "docs" / "schema" / "protocol.schema.json": "embedded/docs/schema/protocol.schema.json",
        }
        for destination, source_name in embedded_scaffold_files.items():
            if destination.exists():
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            content = _apply_scaffold_tokens(_read_scaffold(source_name), manifest, resolved_project_version)
            destination.write_text(content, encoding="utf-8")
            created.append(str(destination))

    if not _snapshot_path(target).exists():
        _write_yaml_file(_snapshot_path(target), _load_catalog())
        created.append(str(_snapshot_path(target)))

    # 配置 git commit template
    import subprocess
    try:
        subprocess.run(
            ["git", "config", "commit.template", ".gitmessage"],
            cwd=target,
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # Git 未安装或配置失败，不影响初始化

    return created


def render_project(target: Path) -> list[str]:
    validate_project(target, check_generated=False)
    outputs, checksums = _expected_managed_outputs(target)
    manifest = _load_release_manifest()
    written: list[str] = []

    for raw_path, content in outputs.items():
        path = Path(raw_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(str(path))

    manifest_data = {
        "managed_by": f"vibe-governance {__version__}",
        "upstream_repo": manifest.repo,
        "upstream_version": manifest.version,
        "upstream_published_at": manifest.published_at,
        "files": [
            {"path": _relative_to_target(target, Path(path)), "checksum": checksum}
            for path, checksum in sorted(checksums.items())
        ],
    }
    _write_yaml_file(_manifest_path(target), manifest_data)
    written.append(str(_manifest_path(target)))
    return written


def validate_project(target: Path, check_generated: bool = True) -> str:
    catalog = _load_catalog()
    profile = _load_profile(target)
    overrides = _load_overrides(target)

    errors = []
    errors.extend(_validate_profile(profile, catalog))
    errors.extend(_validate_overrides(profile, catalog, overrides))
    if profile.get("project_type") == "embedded":
        errors.extend(_validate_embedded_docs(target, profile))

    entries = _load_entries(target)
    for entry in entries:
        if not entry.related_commit_message.strip():
            errors.append(f"Progress entry missing related_commit_message: {entry.path}")
        if "archived" in entry.path.parts and entry.status != "upstreamed":
            errors.append(f"Archived entry must use `upstreamed` status: {entry.path}")

    if check_generated and _manifest_path(target).exists():
        outputs, _ = _expected_managed_outputs(target)
        manifest_data = _load_yaml_file(_manifest_path(target))
        manifest_files = {
            str((target / item["path"]).resolve()): item["checksum"]
            for item in manifest_data.get("files", [])
        }
        expected_paths = set(outputs)
        if expected_paths != set(manifest_files):
            errors.append("Managed output manifest does not match the expected adapter set.")
        for path_str, expected in outputs.items():
            path = Path(path_str)
            if not path.exists():
                errors.append(f"Missing managed output: {path}")
                continue
            actual = path.read_text(encoding="utf-8")
            if actual != expected:
                errors.append(
                    f"Managed output drift detected: {path}. "
                    "Do not edit generated files directly; regenerate them instead."
                )

    if errors:
        raise GovernanceError("\n".join(errors))

    return "Validation passed."


def sync_project(target: Path, dry_run: bool = False) -> dict[str, Any]:
    validate_project(target)
    current_catalog = _load_catalog()
    snapshot = _load_yaml_file(_snapshot_path(target), default={"rules": []})
    current_rules = {rule["rule_id"]: rule for rule in current_catalog.get("rules", [])}
    previous_rules = {rule["rule_id"]: rule for rule in snapshot.get("rules", [])}
    changed_rule_ids = sorted(
        {
            *[rule_id for rule_id in current_rules if current_rules.get(rule_id) != previous_rules.get(rule_id)],
            *[rule_id for rule_id in previous_rules if current_rules.get(rule_id) != previous_rules.get(rule_id)],
        }
    )
    status = "clean" if not changed_rule_ids else "changes_detected"
    report = {
        "status": status,
        "changed_rule_ids": changed_rule_ids,
        "dry_run": dry_run,
    }
    if dry_run or not changed_rule_ids:
        return report

    _write_yaml_file(_snapshot_path(target), current_catalog)
    profile = _load_profile(target)
    manifest = _load_release_manifest()
    profile["upstream"]["repo"] = manifest.repo
    profile["upstream"]["version"] = manifest.version
    _write_yaml_file(_profile_path(target), profile)
    report["status"] = "synced"
    return report


def _resolve_entry_path(target: Path, entry: str) -> Path:
    entry_path = Path(entry)
    if not entry_path.is_absolute():
        entry_path = (target / entry_path).resolve()
    return entry_path


def promote_progress_entry(target: Path, entry: str) -> Path:
    entry_path = _resolve_entry_path(target, entry)
    parsed = _load_entry(entry_path)
    if parsed.status == "upstreamed":
        raise GovernanceError("Upstreamed entries cannot be promoted.")
    updated = ProgressEntry(
        path=entry_path,
        page_id=parsed.page_id,
        entry_date=parsed.entry_date,
        title=parsed.title,
        status="promotable",
        related_commit_message=parsed.related_commit_message,
        related_commit_hash=parsed.related_commit_hash,
        upstream_reference=parsed.upstream_reference,
        keywords=parsed.keywords,
        body=parsed.body,
    )
    entry_path.write_text(_serialize_entry(updated), encoding="utf-8")
    render_project(target)
    return entry_path


def archive_progress_entry(target: Path, entry: str, upstream_ref: str = "") -> Path:
    entry_path = _resolve_entry_path(target, entry)
    parsed = _load_entry(entry_path)
    destination = _progress_archived_dir(target) / entry_path.parent.name / entry_path.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    updated = ProgressEntry(
        path=destination,
        page_id=parsed.page_id,
        entry_date=parsed.entry_date,
        title=parsed.title,
        status="upstreamed",
        related_commit_message=parsed.related_commit_message,
        related_commit_hash=parsed.related_commit_hash,
        upstream_reference=upstream_ref or parsed.upstream_reference,
        keywords=parsed.keywords,
        body=parsed.body,
    )
    destination.write_text(_serialize_entry(updated), encoding="utf-8")
    if destination.resolve() != entry_path.resolve():
        entry_path.unlink()
    render_project(target)
    return destination
