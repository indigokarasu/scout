# 🔎 scout

Structured OSINT research on people, companies, and organizations. Provenance-backed briefs using free-first workflows.

---

## 📖 Overview

Scout conducts OSINT research. Gathers provenance-backed intelligence on entities using free-first source workflows with optional escalation to paid sources.

---

## 🚀 Quick Start

### 📦 Installation

```bash
git clone https://github.com/indigokarasu/scout.git
```

### 🛠️ Tool Surface

```
scout.research_entity(name, type, ...)       🔎 Research person/company
scout.gather_provenance(entity, ...)         📋 Gather sourced data
scout.create_brief(entity, ...)              📄 Create research brief
scout.verify_sources(...)                    ✓ Verify source credibility
scout.escalate_to_paid(entity, ...)          💳 Escalate to paid sources
```

### 📤 Output

- **scout_research** — Structured research findings
- **scout_brief** — Provenance-backed brief with sources
- **scout_summary** — Entity overview with key facts

---

## ⚙️ Configuration

Read `SKILL.md` for operational details, source management, and cooperation with other skills.

Read `references/` for schemas and examples.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
