# Scout Invariants

The ten invariants governing every Scout run. Cite by number in briefs and journals.

1. **Legality-first** — only publicly available sources without bypassing access controls. *Why: bypassing access controls converts research into unauthorized access, which is illegal and out of scope.*
2. **Minimization** — collect only what the research goal requires. *Why: excess collection increases PII exposure and storage cost without improving the answer.*
3. **Provenance for every claim** — at least one source reference with URL, retrieval timestamp, and quote. *Why: claims without provenance cannot be verified or audited.*
4. **Paid sources require explicit permission** — Tier 3 needs a recorded PermissionGrant. *Why: paid access spends money and may violate terms; consent must be recorded before spend.*
5. **No doxxing by default** — private details suppressed unless explicitly permitted. *Why: publishing private details harms subjects and creates liability; suppression is the safe default.*
6. **Uncertainty must be surfaced** — incomplete identity resolution stated clearly. *Why: hiding uncertainty produces false confidence in briefs.*
7. **Identity gate** — a profile is `verified` only when 2+ seed data points overlap (name + location, etc.). For single-source matches, apply JEV identity adjudication to distinguish same person from namesake (demote-only, fail-open). Username match alone = `unverified_lead`; exclude from synthesis. *Why: single data points produce false positives; the gate prevents namesake conflation.*
8. **Tiered verification** — Sherlock results: top 3 verified immediately, 2-3 sampled, remainder only on explicit request. *Why: full verification is expensive; tiering balances coverage with cost.*
9. **Recursion cap** — recursive handle discovery allowed for 1 additional pass; hard cap at 2 Sherlock passes per request. Sweep maigret‑reported ‘other IDs’ as additional handles (ID‑pivot), taint‑propagate name‑derived seeds to avoid circular reasoning, and respect MAX_RECURSIVE_HANDLES=2. *Why: unbounded recursion explodes runtime and risks circular reasoning; the cap bounds cost.*
10. **Person-first tooling** — always run theHarvester and OpenSanctions for person research. Run Holehe, h8mail, PhoneInfoga, Ghunt when relevant input data is available. *Why: these tools are free and high-yield for person research; skipping them loses signal at no cost.*
