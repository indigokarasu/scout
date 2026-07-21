# scout

<p align="center">
<img src="./assets/readme/hero.jpg" width="100%" alt="Scout: structured OSINT research — lawful people, company, and organization research with full provenance.">
</p>

scout — Scout: structured OSINT research — lawful people, company, and organization research with full provenance.


> Tell it what you need. It does the work.

## What it does

Scout makes research provenance a first-class requirement. Every claim traces to a source with URL, retrieval timestamp, and direct quote. It works through a tiered source waterfall: public web automatically, rate-limited registries if useful, paid databases only after explicit permission. Collection is bounded to the stated research goal. Confirmed entities and relationships are emitted to Chronicle.

## Dependencies

- [Weave](https://github.com/indigokarasu/weave) — social graph for identity context
- [Elephas](https://github.com/indigokarasu/elephas) — receives Signal files for confirmed entities
- [Sift](https://github.com/indigokarasu/sift) — web searches during research
- Paid OSINT providers (Tier 3, optional)

---

*scout is part of the [OCAS Agent Suite](https://github.com/indigokarasu).*