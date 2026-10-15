---
license: MIT
name: ocas-scout
description: 'NOT for VPN/captcha or booking tasks. Structured OSINT research on people, companies, and organizations. Use for provenance-backed briefs, entity resolution across public sources, background research with cited sources, or free-first research workflows that escalate to paid sources only with explicit permission. Use Sift for topic research without a person/org focus. Never for illegal data collection. Guard front-loaded into the 57-char router window on 2026-10-15: a prior auto-load fired on a VPN/captcha question, and the existing "Do not use for..." exclusion sat at char 276 where the router cannot see it.'
source: https://github.com/<agent-handle>/scout
includes:
- references/**
- scripts/**
metadata:
  author: Indigo Karasu (indigokarasu)
  version: 4.1.0
  hermes:
    category: research
    tags:
    - OSINT
    - research
    - people
    - companies
    - investigation
    - OCAS-core
    config:
    - key: SCOUT_SEARXNG_URL
      description: Local SearXNG search endpoint used for Tier 1 web search.
      default: http://127.0.0.1:8888/search
    - key: SCOUT_OSINT_VENV
      description: Directory containing OSINT tool binaries.
      default: /root/.hermes/tools/osint-venv
    - key: HERMES_OSINT_CACHE
      description: Base cache directory for large OSINT datasets (e.g. ICIJ offshore leaks).
      default: ~/.cache/hermes-osint
    - key: HERMES_OSINT_UA
      description: User-Agent override for Wikimedia policy compliance.
    - key: SCOUT_GITHUB_TOKEN
      description: GitHub token for source refresh and MCP discovery (optional).
    - key: OPENCORPORATES_API_TOKEN
      description: OpenCorporates API token (optional).
    - key: COURTLISTENER_TOKEN
      description: CourtListener API token (optional).
    - key: SENATE_LDA_TOKEN
      description: Senate lobbying disclosure API token (optional).
tags:
- OSINT
- research
- people
- companies
- investigation
triggers:
- osint research
- people research
- company research
- entity resolution
- provenance brief
---

**Support files:** `references/support-file-map.md` indexes the bundled files not covered inline in this skill — check it before working from assumptions about what is (not) available.

## Interactive Menu

When invoked interactively, present a two-level menu. See `references/interactive-menu.md` for the full menu structure.

## When to Use

- OSINT research on people, companies, or topics
- Structured investigation with source tracking
- Due diligence and background research
- Competitive intelligence gathering
- When Sift needs deeper targeted research
## When NOT to Use

- General topic research (use Sift)
- Image processing (use Look)
- Knowledge graph writes (use Chronicle)
- Social graph management (use Weave)

# Scout

Lawful OSINT on people, companies, and organizations with provenance-backed briefs. Tiered source waterfall (public web → registries → paid with explicit permission) and minimization by research goal, because paid access requires consent and rate-limited registries require quota care. Integrates person-specific tools (theHarvester, Maigret, Holehe, h8mail, PhoneInfoga), public-records fetchers (SEC EDGAR, USAspending, OFAC, ICIJ, ACRIS, OpenCorporates, CourtListener, Wayback, GDELT), and dynamic MCP discovery.

## Responsibility boundary

Scout owns lawful OSINT research on people and organizations with provenance-backed output.

Scout does not own: general topic research (Sift), image processing (Look), knowledge graph writes (Chronicle), social graph (Weave), communications (Dispatch).

## Ontology types

Scout works with Entity/Person, Entity/AI, and Thing/DigitalArtifact (see [[spec-ocas-ontology.md]]). It emits Chronicle Signals (type `Person` or `AI`, `source_journal_type: Research`) with a mandatory `user_relevance` field defaulting to `agent_only` unless the user requested the research or the entity links to a `user` Chronicle entry. Full schema and signal shape: `references/scout_schemas.md`.

## Commands
## Commands

- `scout.research.start` — begin a new research request with subject and goal
- `scout.research.expand --tier <1|2|3>` — escalate to a higher source tier
- `scout.brief.render` — generate the final markdown brief with findings and sources
- `scout.brief.render_pdf` — optional PDF brief generation
- `scout.status` — return current research state
- `scout.journal` — write journal for the current run; called at end of every run
- `scout.update` — pull latest from GitHub source; preserves journals and data
- `scout.sources.discover` — discover new MCP servers relevant to current research
- `scout.sources.refresh` — refresh curated source lists from GitHub
- `scout.sources.status` — show state of dynamic source discovery

## Invariants

See `references/invariants.md` for the ten non-negotiable rules (legality, minimization, provenance, permission gate, no doxxing, surfacing uncertainty, identity gate, tiered verification, recursion cap, person-first tooling).

## Input contract

ResearchRequest requires: request_id, as_of, subject (type, name, aliases, known_locations, known_handles, known_emails, known_phones), goal, constraints (time_budget_minutes, minimize_pii). Read `references/scout_schemas.md` for exact schema.

Example input shape:
```json
{"request_id":"req-001","as_of":"2026-10-15T...Z","subject":{"type":"person","name":"Jane Doe"},"goal":"background","constraints":{"time_budget_minutes":30,"minimize_pii":true}}
```

## Workflow

Full step-by-step workflow, tool commands, handle-expansion logic, identity gating, and verification tiers are in `references/scout_schemas.md`. Phase checklist summarized there (Normalize → Tier 1 collection → Handle expansion → Email/phone tools → Public records → Entity resolution → Optional timing correlation → Dynamic MCP discovery → Compile → Brief → Emit & journal).

## Source waterfall

Tiers and source selection: `references/scout_source_waterfall.md`, `references/scout_person_sources.md`, `references/scout_public_records.md`. Tier 1 (person tools + web) always runs; Tier 1.5 public records for company/org research or when corporate ties surface; Tier 2-3 only when enabled/permitted.

## Output requirements

Markdown brief per `references/scout_brief_template.md` (Executive Summary, Identity Resolution Notes, Findings, Social Graph, Digital Footprint, Public Records, Risk and Uncertainty, Source Log). Omit empty subsections; every finding must carry source-backed provenance.

## Inter-skill interfaces

Scout writes Signal files to Chronicle (via journal signal payload). One Signal per confirmed entity or high-confidence relationship. Use schema from [[`spec-ocas-shared-schemas.md` ⚠️ Pending spec] ⚠️ Pending spec — not yet authored]. Every Signal must include `user_relevance`. See [[`spec-ocas-interfaces.md` ⚠️ Pending spec] ⚠️ Pending spec — not yet authored] for signal format.

## Error Handling

| Failure | Symptom | Handling |
|---|---|---|
| A bundled fetch script exits non-zero (e.g. 429/403) | stderr diagnostic, exit code 2-4 | Log `degraded: <tool>` and continue with remaining sources |
| SearXNG unreachable | Connection refused / timeout | Retry up to 3 times; if still down, skip web search and note gap in brief |
| ICIJ bulk CSV missing or corrupt | Cache load raises IOError | Re-download once; on second failure, skip ICIJ and record `degraded` |
| No profile candidate above identity threshold | Identity gate unresolved | Report `unverified_lead` results explicitly; do not promote to synthesis |
| RapidAPI returns “not subscribed” | 403 with subscription error | Treat as tier-gated, not broken; skip provider and try alternates |
| Tool not installed in OSINT venv | `ModuleNotFoundError` | Log degraded tool; continue; surface install hint in brief footer |
| Tier 3 requested without PermissionGrant | Permission check fails | Skip Tier 3 silently and note in brief that it was withheld |
| Recursive handle expansion exceeds cap | Second Sherlock pass completed | Block further recursion hard; fold settled leads into report |

## Recovery Behavior

This section defines error handling and recovery procedures for all scout jobs.

Implements the recovery contract from `spec-ocas-recovery.md`.

- **Evidence**: Every run writes to `{agent_root}/commons/data/ocas-scout/evidence.jsonl` (including no-op runs; `not_activity_reason` mandatory when no side effects).
- **Gap detection**: On wake, checks evidence log. If gap exceeds cadence (24h update, 7d research), logs `gap_detected`.
- **Degraded mode**: When tools unavailable, logs `degraded: <tool>` and continues with available sources.
- **Log compaction**: Logs older than 30 days (no-op) or 90 days (error/gap) compacted. Last 7 days retained.

## Storage layout

See `references/storage-layout.md` for directory structure. Read `references/scout_config.md` for default config.json and field descriptions.

## OKRs

See `references/okrs.md` for skill OKR definitions.

## Optional skill cooperation

- **Sherlock** — username-to-platform expansion during handle expansion. Falls back to `sift.search("site:<platform> '<handle>'")` if unavailable.
- **Sift** — web search during Tier 1; Sift-dork fallback when Sherlock unavailable
- **Look** — reverse image search for person identification when photo available
- **Weave** — read social graph for identity context before research (read-only)
- **Chronicle** — emit Signal files for Chronicle promotion
- **native-mcp / mcporter** — connect to dynamically discovered MCP-wrapped OSINT servers
- **RapidAPI** — structured social media enrichment via `rapidapi_call` (see RapidAPI Enrichment Workflow below)

---
## RapidAPI Enrichment Workflow

During Phase 3 (Handle Expansion) and Phase 4 (Email/Phone Tools), use RapidAPI social media endpoints to enrich profiles with structured data that free tools (Sherlock/Maigret) can't provide. Full procedure including person/company enrichment pipelines, rate limiting, and tier integration: see `references/rapidapi-enrichment-workflow.md`.

## Journal outputs

- Observation Journal — research runs producing findings
- Research Journal — structured multi-source research sessions

Journals must include an `entities_observed` array (name, type, confidence, user_relevance). See `references/journal.md` for schema.

## Visibility

public

## Initialization

On first invocation, run `scout.init`: create data dirs + default config, create empty JSONL files, create journal dir, register cron jobs, log DecisionRecord, set up SearchX (SearXNG + nginx), verify person-specific tools (install missing via pip), check dark web tools (OnionClaw + Tor, non-blocking).

## Background tasks

| Job | Schedule | Command |
|---|---|---|
| `scout:update` | `0 0 * * *` (midnight daily) | `scout.update` |
| `scout:research` | `0 9 * * 1` (Monday 9am) | `scout.research` |
| `scout:sources-refresh` | `0 6 * * 0` (Sunday 6am) | `scout.sources.refresh` |

## Self-update

`scout.update` pulls the latest package from the `source:` URL in this file's frontmatter. Runs silently — no output unless the version changed or an error occurred.

Read `references/self_update.md` for the full self-update procedure.

## External Catalog Review

Monitors: [awesome-osint-mcp-servers](https://github.com/soxoj/awesome-osint-mcp-servers) (weekly), [awesome-osint](https://github.com/jivoi/awesome-osint) (monthly), [API-s-for-OSINT](https://github.com/cipher387/API-s-for-OSINT) (monthly). New tools classified by tier → added to `references/scout_person_sources.md`. See `references/scout_mcp_discovery.md` for dynamic discovery. See `references/sources-refresh.md` for the concrete refresh procedure that runs on the `scout:sources-refresh` cron.

## Gotchas

See `references/gotchas.md` for the full list (Tier 3 permission, user_relevance default, Sherlock cap, identity gate, minimize_pii, RapidAPI, ICIJ cache, statistical-significance caveat, etc.).

## Support File Map

| File | When to read |
|---|---|
| `references/support-file-map.md` | When adding or verifying bundled files; consult before assuming a tool is absent |
| `references/scout_schemas.md` | Before requests/findings/briefs; full workflow steps |
| `references/scout_config.md` | Default config.json and field descriptions |
| `references/scout_source_waterfall.md` | Before tier selection or escalation |
| `references/scout_brief_template.md` | Before rendering briefs |
| `references/scout_person_sources.md` | At start of every person research run |
| `references/scout_public_records.md` | At start of every company/org research run; when person research reveals corporate ties; before Phase 5 |
| `references/scout_mcp_discovery.md` | Before `scout.sources.discover`; before Tier 2 escalation |
| `references/sources-refresh.md` | Before `scout.sources.refresh`; before weekly cron refresh runs |
| `references/rapidapi-osint-params.md` | Before RapidAPI enrichment; param patterns per platform |
| `references/rapidapi-enrichment-workflow.md` | During Phase 3/4 research; RapidAPI person/company enrichment pipelines |
| `references/journal.md` | Before scout.journal; at end of every run |
| `references/self_update.md` | Before running `scout.update`; when debugging self-update failures |

## Update command

This skill self-updates every 24 hours via:

```bash
scout.update
```

This pulls the latest version from GitHub and restarts the skill's background tasks if applicable.