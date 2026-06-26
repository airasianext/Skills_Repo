# README Design & Formatting Guidelines

This document provides instructions for analyzing a codebase and generating or refactoring its README.md following the standard high-signal format.

## Architectural Guidelines

To maintain a consistent and professional standard across all repositories, adhere to the following principles:

### 1. High-Impact Heading & Introduction
- **Header format:** A single `#` followed by a concise, professional title. Use standard emojis if it matches team conventions, but keep it readable and focused on the technical domain.
- **Intro text:** Highlight key value propositions and technical attributes immediately. Explain what standard/framework it complies with and why it exists.

### 2. ASCII/Text-based Architecture Diagrams
- Every README should include a clean, readable text-based or ASCII flow diagram showing data structures, client/server interactions, or module boundaries.
- Keep it aligned and clean. Ensure it uses standard UTF-8 box-drawing characters (`┌`, `─`, `┐`, `│`, `└`, `┘`, `▲`, `▼`, `◄`, `►`) for crisp rendering in monospace fonts.

### 3. Smart Configuration Table
- Detect environment variables from sources like `app.py`, `main.py`, `.env.example`, `config.py`, etc.
- Organize variables in a Markdown table with `Variable | Description | Example` columns. Avoid missing data or empty descriptions.

### 4. Direct, Pragmatic Deployment Steps
- Subdivide cloud or container deployment into separate step-by-step numbered instructions (e.g., `### 1. Build and Deploy`, `### 2. IAM Roles`).
- Provide concrete CLI snippets (like `gcloud`, `docker`, or custom shell scripts) rather than abstract theories.

### 5. Local Setup & Testing Block
- Categorize operations into logical subgroups (e.g., Running Tests, Running Server).
- State the modern package manager/tooling active in the repo (e.g., if you see `uv.lock` or `pyproject.toml` using `uv`, always recommend `uv run...`; if you see Node.js, recommend `npm` or `yarn`).

### 6. Standard API Spec & Usage Examples
- For APIs or web services, detail request headers, request bodies, a concrete copy-pasteable `curl` example, and the response payload.
- Ensure all example payloads are valid, formatted JSON-RPC or REST JSON structures, matching actual source route configurations.
