import os
from typing import Any, Dict, Optional, Set


def get_extension(filename: str) -> str:
    """Return the extension after the last dot."""
    return os.path.splitext(filename)[1]


def is_too_deep(subdir: str, root: str, max_depth: int) -> bool:
    """Check if the current directory exceeds recursion limits."""
    rel_path: str = os.path.relpath(subdir, root)
    if rel_path == ".":
        return False
    return len(rel_path.split(os.sep)) > max_depth


def is_too_large(filepath: str, max_kb: int) -> bool:
    """Check if file size exceeds the limit."""
    try:
        return (os.path.getsize(filepath) / 1024) > max_kb
    except OSError:
        return True


def is_git_ignored(filepath: str, root: str, spec: Any) -> bool:
    """Check if path matches gitignore rules."""
    if not spec:
        return False
    rel_path: str = os.path.relpath(filepath, root)
    return spec.match_file(rel_path)


def is_excluded_file(filename: str, config: Dict[str, Any]) -> bool:
    """Check if filename or extension is in the exclusion lists."""
    if filename in config.get("exclude_files", []):
        return True
    if get_extension(filename) in config.get("exclude_extensions", []):
        return True
    return False


def get_prefix(filename: str, config: Dict[str, Any]) -> str:
    """Determine comment style from config; fallback to '#'."""
    styles: Dict[str, str] = config.get("comment_styles", {})
    ext: str = get_extension(filename)
    # Priority: Filename > Extension > Fallback
    return styles.get(filename) or styles.get(ext) or "#"


def apply_annotation(filepath: str, root: str, config: Dict[str, Any]) -> bool:
    """Reads, checks for existing header, and writes the new annotation."""
    rel_path: str = os.path.relpath(filepath, root)
    prefix: str = get_prefix(os.path.basename(filepath), config)

    annotation: str
    if prefix in ["<!--", "/*"]:
        suffix: str = " -->" if prefix == "<!--" else " */"
        annotation = f"{prefix} {rel_path}{suffix}\n"
    else:
        annotation = f"{prefix} {rel_path}\n"

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content: str = f.read()

        if content.startswith(annotation.strip()):
            return False

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(annotation + content)
        return True
    except Exception as e:
        print(f"[ERROR] Failed {rel_path}: {e}")
        return False


def annotate_project(
    root: str, config: Dict[str, Any], spec: Optional[Any] = None
) -> None:
    """Traverse and annotate based on template/config settings."""
    settings: Dict[str, Any] = config.get("settings", {})
    max_depth: int = settings.get("max_recursive_depth", 10)
    max_files: int = settings.get("max_num_of_files", 1000)
    max_kb: int = settings.get("max_file_size_kb", 512)
    ex_dirs: Set[str] = set(config.get("exclude_dirs", []))

    annotated_count: int = 0
    for subdir, dirs, files in os.walk(root):
        # 1. Prune depth
        if is_too_deep(subdir, root, max_depth):
            dirs[:] = []
            continue

        # 2. Prune excluded directories (Efficient path exclusion)
        dirs[:] = [d for d in dirs if d not in ex_dirs]

        for file in files:
            if annotated_count >= max_files:
                print(f"[HALT] Reached file limit: {max_files}")
                return

            filepath: str = os.path.join(subdir, file)

            if is_git_ignored(filepath, root, spec):
                continue
            if is_excluded_file(file, config):
                continue
            if is_too_large(filepath, max_kb):
                continue

            if apply_annotation(filepath, root, config):
                annotated_count += 1
                print(f"[OK] {os.path.relpath(filepath, root)}")

    print(f"[DONE] Processed {annotated_count} files.")
