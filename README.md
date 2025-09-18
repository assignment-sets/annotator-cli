# Annotator

**Annotator** is a simple CLI utility that prepends relative file paths as comments to your project files as the first line.  
It’s designed to make AI debugging easier by automatically marking file paths for better context and easier copy-pasting.

---

## ✨ Features

- 🚀 **Automatically annotates** files with their relative paths.
- 🛠️ **Supports many programming languages and file types** out of the box.
- ⚙️ **Fully customizable** via a `.annotator.json` configuration file.
- 🚫 **Exclude** specific directories, files, or extensions.
- ⚡ **Lightweight and fast** — no external dependencies.

---

## 📝 Example `.annotator.json`

```json
{
  "comment_styles": {
    ".md": "<!--",
    "Dockerfile": "#"
  },
  "exclude_extensions": ["*.test.js", "*.spec.ts"],
  "exclude_dirs": ["test", "dist"],
  "exclude_files": [".env"]
}
```

<details>
<summary><strong>Configuration Notes</strong></summary>

- **comment_styles**: Maps file extensions (from the first `.` to the end) or exact filenames to their comment syntax.  
  _Example:_ `.js` → `//`, `.md` → `<!--`. You can add any extension to annotate non-default types.

- **exclude_extensions**: Skips all files with these full extensions (from the first `.`).  
  _Note:_ Even if an extension is mapped in `comment_styles`, files matching an excluded extension will not be annotated.

- **exclude_dirs**: Skips these directories entirely.  
  _Note:_ Any file inside an excluded directory is never annotated, even if its extension is mapped in `comment_styles`.

- **exclude_files**: Skips specific full filenames (with extensions) entirely.  
  _Note:_ These take precedence over both `comment_styles` and `exclude_extensions`.

- **Extension parsing**: Extensions are always taken from the first `.` to the end of the filename.  
  _Example:_ For a file named `file.a.b.c.js`, the full extension is `.a.b.c.js`.

</details>

---

## Installation

### 1. Install pipx

Follow the official guide: [pipx Installation Guide](https://pipxproject.github.io/pipx/installation/)

### 2. Install annotator-cli via [pipx](https://pipx.pypa.io/) (recommended):

```sh
pipx install annotator-cli
```

---

## 🚀 Usage

### 1. Run the CLI

```sh
annotator /path/to/project
```

Annotator will process and annotate all eligible files based on your configuration.

### 2. Uninstall (if needed)

```sh
pipx uninstall annotator-cli
```

---

## ⚠️ Disclaimer

> This software is provided **as-is**, without warranty of any kind.  
> Use at your own risk — the author is not responsible for data loss, crashes, or security issues.

---
