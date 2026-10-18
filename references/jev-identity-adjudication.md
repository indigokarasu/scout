# JEV identity adjudication

`research_person.py` decides identity with rules: a profile corroborates when it
shares the contact's full name (>=2 tokens) or family name. Rules cannot tell a
distinctive name from a common one, so where the whole verdict rests on ONE
profile, a namesake passes the gate exactly like the real person.

JEV (`/root/.hermes/skills/jeveer/jev_client.py`, `POST /v1/systemone`) reads the
contact record and the candidate profile side by side and answers the one
question rules cannot: *is this the same person?*

## The asymmetry (do not break this)

JEV may only make a rule **stricter**. A confident `different_person` demotes a
single-source match; nothing JEV returns can create a match. Any failure — no
key, timeout, 4xx/5xx, bad JSON — returns `None` and the rule verdict stands
unchanged. This is why the hook lives after the level is computed and only ever
writes a lower level.

## When it fires

```
fnc <= 1  AND  len(corroborating) == 1  AND  not curated  AND  not circular_anchor
```

- One corroborating profile only. Two or more independent profiles already
  corroborate; a namesake cannot occupy two sites under the same handle.
- A curated profile is exempt: that is the owner's own assertion, not a
  third party's claim, and JEV must not second-guess it.
- A `circular_anchor` profile is exempt: its name agreement is already
  discounted to zero upstream.

## Reading the verdict

```python
v = jev_same_person(contact, profile)   # None on any failure
if _jev_demotes(v):                     # different_person AND conf >= 0.70
    level = "low"
```

`result["identity"]["jev_verdict"]` carries the raw answer for audit.

## Threshold

`JEV_IDENTITY_MIN_CONFIDENCE = 0.70`. Demotion removes a fact from the write
path, so it needs real confidence. Lower it only with evidence that misses are
costlier than wrong attributions.

## Verifying the question is well-formed

A malformed `criteria` map (wrapping the options in `{"options": {...}}`) is not
rejected: the model picks a single option literally named `options` and returns
confidence 1.0. `jev_same_person` therefore returns `None` unless the returned
`choice` is a member of `_JEV_IDENTITY_CRITERIA`. Sanity-probe with a
known-answer pair before trusting any verdict:

| probe | expected |
|---|---|
| identical name + city + education | `same_person` (~0.98) |
| same name, conflicting city/employer | `different_person` (~0.89) |

If the two probes return the same label, the question is broken — fix it before
reading any production verdict.

## Measured behaviour (2026-10-16)

Live case, Tori Hirata: contact `Google / Program Manager / Chicago`; LinkedIn
profile `tori-hirata-98229056` reads `Brilliant Muse`, `Chicago`, `USC`, and a
post about joining Kindsight as Director of Product Design. JEV: `same_person`
p=0.70, confidence 0.55 — employer conflict treated as a plausible career move,
not a disqualifier. No demotion.

Both `profile_linkedin` facts for that contact were the SAME URL differing only
by `www.` — one profile, not two. Deduplicate URLs (strip `www.`, trailing
slash) before treating fact counts as independent evidence.
