import argparse
import json
import os
import sys
from .core import annotate_project
from .defaults import DEFAULT_COMMENT_STYLES, DEFAULT_EXCLUDE_DIRS

CONFIG_FILE = ".annotator.json"


def load_config(root):
    config_path = os.path.join(root, CONFIG_FILE)
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {CONFIG_FILE}: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"[ERROR] Could not read {CONFIG_FILE}: {e}", file=sys.stderr)
        return {}


def main():
    parser = argparse.ArgumentParser(description="Annotate files with relative paths.")
    parser.add_argument("path", nargs="?", default=".", help="Project root (default: current dir)")
    args = parser.parse_args()

    root = os.path.abspath(args.path)
    if not os.path.exists(root):
        print(f"[ERROR] Path does not exist: {root}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(root):
        print(f"[ERROR] Path is not a directory: {root}", file=sys.stderr)
        sys.exit(1)

    config = load_config(root)
    
    valid_keys = {"comment_styles", "exclude_extensions", "exclude_dirs", "exclude_files"}
    for key in config.keys():
        if key not in valid_keys:
            print(f"[WARN] Unknown key in {CONFIG_FILE}: '{key}'", file=sys.stderr) 

    comment_styles = DEFAULT_COMMENT_STYLES.copy()
    if "comment_styles" in config and isinstance(config["comment_styles"], dict):
        comment_styles.update(config["comment_styles"])

    exclude_exts = set(config.get("exclude_extensions", []))
    exclude_dirs = set(config.get("exclude_dirs", []))
    exclude_files = set(config.get("exclude_files", []))

    print(f"[INFO] Annotating project at {root}")
    annotate_project(
        root,
        comment_styles,
        exclude_exts,
        exclude_dirs,
        exclude_files
    )
    print("[INFO] Done.")
