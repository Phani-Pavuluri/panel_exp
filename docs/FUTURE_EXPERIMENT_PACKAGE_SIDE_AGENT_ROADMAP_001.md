# Future GeoX / Experiment Package-Side Agent Roadmap

**Artifact ID:** `FUTURE_EXPERIMENT_PACKAGE_SIDE_AGENT_ROADMAP_001`  
**Status:** roadmap capture only — **deferred, not implemented**  
**Last updated:** 2026-06-03  
**Package:** `panel_exp` (GeoX experiment engine)  
**Governance context:** `docs/ROADMAP_V4.md`, `docs/EXPERIMENTATION_PLATFORM_VISION.md`, `docs/MIP_AUDIT_REGISTRY.md`

This document records a **future** roadmap for GeoX / experiment **package-side support agents**. It does **not** implement agents, LLM calls, LangGraph, provider SDKs, runtime orchestration, design execution changes, or new APIs.

---

## Priority decision (record now, implement later)

**Conclusion from architecture discussion:**

GeoX / package-side agents can provide incremental value **later**, but only after the experiment framework already emits typed diagnostics, validation errors, run manifests, failure packets, and safe retry boundaries. Agents should reduce operator burden after the system already knows what failed. They must **not** compensate for weak validation, incomplete deterministic design logic, or missing framework contracts.

| Phase | Focus |
|-------|--------|
| **Now** | Document future agents and boundaries (this artifact). |
| **Near term** | Keep `panel_exp` / GeoX deterministic and diagnostics-first. Strengthen typed validation, design diagnostics, method-governance outputs, run manifests, failure packets, artifact lineage, and allowed/blocked retry actions. |
| **Medium term** | Integrate structured outputs with MIP agent / run-manifest / failure-recovery contracts. |
| **Only later** | Implement package-side support agents if repeated experiment workflow failures show that diagnostic interpretation, design-readiness explanation, readout QA, method-governance explanation, or failure recovery would reduce real operator burden. |

**Do not prioritize package-side agents before the prerequisites in [§ Prerequisites](#prerequisites-before-package-side-agents) are complete.**

---

## Architecture boundary

| Layer | Owns |
|-------|------|
| **MIP** | Orchestration, user-facing agent routing, TrustReport governance, evidence routing, CalibrationSignal mapping, decision-support boundaries |
| **GeoX / `panel_exp`** | Experiment design, power/MDE diagnostics, matchability diagnostics, treatment/control assignment logic, randomization/inference execution, experiment readout artifacts |
| **Future package-side agents** | May help **interpret** package diagnostics and failures — must **not** become the experiment authority |

**Design principle:** Agents are optional support layers around the experiment package. They are **not** the experiment design or causal inference engine.

Package-side agents must **not**:

- choose matched markets
- assign treatment/control
- calculate lift
- calculate power/MDE outside governed diagnostics
- certify feasibility
- promote diagnostic methods
- approve readouts

They **may**:

- explain
- diagnose
- validate
- summarize
- propose safe remediation around **governed** experiment/package diagnostics

---

## Prerequisites before package-side agents

Do **not** prioritize GeoX / experiment package-side agents until **all** of the following are complete:

1. Deterministic design/readout interfaces are stable.
2. Method governance and instrument identity are stable.
3. Power/MDE/matchability diagnostics are typed and machine-readable.
4. Treatment/control assignment constraints are explicit and auditable.
5. Readout artifacts expose effect, uncertainty, metric, estimand, scope, and time-window fields.
6. MIP has `AgentRunManifest`, `AgentFailurePacket`, `AgentResolutionPlan`, and `AgentValidationReport` contracts (or equivalent governed equivalents).
7. Package adapters define safe allowed/blocked actions.

**Recommended timing:**

- **Near term:** Keep GeoX / `panel_exp` deterministic and diagnostic-first.
- **Medium term:** Add typed run manifests, failure packets, and diagnostic summaries.
- **Later:** Add package-side support agents as diagnostic interpreters, contract checkers, readout QA assistants, and failure-recovery assistants.
- **Do not** add package-side agents before deterministic diagnostics and failure packets are stable.

---

## Future typed handoff concepts (prerequisites)

These contract names are **roadmap concepts** — prerequisites before package-side agents become useful. They are not implemented by this artifact.

| Concept | Role |
|---------|------|
| `ExperimentRunManifest` | Top-level run identity, steps, hashes, governance tier |
| `ExperimentStepManifest` | Per-step inputs, outputs, validation status |
| `ExperimentFailurePacket` | Typed failure code, context, safe/blocked actions |
| `DesignDiagnosticSummary` | Structured design pass/fail reasons |
| `PowerDiagnosticSummary` | Simulation power/MDE outputs with semantics |
| `MatchabilityDiagnosticSummary` | Donor pool, balance, eligibility diagnostics |
| `AssignmentAuditPacket` | Randomization seed, constraints, eligibility trace |
| `ExperimentReadoutQAPacket` | Effect, uncertainty, metric, estimand, scope, window QA |
| `ExperimentResolutionPlan` | Safe remediation steps and human-approval boundaries |
| `ExperimentRetryPolicy` | Allowed vs blocked retry actions |
| `ExperimentValidationReport` | Contract validation outcome for a run or step |
| `MethodGovernanceReview` | Method-family status, instrument identity, blocked paths |

MIP-side analogs (`AgentRunManifest`, `AgentFailurePacket`, `AgentResolutionPlan`, `AgentValidationReport`) must exist and align with package adapters before agents add value.

---

## Future GeoX / experiment package-side agents

### 1. Experiment Data Contract Agent

**Purpose:** Validate experiment input data contracts and explain missing or incompatible fields.

**Responsibilities:**

- DMA/state/geo field presence
- week/date field presence
- outcome KPI availability
- media/spend/exposure availability
- pre-period coverage
- post-period coverage
- unit eligibility fields
- treatment/control candidate eligibility
- metric/estimand compatibility

**Allowed:**

- explain why input is invalid
- ask for missing geo/time/outcome/media fields
- route to MIP common intake/readiness/advisory

**Not allowed:**

- invent geo mappings
- infer treatment/control assignment
- estimate lift
- declare design feasible

**Trigger condition:** Add when experiment ingestion contracts and design prerequisites are stable.

---

### 2. Design Feasibility Interpreter Agent

**Purpose:** Explain design diagnostic outputs and why designs pass/fail.

**Responsibilities:**

- matchability diagnostics
- power/MDE diagnostics
- duration sensitivity
- pre-period balance
- donor pool suitability
- treated/control eligibility
- multi-cell feasibility
- scale limitations

**Allowed:**

- summarize diagnostic outputs
- explain why design is blocked
- suggest safe remediation questions
- route to alternative design diagnostics if governed

**Not allowed:**

- declare feasibility without diagnostic output
- calculate power/MDE outside governed package
- choose final design
- assign markets

**Trigger condition:** Add after design diagnostics emit structured pass/fail reasons and safe alternatives.

---

### 3. Randomization / Assignment Guard Agent

**Purpose:** Guard treatment/control assignment workflows against unsafe or unaudited changes.

**Responsibilities:**

- assignment constraint checks
- randomization seed traceability
- holdout/control integrity
- multi-cell assignment consistency
- eligibility-policy adherence
- audit trail checks

**Allowed:**

- flag assignment risks
- check assignment metadata
- request human approval where required
- block unaudited assignment changes

**Not allowed:**

- assign treatment/control directly
- relax constraints silently
- change randomization seed without trace
- override governance policy

**Trigger condition:** Add only when assignment workflows become productionized.

---

### 4. Experiment Readout QA Agent

**Purpose:** Validate experiment readout artifacts before downstream use or CalibrationSignal mapping.

**Responsibilities:**

- effect estimate presence
- standard error / CI presence
- metric alignment
- estimand alignment
- scope/time-window alignment
- freshness
- method/instrument identity
- diagnostic vs governed tier
- CalibrationSignal handoff readiness

**Allowed:**

- summarize readout quality
- flag missing uncertainty
- flag metric/estimand mismatch
- route to CalibrationSignal Specialist / MIP mapping

**Not allowed:**

- estimate missing uncertainty
- certify causality beyond method governance
- promote diagnostic readout to decision support

**Trigger condition:** Add after experiment readout artifacts are standardized and CalibrationSignal handoff is stable.

---

### 5. Method Selection Guard Agent

**Purpose:** Explain and enforce method-family governance when SCM, TBR, DID, AugSynth, placebo, jackknife, bootstrap, and related instruments are available.

**Responsibilities:**

- method-family status
- instrument identity
- governed/restricted/diagnostic/research-only classification
- method assumptions
- input requirements
- known blocked paths
- alternative method suggestions

**Allowed:**

- explain why a method is allowed/restricted/diagnostic-only
- route to governed candidate diagnostics
- surface known method limitations

**Not allowed:**

- use research-only methods for production decisions
- override method registry
- claim aggregate TBR feasibility if blocked
- promote diagnostic placebo/readout to causal decision support

**Trigger condition:** Add after method registry and instrument catalog are stable and integrated with package outputs.

---

### 6. GeoX Failure Recovery / Debugging Agent

**Purpose:** Diagnose package-side design/readout failures from typed errors, run manifests, stack traces, and failure packets.

**Responsibilities:**

- stack trace summarization
- typed design error diagnosis
- safe retry plan
- blocked retry plan
- missing data resolution
- fallback workflow routing

**Allowed:**

- explain what failed
- ask user for missing/corrected data
- recommend safe retry
- recommend fallback to advisory/MMM/readiness path

**Not allowed:**

- retry risky diagnostics indefinitely
- bypass method gates
- silently change design constraints
- approve partial failed runs

**Trigger condition:** Add when run manifests/failure packets exist and package execution is adapter-driven.

---

## Deferred general agents (optional, not immediate)

| Agent | Trigger condition |
|-------|-------------------|
| **ML Engineering / MLOps Specialist** | Experiment jobs are scheduled, packaged, Dockerized, deployed behind APIs, monitored, or integrated with artifact stores |
| **Feature Store Explorer** | Experiment features are served from a production feature store (Feast, Tecton, Databricks Feature Store, or equivalent) |
| **Research Scout** | Core GeoX/method workflows are stable; scouts new design/inference methods and proposes research intake items |
| **Data Connector / Integration** | GA4, ads platform, warehouse, S3/GCS, or other production data connectors are introduced |
| **Privacy/Security Review** | Before persistent uploads, customer workspaces, multi-user deployment, public BYOK, platform-managed keys, or raw data access to LLMs |

---

## Examples

### Example 1 — Missing geo column

**Situation:** User requests GeoX design. Data has week/outcome/media but no DMA/state/geo.

**Experiment Data Contract Agent:**

- Explains structural block (missing geo unit column).
- **Safe options:** ask for geo column; confirm whether an existing market column is geo; route to national MMM/advisory path.
- **Blocked:** invent geo mapping; proceed with design; estimate lift.

---

### Example 2 — Too few eligible DMAs

**Situation:** Design diagnostics find only eight eligible DMAs after filtering.

**Design Feasibility Interpreter Agent:**

- Explains why design is under-supported (eligible unit count below governed threshold).
- **Safe options:** relax eligibility constraints if policy allows; extend pre-period; change geography granularity; route to advisory/alternative measurement path.
- **Blocked:** claim design is feasible; assign treatment/control; calculate final power outside governed diagnostics.

---

### Example 3 — Readout missing uncertainty

**Situation:** Experiment readout has effect estimate but no standard error.

**Experiment Readout QA Agent:**

- Blocks CalibrationSignal readiness.
- **Safe option:** request SE or supported uncertainty field from governed inference path.
- **Blocked:** infer SE from point estimate; certify readout as calibration-ready.

---

### Example 4 — Research-only method requested

**Situation:** User asks to use a research-only method for production decision support.

**Method Selection Guard Agent:**

- Explains method status per method registry (research-only / blocked).
- **Blocked:** promote research-only method to governed decision support; bypass method registry.

---

## Acceptance criteria (this artifact)

- [x] Future GeoX/package-side agents are documented as **deferred**.
- [x] Agent boundaries preserve `panel_exp`/GeoX as deterministic/statistical experiment engine.
- [x] Agents cannot choose matched markets, assign treatment/control, estimate lift, calculate power/MDE outside governed diagnostics, or approve design/readout decisions.
- [x] Run manifest / failure packet prerequisites are documented.
- [x] Experiment Data Contract, Design Feasibility Interpreter, Randomization/Assignment Guard, Experiment Readout QA, Method Selection Guard, and GeoX Failure Recovery agents are described.
- [x] Future ML Engineering, Feature Store, Research Scout, Connector, and Privacy/Security agents are captured with trigger conditions.
- [x] Examples include missing geo, too few DMAs, missing uncertainty, and research-only method requests.

---

## Relationship to current `panel_exp` work

Current active lanes (method validation, selection-gate implementation, release gate) remain **deterministic and diagnostics-first**. This roadmap does **not** change method governance verdicts, production authorization flags, or TrustReport/CalibrationSignal/MMM/LLM boundaries documented in `docs/ROADMAP_V4.md` and `docs/MIP_AUDIT_REGISTRY.md`.

**Next recommended phase (package, not agents):**

1. Typed `ExperimentRunManifest` / `ExperimentFailurePacket` emission from design and readout paths.
2. `DATA_DRIVEN_DESIGN_ESTIMATOR_INFERENCE_SELECTION_GATE_IMPLEMENTATION_PLAN_001` (selection-gate routing).
3. Standardized readout QA fields (effect, uncertainty, metric, estimand, scope, time window).
4. Package adapters with explicit allowed/blocked retry actions.
5. Revisit package-side agents only after repeated operator pain on **interpretation** of stable structured failures.

---

## Verdict

**`future_experiment_package_side_agent_roadmap_defined_no_implementation`**

No agents implemented. No production authorization. GeoX / `panel_exp` remains the deterministic experiment engine.
