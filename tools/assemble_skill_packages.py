#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
PACKAGES_ROOT = REPO_ROOT / "packages" / "skills"
PRIVATE_RUNTIME_DIR = ".loom-runtime"
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
URL_SCHEMES = ("http://", "https://", "mailto:")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assemble single-skill Loom packages under packages/skills.",
    )
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="Only rebuild the selected skill id(s). Defaults to every public skill.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def copy_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        write_bytes(target, path.read_bytes())


def relative_posix(path: Path, start: Path) -> str:
    return Path(path.relative_to(start) if path.is_relative_to(start) else path).as_posix()


def sort_object(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sort_object(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [sort_object(item) for item in value]
    return value


def load_public_skills() -> list[dict[str, Any]]:
    registry = read_json(SKILLS_ROOT / "registry.json")
    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RuntimeError("skills/registry.json must declare a non-empty entries list")
    result: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        skill_id = entry.get("id")
        if not isinstance(skill_id, str) or not skill_id:
            continue
        skill_dir = SKILLS_ROOT / skill_id
        if not skill_dir.exists():
            raise RuntimeError(f"missing skill directory for `{skill_id}`: {skill_dir}")
        result.append(entry)
    return result


def source_runtime_script(skill_id: str) -> str:
    return "loom_init.py" if skill_id in {"loom-init", "loom-adopt"} else "loom_flow.py"


def top_level_wrapper(skill_id: str) -> str:
    runtime_script = source_runtime_script(skill_id)
    return (
        "#!/usr/bin/env python3\n"
        "from __future__ import annotations\n\n"
        "import os\n"
        "import runpy\n"
        "import sys\n"
        "from pathlib import Path\n\n"
        "SCRIPT_PATH = Path(__file__).resolve()\n"
        "PACKAGE_ROOT = SCRIPT_PATH.parents[1]\n"
        f"RUNTIME_ROOT = PACKAGE_ROOT / \"{PRIVATE_RUNTIME_DIR}\"\n\n"
        "os.environ.setdefault(\"LOOM_INSTALLED_SKILLS_ROOT\", str(RUNTIME_ROOT))\n"
        f"os.environ.setdefault(\"LOOM_PACKAGE_SKILL_ID\", \"{skill_id}\")\n"
        "sys.path.insert(0, str(RUNTIME_ROOT / \"shared/scripts\"))\n"
        f"runpy.run_path(RUNTIME_ROOT / \"shared/scripts/{runtime_script}\", run_name=\"__main__\")\n"
    )


def runtime_manifest_paths(skill_id: str) -> dict[Path, Path]:
    package_root = PACKAGES_ROOT / skill_id
    runtime_root = package_root / PRIVATE_RUNTIME_DIR
    skill_root = SKILLS_ROOT / skill_id

    mapping: dict[Path, Path] = {
        SKILLS_ROOT / "registry.json": runtime_root / "registry.json",
        SKILLS_ROOT / "install-layout.json": runtime_root / "install-layout.json",
        SKILLS_ROOT / "upgrade-contract.json": runtime_root / "upgrade-contract.json",
        SKILLS_ROOT / "route-matrix.md": runtime_root / "route-matrix.md",
        skill_root / "SKILL.md": runtime_root / skill_id / "SKILL.md",
        skill_root / "contract.json": runtime_root / skill_id / "contract.json",
        skill_root / "agents" / "openai.yaml": runtime_root / skill_id / "agents" / "openai.yaml",
    }

    for path in sorted((skill_root / "references").rglob("*")):
        if path.is_file():
            mapping[path] = runtime_root / skill_id / "references" / path.relative_to(skill_root / "references")

    if skill_id != "loom-init":
        init_refs_root = SKILLS_ROOT / "loom-init" / "references"
        for path in sorted(init_refs_root.rglob("*")):
            if path.is_file():
                mapping[path] = runtime_root / "loom-init" / "references" / path.relative_to(init_refs_root)
    return mapping


def top_level_doc_paths(skill_id: str) -> dict[Path, Path]:
    package_root = PACKAGES_ROOT / skill_id
    skill_root = SKILLS_ROOT / skill_id
    mapping: dict[Path, Path] = {
        skill_root / "SKILL.md": package_root / "SKILL.md",
        skill_root / "contract.json": package_root / "contract.json",
        skill_root / "agents" / "openai.yaml": package_root / "agents" / "openai.yaml",
        SKILLS_ROOT / "route-matrix.md": package_root / "references" / "route-matrix.md",
        SKILLS_ROOT / "registry.json": package_root / PRIVATE_RUNTIME_DIR / "registry.json",
        SKILLS_ROOT / "install-layout.json": package_root / PRIVATE_RUNTIME_DIR / "install-layout.json",
        SKILLS_ROOT / "upgrade-contract.json": package_root / PRIVATE_RUNTIME_DIR / "upgrade-contract.json",
    }

    for path in sorted((skill_root / "references").rglob("*")):
        if path.is_file():
            mapping[path] = package_root / "references" / path.relative_to(skill_root / "references")

    if skill_id != "loom-init":
        init_refs_root = SKILLS_ROOT / "loom-init" / "references"
        for path in sorted(init_refs_root.rglob("*")):
            if path.is_file():
                mapping[path] = package_root / "references" / "loom-init" / path.relative_to(init_refs_root)

    shared_refs_root = SKILLS_ROOT / "shared" / "references"
    for path in sorted(shared_refs_root.rglob("*")):
        if path.is_file():
            mapping[path] = package_root / "references" / "shared" / path.relative_to(shared_refs_root)

    return mapping


def rewrite_path_literals(text: str, source_path: Path, destination_path: Path, path_map: dict[Path, Path]) -> str:
    rewrites: list[tuple[str, str]] = []
    for source, mapped in path_map.items():
        expressions = {Path(os.path.relpath(source, source_path.parent)).as_posix()}
        if source.is_relative_to(SKILLS_ROOT):
            expressions.add((Path("skills") / source.relative_to(SKILLS_ROOT)).as_posix())
        replacement = Path(os.path.relpath(mapped, destination_path.parent)).as_posix()
        rewrites.extend((expression, replacement) for expression in expressions if expression and expression != ".")

    for expression, replacement in sorted(rewrites, key=lambda item: len(item[0]), reverse=True):
        text = text.replace(expression, replacement)
    return text


def rewrite_markdown_links(text: str, source_path: Path, destination_path: Path, path_map: dict[Path, Path]) -> str:
    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2)
        if target.startswith("#") or target.startswith(URL_SCHEMES):
            return match.group(0)
        anchor = ""
        target_path = target
        if "#" in target:
            target_path, anchor = target.split("#", 1)
            anchor = f"#{anchor}"
        if not target_path:
            return match.group(0)
        candidate = (source_path.parent / target_path).resolve()
        mapped = path_map.get(candidate)
        if mapped is None:
            return match.group(0)
        rewritten = Path(os.path.relpath(mapped, destination_path.parent)).as_posix()
        return f"[{label}]({rewritten}{anchor})"

    return rewrite_path_literals(MARKDOWN_LINK_RE.sub(replace, text), source_path, destination_path, path_map)


def rewrite_json_paths(value: Any, source_anchor: Path, destination_anchor: Path, path_map: dict[Path, Path]) -> Any:
    if isinstance(value, dict):
        return {key: rewrite_json_paths(item, source_anchor, destination_anchor, path_map) for key, item in value.items()}
    if isinstance(value, list):
        return [rewrite_json_paths(item, source_anchor, destination_anchor, path_map) for item in value]
    if not isinstance(value, str):
        return value
    if value.startswith(URL_SCHEMES) or value.startswith("#"):
        return value
    candidate = (source_anchor / value).resolve()
    mapped = path_map.get(candidate)
    if mapped is None:
        return value
    return Path(os.path.relpath(mapped, destination_anchor)).as_posix()


def filtered_install_layout(skill_id: str, all_skill_ids: set[str]) -> dict[str, Any]:
    layout = read_json(SKILLS_ROOT / "install-layout.json")
    required = layout.get("required_paths")
    if not isinstance(required, list):
        raise RuntimeError("skills/install-layout.json missing required_paths")

    filtered: list[str] = []
    for entry in required:
        if not isinstance(entry, str):
            continue
        top_level = entry.split("/", 1)[0]
        if top_level in all_skill_ids and top_level != skill_id:
            continue
        if entry.startswith(tuple(f"{other}/" for other in all_skill_ids if other != skill_id)):
            continue
        filtered.append(entry)

    layout["required_paths"] = filtered
    return sort_object(layout)


def filtered_registry(skill_entry: dict[str, Any], skill_id: str) -> dict[str, Any]:
    registry = read_json(SKILLS_ROOT / "registry.json")
    registry["root_entry"] = skill_id
    registry["entries"] = [sort_object(skill_entry)]
    return sort_object(registry)


def filtered_upgrade_contract(skill_entry: dict[str, Any], skill_id: str) -> dict[str, Any]:
    upgrade_contract = read_json(SKILLS_ROOT / "upgrade-contract.json")
    upgrade_contract["root_entry"] = skill_id
    upgrade_contract["current_contract_version"] = skill_entry.get("contract_version")
    return sort_object(upgrade_contract)


def visible_contract(skill_id: str, path_map: dict[Path, Path]) -> dict[str, Any]:
    contract_path = SKILLS_ROOT / skill_id / "contract.json"
    contract = read_json(contract_path)
    rewritten = rewrite_json_paths(contract, contract_path.parent, (PACKAGES_ROOT / skill_id), path_map)
    return sort_object(rewritten)


def runtime_contract(skill_id: str) -> dict[str, Any]:
    contract_path = SKILLS_ROOT / skill_id / "contract.json"
    contract = read_json(contract_path)
    contract["root_entry"] = True
    return sort_object(contract)


def patched_governance_surface() -> str:
    source = (SKILLS_ROOT / "shared" / "scripts" / "governance_surface.py").read_text(encoding="utf-8")
    source = source.replace(
        "from runtime_paths import installed_skill_script\n",
        "from runtime_paths import installed_skill_script\n\n\n"
        "def installed_skill_script_or_unknown(skill_id: str) -> Path | None:\n"
        "    try:\n"
        "        return installed_skill_script(__file__, skill_id)\n"
        "    except RuntimeError:\n"
        "        return None\n",
    )
    source = source.replace(
        "        return f\"python3 {installed_skill_script(__file__, 'loom-init')}\"\n",
        "        script = installed_skill_script_or_unknown('loom-init')\n"
        "        return f\"python3 {script}\" if script is not None else \"unknown\"\n",
    )
    source = source.replace(
        "        return f\"python3 {installed_skill_script(__file__, 'loom-resume')}\"\n",
        "        script = installed_skill_script_or_unknown('loom-resume')\n"
        "        return f\"python3 {script}\" if script is not None else \"unknown\"\n",
    )
    source = source.replace(
        "        return f\"python3 {installed_skill_script(__file__, 'loom-init')} verify --target <repo>\"\n",
        "        script = installed_skill_script_or_unknown('loom-init')\n"
        "        return f\"python3 {script} verify --target <repo>\" if script is not None else \"unknown\"\n",
    )
    return source


def assemble_visible_surface(skill_id: str, path_map: dict[Path, Path]) -> None:
    package_root = PACKAGES_ROOT / skill_id
    skill_root = SKILLS_ROOT / skill_id

    top_skill_path = package_root / "SKILL.md"
    skill_text = rewrite_markdown_links(
        (skill_root / "SKILL.md").read_text(encoding="utf-8"),
        skill_root / "SKILL.md",
        top_skill_path,
        path_map,
    )
    write_text(top_skill_path, skill_text)
    write_json(package_root / "contract.json", visible_contract(skill_id, path_map))
    write_text(package_root / "agents" / "openai.yaml", (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    write_text(package_root / "scripts" / f"{skill_id}.py", top_level_wrapper(skill_id))

    for source, destination in sorted(path_map.items()):
        if source in {
            skill_root / "SKILL.md",
            skill_root / "contract.json",
            skill_root / "agents" / "openai.yaml",
            SKILLS_ROOT / "registry.json",
            SKILLS_ROOT / "install-layout.json",
            SKILLS_ROOT / "upgrade-contract.json",
        }:
            continue
        if source.suffix != ".md":
            write_bytes(destination, source.read_bytes())
            continue
        write_text(
            destination,
            rewrite_markdown_links(source.read_text(encoding="utf-8"), source, destination, path_map),
        )


def assemble_private_runtime(skill_entry: dict[str, Any], all_skill_ids: set[str]) -> None:
    skill_id = skill_entry["id"]
    package_root = PACKAGES_ROOT / skill_id
    runtime_root = package_root / PRIVATE_RUNTIME_DIR
    skill_root = SKILLS_ROOT / skill_id

    copy_tree(SKILLS_ROOT / "shared" / "assets", runtime_root / "shared" / "assets")
    copy_tree(SKILLS_ROOT / "shared" / "references", runtime_root / "shared" / "references")
    copy_tree(SKILLS_ROOT / "shared" / "scripts", runtime_root / "shared" / "scripts")
    copy_tree(skill_root / "references", runtime_root / skill_id / "references")
    if skill_id != "loom-init":
        copy_tree(SKILLS_ROOT / "loom-init" / "references", runtime_root / "loom-init" / "references")
    write_bytes(runtime_root / "route-matrix.md", (SKILLS_ROOT / "route-matrix.md").read_bytes())
    write_text(runtime_root / skill_id / "SKILL.md", (skill_root / "SKILL.md").read_text(encoding="utf-8"))
    write_text(runtime_root / skill_id / "agents" / "openai.yaml", (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    write_json(runtime_root / skill_id / "contract.json", runtime_contract(skill_id))
    write_text(
        runtime_root / skill_id / "scripts" / f"{skill_id}.py",
        (skill_root / "scripts" / f"{skill_id}.py").read_text(encoding="utf-8"),
    )
    write_json(runtime_root / "registry.json", filtered_registry(skill_entry, skill_id))
    write_json(runtime_root / "install-layout.json", filtered_install_layout(skill_id, all_skill_ids))
    write_json(runtime_root / "upgrade-contract.json", filtered_upgrade_contract(skill_entry, skill_id))
    write_text(runtime_root / "shared" / "scripts" / "governance_surface.py", patched_governance_surface())


def reset_output_root(selected_skill_ids: set[str] | None) -> None:
    PACKAGES_ROOT.mkdir(parents=True, exist_ok=True)
    if selected_skill_ids is None:
        shutil.rmtree(PACKAGES_ROOT)
        PACKAGES_ROOT.mkdir(parents=True, exist_ok=True)
        return
    for skill_id in sorted(selected_skill_ids):
        target = PACKAGES_ROOT / skill_id
        if target.exists():
            shutil.rmtree(target)


def assemble(skill_entries: list[dict[str, Any]], selected_skill_ids: set[str] | None = None) -> list[str]:
    all_skill_ids = {entry["id"] for entry in skill_entries if isinstance(entry.get("id"), str)}
    reset_output_root(selected_skill_ids)
    built: list[str] = []
    for skill_entry in skill_entries:
        skill_id = skill_entry["id"]
        if selected_skill_ids is not None and skill_id not in selected_skill_ids:
            continue
        package_root = PACKAGES_ROOT / skill_id
        package_root.mkdir(parents=True, exist_ok=True)
        path_map = {**runtime_manifest_paths(skill_id), **top_level_doc_paths(skill_id)}
        assemble_visible_surface(skill_id, path_map)
        assemble_private_runtime(skill_entry, all_skill_ids)
        built.append(skill_id)
    return built


def main() -> int:
    args = parse_args()
    skill_entries = load_public_skills()
    available = {entry["id"] for entry in skill_entries}
    selected: set[str] | None = None
    if args.skills:
        selected = set(args.skills)
        unknown = sorted(selected - available)
        if unknown:
            raise RuntimeError("unknown skill ids: " + ", ".join(unknown))

    built = assemble(skill_entries, selected_skill_ids=selected)
    print(json.dumps({"built_packages": built, "output_root": str(PACKAGES_ROOT)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
