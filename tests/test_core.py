from annotator.core import (
    get_extension,
    should_skip_extensionless_file,
    is_too_deep,
    is_too_large,
    is_in_excluded_directory,
    get_prefix,
    get_annotation_text,
    apply_annotation,
    remove_annotation,
    SIGNATURE,
)

# --- Pure Function Tests ---


def test_get_extension():
    assert get_extension("script.py") == ".py"
    assert get_extension("archive.tar.gz") == ".gz"
    assert get_extension("Makefile") == ""
    assert (
        get_extension(".gitignore") == ""
    )  # os.path.splitext treats this as root, empty ext


def test_is_too_deep():
    root = "/app"
    assert is_too_deep("/app/src/main", root, max_depth=1) is True
    assert is_too_deep("/app/src/main", root, max_depth=2) is False
    assert is_too_deep("/app", root, max_depth=0) is False


def test_is_in_excluded_directory():
    exclude_dirs = {"node_modules", "build", ".git"}

    # Direct match
    assert is_in_excluded_directory("node_modules/react/index.js", exclude_dirs) is True
    assert is_in_excluded_directory("build/output.css", exclude_dirs) is True

    # Nested match
    assert (
        is_in_excluded_directory("src/components/node_modules/test.js", exclude_dirs)
        is False
    )  # Only matches prefix or exact folder
    exclude_nested = {"src/generated"}
    assert is_in_excluded_directory("src/generated/api.ts", exclude_nested) is True

    # Safe path
    assert is_in_excluded_directory("src/main.py", exclude_dirs) is False


def test_get_prefix():
    config = {
        "comment_styles": {".py": "#", ".js": "//", "Dockerfile": "#", ".html": "<!--"}
    }
    assert get_prefix("script.py", config) == "#"
    assert get_prefix("app.js", config) == "//"
    assert get_prefix("Dockerfile", config) == "#"  # Matches filename
    assert get_prefix("unknown.xyz", config) == "#"  # Fallback


def test_get_annotation_text():
    config = {"comment_styles": {".py": "#", ".html": "<!--"}}

    text_py = get_annotation_text("src/main.py", "main.py", config)
    assert text_py == f"# src/main.py {SIGNATURE}\n"

    text_html = get_annotation_text("public/index.html", "index.html", config)
    assert text_html == f"<!-- public/index.html {SIGNATURE} -->\n"


# --- File I/O Tests (Using pytest tmp_path fixture) ---


def test_should_skip_extensionless_file(tmp_path):
    # Test Shebang
    bash_file = tmp_path / "script"
    bash_file.write_text("#!/bin/bash\necho 'hello'")
    assert should_skip_extensionless_file(str(bash_file)) is True

    # Test XML
    xml_file = tmp_path / "config"
    xml_file.write_text('<?xml version="1.0"?>\n<root></root>')
    assert should_skip_extensionless_file(str(xml_file)) is True

    # Normal text
    txt_file = tmp_path / "notes"
    txt_file.write_text("Just some regular text\nNothing special.")
    assert should_skip_extensionless_file(str(txt_file)) is False


def test_is_too_large(tmp_path):
    big_file = tmp_path / "large.bin"
    # Create a 2KB file (2048 bytes)
    big_file.write_bytes(b"0" * 2048)

    assert is_too_large(str(big_file), max_kb=1) is True
    assert is_too_large(str(big_file), max_kb=3) is False


def test_apply_and_remove_annotation(tmp_path):
    target_file = tmp_path / "test_script.py"
    target_file.write_text("print('hello world')\n")

    filepath = str(target_file)
    rel_path = "test_script.py"
    config = {"comment_styles": {".py": "#"}}

    # 1. Apply annotation
    success = apply_annotation(filepath, rel_path, config)
    assert success is True
    content = target_file.read_text()
    assert content.startswith(f"# {rel_path} {SIGNATURE}\n")
    assert "print('hello world')" in content

    # 2. Prevent double annotation
    success_duplicate = apply_annotation(filepath, rel_path, config)
    assert success_duplicate is False  # Should return False because signature exists

    # 3. Remove annotation
    success_remove = remove_annotation(filepath, rel_path)
    assert success_remove is True
    clean_content = target_file.read_text()
    assert clean_content == "print('hello world')\n"  # Back to original

    # 4. Remove when no annotation exists
    success_remove_again = remove_annotation(filepath, rel_path)
    assert success_remove_again is False


class MockGitIgnore:
    def match_file(self, path):
        return path == "ignored_file.txt"


def test_is_git_ignored():
    spec = MockGitIgnore()

    from annotator.core import is_git_ignored

    assert is_git_ignored("ignored_file.txt", spec) is True
    assert is_git_ignored("tracked_file.txt", spec) is False
    assert is_git_ignored("file.txt", None) is False
