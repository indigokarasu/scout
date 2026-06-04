---
name: ocas-scout
description: 'Scout: structured OSINT research on people, companies, and organizations.
  Use when the user wants a provenance-backed brief, entity resolution across public
  sources, background research with cited sources, or a free-first research workflow
  that escalates to paid sources only with explicit permission. Trigger phrases: ''research
  this person'', ''who is'', ''background check'', ''look up this company'', ''what
  do we know about'', ''update scout''. Do not use for topic research without a person/org
  focus (use Sift) or illegal data collection.

  '
license: MIT
source: https://github.com/indigokarasu/scout
includes:
- references/**
- scripts/**
metadata:
  author: Indigo Karasu (indigokarasu)
  version: 3.0.0
triggers:
- osint research
- people research
- company research
- entity resolution
- provenance brief
---
## Interactive Menu

When invoked interactively (via `/` command), present a two-level menu using the `clarify` tool so the user can pick which function to run.

**Level 1 — Category selection** (max 4 choices):

```python
result = clarify(
    question="What would you like to do?",
    choices=[
        "Research — start new project, expand tier, discover sources",
        "Briefs — render research brief or PDF",
        "Sources — refresh and check source status",
        "Status — show system status",
    ]
)
```

**Level 2 — Action selection** based on Level 1 choice:

- **Research** → clarify with choices: "research.start — Start a new research project", "research.expand — Expand to next tier", "sources.discover — Discover new sources"
- **Briefs** → clarify with choices: "brief.render — Render research brief", "brief.render_pdf — Render brief as PDF"
- **Sources** → clarify with choices: "sources.refresh — Refresh source lists", "sources.status — Show source status"
- **Status** → run "status — Show system status" directly (single action — no sub-menu needed)

After the user selects an action, execute it following the relevant procedure in this skill. Loop back to the menu after each action completes, until the user chooses to exit or sends `/stop`.

### Response parsing

Match the user's response against the full choice string. Extract the action key by splitting on `" — "` and taking the first segment. If the response doesn't match any known choice (user typed free-form via "Other"), match key prefixes case-insensitively. Re-present the current menu level on no match.

### Platform adaptation

On CLI, choices are navigable with arrow keys. On messaging platforms, choices render as a numbered list. The two-level hierarchy ensures no more than 4 options appear at any level on any platform.


## When to Use

- OSINT research on people, companies, or topics
- Structured investigation with source tracking
- Due diligence and background research
- Competitive intelligence gathering
- When Sift needs deeper targeted research
## When NOT to Use

- General topic research (use Sift)
- Image processing (use Look)
- Knowledge graph writes (use Elephas)
- Social graph management (use Weave)

# Scout

Scout conducts lawful OSINT research on people, companies, and organizations, assembling provenance-backed briefs where every claim carries a source reference, retrieval timestamp, and direct quote. It works through a tiered source waterfall — public web first, then rate-limited registries, then paid databases only with explicit permission — collecting no more than the stated research goal requires.

Scout integrates curated person-specific OSINT tools (theHarvester, Maigret, Holehe, h8mail, PhoneInfoga, and others) and dynamically discovers new MCP-wrapped OSINT servers at runtime.

## Responsibility boundary

Scout owns lawful OSINT research on people and organizations with provenance-backed output.

Scout does not own: general topic research (Sift), image processing (Look), knowledge graph writes (Elephas), social graph (Weave), communications (Dispatch).

## Ontology types

Scout works with these types from `spec-ocas-ontology.md`:

- **Entity/Person** — people and their public profiles. The primary entity type Scout extracts.
- **Entity/AI** — AI agents or organizations when relevant to research.
- **Thing/DigitalArtifact** — public documents, profiles, and digital records found during research.

Scout emits Signals to Elephas after each completed research request, for each extracted entity with confidence >= med. Signal `payload.type` is `"Person"` or `"AI"`. `source_journal_type` is `"Research"`. Every emitted Signal must include a `user_relevance` field.

### user_relevance field

Every Signal emitted by Scout carries a `user_relevance` field:

- `"user"` — the signal is relevant to the user's personal knowledge graph
- `"agent_only"` — agent-initiated research with no demonstrated user connection

**Default is `"agent_only"`**. A signal receives `user_relevance: "user"` only when: (1) the user explicitly requested the research, OR (2) the entity connects to a `user_relevance: "user"` Chronicle entry. When in doubt, default to `"agent_only"`.

Signal example:
```json
{
  "signal_id": "sig-scout-20260402-001",
  "source_skill": "ocas-scout",
  "source_journal_type": "Research",
  "emitted_at": "2026-04-02T14:30:00Z",
  "user_relevance": "agent_only",
  "payload": {
    "type": "Person",
    "name": "Jane Doe",
    "confidence": "high",
    "source_refs": ["https://example.com/profile"]
  }
}
```

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

1. Legality-first — only publicly available sources without bypassing access controls
2. Minimization — collect only what the research goal requires
3. Provenance for every claim — at least one source reference with URL, retrieval timestamp, and quote
4. Paid sources require explicit permission — Tier 3 needs a recorded PermissionGrant
5. No doxxing by default — private details suppressed unless explicitly permitted
6. Uncertainty must be surfaced — incomplete identity resolution stated clearly
7. Identity gate — a profile is `verified` only when 2+ seed data points overlap (name + location, etc.). Username match alone = `unverified_lead`; exclude from synthesis
8. Tiered verification — Sherlock results: top 3 verified immediately, 2-3 sampled, remainder only on explicit request
9. Recursion cap — recursive handle discovery allowed for 1 additional pass; hard cap at 2 Sherlock passes per request
10. Person-first tooling — always run theHarvester and OpenSanctions for person research. Run Holehe, h8mail, PhoneInfoga, Ghunt when relevant input data is available.

## Input contract

ResearchRequest requires: request_id, as_of, subject (type, name, aliases, known_locations, known_handles, known_emails, known_phones), goal, constraints (time_budget_minutes, minimize_pii). Read `references/scout_schemas.md` for exact schema.

## Research workflow

Full step-by-step workflow with tool commands, handle expansion logic, identity gating, and verification tiers is in `references/scout_schemas.md`.

**Phase summary:**

1. **Normalize** — parse request, validate subject identity inputs
2. **Tier 1 collection** — run person-specific tools (theHarvester, OpenSanctions) and public web search in parallel
3. **Handle expansion** — extract handles, run Sherlock/Maigret, apply identity gate (inv 7), tiered verification (inv 8), recursion cap at 2 passes (inv 9)
4. **Email/phone tools** — run Holehe, h8mail, EmailRep, Ghunt (if Gmail), PhoneInfoga as data is available
5. **Dynamic MCP discovery** — if Tier 1 results are thin, discover and connect to MCP-wrapped OSINT servers
6. **Compile** — record provenance, assign confidence, escalate to Tier 2/3 only as permitted
7. **Brief** — render markdown brief (see Output requirements). Near-match profiles surfaced explicitly, not discarded.
8. **Emit & journal** — store findings, emit Signal files per confirmed entity (with `user_relevance`), write journal via `scout.journal`

When `minimize_pii=true`, suppress unnecessary sensitive details in the final brief.

## Source waterfall

Read `references/scout_source_waterfall.md` for full tier logic.

- **Tier 1 — Person-specific tools** — theHarvester, OpenSanctions, Sherlock, Maigret, Holehe, h8mail, EmailRep, Ghunt, PhoneInfoga. See `references/scout_person_sources.md` for full list and execution order.
- **Web + platform search** — public web via SearchX (local SearXNG), including Twitter/X, Reddit, LinkedIn, GitHub. Always runs.
- **Tier 2** — rate-limited sources, registries, MCP-discovered servers. Only if enabled and useful.
- **Tier 3** — paid OSINT providers, background databases. Requires explicit permission grant.

## Output requirements

Markdown brief: Executive Summary, Identity Resolution Notes, Findings, Social Graph (if handles found), Digital Footprint (if email/phone tools ran), Risk and Uncertainty, Source Log. Every finding carries source-backed provenance.

- **Social Graph**: verified profiles (platform, URL, discovery method, verification evidence) + unverified leads separately. Omit if no handles found.
- **Digital Footprint**: email accounts (Holehe), breaches (h8mail/HIBP), Google data (Ghunt), phone metadata (PhoneInfoga), email risk (EmailRep), dark web (OnionClaw). Omit if no data available.

Read `references/scout_brief_template.md` for the full template.

## Inter-skill interfaces

Scout writes Signal files to Elephas (via journal signal payload). One Signal per confirmed entity or high-confidence relationship. Use schema from `spec-ocas-shared-schemas.md`. Every Signal must include `user_relevance`. See `spec-ocas-interfaces.md` for signal format.

## Recovery Behavior

Implements the recovery contract from `spec-ocas-recovery.md`.

- **Evidence**: Every run writes to `{agent_root}/commons/data/ocas-scout/evidence.jsonl` (including no-op runs; `not_activity_reason` mandatory when no side effects).
- **Gap detection**: On wake, checks evidence log. If gap exceeds cadence (24h update, 7d research), logs `gap_detected`.
- **Degraded mode**: When tools unavailable, logs `degraded: <tool>` and continues with available sources.
- **Log compaction**: Logs older than 30 days (no-op) or 90 days (error/gap) compacted. Last 7 days retained.

## Storage layout

```
{agent_root}/commons/data/ocas-scout/    → config, JSONL files, briefs/, reports/, caches
{agent_root}/commons/journals/ocas-scout/ → YYYY-MM-DD/{run_id}.json
```

Read `references/scout_config.md` for default config.json and field descriptions.

## OKRs

```yaml
skill_okrs:
  - {name: verified_claim_ratio, target: 0.70, window: 30_runs}
  - {name: entity_resolution_accuracy, target: 0.90, window: 30_runs}
  - {name: source_diversity, target: 6, window: 30_runs}
  - {name: person_tool_coverage, target: 0.80, window: 30_runs}
  - {name: schedule_adherence, target: 0.95, window: 30_days}
  - {name: data_integrity, target: 0.99, window: 30_days}
```

All metrics: maximize. Universal OKRs from spec-ocas-journal.md apply.

## Optional skill cooperation

- **Sherlock** — username-to-platform expansion during handle expansion. Falls back to `sift.search("site:<platform> '<handle>'")` if unavailable.
- **Sift** — web search during Tier 1; Sift-dork fallback when Sherlock unavailable
- **Look** — reverse image search for person identification when photo available
- **Weave** — read social graph for identity context before research (read-only)
- **Elephas** — emit Signal files for Chronicle promotion
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

Monitors: [awesome-osint-mcp-servers](https://github.com/soxoj/awesome-osint-mcp-servers) (weekly), [awesome-osint](https://github.com/jivoi/awesome-osint) (monthly), [API-s-for-OSINT](https://github.com/cipher387/API-s-for-OSINT) (monthly). New tools classified by tier → added to `references/scout_person_sources.md`. See `references/scout_mcp_discovery.md` for dynamic discovery.

## Gotchas

- **Tier 3 sources require explicit permission** — Paid OSINT providers and background databases (Tier 3) cannot be queried without a recorded PermissionGrant. The skill will silently skip Tier 3 even if credentials are configured.
- **User relevance defaults to `agent_only`** — Signals emitted to Elephas default to `user_relevance: "agent_only"` unless the user explicitly requested the research or the entity connects to a known `user` Chronicle entry. This means most Scout entities won't be promoted.
- **Hard cap at 2 Sherlock passes** — Recursive handle discovery is allowed for exactly 1 additional pass (2 total). Further recursion is silently blocked regardless of leads found.
- **Identity gate requires 2+ data points** — A username match alone produces only `unverified_lead` status. Profiles are `verified` only when 2+ seed data points overlap (name + location, etc.).
- **minimize_pii suppresses home addresses and personal details** — When the user sets `minimize_pii=true`, the final brief suppresses unnecessary sensitive details even if they were found during research. Re-run without the flag to see full data.
- **`execute_code` blocked in cron mode** — When Scout runs as a scheduled cron job, `execute_code` is denied by policy. Use `terminal()` for all shell commands and Python workarounds. Structure multi-step work as a single piped `terminal()` call rather than relying on `execute_code` for programmatic logic.
- **`gh api` base64 content is unreliable for counting** — `gh api repos/<owner>/<repo>/readme --jq '.content' | base64 -d` can silently return truncated or empty results. For fetching raw GitHub README content, use `curl -s "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/README.md"` instead. This returns clean text that `wc -l` and `grep` can process directly.
- **Branch names vary across repos** — `jivoi/awesome-osint` uses `master` (not `main`). Always verify branch name with a quick `curl -s -o /dev/null -w "%{http_code}"` probe before fetching content.
- **curl timeout for unreliable endpoints** — Some GitHub endpoints return 0 bytes under rate-limiting. Use `--max-time 15` and check HTTP status code before processing output.

## Support File Map

| File | When to read |
|---|---|
| `references/scout_schemas.md` | Before requests/findings/briefs; full workflow steps |
| `references/scout_config.md` | Default config.json and field descriptions |
| `references/scout_source_waterfall.md` | Before tier selection or escalation |
| `references/scout_brief_template.md` | Before rendering briefs |
| `references/scout_person_sources.md` | At start of every person research run |
|| `references/scout_mcp_discovery.md` | Before `scout.sources.discover`; before Tier 2 escalation |
|| `references/rapidapi-osint-params.md` | Before RapidAPI enrichment; param patterns per platform |
|| `references/rapidapi-enrichment-workflow.md` | During Phase 3/4 research; RapidAPI person/company enrichment pipelines |
|| `references/journal.md` | Before scout.journal; at end of every run |
|| `references/self_update.md` | Before running `scout.update`; when debugging self-update failures |

## Update command

This skill self-updates every 24 hours via:

```bash
scout.update
```

This pulls the latest version from GitHub and restarts the skill's background tasks if applicable.
