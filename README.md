# 🔍 Scout

> **Structured OSINT research — every claim sourced with full provenance.**

## Why Scout?

Most research tools either give you raw search results or make unsupported claims. Scout does neither. It assembles provenance-backed briefs where every claim carries a source reference, retrieval timestamp, and direct quote. It works through a tiered source waterfall — public web first, then rate-limited registries, then paid databases only with explicit permission.

Skill packages follow the [agentskills.io](https://agentskills.io/specification) open standard and are compatible with OpenClaw, Hermes Agent, Claude, and any agentskills.io-compliant client.

## Quick Start

```
# Research a person
"Research John Smith, CEO of Acme Corp"

# Research a company
"What can you find about Anthropic's recent funding?"

# Generate a brief
"Render a brief on the findings"
```

Scout auto-initializes on first use. No manual setup required.

## What It Does

Scout makes research provenance a first-class requirement. Every claim traces to a source with URL, retrieval timestamp, and direct quote. It works through a tiered source waterfall: public web automatically, rate-limited registries if useful, paid databases only after explicit permission. Collection is bounded to the stated research goal. Confirmed entities and relationships are emitted to Chronicle.

## Commands

| Command | Description |
|---|---|
| `scout.research.start` | Begin a new research request |
| `scout.research.expand --tier <1\|2\|3>` | Escalate to a higher source tier |
| `scout.brief.render` | Generate the final markdown brief |
| `scout.brief.render_pdf` | Optional PDF brief generation |
| `scout.status` | Current research state |
| `scout.journal` | Write journal |
| `scout.update` | Self-update |

## Dependencies

- [Weave](https://github.com/indigokarasu/weave) — social graph for identity context
- [Elephas](https://github.com/indigokarasu/elephas) — receives Signal files for confirmed entities
- [Sift](https://github.com/indigokarasu/sift) — web searches during research
- Paid OSINT providers (Tier 3, optional)

## Scheduled Tasks

| Job | Schedule | Command |
|---|---|---|
| `scout:update` | `0 0 * * *` | Self-update |

## Changelog

### v2.10.0 — April 12, 2026
- Sherlock integration, Social Graph section in briefs

### v2.6.0 — April 2, 2026
- Added `user_relevance` field on emitted signals

### v2.0.0 — March 18, 2026
- Initial release

---

*Scout is part of the [OCAS Agent Suite](https://github.com/indigokarasu).*