---
name: ocas-scout
description: >
  Structured OSINT research on people, companies, and organizations.
  Provenance-backed briefs using a free-first source waterfall.
  Escalates to paid sources only with explicit permission.
---

# Scout

Lawful, provenance-backed OSINT research on people, companies, and organizations. Produces concise auditable briefs using a free-first source waterfall.

## When to use

- Research a person and build a source-backed brief
- Do background research on a company using public sources
- Resolve whether two profiles are the same person with cited sources
- Compile what is publicly knowable about a subject
- Expand a quick lookup into an auditable brief

## When not to use

- Illegal intrusion into private systems
- Credential theft or bypassing access controls
- Covert surveillance
- Speculative doxxing
- Topic research without a person/org focus — use Sift

## Core promise

Scout performs lawful, minimized, provenance-backed OSINT research. Free-first source waterfall. Every finding cites its source. Uncertainty is surfaced, not buried.

## Invariants

1. Legality-first — only publicly available sources without bypassing access controls
2. Minimization — collect only what the research goal requires
3. Provenance for every claim — at least one source reference with URL, retrieval timestamp, and quote
4. Paid sources require explicit permission — Tier 3 needs a recorded PermissionGrant
5. No doxxing by default — private details suppressed unless explicitly permitted
6. Uncertainty must be surfaced — incomplete identity resolution stated clearly

## External interface

Commands:
- `scout.research.start` — begin a new research request with subject and goal
- `scout.research.expand --tier <1|2|3>` — escalate to a higher source tier
- `scout.brief.render` — generate the final markdown brief with findings and sources
- `scout.brief.render_pdf` — optional PDF brief generation
- `scout.status` — return current research state

Config: `.scout/config.json`
- `research.goal_templates` — preset research goal templates
- `waterfall.enabled_tiers` — which tiers are available
- `paid_sources.enabled` — whether Tier 3 is available at all
- `retention.days` — how long to retain research data
- `brief.format` — default output format

## Input contract

ResearchRequest requires: request_id, as_of, subject (type, name, aliases, known_locations, known_handles), goal, constraints (time_budget_minutes, minimize_pii).

Read `references/scout_schemas.md` for exact schema.

## Research workflow

1. Normalize request and subject identity inputs
2. Resolve likely identity matches conservatively
3. Run Tier 1 public-source collection
4. Record provenance for every retained claim
5. Compile preliminary findings with confidence levels
6. Escalate to Tier 2 only if enabled and useful
7. Escalate to Tier 3 only after explicit permission grant is recorded
8. Generate brief with findings, uncertainty, and source log
9. Store request, findings, sources, and decisions locally

When `minimize_pii=true`, suppress unnecessary sensitive details in the final brief.

## Source waterfall

Read `references/scout_source_waterfall.md` for full tier logic.

- **Tier 1** — public web, official sites, news, filings, public social profiles. Automatic.
- **Tier 2** — rate-limited sources, registries, extended datasets. Only if enabled and useful.
- **Tier 3** — paid OSINT providers, background databases. Requires explicit permission grant.

## Output requirements

Markdown brief with: Executive Summary, Identity Resolution Notes, Findings, Risk and Uncertainty, Source Log.

Every finding carries source-backed provenance.

## Support file map

- `references/scout_schemas.md` — ResearchRequest, Finding, PermissionGrant, BriefRecord, DecisionRecord
- `references/scout_source_waterfall.md` — tier definitions, escalation rules, permission gating, minimization
- `references/scout_brief_template.md` — default brief structure and tone

## Storage layout

```
.scout/
  config.json
  requests.jsonl
  sources.jsonl
  findings.jsonl
  decisions.jsonl
  briefs/
  reports/
```

## Validation rules

- Every finding has at least one source reference
- Tier 3 cannot run without recorded permission grant
- When minimize_pii=true, sensitive fields are suppressed
- Brief contains uncertainty where identity resolution is incomplete
