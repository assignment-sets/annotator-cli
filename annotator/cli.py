import os
import sys
import json
import argparse
import pathspec
from typing import Any, Dict, List, Optional
from .core import annotate_project

CONFIG_NAME: str = ".annotator.json"
TEMPLATES_BASE: str = os.path.join(os.path.dirname(__file__), "templates")


def load_json(path: str) -> Dict[str, Any]:
    """Safe JSON loader."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def merge_configs(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Merges dictionaries and combines lists uniquely."""
    result: Dict[str, Any] = base.copy()
    for key, value in overlay.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = {**result[key], **value}
        elif (
            isinstance(value, list) and key in result and isinstance(result[key], list)
        ):
            result[key] = list(set(result[key] + value))
        else:
            result[key] = value
    return result


def get_config(root: str) -> Dict[str, Any]:
    """Loads default, then templates, then local config."""
    user_config: Dict[str, Any] = load_json(os.path.join(root, CONFIG_NAME))

    final_config: Dict[str, Any] = {}
    # Default is always the starting point
    template_names: List[str] = user_config.get("templates", ["default"])

    for name in template_names:
        t_path: str = os.path.join(TEMPLATES_BASE, f"{name}.json")
        final_config = merge_configs(final_config, load_json(t_path))

    # User's local .annotator.json overrides everything
    return merge_configs(final_config, user_config)


def get_spec(root: str) -> Optional[pathspec.PathSpec]:
    """Parses .gitignore using pathspec."""
    git_path: str = os.path.join(root, ".gitignore")
    if not os.path.exists(git_path):
        return None
    try:
        with open(git_path, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Recursive File Annotator")
    parser.add_argument("path", nargs="?", default=".", help="Project root")
    args = parser.parse_args()

    root: str = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"[ERROR] Directory not found: {root}")
        sys.exit(1)

    config: Dict[str, Any] = get_config(root)
    spec: Optional[pathspec.PathSpec] = get_spec(root)

    print(f"[START] Root: {root}")
    annotate_project(root, config, spec)


if __name__ == "__main__":
    main()
