# Support File Index

One line per bundled file that SKILL.md does not cover inline. Read entries relevant to your task before assuming a file or tool does not exist.

| File | Notes |
|------|-------|
| `references/correlation_and_expansion.md` | Scout: Cross-Site Correlation, Recursive Expansion & Domain Verification |
| `references/plans/contact-enrichment.plan.md` | --- |
| `references/profile_extraction.md` | Scout Person Research: Profile Extraction |
| `references/source_reliability.md` | Scout Source Reliability |
| `scripts/_envelope.py` | Shared JSON envelope + output-format helper for Scout scripts (stdlib-only). Two conventions applied across... |
| `scripts/_http.py` | Tiny stdlib HTTP helper used by fetch_*.py scripts. Provides polite retry + JSON convenience + User-Agent e... |
| `scripts/_normalize.py` | Shared entity-name normalization helpers (stdlib-only). Used by entity_resolution.py and timing_analysis.py. |
| `scripts/correlate_profiles.py` | Cross-site profile correlation (stdlib-only; Pillow optional). Clusters Found/Maybe profiles that look like... |
| `scripts/domain_check.py` | Domain availability check for a username (stdlib-only). Tests ``<username>.<tld>`` across common TLDs: DNS ... |
| `scripts/profile_extract.py` | Structured profile extraction from a page (stdlib-only). Turns a profile page into an ENTITY record — displ... |
| `scripts/recurse_expand.py` | Recursive handle expansion from found profiles (stdlib-only). Mines linked usernames out of profile bios an... |
| `scripts/research_person.py` |  |
| `scripts/source_reliability.py` | Source reliability scoring for Scout tools (stdlib-only). Computes precision / recall / F1 / false-positive... |
| `scripts/test_name_tokens.py` | Regression tests for the min_len=4 defect in name_tokens. Root cause: name tokens shorter than 4 chars were... |
| `scripts/test_new_pipeline.py` | Regression tests for the Aliens Eye integration scripts. Run: python3 test_new_pipeline.py |
| `scripts/update.sh` |  |
