# WildfiresAI

![GitHub stars](https://img.shields.io/github/stars/PalmaBejarano/WildfiresAI)
![GitHub forks](https://img.shields.io/github/forks/PalmaBejarano/WildfiresAI)
![Repo Views](https://komarev.com/ghpvc/?username=PalmaBejarano&repo=WildfiresAI)

WildfiresAI is an independent research project exploring how controlled multi-agent AI systems can support transparent scientific workflows in domains where physical constraints and real-world data matter.

The repository implements an experimental pipeline built with AG² / AutoGen, combining:

- structured task refinement
- explicit execution planning
- validated retrieval from the Materials Project API
- quantitative materials analysis
- controlled generation and validation of scientific visualizations
- optional production of a technical report in LaTeX/PDF

The objective of the project is not to build a consumer AI product.  
Instead, WildfiresAI investigates how AI systems can be engineered to operate as structured scientific workflows, where reasoning steps remain visible, verifiable, and reproducible.

The current experimental application focuses on materials analysis relevant to high-risk infrastructure environments, such as wildfire-exposed power systems. However, the architectural principles are designed to generalize to broader scientific and environmental reasoning tasks.

---

# Core Idea

WildfiresAI is designed as a controlled multi-agent workflow in which each stage performs a strictly defined role.

Rather than allowing a single model to interpret a problem, retrieve data, analyze results, generate figures, and produce conclusions, the system decomposes the process into multiple cooperating agents.

Each agent:

- performs a limited and explicit responsibility
- communicates through structured artifacts
- interacts with the environment only through validated tools

This approach prioritizes traceability and reliability over convenience.

The system follows the execution flow:

```
Human
 → Task Improver
 → Planner
 → Plan Reviewer
 → Materials Retriever
 → Analyzer
 → Plot Suggester
 → Plot Selector
 → Coder
 → Plot Validator
 → Human
```

If documentation is requested, the workflow may continue:

```
Human
 → LaTeX Writer
 → LaTeX Compiler
 → Human
```

Internally, execution is organized through explicit plan steps such as:

- `retrieve`
- `analyze`
- `plot_suggest`
- `plot_select`
- `plot_generate_v1`
- `plot_validate`
- `plot_generate_v2`
- `latex_write`
- `latex_compile`

Transitions between stages are not implicit conversational moves.  
Instead, routing is determined by a validated execution plan stored in shared context variables.

---

# Architecture Overview

The pipeline is implemented in:

```
Pipeline WildfiresAI.ipynb
```

The system coordinates multiple agents with strict boundaries between reasoning, data retrieval, analysis, visualization, and documentation.

---

## AgentTaskImprover — Task Refinement

Refines the user’s request into a clearer operational task while preserving the original intent.

Responsibilities:

- remove ambiguity
- avoid introducing new requirements
- produce a cleaner task description for planning

---

## AgentPlanner — Structured Planning

Transforms the improved task into a structured execution plan.

The plan defines:

- Materials Project retrieval constraints
- allowed fields and filters
- sampling limits
- visualization configuration
- execution steps
- routing between agents
- success criteria

The plan acts as the formal specification of the workflow.

---

## AgentPlanReviewer — Plan Validation

A separate agent reviews the generated plan before execution.

This stage verifies:

- structural consistency
- required pipeline steps
- valid routing
- compatibility with system guardrails

The reviewer decides whether the plan should be:

- approved
- revised
- returned to the user

This prevents invalid plans from reaching execution.

---

## AgentMaterialsRetriever — Materials Project Retrieval

Executes the validated query against the Materials Project API.

The retrieval stage enforces strict contracts on:

- allowed search filters
- allowed returned fields
- numeric ranges
- explicit exclusion rules

Invalid filters are rejected rather than silently corrected.

Retrieved materials are stored in shared execution state for later stages.

---

## AgentAnalyzer — Data-Grounded Analysis

Performs quantitative analysis of the retrieved dataset.

Typical interpreted properties include:

- band gap
- energy above hull
- density

The agent summarizes observable patterns and ranges rather than generating speculative conclusions.

Results are persisted as structured artifacts so later stages do not rely on hidden model state.

---

## AgentPlotSuggester — Visualization Proposal

Proposes candidate plots compatible with the available dataset.

The suggester ensures that proposed visualizations reference fields actually retrieved from the data source.

Outputs are structured visualization candidates.

---

## AgentPlotSelector — Plot Selection

Selects the most informative and technically valid plots from the candidates.

Responsibilities include:

- enforcing plot selection constraints
- validating plot compatibility
- passing the final plot list to the coding stage

---

## AgentCoder — Controlled Code Execution

Generates Python code to produce figures and analysis artifacts.

Execution occurs only through a controlled tool environment, ensuring that:

- code execution is traceable
- artifacts are stored
- errors are captured

Typical outputs include:

- scientific plots
- CSV summaries
- execution logs

---

## AgentPlotValidator — Visualization Validation

Evaluates the correctness and clarity of generated plots.

The validator may trigger:

- plot regeneration
- corrections to visualization logic
- second-version plots

This stage ensures that figures reflect the underlying data correctly.

---

## AgentLatexWriter — Report Generation

Produces structured LaTeX sections summarizing the analysis.

The output can include:

- dataset summaries
- generated figures
- interpretation of materials properties

---

## AgentLatexCompiler — Document Compilation

Compiles the LaTeX source into a PDF technical report, producing a reproducible artifact of the pipeline execution.

---

# How the Pipeline Works

## 1. Task formalization

The user query is not executed directly.

Instead, it is refined into a precise operational task.

---

## 2. Structured planning

The refined task becomes a structured execution plan describing the workflow.

---

## 3. Validated materials retrieval

The system retrieves candidate materials from the Materials Project under strict constraints.

---

## 4. Data-grounded analysis

The dataset is analyzed quantitatively to identify patterns in physical properties.

---

## 5. Visualization pipeline

Visualization proceeds through multiple stages:

1. candidate plot proposal
2. plot selection
3. controlled code generation
4. plot validation
5. optional regeneration

---

## 6. Optional report generation

If requested, the system generates a LaTeX report and compiles it into a PDF.

---

# Design Principles

WildfiresAI follows several explicit engineering principles.

**Separation of responsibilities**  
Each agent performs a narrowly defined task.

**Tool-bounded computation**  
Critical transformations occur through validated tools.

**Data-grounded reasoning**  
All conclusions are derived from retrieved data.

**Traceability**  
Intermediate artifacts and execution state are stored explicitly.

**Reproducibility**  
Results, figures, and reports are persisted.

**Controlled routing**  
Pipeline transitions are determined by structured state rather than conversational flow.

---

# Evolution of the Project

Early versions of WildfiresAI implemented a simpler architecture with only a few agents responsible for explanation, retrieval, analysis, and coding.

The current system extends that design with:

- explicit task refinement
- structured planning and plan review
- a multi-stage visualization pipeline
- plot validation and regeneration
- optional LaTeX report generation

The resulting system resembles a scientific workflow engine more than a traditional question-answering AI pipeline.

---

# Repository Structure

```
WildfiresAI/
├── ag2_project/
├── examples/
│   └── example_run/
├── data/
│   └── processed/
├── docs/
│   └── DATA.md
├── figs/
├── reports/
├── .env.example
├── .gitignore
├── Pipeline WildfiresAI.ipynb
└── setup_firms_env.sh
```

Large raw datasets and runtime execution artifacts are excluded from version control.

Only lightweight example outputs are versioned.

---

# Environment Variables

All credentials are provided locally.

Create a `.env` file from the template:

```
cp .env.example .env
```

No API keys are committed to the repository.

---

# Research Context

WildfiresAI is an independent research effort developed under mentorship with a focus on scientific rigor, architectural transparency, and responsible AI system design.

The project investigates how multi-agent systems can support structured reasoning in domains where physical reality and uncertainty matter.

The aim is not to demonstrate impressive model behavior, but to design systems where reasoning remains visible, auditable, and correctable.
