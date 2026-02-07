# Annotator CLI

**Annotator** is a simple CLI utility that prepends relative file paths as comments to your project files as the first line.  
It’s designed to make AI debugging easier by automatically marking file paths for better context and easier copy-pasting.

---

## ✨ Features

- 🚀 **Automatically annotates** files with their relative paths
- 🔄 **Reversible** — clean annotations with `--revert`
- 🎯 **Template system** — framework-specific presets (Next.js, Spring Boot, Python, React, Prisma)
- ⚙️ **Fully customizable** via `.annotator.jsonc` configuration
- 🚫 **Smart filtering** — respects `.gitignore`, excludes binaries, and skips nested paths
- 🔍 **Stateless revert** — removes annotations using unique signature (`~annotator~`)
- ⚡ **Lightweight and fast** — minimal dependencies

---

## 📦 Installation

### Via [pipx](https://pipx.pypa.io/) (recommended):

```sh
pipx install annotator-cli
```

### Via pip:

```sh
pip install annotator-cli
```

---

## 🚀 Quick Start

### 1. Initialize configuration

```sh
cd /path/to/your/project
annotator --init
```

This creates `.annotator.jsonc` with sensible defaults and helpful comments.

### 2. Annotate your project

```sh
annotator
```

### 3. Revert annotations (if needed)

```sh
annotator --revert
```

---

## 📝 Configuration

Annotator uses a layered configuration system:

**Priority Chain:**  
`.gitignore` → `.annotator.jsonc` → `templates` (cumulative)

### Example `.annotator.jsonc`

```jsonc
{
  // List of templates to apply (keeping default is recommended)
  // pick additional: nextjs, react, springboot, python3, prisma ...
  "templates": ["default", "nextjs"],

  // Behavior settings
  "settings": {
    "max_recursive_depth": 10, // How deep to recurse into folders
    "max_num_of_files": 1000, // Maximum files to process
    "max_file_size_kb": 512, // Skip files larger than this
  },

  // Override comment styles for specific extensions
  // Example: ".kt": "//", ".scala": "//"
  "comment_styles": {},

  // Additional file extensions to exclude
  "exclude_extensions": [".log", ".cache"],

  // Additional directories to exclude (supports nested paths)
  // Example: ["temp", "src/generated/proto"]
  "exclude_dirs": ["node_modules", ".venv", "__pycache__"],

  // Additional specific file names to exclude
  "exclude_files": [".env", ".annotator.jsonc"],
}
```

<details>
<summary><strong>📋 Configuration Details</strong></summary>

### Templates

Annotator includes built-in templates for common frameworks:

- **`default`** - General-purpose config with 40+ languages, common excludes
- **`nextjs`** - Next.js specific exclusions (`.next`, config files, etc.)
- **`react`** - React/Vite/CRA exclusions
- **`springboot`** - Spring Boot/Maven/Gradle exclusions
- **`python3`** - Python virtual envs, caches, Jupyter notebooks
- **`prisma`** - Prisma schema and migration exclusions

Templates are applied cumulatively in order. See all templates at:  
[github.com/assignment-sets/annotator-cli/tree/main/annotator/templates](https://github.com/assignment-sets/annotator-cli)

### Comment Styles

Maps file extensions or exact filenames to comment syntax:

```jsonc
".js": "//",
".py": "#",
".html": "<!--",
".css": "/*"
```

### Exclusion Rules

- **`exclude_extensions`**: Skip files by extension (e.g., `[".log", ".bin"]`)
- **`exclude_dirs`**: Skip directories by name or nested path (e.g., `["node_modules", "src/generated"]`)
- **`exclude_files`**: Skip specific filenames (e.g., `[".env", "package-lock.json"]`)

**Note:** `.gitignore` patterns are always respected and have highest priority.

### Extension Parsing

Extensions are parsed from the last `.` to the end:

- `file.js` → `.js`
- `component.test.tsx` → `.tsx`
- `archive.tar.gz` → `.gz`

</details>

---

## 🎯 CLI Commands

```sh
# Annotate current directory
annotator

# Annotate specific path
annotator /path/to/project

# Initialize configuration
annotator --init

# Remove all annotations
annotator --revert

# Show help
annotator --help
```

---

## 🔧 How It Works

1. **Loads configuration** from `.annotator.jsonc` and merges with selected templates
2. **Respects `.gitignore`** patterns (highest priority)
3. **Applies filters** based on extensions, directories, files, and size limits
4. **Prepends comments** with relative path and unique signature:

```python
   # src/utils/helper.py ~annotator~
```

5. **Skips already annotated** files (idempotent)
6. **Revert support** removes only lines containing `~annotator~` signature

---

## 📚 Common Use Cases

### Next.js Project

```jsonc
{
  "templates": ["default", "nextjs"],
}
```

### Python Data Science Project

```jsonc
{
  "templates": ["default", "python3"],
  // customize more as you need for example
  "exclude_extensions": [".parquet"],
}
```

### Spring Boot Microservice

```jsonc
{
  "templates": ["default", "springboot"],
}
```

### Full-Stack React + Prisma

```jsonc
{
  "templates": ["default", "react", "prisma"],
}
```

---

## 🤝 Contributing

Want to add a template for your favorite framework? PRs welcome!

Repository: [github.com/assignment-sets/annotator-cli](https://github.com/assignment-sets/annotator-cli)

---

## ⚠️ Disclaimer

> This software is provided **as-is**, without warranty of any kind.  
> Use at your own risk — the author is not responsible for data loss, crashes, or security issues.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built to make AI-assisted debugging easier by providing better file context.
