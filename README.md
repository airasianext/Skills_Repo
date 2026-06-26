# Curated Agent Skills Collection

Welcome to the **Skills_Repo** repository! This is a curated collection of professional, production-tested [Agent Skills](https://agentskills.io) designed for the **Gemini CLI** (and other interoperable LLM/agent platforms).

Each skill in this collection extends your agent's capabilities with specialized knowledge, expert procedural workflows, and advanced code patterns.

---

## 📦 Collection Overview

Here is a summary of the custom skills available in this repository:

| Skill Name | Description | Installation Command |
| :--- | :--- | :--- |
| **`agent-card-finder`** | Expert skill for locating, deriving, and displaying Gemini Enterprise and Cloud Run agent card configurations. Helps developers extract and audit the technical definitions of deployed agents. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/agent-card-finder` |
| **`adk-evaluation-hardener`** | Expert skill for configuring offline, crash-resistant, and high-performance Google ADK automated evaluations with togglable mock/live runs, evaluation topologies, and multi-tier data bootstrapping. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/adk-evaluation-hardener` |
| **`bigquery-nl2sql-recommender`** | Analyzes BigQuery dataset schemas, interviews the user on business goals, and recommends fully-verified, production-ready Natural Language to SQL (NL2SQL) query pairs. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/bigquery-nl2sql-recommender` |
| **`fastapi-dynamic-openapi-composition`** | Provides expert procedural guidance, production patterns, and test suites for implementing a Dynamic OpenAPI Schema Composition pattern in Python FastAPI projects. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/fastapi-dynamic-openapi-composition` |
| **`fastapi-to-fastmcp`** | Expert guide for converting a Python FastAPI application into a hybrid FastAPI + FastMCP Model Context Protocol (MCP) server that concurrently exposes standard REST endpoints and LLM tools. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/fastapi-to-fastmcp` |
| **`front-end-design`** | Guides the creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Focuses on building aesthetic but highly functional and low-friction user experiences through a "Design-First" approach. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/front-end-design` |
| **`gcp-cloud-run-migrator`** | Helps users inspect, plan, and migrate Cloud Run services and their dependencies (secrets, service accounts, enabled APIs, logging policies, container images) from a source GCP project to a target GCP project. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/gcp-cloud-run-migrator` |
| **`readme-format`** | Create and format high-signal, standard-compliant README.md files. Use when a repository needs a new README.md, when refactoring an outdated or poorly structured README, or when preparing to commit code and release a project following team standards. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/readme-format` |
| **`security-auditor`** | Defensive Security Auditor specializing in Static Application Security Testing (SAST), active browser-based Dynamic Application Security Testing (DAST) using Playwright, and LLM application security. | `gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/security-auditor` |

---

## 🚀 Installation & Usage

Because this is a multi-skill collection, you can install individual skills selectively using the `--path` flag to point to the skill's specific sub-directory within the repository.

### Installing a Skill

To install any of these skills into your active Gemini CLI scope, run the following command (replacing `<your-username>` with your GitHub username or the actual Git URL of your repository):

```bash
gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/<skill-name>
```

#### Example (Installing the Security Auditor):
```bash
gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/security-auditor
```

### Installation Scopes

* **User Scope (Default):** Installs globally to `~/.gemini/skills/`. The skill is active across all of your CLI sessions.
* **Workspace Scope:** Installs locally to your current project’s `.gemini/skills/` directory, which is excellent for checking into your team's version control.
  ```bash
  gemini skills install https://github.com/<your-username>/Skills_Repo.git --path skills/security-auditor --scope workspace
  ```

---

## 🛠️ Local Development & Symlinking

If you want to modify any of these skills locally and test them in real-time, you can symlink them to your active environment instead of reinstalling them:

1. Clone this repository locally.
2. Link the desired skill folder using the CLI terminal or interactive console:
   ```bash
   gemini skills link ./skills/security-auditor
   ```
   *(Or within an active interactive session, run `/skills link ./skills/security-auditor`)*

---

## 📄 License & Standards

All skills are compliant with the open **Agent Skills** specification format. Feel free to fork, customize, or contribute your own skills to this collection!
