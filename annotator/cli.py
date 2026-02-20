import os
import sys
import json
import argparse
from typing import Any, Dict, List, Optional
import pathspec

from .core import annotate_project

CONFIG_NAME: str = ".annotator.jsonc"
TEMPLATES_BASE: str = os.path.join(os.path.dirname(__file__), "templates")

# The exact template with comments for the --init command
INIT_CONFIG_CONTENT = """{
  // List of templates to apply (keeping default as is always recommended)
  // Add more templates in the list
  // existing templates can be seen here `https://github.com/assignment-sets/annotator-cli`
  "templates": ["default"],

  // Behavior settings
  "settings": {
    "max_recursive_depth": 10,      // How deep to recurse into folders
    "max_num_of_files": 1000,       // Maximum files to process
    "max_file_size_kb": 512         // Skip files larger than this
  },

  // Override comment styles for specific extensions
  // Example: ".kt": "//", ".scala": "//"
  "comment_styles": {},

  // Additional file extensions to exclude (beyond defaults)
  // Example: [".txt", ".log"]
  // keeping existing items is prefered
  "exclude_extensions": [".log", ".cache"],

  // Additional directories to exclude (supports nested paths)
  // Example: ["temp", "cache", "src/generated/proto"]
  // keeping existing items is prefered
  "exclude_dirs": ["node_modules", ".venv", "__pycache__", "dist", "build", "target", "bin", ".git"],

  // Additional specific file `names` to exclude [no support for nested paths]
  // Example: [".env.local", "config.json"]
  // keeping existing items is prefered
  "exclude_files": [".env", ".annotator.jsonc", ".gitignore"]
}
"""


def load_json_with_comments(path: str) -> Dict[str, Any]:
    """
    Loads JSONC (JSON with Comments) - supports // comments and trailing commas.
    """
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove single-line comments
        lines = content.split("\n")
        cleaned_lines = []
        for line in lines:
            # Find // that's not inside a string
            comment_pos = -1
            in_string = False
            escape_next = False

            for i, char in enumerate(line):
                if escape_next:
                    escape_next = False
                    continue
                if char == "\\":
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                if not in_string and i < len(line) - 1 and line[i : i + 2] == "//":
                    comment_pos = i
                    break

            if comment_pos >= 0:
                cleaned_lines.append(line[:comment_pos])
            else:
                cleaned_lines.append(line)

        content = "\n".join(cleaned_lines)

        # Remove trailing commas before } or ]
        import re

        content = re.sub(r",(\s*[}\]])", r"\1", content)

        data = json.loads(content)
        return data if isinstance(data, dict) else {}

    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed for {path}: {e}")
        print(f"[ERROR] Line {e.lineno}: {e.msg}")
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return {}


def load_template(path: str) -> Dict[str, Any]:
    """
    Loads a template JSON file. Templates should be pure JSON without comments.
    """
    if not os.path.exists(path):
        print(f"[ERROR] Template not found: {path}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print(f"[ERROR] Template {path} is not a JSON object")
                return {}
            return data
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in template {path}")
        print(f"[ERROR] Line {e.lineno}, Column {e.colno}: {e.msg}")
        return {}
    except Exception as e:
        print(f"[ERROR] Failed to load template {path}: {e}")
        return {}


def merge_configs(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges dictionaries and combines lists uniquely.
    Special handling: don't merge 'name' and 'templates' fields from templates.
    """
    if not base:
        return overlay.copy()

    result = base.copy()
    for key, value in overlay.items():
        # Skip 'name' field from templates (it's metadata, not config)
        if key == "name":
            continue

        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            # Deep merge dictionaries
            result[key] = {**result[key], **value}
        elif (
            isinstance(value, list) and key in result and isinstance(result[key], list)
        ):
            # Combine lists and remove duplicates
            result[key] = list(set(result[key] + value))
        else:
            result[key] = value
    return result


def get_config(root: str) -> Dict[str, Any]:
    """
    Loads default, then templates specified in user config,
    then applies local .annotator.json as the final override.
    """
    user_config: Dict[str, Any] = load_json_with_comments(
        os.path.join(root, CONFIG_NAME)
    )
    final_config: Dict[str, Any] = {}

    # Identify which templates to load (defaults to just "default")
    template_names: List[str] = user_config.get("templates", ["default"])

    print(f"[INFO] Loading templates: {template_names}")

    for name in template_names:
        t_path: str = os.path.join(TEMPLATES_BASE, f"{name}.json")
        print(f"[INFO] Attempting to load template: {t_path}")

        loaded_template = load_template(t_path)

        if loaded_template:
            print(f"[INFO] Successfully loaded template '{name}'")
            if "comment_styles" in loaded_template:
                print(
                    f"[INFO]   - {len(loaded_template.get('comment_styles', {}))} comment styles"
                )
            if "exclude_extensions" in loaded_template:
                print(
                    f"[INFO]   - {len(loaded_template.get('exclude_extensions', []))} excluded extensions"
                )
            if "exclude_files" in loaded_template:
                print(
                    f"[INFO]   - {len(loaded_template.get('exclude_files', []))} excluded files"
                )
            if "exclude_dirs" in loaded_template:
                print(
                    f"[INFO]   - {len(loaded_template.get('exclude_dirs', []))} excluded directories"
                )

            final_config = merge_configs(final_config, loaded_template)
        else:
            print(f"[ERROR] Failed to load template '{name}' from {t_path}")

    # Final override with user config (excluding 'templates' field)
    user_overrides = {k: v for k, v in user_config.items() if k != "templates"}
    final_config = merge_configs(final_config, user_overrides)

    # Final summary
    print("\n[CONFIG SUMMARY]")
    print(f"  Comment styles: {len(final_config.get('comment_styles', {}))}")
    print(f"  Excluded extensions: {len(final_config.get('exclude_extensions', []))}")
    print(f"  Excluded files: {len(final_config.get('exclude_files', []))}")
    print(f"  Excluded directories: {len(final_config.get('exclude_dirs', []))}")

    # Show a sample of comment styles for verification
    if final_config.get("comment_styles"):
        sample = list(final_config["comment_styles"].items())[:5]
        print(f"  Sample comment styles: {dict(sample)}")

    return final_config


def load_gitignore(root: str) -> Optional[pathspec.PathSpec]:
    """Loads .gitignore patterns using pathspec."""
    gitignore_path = os.path.join(root, ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                spec = pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern, f
                )
                return spec
        except Exception as e:
            print(f"[WARN] Failed to load .gitignore: {e}")
    return None


def run_init(root: str) -> None:
    """Creates initial config and gitignore files."""
    config_path = os.path.join(root, CONFIG_NAME)
    gitignore_path = os.path.join(root, ".gitignore")

    # Create .annotator.json with the raw string (preserving comments)
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(INIT_CONFIG_CONTENT)
            print(f"[INIT] Created {CONFIG_NAME} (with guide comments)")
        except Exception as e:
            print(f"[ERROR] Failed to create config: {e}")
    else:
        print(f"[SKIP] {CONFIG_NAME} already exists.")

    # Create .gitignore if missing
    if not os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write("# Annotator exclusions\nnode_modules/\n.DS_Store\n")
            print("[INIT] Created .gitignore")
        except Exception as e:
            print(f"[ERROR] Failed to create .gitignore: {e}")
    else:
        print("[SKIP] .gitignore already exists.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Annotate project files with their relative paths."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project root (default: current dir)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize a new .annotator.json and .gitignore",
    )
    parser.add_argument(
        "--revert",
        action="store_true",
        help="Remove annotations instead of adding them",
    )

    args = parser.parse_args()
    root_path = os.path.abspath(args.path)

    if not os.path.isdir(root_path):
        print(f"[ERROR] Invalid path: {root_path}")
        sys.exit(1)

    if args.init:
        run_init(root_path)
        return

    # Check for config presence
    config_file_path = os.path.join(root_path, CONFIG_NAME)
    if not os.path.exists(config_file_path):
        print(f"[INFO] No {CONFIG_NAME} found. Run 'annotator --init' to get started.")
        sys.exit(0)

    # 1. Load merged configuration
    config = get_config(root_path)

    # 2. Load gitignore
    spec = load_gitignore(root_path)

    # 3. Execute core logic
    mode_text = "Reverting" if args.revert else "Applying"
    print(f"\n[{mode_text}] Running in: {root_path}\n")

    annotate_project(root_path, config, spec=spec, revert=args.revert)


if __name__ == "__main__":
    main()
