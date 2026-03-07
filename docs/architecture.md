# WildfiresAI — AG² Architecture (Controlled Multi-Agent Scientific Pipeline)

**Author:** Palma Bejarano  
**Mentor:** Dr. Alireza Ghafarollahi (MIT)

**Purpose:**  
This document describes the architecture of WildfiresAI as implemented using AG² / AutoGen.  
The system is designed as a controlled multi-agent scientific workflow where reasoning, data access, analysis, visualization, and reporting are explicitly separated.

The architecture emphasizes transparency, validation, and reproducibility when interacting with external scientific datasets.

---

# 1. Architectural Overview

WildfiresAI is implemented as a structured multi-agent execution pipeline**.

Each agent performs a narrowly defined role and communicates through structured artifacts stored in shared context variables.

The pipeline enforces:

- strict tool boundaries
- explicit execution planning
- validated data retrieval
- data-grounded analysis
- controlled code execution
- reproducible artifact generation

The full pipeline is implemented in:

```
Pipeline WildfiresAI.ipynb
```

---

# 2. Execution Flow

The system follows a deterministic execution sequence.

```
Human
 → AgentTaskImprover
 → AgentPlanner
 → AgentPlanReviewer
 → AgentMaterialsRetriever
 → AgentAnalyzer
 → AgentPlotSuggester
 → AgentPlotSelector
 → AgentCoder
 → AgentPlotValidator
 → Human
```

If the user requests documentation generation, the workflow may extend to:

```
Human
 → AgentLatexWriter
 → AgentLatexCompiler
 → Human
```

Routing between agents is determined by a structured execution plan, which defines the allowed transitions between stages.

---

# 3. Planning Layer

The first stage of the system focuses on transforming an open-ended user request into a formally defined workflow.

## 3.1 AgentTaskImprover — Task Refinement

Responsibilities:

- interpret the user request
- remove ambiguity
- preserve the original intent of the query
- produce a clearer operational task

Constraints:

- cannot introduce new requirements not present in the original request
- cannot retrieve data
- cannot perform analysis

Output:

```
main_task_improved
```

stored in shared execution state.

---

## 3.2 AgentPlanner — Structured Planning

The planner converts the refined task into a **structured execution plan**.

The plan specifies:

- Materials Project retrieval constraints
- allowed search filters
- allowed returned fields
- sampling limits
- visualization configuration
- required pipeline steps
- routing rules between agents
- success criteria

The plan is stored in:

```
context_variables["plan"]
```

The plan acts as the formal specification of the workflow.

---

## 3.3 AgentPlanReviewer — Plan Validation

The reviewer verifies that the generated plan is valid before execution.

Checks include:

- structural integrity of the plan
- presence of required pipeline stages
- compatibility with system guardrails
- valid routing between agents

Possible outcomes:

```
approve
revise
handoff
```

Only approved plans are allowed to proceed to execution.

---

# 4. Data Retrieval Layer

## 4.1 AgentMaterialsRetriever — Materials Project Query Execution

The retriever executes the plan-defined query against the Materials Project API.

The system enforces strict validation of:

- allowed search criteria
- allowed returned fields
- numeric range formats
- explicit exclusion filters

Examples of validated fields include:

- band_gap
- energy_above_hull
- density
- bulk_modulus
- shear_modulus

Unsupported filters are rejected rather than silently corrected.

Retrieved materials are stored in shared state:

```
context_variables["mp_results"]
```

---

# 5. Analysis Layer

## 5.1 AgentAnalyzer — Data-Grounded Scientific Analysis

The analyzer performs quantitative interpretation of the retrieved dataset.

Typical interpreted properties include:

- band gap
- energy above hull
- density
- structural characteristics

The analyzer summarizes observable patterns rather than generating speculative conclusions.

Outputs include:

```
analysis_summary
final_conclusion
materials_data_path
```

Artifacts are persisted to disk to ensure reproducibility.

---

# 6. Visualization Pipeline

Visualization is treated as a structured multi-stage process rather than a side effect of analysis.

## 6.1 AgentPlotSuggester

Generates candidate visualization proposals.

Constraints:

- proposals must reference fields present in retrieved data
- candidates must follow a strict schema
- candidates must include metadata describing axes and intent

Typical plot types include:

- scatter plots
- histograms
- heatmaps
- derived bar plots

Candidates are stored in:

```
context_variables["plot_candidates"]
```

---

## 6.2 AgentPlotSelector

Selects a subset of the proposed plots for execution.

Responsibilities:

- enforce selection limits
- validate plot compatibility
- ensure the selection follows plotting constraints

Selected plots are stored in:

```
context_variables["plot_selected"]
```

---

## 6.3 AgentCoder — Controlled Code Execution

Generates Python code to produce visualizations and artifacts.

Execution occurs exclusively through a controlled execution tool.

The coding stage:

- reads selected plot specifications
- generates figures
- saves plots to disk
- records executed code and outputs

Artifacts are typically written to:

```
plots/
plots_v2/
```

All executed code is stored for traceability.

---

## 6.4 AgentPlotValidator

Evaluates the generated plots for correctness and clarity.

Checks include:

- compatibility with plot specifications
- correctness of data usage
- visualization quality

If necessary, the system can trigger a second plot generation stage.

---

# 7. Documentation Layer (Optional)

If documentation is requested, the system generates a technical report.

## 7.1 AgentLatexWriter

Produces structured LaTeX sections describing:

- dataset properties
- analysis results
- generated figures

---

## 7.2 AgentLatexCompiler

Compiles the LaTeX source into a final PDF report.

Outputs include:

```
report.tex
report.pdf
```

This allows the pipeline to produce a reproducible technical artifact from a natural language query.

---

# 8. Shared Execution State

The pipeline maintains a shared execution state using context variables.

Key elements include:

- original user query
- improved task
- validated execution plan
- retrieved materials
- analysis results
- plot candidates
- selected plots
- generated artifacts
- report generation status

This design ensures that pipeline stages communicate through explicit artifacts rather than hidden model state.

---

# 9. Data Provenance and Reproducibility

The architecture is designed to ensure reproducibility.

- retrieval queries can be replayed
- analysis artifacts are persisted
- plots and reports are generated deterministically from stored data

Secrets such as API keys are provided locally via:

```
.env
```

and are never committed to the repository.

Data handling policies are documented in:

```
docs/DATA.md
```

---

# 10. Design Rationale

The multi-agent separation is a deliberate engineering decision intended to avoid common failure modes in LLM systems.

The architecture prevents:

**Hidden reasoning**  
through explicit execution steps.

**Hallucinated data**  
by restricting retrieval to validated tools.

**Schema drift**  
through strict validation and whitelists.

**Untraceable computation**  
through controlled code execution.

WildfiresAI therefore functions not as a conversational assistant, but as a structured scientific workflow system.

