# Build Specification: `ocas-scout` v1.1.0

## Skill identity
- Skill name: `ocas-scout`
- Version: `1.1.0`
- Author: `Indigo Karasu`
- Email: `mx.indigo.karasu@gmail.com`
- Skill type: `workflow`

## One-sentence build objective
Build a complete, ready-to-install Agent Skill package that performs provenance-backed OSINT research on people, companies, and organizations using a lawful free-first source waterfall, produces concise auditable briefs, and escalates to paid or higher-friction sources only with explicit permission.

## Responsibility Boundary

Scout specializes in investigative intelligence about people and organizations.

Sift specializes in topic research, fact discovery, and general web knowledge.

If the primary entity of a query is a person, Scout should be invoked.

---

## Build rules
The coder must build a real Agent Skill package, not a design memo or partial scaffold.

The package must be self-contained and installable.

The package must preserve the original Scout functional surface, including:
- structured research requests
- a free-first source waterfall
- optional tier escalation
- explicit permission gating for paid sources
- provenance-backed findings
- concise brief generation
- minimization rules
- no-doxxing constraints
- per-run status visibility
- local storage layout for requests, findings, sources, decisions, and briefs

Do not compress away capabilities for the sake of brevity.

Keep `SKILL.md` operational and routing-aware, but include enough precision that a coder LLM can build the package correctly.

## Critical installability requirement
`SKILL.md` must begin on line 1 with valid YAML frontmatter delimited by `---`.

The YAML frontmatter must be syntactically valid and parseable.

Do not place any prose, comments, blank lines, code fences, or BOM characters before the opening `---`.

The build is invalid if `SKILL.md` does not start with valid YAML frontmatter.

## Required package output
Produce this package:

```text
ocas-scout/
  skill.json
  SKILL.md
  references/
    scout_schemas.md
    scout_source_waterfall.md
    scout_brief_template.md
```

Do not add `scripts/` unless the implementation genuinely requires one. This spec does not require scripts.

## `skill.json` requirements
Create a valid `skill.json` with at least these fields:
- `name`: `ocas-scout`
- `version`: `1.0.1`
- `description`: routing-optimized description
- `author`: `Indigo Karasu`
- `email`: `mx.indigo.karasu@gmail.com`

The description must make clear that Scout should be used when the user wants structured OSINT-style research, background research, entity resolution, source-backed briefing, or escalation from quick lookup to provenance-backed findings.

The description must also make clear that Scout is not for illegal collection, covert intrusion, or speculative doxxing.

## `SKILL.md` requirements
### YAML frontmatter
`SKILL.md` must start exactly with valid YAML frontmatter. Include fields that match the package identity and runtime intent.

Use frontmatter shaped like this, with valid YAML syntax:

```yaml
---
name: scout
version: 1.1.0
description: >
  Use this skill when the user wants structured OSINT research on a person,
  company, or organization; a provenance-backed brief; entity resolution across
  public sources; or a free-first research workflow that can escalate to
  higher-friction or paid sources only with explicit permission.
metadata:
  openclaw:
    id: ocas-scout
    emoji: "🛰️"
    requires:
      bins: ["python3"]
    install:
      - kind: pip
        package: httpx
      - kind: pip
        package: pydantic
    storage:
      root: ".scout"
    permissions:
      os: []
      network: ["required:osint_sources"]
---
```

The coder may add additional valid YAML fields if useful, but must keep the YAML parseable.

### Required `SKILL.md` sections
After the YAML frontmatter, `SKILL.md` must contain these sections in this order:
1. `# Scout (ocas-scout) — OSINT Briefing Skill`
2. `## When to use`
3. `## When not to use`
4. `## Core promise`
5. `## Invariants`
6. `## External interface`
7. `## Input contract`
8. `## Research workflow`
9. `## Source waterfall`
10. `## Output requirements`
11. `## Support file map`
12. `## Storage layout`
13. `## Validation rules`

### Section content requirements
#### `## When to use`
Must include realistic trigger language such as:
- research this person
- build a source-backed brief on this company
- do background research on this organization
- resolve whether these identities are the same person
- compile what is publicly knowable about this subject
- expand this quick lookup into an auditable brief

#### `## When not to use`
Must explicitly exclude:
- illegal intrusion
- credential theft
- bypassing access controls
- covert surveillance
- speculative doxxing
- exposing private addresses or phone numbers without clear lawful and user-approved need

#### `## Core promise`
State clearly that Scout performs lawful, minimized, provenance-backed OSINT research using a free-first waterfall and outputs concise briefs with uncertainty called out.

#### `## Invariants`
Include these non-negotiable rules:
- legality-first
- minimization
- provenance for every claim
- paid sources require explicit permission
- no doxxing by default
- uncertainty must be surfaced explicitly

#### `## External interface`
Include these commands:
- `scout.research.start`
- `scout.research.expand --tier <1|2|3>`
- `scout.brief.render`
- `scout.brief.render_pdf` as optional
- `scout.status`

Include these recommended hooks:
- contact or subject crosses threshold event from another system
- optional end-of-day reporting

Include config file path and fields:
- `.scout/config.json`
- `research.goal_templates`
- `waterfall.enabled_tiers`
- `paid_sources.enabled`
- `retention.days`
- `brief.format`

#### `## Input contract`
Define `ResearchRequest` with:
- `request_id`
- `as_of`
- `subject`
- `goal`
- `constraints`

The `subject` object must support:
- `type` as `person|company|org`
- `name`
- `aliases`
- `known_locations`
- `known_handles`

The `constraints` object must support:
- `time_budget_minutes`
- `minimize_pii`

#### `## Research workflow`
Describe the ordered process:
1. normalize request and subject identity inputs
2. resolve likely identity matches conservatively
3. run Tier 1 public-source collection first
4. record provenance for every retained claim
5. compile preliminary findings with confidence levels
6. escalate to Tier 2 only if allowed by config and useful to the goal
7. escalate to Tier 3 only after an explicit permission grant is recorded
8. generate concise brief with findings, uncertainty, and source log
9. store request, findings, sources, and decisions locally

The workflow must explicitly say that when `minimize_pii=true`, unnecessary sensitive details are suppressed in the final brief.

#### `## Source waterfall`
State the three tiers clearly.

Tier 1:
- public web search
- official sites
- reputable news
- public filings
- public social profiles
- automatic by default

Tier 2:
- rate-limited sources
- registries
- extended public datasets
- allowed only if enabled and useful

Tier 3:
- paid OSINT providers
- background databases
- any higher-friction paid source
- requires explicit permission grant record before use

#### `## Output requirements`
Require markdown brief output with these sections:
- Executive summary
- Identity resolution notes
- Findings
- Risk and uncertainty
- Source log

Require every finding to carry source-backed provenance.

#### `## Support file map`
Point to:
- `references/scout_schemas.md` for data contracts and JSON examples
- `references/scout_source_waterfall.md` for tier logic and escalation rules
- `references/scout_brief_template.md` for the default brief structure and tone

#### `## Storage layout`
Require this exact layout:

```text
.scout/
  config.json
  requests.jsonl
  sources.jsonl
  findings.jsonl
  decisions.jsonl
  briefs/
  reports/
```

#### `## Validation rules`
Must include at least:
- every finding has at least one source reference
- Tier 3 cannot run without explicit permission grant record
- when `minimize_pii=true`, sensitive fields are suppressed by default unless clearly needed and permitted
- the brief must contain uncertainty where identity resolution is incomplete

## Reference file requirements
### `references/scout_schemas.md`
This file must define and exemplify:
- `ResearchRequest`
- `Finding`
- `PermissionGrant`
- `BriefRecord`
- `DecisionRecord` for Scout-specific decisions

`Finding` must include:
- `claim`
- `confidence` as `high|med|low`
- `source_refs`

Each `source_ref` must include:
- `url`
- `retrieved_at`
- `quote`

### `references/scout_source_waterfall.md`
This file must explain:
- the intent of the free-first waterfall
- what belongs in Tier 1, Tier 2, Tier 3
- how to decide whether escalation is justified
- how permission gating works for Tier 3
- how minimization applies at each tier
- when to stop instead of escalating further

### `references/scout_brief_template.md`
This file must provide a concrete markdown brief template that the skill can follow.

It must preserve the required brief sections and bias toward concise executive-useful reporting rather than essay-style output.

## Exact constraints
### Naming
Use `ocas-scout` consistently in package metadata.

### Paths
Use `.scout/` as the storage root.

### Metadata
Use:
- Author: `Indigo Karasu`
- Email: `mx.indigo.karasu@gmail.com`
- Version: `1.1.0`

### Precision-required areas
Be exact about:
- YAML frontmatter validity in `SKILL.md`
- command names
- config path and keys
- storage layout
- tier escalation logic
- explicit permission gating for Tier 3
- required brief sections
- provenance requirements for every finding

### Flexible areas
Minor prose wording may vary as long as meaning is preserved.

## Validation requirements
A build is complete only if all of the following pass.

### Routing validation
Should trigger:
- “Research this founder and make a source-backed brief.”
- “Do background research on this company using public sources first.”
- “Figure out whether these two profiles are the same person and cite your sources.”
- “Expand this quick lookup into an auditable public-record brief.”

Should not trigger:
- “Hack this person’s email.”
- “Find their home address and private phone number.”
- “Bypass a login wall and scrape the data.”
- “Write a fictional spy dossier with invented facts.”

### Structural validation
Confirm:
- `skill.json` exists
- `SKILL.md` exists
- `SKILL.md` starts on line 1 with valid YAML frontmatter
- YAML frontmatter parses cleanly
- all three required reference files exist
- `SKILL.md` points to the reference files
- package paths and names are consistent

### Usefulness validation
Confirm:
- the skill has one sharp promise
- first useful action is obvious
- escalation rules are explicit
- provenance requirements are explicit
- minimization and no-doxxing boundaries are explicit
- the package is installable and operational without hidden context

## Optional Skill Cooperation

This skill may cooperate with other skills when present but must never depend on them.
If a cooperating skill is absent, this skill must still function normally.

- Weave — query social graph for identity context and relationship history.
- Elephas — query Chronicle for prior entity records and known aliases.
- Sift — delegate general web research when Scout needs non-person topic context.

---

## Journal Outputs

This skill emits the following journal types as defined in the OCAS Journal Specification (spec-ocas-Journals.md):

- Observation Journal
- Research Journal

Scout emits Observation Journal entries for discovered signals and Research Journal entries for completed research sessions with source logs.

---

## Visibility

visibility: public

---

## Universal OKRs

This skill must implement the universal OKRs defined in the OCAS Journal Specification (spec-ocas-Journals.md).

Required universal OKRs:

- Reliability: success_rate >= 0.95, retry_rate <= 0.10
- Validation Integrity: validation_failure_rate <= 0.05
- Efficiency: latency trending downward, repair_events <= 0.05
- Context Stability: context_utilization <= 0.70
- Observability: journal_completeness = 1.0

Skill-specific OKRs should be defined in the built SKILL.md to measure domain-relevant outcomes.

---

## Final response format for the coder LLM
Return:
1. package tree
2. full contents of every file
3. brief validation summary confirming YAML frontmatter validity and package completeness

Do not return a planning memo, process narration, or references to any absent upstream design document.
