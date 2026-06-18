---
name: bigquery-nl2sql-recommender
description: Analyzes provided BigQuery dataset schemas, interviews the user on their business goals, and recommends verified NL2SQL query pairs (natural language questions matched with fully-verified SQL queries).
---

# BigQuery NL2SQL Recommender Skill

This skill allows the AI assistant to analyze BigQuery dataset schemas, conduct targeted business interviews, and produce fully-verified, production-ready Natural Language to SQL (NL2SQL) query pairs formatted in a beautiful Markdown report.

---

## 🎯 Architecture & Core Rules

### 1. Dynamic BigQuery Project Scoping & Confirmation
- **Project Confirmation:** At the very beginning of the interaction, the agent **MUST** confirm the target Google Cloud Project ID for execution, billing, and schema metadata.
- **Default/Preferred Project:** Suggest `analytics-183110` as the default/recommended project (as it may have reserved slots and prevent on-demand costs for authorized users), but explicitly ask the user to confirm or provide their preferred billing/execution project.
- **Scoping Context:** Once confirmed, all subsequent schema discoveries, dry-runs, query executions, and recommended queries must use this confirmed project ID (referred to below as `<PROJECT_ID>`).
- **Query Context:** When generating or executing SQL queries, assume the execution context is the confirmed `<PROJECT_ID>`. Fully qualify table names as `` `<PROJECT_ID>.dataset_name.table_name` `` unless a different project is explicitly requested by the user.

### 2. High-Fidelity Verification
- **Never recommend unverified SQL:** Every recommended SQL query must be verified using a dry-run or actual execution with `LIMIT 0` against BigQuery under the confirmed `<PROJECT_ID>` billing project to ensure syntactic correctness, valid table/column references, and to retrieve cost/bytes-billed estimates.

---

## 🛠️ Step-by-Step NL2SQL Workflow

### Step 1: Project & Schema Retrieval Setup
1. **Confirm Project ID:** Ask the user: *"Which Google Cloud Project should be used for execution and billing? (Default: analytics-183110)"* and wait for confirmation.
2. **Discover Schema:** Once the project ID (referred to as `<PROJECT_ID>`) is confirmed, discover the schema of the target dataset or tables.
3. Run a query or use the `bq` command-line tool (if available) to inspect the table structures:
   ```sql
   SELECT table_name, column_name, data_type
   FROM `<PROJECT_ID>.YOUR_DATASET.INFORMATION_SCHEMA.COLUMNS`
   ORDER BY table_name, ordinal_position;
   ```
4. Identify primary keys, foreign keys, relationships, timestamp/date columns, metrics (numeric fields), and dimensions (categorical fields).

### Step 2: Business-Driven Interview
Conduct a brief interview of 3–4 targeted, business-driven questions to extract their underlying goals:
- **Core Metrics:** What performance indicators are they trying to measure (e.g., revenue, active days, growth rates)?
- **Dimensions & Filters:** How should the data be segmented or filtered (e.g., by region, device type, user cohort)?
- **Time Intelligence:** What are the temporal requirements (e.g., Q2 comparison, month-over-month, rolling 30-day average)?
- **Aggregations:** Do they require granular records, daily rollups, or lifetime totals?

### Step 3: Query Generation (Candidate Pairs)
Draft 3–5 candidate pairs based on the schema and interview answers. Each pair consists of:
- **Natural Language Question:** A clear, business-oriented question that a non-technical stakeholder would ask (e.g., "What is the sales growth for Q2 2026?").
- **Targeted SQL Query:** A standard GoogleSQL query tailored for BigQuery, incorporating best practices (proper grouping, handling NULLs safely, efficient filtering, and fully qualified `<PROJECT_ID>`).

### Step 4: Verification & Validation
Before presenting the queries, verify each candidate:
1. Run a BigQuery dry-run to ensure the query parses successfully and to estimate cost:
   ```bash
   bq query --project_id=<PROJECT_ID> --use_legacy_sql=false --dry_run "YOUR_SQL_QUERY"
   ```
2. Ensure there are no syntax errors, unrecognized columns, or type mismatches.
3. Record the estimated bytes processed to display to the user.

### Step 5: Generate the Markdown Report
Compile the verified pairs into a structured Markdown document.

---

## 📋 Standard Output Format

All recommended query pairs must be presented in the following Markdown format:

```markdown
# BigQuery NL2SQL Recommendation Report

**Target Dataset:** `<PROJECT_ID>.[dataset_name]`
**Analysis Date:** [YYYY-MM-DD]

---

## 📊 Summary of Schema & Business Context
[Brief description of the tables analyzed and the business goals extracted from the user interview.]

---

## 💡 Recommended NL2SQL Query Pairs

### Query 1: [Descriptive Title]
* **Natural Language Question:** "[The exact business question answered]"
* **Business Value:** [Briefly explain what decision or insight this query enables.]
* **Estimated Cost:** [X.XX MB/GB/TB bytes processed (Dry-run estimate)]
* **Verified SQL:**
  ```sql
  -- Fully qualified and formatted GoogleSQL
  SELECT ...
  ```
* **Query Explanation:**
  - **Metrics/Filters used:** [Explain the WHERE clauses, aggregations, etc.]
  - **Assumption notes:** [Any specific assumptions made, such as timezone handling or null defaults.]

---

## 🛠️ Verification Command
To manually execute or test these queries, use the following `bq` command:
```bash
bq query --project_id=<PROJECT_ID> --use_legacy_sql=false "YOUR_SQL_QUERY"
```
```