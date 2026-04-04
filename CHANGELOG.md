## [2026-04-04] Spec Compliance Update

### Changes
- Added missing SKILL.md sections per ocas-skill-authoring-rules.md
- Updated skill.json with required metadata fields
- Ensured all storage layouts and journal paths are properly declared
- Aligned ontology and background task declarations with spec-ocas-ontology.md

### Validation
- ✓ All required SKILL.md sections present
- ✓ All skill.json fields complete
- ✓ Storage layout properly declared
- ✓ Journal output paths configured
- ✓ Version: 2.7.1 → 2.7.2

# CHANGELOG

## [2.7.1] - 2026-04-02

### Changed
- Aligned Tier 1 platform search with Sift's shared search stack (agent-reach now provided by Sift)
- Scout no longer implements its own parallel search — delegates to Sift infrastructure

## [2.7.0] - 2026-04-02

### Added
- Tier 1 parallel search with agent-reach: Tavily/DuckDuckGo + platform search (Twitter/X, Reddit, LinkedIn, GitHub, Weibo, etc.)
- Deduplication by URL and content hash for merged search results
- Source waterfall updated to document parallel execution model

## [2.6.0] - 2026-04-02

### Added
- `user_relevance` field on all emitted Elephas signals (default `agent_only` for research, `user` when user-requested)
- Structured entity observations in journal payloads (`entities_observed` with relevance tags)

## 2.5.0 — 2026-03-30

### Added
- `references/plans/contact-enrichment.plan.md` — bundled workflow plan: Weave lookup → Scout research → Weave social graph update
- Ontology mapping: Scout extracts Entity/Person, Entity/AI, and Thing/DigitalArtifact types
- Weave cooperative read interface documented in Optional skill cooperation

## Prior

See git log for earlier history.
