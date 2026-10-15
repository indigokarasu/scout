# Support File Index

One line per bundled file that SKILL.md does not cover inline. Read entries relevant to your task before assuming a file or tool does not exist.

| File | When to read |
|------|--------------|
| `references/correlation_and_expansion.md` | When correlating entities across sources; during Phase 5 resolution |
| `references/profile_extraction.md` | When extracting structured profiles from pages; during Phase 2-3 |
| `references/source_reliability.md` | When scoring source quality; before final brief confidence assignment |
| `references/support-file-map.md` | When verifying bundled files or assuming a tool is absent |
| `scripts/_envelope.py` | When emitting JSON envelopes; before modifying script output |
| `scripts/_http.py` | When fetch scripts need polite retry/HTTP; during any HTTP fetch failure |
| `scripts/_normalize.py` | When normalizing entity names; before changing token logic |
| `scripts/correlate_profiles.py` | When cross-linking profiles across sites; Phase 5 resolution |
| `scripts/domain_check.py` | When checking username domain availability; handle expansion |
| `scripts/profile_extract.py` | When turning a profile page into an ENTITY record; Phase 3-4 |
| `scripts/recurse_expand.py` | When expanding handles recursively; subject to the 2-pass cap |
| `scripts/research_person.py` | When running the flagship person research pipeline; at start of person research |
| `scripts/source_reliability.py` | When computing precision/recall/F1; final brief scoring |
| `scripts/test_name_tokens.py` | When regressing name-token matching; before changing _normalize |
| `scripts/test_new_pipeline.py` | When validating the Aliens Eye / new pipeline integration |
| `scripts/update.sh` | Before running scout.update; when debugging self-update |
| `references/plans/contact-enrichment.plan.md` | When working the contact-enrichment roadmap |