---
name: ocas-scout
description: >
  Scout: structured OSINT research on people, companies, and organizations.
  Use when the user wants a provenance-backed brief, entity resolution across
  public sources, background research with cited sources, or a free-first
  research workflow that escalates to paid sources only with explicit
  permission. Trigger phrases: 'research this person', 'who is', 'background
  check', 'look up this company', 'what do we know about', 'update scout'. Do
  not use for topic research without a person/org focus (use Sift) or illegal
  data collection.
metadata:
  author: Indigo Karasu
  email: mx.indigo.karasu@gmail.com
  version: "2.9.3"
  hermes:
    tags: [research, osint, people]
    category: signal
    cron:
      - name: "scout:update"
        schedule: "0 0 * * *"
        command: "scout.update"
      - name: "scout:research"
        schedule: "0 9 * * 1"
        command: "scout.research"
  openclaw:
    skill_type: system
    visibility: public
    filesystem:
      read:
        - "{agent_root}/commons/data/ocas-scout/"
        - "{agent_root}/commons/journals/ocas-scout/"
      write:
        - "{agent_root}/commons/data/ocas-scout/"
        - "{agent_root}/commons/journals/ocas-scout/"
    self_update:
      source: "https://github.com/indigokarasu/scout"
      mechanism: "version-checked tarball from GitHub via gh CLI"
      command: "scout.update"
      requires_binaries: [gh, tar, python3]
    requires:
      credentials:
        - name: "hunter_api_key"
          description: "Hunter.io API key for professional email discovery and verification"
          required: false
    cron:
      - name: "scout:update"
        schedule: "0 0 * * *"
        command: "scout.update"
      - name: "scout:research"
        schedule: "0 9 * * 1"
        command: "scout.research"
---

# Scout

Scout conducts lawful OSINT research on people, companies, and organizations, assembling provenance-backed briefs where every claim carries a source reference, retrieval timestamp, and direct quote. It works through a tiered source waterfall — public web first, then rate-limited registries, then paid databases only with explicit permission — collecting no more than the stated research goal requires.

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

## Responsibility boundary

Scout owns lawful OSINT research on people and organizations with provenance-backed output.

Scout does not own: general topic research (Sift), image processing (Look), knowledge graph writes (Elephas), social graph (Weave), communications (Dispatch).

## Ontology types

Scout works with these types from `spec-ocas-ontology.md`:

- **Entity/Person** — people and their public profiles. The primary entity type Scout extracts.
- **Entity/AI** — AI agents or organizations when relevant to research.
- **Thing/DigitalArtifact** — public documents, profiles, and digital records found during research.

Scout emits Signals to Elephas after each completed research request, for each extracted entity with confidence ≥ med. Signal `payload.type` is `"Person"` or `"AI"`. `source_journal_type` is `"Research"`. Every emitted Signal must include a `user_relevance` field.

### user_relevance field

Every Signal emitted by Scout carries a `user_relevance` field with one of two values:

- `"user"` — the signal is relevant to the user's personal knowledge graph
- `"agent_only"` — the signal is agent-initiated research with no demonstrated user connection

**Default is `"agent_only"`** because most Scout research is agent-initiated (e.g., scheduled weekly runs, background enrichment). A signal receives `user_relevance: "user"` only when:

1. The user explicitly requested the research (e.g., "research this person", "who is X", or any direct user prompt that triggered the run), OR
2. The entity has a demonstrated connection to an entity already in Chronicle with `user_relevance: "user"` (check Chronicle before emitting if feasible).

When in doubt, default to `"agent_only"`. Elephas can promote later if a user connection is established.

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

## Invariants

1. Legality-first — only publicly available sources without bypassing access controls
2. Minimization — collect only what the research goal requires
3. Provenance for every claim — at least one source reference with URL, retrieval timestamp, and quote
4. Paid sources require explicit permission — Tier 3 needs a recorded PermissionGrant
5. No doxxing by default — private details suppressed unless explicitly permitted
6. Uncertainty must be surfaced — incomplete identity resolution stated clearly

## Input contract

ResearchRequest requires: request_id, as_of, subject (type, name, aliases, known_locations, known_handles), goal, constraints (time_budget_minutes, minimize_pii).

Read `references/scout_schemas.md` for exact schema.

## Research workflow

1. Normalize request and subject identity inputs
2. Resolve likely identity matches conservatively
3. Run Tier 1 public-source collection (via Sift shared search stack)
4. Record provenance for every retained claim
5. Compile preliminary findings with confidence levels
6. Escalate to Tier 2 only if enabled and useful
7. Escalate to Tier 3 only after explicit permission grant is recorded
8. Generate brief with findings, uncertainty, and source log
9. Store request, findings, sources, and decisions locally
10. Emit Signal files for confirmed entities and relationships to the `signal` payload field in the journal entry. Use Signal schema from `spec-ocas-shared-schemas.md`. One file per entity or relationship with sufficient confidence. Every Signal must include `user_relevance` (see Ontology types section). Set `"user"` if the run was user-initiated or the entity connects to a `user_relevance: "user"` Chronicle entry; otherwise `"agent_only"`.
11. Write journal via `scout.journal`

When `minimize_pii=true`, suppress unnecessary sensitive details in the final brief.

## Source waterfall

Read `references/scout_source_waterfall.md` for full tier logic.

All configured sources fire in parallel. Results are merged and deduplicated. A source without a configured key is silently skipped.

- **Web + platform search** — public web via Sift's shared search stack (Twitter/X, Reddit, LinkedIn, GitHub agent-reach). Always runs.
- **Hunter.io** — professional email discovery, domain search, and author identification. Runs automatically when `HUNTER_API_KEY` is set. Three queries in parallel: `domain-search` (all emails at target company), `email-finder` (find email for name + domain), `author-finder` (identify article authors by URL). Free tier: 50 requests/month.
- **Tier 2** — rate-limited sources, registries, extended datasets. Only if enabled and useful.
- **Tier 3** — paid OSINT providers, background databases. Requires explicit permission grant.

## Output requirements

Markdown brief with: Executive Summary, Identity Resolution Notes, Findings, Professional Contacts (if Hunter results available), Risk and Uncertainty, Source Log. Every finding carries source-backed provenance.

**Professional Contacts section** (included when Hunter returns results):
- List each discovered email with: address, confidence score (Hunter-native 0–100), type (`personal` or `generic`), source count
- Provenance tag: `hunter.io`
- Do not include emails with confidence < 50 unless explicitly requested

## Inter-skill interfaces

Scout writes Signal files to Elephas (via journal signal payload): the `signal` payload field in the journal entry

Emit one Signal file per confirmed entity or high-confidence relationship discovered during research. Use the Signal schema from `spec-ocas-shared-schemas.md`. Every Signal must include the `user_relevance` field (`"user"` or `"agent_only"`). Elephas decides promotion.

See `spec-ocas-interfaces.md` for signal format.

## Storage layout

```
{agent_root}/commons/data/ocas-scout/
  config.json
  requests.jsonl
  sources.jsonl
  findings.jsonl
  decisions.jsonl
  briefs/
  reports/

{agent_root}/commons/journals/ocas-scout/
  YYYY-MM-DD/
    {run_id}.json
```


Default config.json:
```json
{
  "skill_id": "ocas-scout",
  "skill_version": "2.3.0",
  "config_version": "1",
  "created_at": "",
  "updated_at": "",
  "waterfall": {
    "enabled_tiers": [1, 2]
  },
  "paid_sources": {
    "enabled": false
  },
  "brief": {
    "format": "markdown"
  },
  "retention": {
    "days": 90,
    "max_records": 10000
  }
}
```

## OKRs

Universal OKRs from spec-ocas-journal.md apply to all runs.

```yaml
skill_okrs:
  - name: verified_claim_ratio
    metric: fraction of findings with at least one verified source reference
    direction: maximize
    target: 0.70
    evaluation_window: 30_runs
  - name: entity_resolution_accuracy
    metric: fraction of identity resolutions confirmed correct
    direction: maximize
    target: 0.90
    evaluation_window: 30_runs
  - name: source_diversity
    metric: median unique source domains per brief
    direction: maximize
    target: 6
    evaluation_window: 30_runs
```

## Optional skill cooperation

- Weave — read social graph (read-only) for identity context
- Elephas — optionally emit Signal files for Chronicle promotion
- Sift — may use Sift for web searches during research
- Weave — read social graph for identity context before research (read-only; see `spec-ocas-interfaces.md` Cooperative Query Interfaces)

## Journal outputs

- Observation Journal — research runs producing findings
- Research Journal — structured multi-source research sessions

Journals must include an `entities_observed` array listing every entity encountered during the run, each tagged with its relevance:

```json
{
  "entities_observed": [
    { "name": "Jane Doe", "type": "Person", "confidence": "high", "user_relevance": "user" },
    { "name": "Acme Corp", "type": "Organization", "confidence": "med", "user_relevance": "agent_only" }
  ]
}
```

## Visibility

public

## Initialization

On first invocation of any Scout command, run `scout.init`:

1. Create `{agent_root}/commons/data/ocas-scout/` and all subdirectories (`briefs/`, `reports/`)
2. Write default `config.json` with ConfigBase fields if absent
3. Create empty JSONL files: `requests.jsonl`, `sources.jsonl`, `findings.jsonl`, `decisions.jsonl`
4. Create `{agent_root}/commons/journals/ocas-scout/`
5. Ensure journal payload fields (see interfaces specification) exists (create if missing)
6. Register cron job `scout:update` if not already present (check the platform scheduling registry first)
7. Log initialization as a DecisionRecord in `decisions.jsonl`
8. **Hunter.io setup** (run once; skip if `HUNTER_API_KEY` already set in environment):
   - Check environment: `echo $HUNTER_API_KEY`
   - If empty: open `https://hunter.io/users/sign_up` in browser
   - Guide free account creation (no credit card required)
   - After signup, navigate to `https://hunter.io/api-keys`
   - Copy API key and store: add `HUNTER_API_KEY=<key>` to platform environment config
   - Free tier provides 50 requests/month (sufficient for OSINT work)

## Background tasks

| Job name | Mechanism | Schedule | Command |
|---|---|---|---|
| `scout:update` | cron | `0 0 * * *` (midnight daily) | `scout.update` |
| `scout:research` | cron | `0 9 * * 1` (Monday 9am) | `scout.research` |

```
# Task declared in SKILL.md frontmatter metadata.{platform}.cron
# Task declared in SKILL.md frontmatter metadata.{platform}.cron
```


## Self-update

`scout.update` pulls the latest package from the `source:` URL in this file's frontmatter. Runs silently — no output unless the version changed or an error occurred.

1. Read `source:` from frontmatter → extract `{owner}/{repo}` from URL
2. Read local version from SKILL.md frontmatter `metadata.version`
3. Fetch remote version from SKILL.md frontmatter: `gh api "repos/{owner}/{repo}/contents/SKILL.md" --jq '.content' | base64 -d | grep 'version:' | head -1 | sed 's/.*"\(.*\)".*/\1/'`
4. If remote version equals local version → stop silently
5. Download and install:
   ```bash
   TMPDIR=$(mktemp -d)
   gh api "repos/{owner}/{repo}/tarball/main" > "$TMPDIR/archive.tar.gz"
   mkdir "$TMPDIR/extracted"
   tar xzf "$TMPDIR/archive.tar.gz" -C "$TMPDIR/extracted" --strip-components=1
   cp -R "$TMPDIR/extracted/"* ./
   rm -rf "$TMPDIR"
   ```
6. On failure → retry once. If second attempt fails, report the error and stop.
7. Output exactly: `I updated Scout from version {old} to {new}`

## Support file map

| File | When to read |
|---|---|
| `references/scout_schemas.md` | Before creating requests, findings, or briefs |
| `references/scout_source_waterfall.md` | Before tier selection or escalation decisions |
| `references/scout_brief_template.md` | Before rendering briefs |
| `references/journal.md` | Before scout.journal; at end of every run |

## Update command

This skill self-updates every 24 hours via:

```bash
scout.update
```

This pulls the latest version from GitHub and restarts the skill's background tasks if applicable.
