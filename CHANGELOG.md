# CHANGELOG

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
