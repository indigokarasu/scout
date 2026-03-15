# 🔎 Scout

Scout performs structured open-source intelligence research on entities (people, companies, organizations) using a free-first source waterfall. Every finding is provenance-backed with citations. Scout escalates from free sources (web search, public records) to paid providers only with explicit permission. Outputs are auditable, evidence-linked briefs suitable for decision-making.

---

## 📖 Overview

Structured OSINT research on people, companies, and organizations. Provenance-backed briefs using a free-first source waterfall.

---

## 🔧 Tool Surface

- `scout.research.start` — begin structured research on entity
- `scout.research.status` — current research progress and findings
- `scout.sources.available` — available sources tier-by-tier
- `scout.findings.list` — current findings with confidence and sources
- `scout.brief.generate` — produce final research brief
- `scout.identity.resolve` — determine if two profiles refer to same entity
- `scout.status` — active research threads, source tier usage, brief queue

---

## 📊 Output & Journals

Produces: Produces research session logs, finding records with source citations, and identity resolution reports.

---

## ⏱️ Heartbeat & Background Tasks

**Background Source Monitoring**: Scout maintains source reputation scores and updates them based on cross-source agreement and historical accuracy.

---

## 📚 Documentation

Read `SKILL.md` for operational details, schemas, and validation rules.

See `references/` for detailed specifications and examples.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
