import os
from typing import Any, Dict, Optional, Set

# Unique signature to identify our annotations for stateless revert
SIGNATURE: str = "~annotator~"


def get_extension(filename: str) -> str:
    """
    Return the extension after the last dot.
    In this app, we define extension strictly as the final suffix (e.g., .ts, .js).
    """
    return os.path.splitext(filename)[1]


def should_skip_extensionless_file(filepath: str) -> bool:
    """
    Peeks at the first line of an extensionless file to identify
    protected headers like Shebangs or XML declarations.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline().strip()
            if first_line.startswith("#!") or first_line.startswith("<?xml"):
                return True
    except Exception:
        return True
    return False


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


def is_git_ignored(rel_path: str, spec: Any) -> bool:
    """Check if a relative path matches gitignore rules."""
    if not spec:
        return False
    return spec.match_file(rel_path)


def is_excluded_file(
    rel_path: str, filename: str, filepath: str, config: Dict[str, Any]
) -> bool:
    """
    Check if filename, relative path, extension, or content-headers
    are in exclusion lists.
    """
    exclude_files = config.get("exclude_files", [])

    # 1. Check Global Blacklist (Filename match or Full Relative Path match)
    if filename in exclude_files or rel_path in exclude_files:
        return True

    # 2. Check Type Filtering (Extension match)
    ext = get_extension(filename)
    if ext in config.get("exclude_extensions", []):
        return True

    # 3. Mystery File Check (No extension)
    if not ext:
        if should_skip_extensionless_file(filepath):
            return True

    return False


def is_in_excluded_directory(rel_path: str, exclude_dirs: Set[str]) -> bool:
    """
    Check if a file's relative path is within any excluded directory.
    Handles both direct directory names and nested paths like 'src/generated/bin'.
    """
    # Normalize the path to use forward slashes
    normalized_path = rel_path.replace(os.sep, "/")

    for excluded in exclude_dirs:
        # Normalize excluded path as well
        normalized_excluded = excluded.replace(os.sep, "/")

        # Check if file is directly in this excluded dir or in a subdirectory
        if normalized_path.startswith(normalized_excluded + "/"):
            return True

        # Also check if any parent directory matches
        path_parts = normalized_path.split("/")
        for i in range(len(path_parts)):
            partial_path = "/".join(path_parts[: i + 1])
            if partial_path == normalized_excluded:
                return True

    return False


def get_prefix(filename: str, config: Dict[str, Any]) -> str:
    """Determine comment style from config; fallback to '#'."""
    styles: Dict[str, str] = config.get("comment_styles", {})
    ext = get_extension(filename)
    # Priority: Filename > Extension > Fallback
    return styles.get(filename) or styles.get(ext) or "#"


def get_annotation_text(rel_path: str, filename: str, config: Dict[str, Any]) -> str:
    """Constructs the annotation string with the unique signature."""
    prefix = get_prefix(filename, config)

    if prefix in ["<!--", "/*"]:
        suffix = " -->" if prefix == "<!--" else " */"
        return f"{prefix} {rel_path} {SIGNATURE}{suffix}\n"

    return f"{prefix} {rel_path} {SIGNATURE}\n"


def apply_annotation(filepath: str, rel_path: str, config: Dict[str, Any]) -> bool:
    """Reads, checks for existing header, and writes the new annotation."""
    filename = os.path.basename(filepath)
    annotation = get_annotation_text(rel_path, filename, config)

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Check the first line for existing signature
        first_line = content.split("\n", 1)[0]
        if SIGNATURE in first_line:
            return False

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(annotation + content)
        return True
    except Exception as e:
        print(f"[ERROR] Failed to annotate {rel_path}: {e}")
        return False


def remove_annotation(filepath: str, rel_path: str) -> bool:
    """Checks the first line for the signature and removes it if found."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        if not lines:
            return False

        if SIGNATURE in lines[0]:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines[1:])
            return True
        return False
    except Exception as e:
        print(f"[ERROR] Failed to revert {rel_path}: {e}")
        return False


def annotate_project(
    root: str, config: Dict[str, Any], spec: Optional[Any] = None, revert: bool = False
) -> None:
    """Traverse and annotate (or revert) based on template/config settings."""
    settings = config.get("settings", {})
    max_depth = settings.get("max_recursive_depth", 10)
    max_files = settings.get("max_num_of_files", 1000)
    max_kb = settings.get("max_file_size_kb", 512)
    ex_dirs = set(config.get("exclude_dirs", []))

    action_count = 0
    for subdir, dirs, files in os.walk(root):
        # 1. Prune depth
        if is_too_deep(subdir, root, max_depth):
            dirs[:] = []
            continue

        # 2. Prune directories (Path-aware with nested path support)
        kept_dirs = []
        for d in dirs:
            dir_path = os.path.join(subdir, d)
            rel_dir_path = os.path.relpath(dir_path, root).replace(os.sep, "/")

            # Skip if directory name is in exclude_dirs
            if d in ex_dirs:
                continue

            # Skip if the full relative path matches any excluded directory pattern
            if is_in_excluded_directory(rel_dir_path, ex_dirs):
                continue

            # Skip if git-ignored (only when not reverting)
            if not revert and is_git_ignored(rel_dir_path, spec):
                continue

            kept_dirs.append(d)
        dirs[:] = kept_dirs

        # 3. Process Files
        for file in files:
            filepath = os.path.join(subdir, file)
            rel_path = os.path.relpath(filepath, root).replace(os.sep, "/")

            if not revert:
                # Sequence: Gitignore -> Directory Exclusion -> Custom File Exclusions -> Size Limit
                if is_git_ignored(rel_path, spec):
                    continue

                # Check if file is in an excluded directory
                if is_in_excluded_directory(rel_path, ex_dirs):
                    continue

                if is_excluded_file(rel_path, file, filepath, config):
                    continue
                if is_too_large(filepath, max_kb):
                    continue

                if action_count >= max_files:
                    print(f"[HALT] Reached file limit: {max_files}")
                    return

            # Perform Action
            if revert:
                if remove_annotation(filepath, rel_path):
                    action_count += 1
                    print(f"[CLEAN] {rel_path}")
            else:
                if apply_annotation(filepath, rel_path, config):
                    action_count += 1
                    print(f"[OK] {rel_path}")

    status = "Reverted" if revert else "Annotated"
    print(f"[DONE] {status} {action_count} files.")
