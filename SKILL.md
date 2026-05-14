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
  version: "3.0.0"
  hermes:
    tags: [research, osint, people]
    category: signal
    cron:
      - name: "scout:update"
        schedule: "5 7 * * *"
        command: "scout.update"
      - name: "scout:research"
        schedule: "0 16 * * 1"
        command: "scout.research"
      - name: "scout:sources-refresh"
        schedule: "0 6 * * 0"
        command: "scout.sources.refresh"
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
      requires_binaries: [gh, tar]
    requires:
      credentials:
        - name: \"searchx_api_key\"
          description: \"Local SearchX (SearXNG) access key (if required by local instance)\"
          required: false
    cron:
      - name: "scout:update"
        schedule: "5 7 * * *"
        command: "scout.update"
      - name: "scout:research"
        schedule: "0 16 * * 1"
        command: "scout.research"
      - name: "scout:sources-refresh"
        schedule: "0 6 * * 0"
        command: "scout.sources.refresh"
---

# Scout

Scout conducts lawful OSINT research on people, companies, and organizations, assembling provenance-backed briefs where every claim carries a source reference, retrieval timestamp, and direct quote. It works through a tiered source waterfall — public web first, then rate-limited registries, then paid databases only with explicit permission — collecting no more than the stated research goal requires.

Scout integrates curated person-specific OSINT tools (theHarvester, Maigret, Holehe, h8mail, PhoneInfoga, and others) and dynamically discovers new MCP-wrapped OSINT servers at runtime.

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

Scout emits Signals to Elephas after each completed research request, for each extracted entity with confidence >= med. Signal `payload.type` is `"Person"` or `"AI"`. `source_journal_type` is `"Research"`. Every emitted Signal must include a `user_relevance` field.

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
7. Identity gate — a profile found via handle expansion is `verified` only when 2+ data points from the seed overlap (e.g., name + location, name + bio keywords). A username match alone is `unverified_lead`; exclude unverified leads from final synthesis
8. Tiered verification — Sherlock results processed in tiers: top 3 verified immediately, 2-3 sampled, remainder only on explicit user request
9. Recursion cap — recursive handle discovery (a verified profile reveals a new handle) is allowed for one additional pass; hard cap at 2 Sherlock passes total per research request
10. Person-first tooling — when researching a person, always run theHarvester and OpenSanctions. Run person-specific tools (Holehe, h8mail, PhoneInfoga, Ghunt) when the relevant input data (email, phone, Gmail) is available.

## Input contract

ResearchRequest requires: request_id, as_of, subject (type, name, aliases, known_locations, known_handles, known_emails, known_phones), goal, constraints (time_budget_minutes, minimize_pii).

Read `references/scout_schemas.md` for exact schema.

## Research workflow

1. Normalize request and subject identity inputs
2. Resolve likely identity matches conservatively
3. **Run Tier 1 person-specific tools** (parallel):
   - **theHarvester** — always run on person research (gathers names, emails, subdomains from 40+ sources)
   - **OpenSanctions** — always run (sanctions/PEP screening)
4. Run Tier 1 public-source collection (via Sift shared search stack) — in parallel with step 3
5. **Extract high-confidence handles** — from Tier 1 results, identify: any unique string preceded by `@`, usernames in URL paths (e.g., `github.com/username`), and strings explicitly labeled as social aliases. Deduplicate handles before proceeding.
6. **Handle expansion** — if one or more handles found:
   - **Sherlock** — call `sherlock(handle)` for each unique handle
   - If Sherlock returns < 3 verified profiles: run **Maigret** as second pass
   - Filter results to high-value tiers — Dev: GitHub, StackOverflow; Professional: LinkedIn, Medium; Social: X, Instagram, Reddit
   - **Tiered verification** (invariant 8): call `sift.extract(url)` on the top 3 results immediately; sample 2-3 others; surface remaining URLs in the brief as "unverified leads — available on request"
   - **Identity gate** (invariant 7): require 2+ overlapping data points from seed (name + location, name + bio keywords, etc.) to mark a profile `verified`; label all others `unverified_lead` and exclude from synthesis
   - **Recursive discovery** (invariant 9): if a `verified` profile reveals a new handle not in the original seed, run one additional Sherlock/Maigret pass on that handle; stop after 2 total passes
7. **Run email-specific tools** (parallel, if email known):
   - **Holehe** — discover which sites the email is registered on
   - **h8mail** — search 20+ breach databases locally
   - **EmailRep** — email risk/reputation scoring
   - **Ghunt** — if email is Gmail (reveals Google Maps reviews, Photos, YouTube channel)
8. **Run phone-specific tools** (if phone known):
   - **PhoneInfoga** — carrier, location, line type
9. **Dynamic MCP discovery** (if Tier 1 results are thin or specific capabilities needed):
   - Run `scout.sources.discover` with query matching unresolved research questions
   - Connect to discovered MCP servers via `native-mcp` skill
   - Use MCP tools for the current research step
   - Record MCP server name and endpoint in source log
10. Record provenance for every retained claim
11. Compile preliminary findings with confidence levels
12. Escalate to Tier 2 only if enabled and useful
13. Escalate to Tier 3 only after explicit permission grant is recorded
14. Generate brief with findings, uncertainty, and source log
    - Include a **Social Graph** section if handle expansion ran (see Output requirements)
    - Include a **Digital Footprint** section if email/phone tools ran (see Output requirements)
    - Near-match flag: if a profile matches the name but contradicts a known seed attribute (e.g., different city), surface it explicitly rather than discarding: *"Found a [Platform] profile with a matching name but listed in [Location] rather than [expected]. Flag as possible alt-account?"*
15. Store request, findings, sources, and decisions locally
16. Emit Signal files for confirmed entities and relationships to the `signal` payload field in the journal entry. Use Signal schema from `spec-ocas-shared-schemas.md`. One file per entity or relationship with sufficient confidence. Every Signal must include `user_relevance` (see Ontology types section). Set `"user"` if the run was user-initiated or the entity connects to a `user_relevance: "user"` Chronicle entry; otherwise `"agent_only"`. When social graph data is present, include `social_graph` in the Signal payload (handles array and verified profiles list with platform, url, status, discovery_method, verification_evidence).
17. Write journal via `scout.journal`

When `minimize_pii=true`, suppress unnecessary sensitive details in the final brief.

## Source waterfall

Read `references/scout_source_waterfall.md` for full tier logic.

All configured sources fire in parallel. Results are merged and deduplicated. A source without a configured key is silently skipped.

- **Tier 1 — Person-specific tools** — theHarvester, OpenSanctions, Sherlock, Maigret, Holehe, h8mail, EmailRep, Ghunt, PhoneInfoga. Run automatically when relevant input data is available. See `references/scout_person_sources.md` for the full tool list and execution order.
- **Web + platform search** — public web via SearchX (local SearXNG instance), including Twitter/X, Reddit, LinkedIn, GitHub agent-reach. Always runs.
- **Tier 2** — rate-limited sources, registries, extended datasets, MCP-discovered servers. Only if enabled and useful.
- **Tier 3** — paid OSINT providers, background databases. Requires explicit permission grant.

## Output requirements

Markdown brief with: Executive Summary, Identity Resolution Notes, Findings, Social Graph (if handle expansion ran), Digital Footprint (if email/phone tools ran), Risk and Uncertainty, Source Log. Every finding carries source-backed provenance.

**Social Graph section** (included when handle expansion ran):
- List verified profiles: platform, URL, discovery method (sherlock / maigret / sift-dork), verification evidence (which two data points matched)
- List unverified leads separately with a note that they are available for further investigation on request
- Omit this section entirely if no handles were found

**Digital Footprint section** (included when email/phone tools ran):
- Email accounts discovered (via Holehe): list platforms where the email is registered
- Breach exposure (via h8mail/HIBP): list breaches the email appears in, with breach date and data classes
- Google account data (via Ghunt): Google Maps reviews, Photos, YouTube channel if found
- Phone metadata (via PhoneInfoga): carrier, location, line type
- Email risk score (via EmailRep): risk level and associated profiles
- Omit this section entirely if no email/phone data was available or tools were not run

- **Professional Contacts section** (removed: no longer using Hunter.io)

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
  mcp_discovery_cache.json
  source_list_hashes.json
  mcp_servers.json

{agent_root}/commons/journals/ocas-scout/
  YYYY-MM-DD/
    {run_id}.json
```

Default config.json:
```json
{
  "skill_id": "ocas-scout",
  "skill_version": "3.0.0",
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
  "person_tools": {
    "theHarvester": true,
    "maigret": true,
    "holehe": true,
    "h8mail": true,
    "ghunt": true,
    "phoneinfoga": true,
    "emailrep": true,
    "opensanctions": true
  },
  "mcp_discovery": {
    "enabled": true,
    "registry_url": "https://nothumansearch.ai",
    "cache_ttl_hours": 24,
    "rate_limit_per_minute": 10
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
  - name: person_tool_coverage
    metric: fraction of applicable person-specific tools actually invoked per run
    direction: maximize
    target: 0.80
    evaluation_window: 30_runs
```

## Optional skill cooperation

- **Sherlock** — username-to-platform expansion. Check at runtime via the platform skill registry. If installed, called during handle expansion phase (step 6). If absent, Scout falls back to targeted `sift.search("site:<platform> '<handle>'")` queries across top-5 platforms.
- **Sift** — web search during Tier 1 collection and Sift-dork fallback when Sherlock is unavailable
- **Weave** — read social graph for identity context before research (read-only; see `spec-ocas-interfaces.md` Cooperative Query Interfaces)
- **Elephas** — emit Signal files for Chronicle promotion after each completed research request
- **native-mcp / mcporter** — connect to dynamically discovered MCP-wrapped OSINT servers at runtime

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
8. **SearchX Setup** (run once):
   - Ensure the `web_search` skill is initialized by running `web_search_init()` via `execute_code`.
   - This sets up the local SearXNG container and nginx proxy.
9. **Person tools check** (run once):
   - Verify person-specific tools are installed: `theHarvester`, `maigret`, `holehe`, `h8mail`, `ghunt`, `phoneinfoga`
   - For each missing tool: attempt `pip install <tool>` and log result
   - Log tool availability in `decisions.jsonl`

## Background tasks

| Job name | Mechanism | Schedule | Command |
|---|---|---|---|
| `scout:update` | cron | `0 0 * * *` (midnight daily) | `scout.update` |
| `scout:research` | cron | `0 9 * * 1` (Monday 9am) | `scout.research` |
| `scout:sources-refresh` | cron | `0 6 * * 0` (Sunday 6am) | `scout.sources.refresh` |

```
# Task declared in SKILL.md frontmatter metadata.{platform}.cron
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
| `references/scout_person_sources.md` | At start of every person research run; before tool selection |
| `references/scout_mcp_discovery.md` | Before `scout.sources.discover`; before Tier 2 escalation |
| `references/journal.md` | Before scout.journal; at end of every run |

## Update command

This skill self-updates every 24 hours via:

```bash
scout.update
```

This pulls the latest version from GitHub and restarts the skill's background tasks if applicable.
