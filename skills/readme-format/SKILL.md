---
name: readme-format
description: Create and format high-signal, standard-compliant README.md files. Use when a repository needs a new README.md, when refactoring an outdated or poorly structured README, or when preparing to commit code and release a project following team standards.
---

# README Standard Formatter Skill

This skill guides Gemini CLI to autonomously discover a project's technology stack, architecture, configuration variables, and APIs to generate a clean, standard-compliant, high-signal `README.md` file.

## 🏗️ Workflow Decision Tree

```
                       ┌──────────────────────────┐
                       │   1. Analyze Repository  │
                       │   (Tech stack, APIs,     │
                       │    Config, Architecture) │
                       └─────────────┬────────────┘
                                     ▼
                       ┌──────────────────────────┐
                       │   2. Load Guidelines &   │
                       │      Template Asset      │
                       └─────────────┬────────────┘
                                     ▼
                       ┌──────────────────────────┐
                       │ 3. Draft Standard README │
                       │    (Apply ASCII art,     │
                       │     config, and API specs)│
                       └─────────────┬────────────┘
                                     ▼
                       ┌──────────────────────────┐
                       │   4. Verify & Validate   │
                       │   (Check code, links,    │
                       │    and formatting)       │
                       └──────────────────────────┘
```

---

## 📋 Step-by-Step Instructions

### Step 1: Discover & Analyze Codebase
To construct an accurate, high-signal README, search and parse files to gather critical project attributes:
1. **Identify Language/Runtime:** Look for key manifest files:
   - Python: `pyproject.toml`, `requirements.txt`, `poetry.lock`, `uv.lock`
   - Node.js: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - Go: `go.mod`
   - Rust: `Cargo.toml`
2. **Detect Configuration Keys:** Search for environment variable declarations (e.g., `os.getenv`, `os.environ`, `process.env`, `dotenv`, Pydantic `BaseSettings`) to construct a comprehensive environment configuration table.
3. **Map API Endpoints & Payloads:** Look for route definitions (FastAPI routers, Express routes, Flask controllers) to build a precise **API Spec Sheet** and **Calling Guide** including a concrete `curl` snippet.
4. **Understand Architecture:** Trace key modules and components to create an ASCII flowchart mapping request flows.

### Step 2: Retrieve Template & Guidelines
Before drafting, read the provided team template and detail-oriented guidelines:
- Read the team template asset: `assets/README_TEMPLATE.md`
- Read the detailed formatting rules: `references/readme_guidelines.md`

### Step 3: Implement standard README
Synthesize your findings and write the resulting `README.md` file following the template's precise layout:
- **Title and Description:** Keep it professional and domain-focused. Highlight compliance (e.g., standard Agent-to-Agent protocol compliance).
- **Architecture Diagram:** Draft a neat, aligned ASCII diagram showing module boundaries, service boundaries, or client-server requests.
- **Environment Table:** Ensure every variable has a brief, meaningful description and a realistic example value.
- **Prerequisites and Local Dev commands:** Align commands with the package manager and tools actually present in the repo (e.g., use `uv run` if `uv.lock` is present; use `npm` or `yarn` if `package.json` is present).
- **No placeholders:** Ensure absolutely no brackets, "TODOs", or template placeholders (`[your-gcp-project]`) are committed. Every field must contain actual, verified project-specific details.

### Step 4: Verify Formatting
Confirm the file is structured correctly and contains clean formatting. Ensure code blocks are designated with correct syntax highlights (e.g., `bash`, `json`, `python`) and tables render properly.
