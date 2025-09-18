# annotator/defaults.py

DEFAULT_COMMENT_STYLES = {
    ".py": "#",
    ".js": "//",
    ".ts": "//",
    ".jsx": "//",
    ".tsx": "//",
    ".java": "//",
    ".c": "//",
    ".cpp": "//",
    ".h": "//",
    ".hpp": "//",
    ".php": "//",
    ".swift": "//",
    ".kt": "//",
    ".kts": "//",
    ".html": "<!--",
    ".xml": "<!--",
    ".css": "/*",
    ".scss": "/*",
    ".less": "/*",
    ".sh": "#",
    ".rb": "#",
    ".go": "//",
    ".rs": "//",
    ".pl": "#",
    ".pm": "#",
    ".lua": "--",
    ".sql": "--",
    ".scala": "//",
    ".dart": "//",
    ".m": "%",
    ".r": "#"
}

# Common dependency/build/virtual env directories we should skip
DEFAULT_EXCLUDE_DIRS = {
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".git",
    ".hg",
    ".svn",
    "target",     # Java/Maven/Gradle, Rust
    "out",        # C++/Java builds
    "bin",        # Compiled bins
    "obj",        # Compiled objs
    ".idea",      # JetBrains IDEs
    ".vscode",    # VSCode settings
    ".DS_Store",  # macOS Finder metadata
    ".cache",     # General cache
    ".gradle",    # Gradle cache
    ".settings",  # Eclipse settings
    ".history",   # Some editors
    ".coverage",  # Coverage.py
    ".env",       # Environment files
    ".eggs",      # Python eggs
    ".bundle",    # Ruby bundle
    "log",        # Log files
    "logs",       # Log files
    ".sass-cache" # Sass cache
}
