import os
from .defaults import DEFAULT_COMMENT_STYLES, DEFAULT_EXCLUDE_DIRS


def get_full_extension(filename: str) -> str:
    """Return everything after the first dot, e.g., 'unit.test.js' -> '.test.js'."""
    if "." not in filename:
        return ""
    return filename[filename.index("."):]  # keeps the dot


def is_excluded_dir(filepath: str, root: str, exclude_dirs: set) -> bool:
    """Check if file lives in an excluded directory (relative to root)."""
    rel_path = os.path.relpath(filepath, root)
    parts = rel_path.split(os.sep)
    return any(part in exclude_dirs for part in parts)


def is_excluded_file(filename: str, exclude_files: set) -> bool:
    """Check if filename matches exactly one of the excluded files."""
    return filename in exclude_files


def is_excluded_ext(filename: str, exclude_exts: set) -> bool:
    """Check if full extension matches excluded extensions."""
    ext = get_full_extension(filename)
    return ext in exclude_exts


def annotate_file(root, filepath, comment_styles):
    rel_path = os.path.relpath(filepath, root)
    ext = get_full_extension(os.path.basename(filepath))

    prefix = comment_styles.get(ext)
    if not prefix:
        return

    annotation = f"{prefix} {rel_path}\n"
    if prefix in ["<!--", "/*"]:
        annotation = f"{prefix} {rel_path} {'-->' if prefix == '<!--' else '*/'}\n"

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[WARN] Skipping {filepath}: {e}")
        return

    if lines and rel_path in lines[0]:
        return

    new_content = [annotation] + lines
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_content)
        print(f"[OK] Annotated {rel_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write {filepath}: {e}")


def annotate_project(root=".", comment_styles=None,
                     exclude_exts=None, exclude_dirs=None, exclude_files=None):
    if comment_styles is None:
        comment_styles = DEFAULT_COMMENT_STYLES
    if exclude_exts is None:
        exclude_exts = set()
    if exclude_dirs is None:
        exclude_dirs = set()
    if exclude_files is None:
        exclude_files = set()

    effective_exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(exclude_dirs)

    for subdir, dirs, files in os.walk(root):
        # skip excluded dirs at traversal level
        dirs[:] = [d for d in dirs if d not in effective_exclude_dirs]

        for file in files:
            filepath = os.path.join(subdir, file)

            # precedence rules
            if is_excluded_dir(filepath, root, effective_exclude_dirs):
                continue
            if is_excluded_file(file, exclude_files):
                continue
            if is_excluded_ext(file, exclude_exts):
                continue

            annotate_file(root, filepath, comment_styles)
