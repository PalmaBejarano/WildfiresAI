# WildfiresAI — AG² Architecture (Controlled Multi-Agent Scientific Pipeline)

**Author:** Palma Bejarano  
**Mentor:** Dr. Alireza Ghafarollahi (MIT)

**Purpose:** This document describes the implemented AG² / AutoGen architecture of WildfiresAI, designed as a controlled multi-agent scientific pipeline with strict separation between explanation, retrieval, analysis, and code execution.

---

## 1. Overview

WildfiresAI is structured as a fixed multi-agent pipeline that emphasizes:

- **Strict tool boundaries** (no data access without tools)
- **Validated retrieval** (whitelists and schema-safe queries)
- **Data-grounded analysis** (conclusions derived from retrieved values)
- **Traceable computation** (optional code execution only through a controlled executor)
- **Reproducibility** (artifacts persisted to disk)

The pipeline is implemented in `Pipeline WildfiresAI.ipynb`.

---

## 2. Agent Order and Control Flow

The pipeline follows a fixed order:

**Human → Agent A → Agent B → Agent C → Agent D → Human**

There are no hidden loops. Any iteration (e.g., reformulating a query) is explicit and user-driven.

---

## 3. Roles and Boundaries

### Agent A — Explainer (Interpretation only)
**Responsibilities**
- Interpret the user request.
- Formalize the question in scientific terms.
- Define the information needs and constraints for retrieval.

**Not allowed**
- No external data access.
- No conclusions based on unknown values.

**Output**
- A structured, concise interpretation passed through shared context variables.

---

### Agent B — Materials Retriever (Data access with hard constraints)
**Responsibilities**
- Translate Agent A’s interpretation into a valid Materials Project query.
- Enforce hard whitelists for:
  - allowed `search_criteria`
  - allowed `fields`
- Fail loudly on unsupported filters instead of silently inventing or correcting them.
- Store raw results in shared context variables.

**Data source (current core pipeline)**
- **Materials Project API** (via `MP_API_KEY` provided locally)

**Output**
- Raw materials results and retrieval metadata in shared context.

---

### Agent C — Analyzer (Scientific analysis, no retrieval)
**Responsibilities**
- Perform data-grounded analysis of retrieved materials.
- Interpret quantitative fields (e.g., `band_gap`, `energy_above_hull`, `density`) to produce a scientific summary.
- Rank or shortlist candidates using explicit criteria.
- Emit a JSON output.

**Not allowed**
- No external retrieval.
- No hallucinated properties or unsupported claims.

**Persistence**
- Writes structured outputs to disk (e.g., `materials_data.json`) for reproducibility.

---

### Agent D — Python Coder (Controlled execution only)
**Responsibilities**
- Execute Python code only through a controlled tool or executor.
- Typical tasks:
  - export CSV summaries
  - generate plots (e.g., band gap distributions)
  - serialize intermediate results

**Execution constraints**
- No direct code execution outside the tool.
- All executed code and outputs are persisted (e.g., under `ag2_project/`).

---

## 4. Data Provenance and Reproducibility

The repository does not version large datasets or secrets.

- Secrets are provided locally via `.env` (never committed).
- Public templates are documented in `.env.example`.
- Data handling policy is documented in `docs/DATA.md`.

The architecture is designed so that:
- **retrieval can be replayed** from the same query constraints,
- **analysis is reproducible** from persisted artifacts,
- and **outputs are inspectable** without relying on hidden model state.

---

## 5. Artifact Outputs (Expected)

Depending on the run configuration, the pipeline may generate:

- `materials_data.json`  
  Structured analysis output produced by Agent C.

- `ag2_project/`  
  Controlled execution artifacts from Agent D (scripts, plots, CSVs, logs).

- `figs/`, `reports/`  
  Optional exported figures and lightweight reports.

The repository remains lightweight by design; raw external data is treated as an input, not a tracked asset.

---

## 6. Design Rationale

The multi-agent separation is a deliberate engineering choice to avoid common failure modes in LLM systems:

- **Hidden reasoning:** prevented by explicit routing and strict boundaries.
- **Hallucinated data:** prevented by tool-only retrieval and value-grounded analysis.
- **Silent schema drift:** prevented by hard whitelists and validation.
- **Untraceable computation:** prevented by controlled code execution and persisted outputs.




