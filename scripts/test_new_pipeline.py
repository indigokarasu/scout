#!/usr/bin/env python3
"""Regression tests for the Aliens Eye integration scripts.

Run: python3 test_new_pipeline.py
"""
import csv
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── profile_extract: botwall → name_from_profile false ──────────

def test_botwall_no_structured_name():
    from profile_extract import extract_profile
    bad = ("<!doctype html><html><head>"
           "<title>Just a moment...</title>"
           "<meta name='description' content='Checking your browser'>"
           "</head><body></body></html>")
    p = extract_profile(bad, "generic", "https://example.com/x")
    assert p["name_from_profile"] is False, "botwall title must not be a structured name"

# ── profile_extract: OpenGraph yields structured name ───────────

def test_extract_og_profile():
    from profile_extract import extract_profile
    html = ("<!doctype html><html><head>"
            "<title>Someone Smith · GitHub</title>"
            "<meta property='og:title' content='Someone Smith'>"
            "<meta property='og:description' content='Builder of things'>"
            "<meta property='og:image' content='https://example.com/av.png'>"
            "</head><body>Hi</body></html>")
    p = extract_profile(html, "github", "https://github.com/s")
    assert p["name"] == "Someone Smith"
    assert p["name_from_profile"] is True
    assert p["bio"] == "Builder of things"
    assert p["avatar"] == "https://example.com/av.png"
    assert p["sources"]["name"] == "og"

# ── correlation: two same-person profiles cluster ────────────────

def test_correlation_clusters_same_person():
    from correlate_profiles import correlate
    profiles = [
        {"site": "a", "url": "https://a.example", "avatar": "", "name": "Someone",
         "raw_name": "Someone",
         "bio": "Builder. https://example.org/mylink @mirrorhandle",
         "links": {"https://example.org/mylink"},
         "handles": {"mirrorhandle"}, "status": "Found", "avatar_hash": None},
        {"site": "b", "url": "https://b.example", "avatar": "", "name": "Someone",
         "raw_name": "Someone",
         "bio": "Builder. https://example.org/mylink @mirrorhandle",
         "links": {"https://example.org/mylink"},
         "handles": {"mirrorhandle"}, "status": "Found", "avatar_hash": None},
        {"site": "c", "url": "https://c.example", "avatar": "", "name": "Other",
         "raw_name": "Other",
         "bio": "Totally different person writing about databases.",
         "links": set(), "handles": set(), "status": "Found",
         "avatar_hash": None},
    ]
    res = correlate(profiles, fetch_avatars=False)
    assert len(res["clusters"]) == 1, "expected one cluster"
    cluster = res["clusters"][0]
    assert cluster["size"] == 2
    assert cluster["strength"] in ("high", "medium")
    assert "link" in cluster["signals"] or "name" in cluster["signals"]

# ── expansion: handles mined from bios ───────────────────────────

def test_expansion_mines_handles():
    from recurse_expand import expand
    data = {
        "profiles": [
            {"site": "github", "bio": "Builder @oldhandle also "
             "https://twitter.com/onetw and https://github.com/secondhandle"},
            {"site": "twitter", "bio": "Builder @oldhandle and "
             "https://github.com/secondhandle"},
        ]
    }
    res = expand(data, current_pass=1, known={"oldhandle"})
    handles = {c["handle"] for c in res["candidates"]}
    assert "secondhandle" in handles
    second = [c for c in res["candidates"] if c["handle"] == "secondhandle"][0]
    assert second["corroborated"] is True
    assert second["pass"] == 2

# ── expansion: cap at two passes ─────────────────────────────────

def test_expansion_cap_enforced():
    from recurse_expand import expand
    res = expand({}, current_pass=2)
    assert res["refused"] is True
    assert "recursion cap" in res.get("reason", "").lower()

# ── expansion: bio-less profiles yield nothing ──────────────────

def test_expansion_no_bios():
    from recurse_expand import expand
    res = expand({"profiles": [{"site": "x", "bio": ""},
                               {"site": "y", "bio": ""}]},
                  current_pass=1)
    assert not res["candidates"]

# ── domain check: label reduction ────────────────────────────────

def test_domain_label_reduces():
    from domain_check import domain_label
    # Underscore becomes a hyphen (both are valid DNS label chars);
    # underscores are not legal in DNS labels so the hyphen form is the safe choice.
    assert domain_label("someone_name") == "someone-name"
    assert domain_label("Someone") == "someone"
    assert domain_label("a" * 100) == "a" * 63  # capped at 63

# ── reliability: real metrics from a tiny corpus ─────────────────

def test_reliability_metrics():
    from source_reliability import score
    rows = [
        {"tool": "t", "site": "s", "predicted": True, "actual": True},
        {"tool": "t", "site": "s", "predicted": True, "actual": True},
        {"tool": "t", "site": "s", "predicted": True, "actual": False},
        {"tool": "t", "site": "s", "predicted": False, "actual": True},
    ]
    res = score(rows, min_n=1)
    m = res["tools"]["t"]
    assert m["tp"] == 2
    assert m["fp"] == 1
    assert m["fn"] == 1
    assert m["tn"] == 0
    assert abs(m["precision"] - 0.667) < 0.01
    assert abs(m["recall"] - 0.667) < 0.01

# ── reliability: empty corpus rejected ───────────────────────────

def test_reliability_empty():
    from source_reliability import score
    res = score([], min_n=1)
    assert res["labeled_observations"] == 0
    assert not res["tools"]

# ── entity resolution: exact, fuzzy, and token_overlap match ─────

def test_entity_resolution_matching():
    from entity_resolution import resolve

    left_rows = [
        {"name": "John Alexander Smith"},   # Exact & token_overlap match with right_rows[0]
        {"name": "Alice Williams"},         # Fuzzy match with right_rows[1] ("Williams Alice")
        {"name": "Robert James Johnson"},   # Token overlap with right_rows[2] ("Robert Johnson")
        {"name": "Unique Name Person"},     # No match
    ]
    right_rows = [
        {"fullname": "John Alexander Smith"},
        {"fullname": "Williams Alice"},
        {"fullname": "Robert Johnson"},
        {"fullname": "Unrelated Stranger"},
    ]

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", newline="") as f_left, \
         tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", newline="") as f_right, \
         tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv", newline="") as f_out:

        writer_left = csv.DictWriter(f_left, fieldnames=["name"])
        writer_left.writeheader()
        writer_left.writerows(left_rows)
        f_left.close()

        writer_right = csv.DictWriter(f_right, fieldnames=["fullname"])
        writer_right.writeheader()
        writer_right.writerows(right_rows)
        f_right.close()

        out_path = f_out.name
        f_out.close()

        try:
            count = resolve(
                left_path=f_left.name,
                left_col="name",
                right_path=f_right.name,
                right_col="fullname",
                out_path=out_path,
                overlap_threshold=0.5,
                min_shared=2,
            )
            assert count >= 3

            with open(out_path, newline="", encoding="utf-8") as fh:
                matches = list(csv.DictReader(fh))

            types = [m["match_type"] for m in matches]
            assert "exact" in types
            assert "fuzzy" in types
            assert "token_overlap" in types
        finally:
            os.unlink(f_left.name)
            os.unlink(f_right.name)
            os.unlink(out_path)


# ── research_person: bounded ID-recursion sweeps maigret's other IDs ──

def test_recursion_sweeps_discovered_other_ids():
    """A username maigret reports as an 'other ID' is swept, and its profile
    still has to pass the same name-corroboration gate."""
    import research_person as R

    calls = []
    real = R.run_maigret

    def fake(handle, timeout=200, top_sites=300):
        calls.append(handle)
        if handle == "seedhandle":
            return ({"Example": {"url": "https://example.com/seedhandle",
                                 "fullname": "Wrong Person", "location": "",
                                 "bio": "", "blog_url": ""}},
                    {"tool_name": "maigret", "invoked_at": "", "input_type": "handle",
                     "input_value": handle, "status": "success",
                     "findings_count": 1, "error": None,
                     "other_ids": ["realname77", "seedhandle"]})
        if handle == "realname77":
            return ({"Portfolio": {"url": "https://portfolio.example/realname77",
                                   "fullname": "Rhea Ott", "location": "",
                                   "bio": "", "blog_url": ""}},
                    {"tool_name": "maigret", "invoked_at": "", "input_type": "handle",
                     "input_value": handle, "status": "success",
                     "findings_count": 1, "error": None, "other_ids": []})
        return ({}, {"tool_name": "maigret", "invoked_at": "", "input_type": "handle",
                     "input_value": handle, "status": "success",
                     "findings_count": 0, "error": None, "other_ids": []})

    R.run_maigret = fake
    try:
        res = R.research_person(
            "Rhea Ott", handles=["seedhandle"],
            enable_search=False, enable_whois=False,
            enable_email_permutation=False, enable_company_domain=False,
            enable_company_pages=False, enable_github_emails=False,
            enable_targeted_site_search=False, enable_user_scanner=False,
            enable_github_user_search=False,
        )
    finally:
        R.run_maigret = real

    assert "realname77" in calls, "the discovered other ID must be swept"
    assert "seedhandle" not in res["recursive_handles"], \
        "a handle already swept must not be re-swept"
    assert res["recursive_handles"] == ["realname77"], res["recursive_handles"]
    # The recursive profile names the contact, so it corroborates — proving the
    # pivot's output faces the same gate as any other profile.
    assert "Portfolio" in res["identity"]["corroborating_sites"], \
        res["identity"]["corroborating_sites"]


def test_recursion_capped_and_skips_bare_names():
    """The pivot is capped, and a discovered bare name part is not swept."""
    import research_person as R

    calls = []
    real = R.run_maigret

    def fake(handle, timeout=200, top_sites=300):
        calls.append(handle)
        if handle == "seedhandle":
            return ({}, {"tool_name": "maigret", "invoked_at": "",
                         "input_type": "handle", "input_value": handle,
                         "status": "success", "findings_count": 0, "error": None,
                         "other_ids": ["ott", "aaa111", "bbb222", "ccc333"]})
        return ({}, {"tool_name": "maigret", "invoked_at": "", "input_type": "handle",
                     "input_value": handle, "status": "success",
                     "findings_count": 0, "error": None, "other_ids": []})

    R.run_maigret = fake
    try:
        res = R.research_person(
            "Rhea Ott", handles=["seedhandle"],
            enable_search=False, enable_whois=False,
            enable_email_permutation=False, enable_company_domain=False,
            enable_company_pages=False, enable_github_emails=False,
            enable_targeted_site_search=False, enable_user_scanner=False,
            enable_github_user_search=False,
        )
    finally:
        R.run_maigret = real

    assert "ott" not in res["recursive_handles"], "a bare surname must not be swept"
    assert len(res["recursive_handles"]) == R.MAX_RECURSIVE_HANDLES, \
        res["recursive_handles"]


def test_recursion_disabled_when_asked():
    import research_person as R

    calls = []
    real = R.run_maigret

    def fake(handle, timeout=200, top_sites=300):
        calls.append(handle)
        return ({}, {"tool_name": "maigret", "invoked_at": "", "input_type": "handle",
                     "input_value": handle, "status": "success",
                     "findings_count": 0, "error": None,
                     "other_ids": ["realname77"]})

    R.run_maigret = fake
    try:
        res = R.research_person(
            "Rhea Ott", handles=["seedhandle"], enable_recursion=False,
            enable_search=False, enable_whois=False,
            enable_email_permutation=False, enable_company_domain=False,
            enable_company_pages=False, enable_github_emails=False,
            enable_targeted_site_search=False, enable_user_scanner=False,
            enable_github_user_search=False,
        )
    finally:
        R.run_maigret = real

    assert res["recursive_handles"] == []
    assert "realname77" not in calls


# ── JEV identity adjudication: demote-only, fail-open ──

def test_jev_demotes_only_on_confident_different_person():
    import research_person as R

    assert R._jev_demotes({"choice": "different_person", "confidence": 0.9})
    # below threshold → no demotion
    assert not R._jev_demotes({"choice": "different_person", "confidence": 0.4})
    # JEV may never create a match or a demotion from anything but different_person
    assert not R._jev_demotes({"choice": "same_person", "confidence": 1.0})
    assert not R._jev_demotes({"choice": "insufficient_evidence", "confidence": 1.0})
    assert not R._jev_demotes(None)
    assert not R._jev_demotes({"choice": "different_person"})


def test_jev_adjudicator_fails_open_without_a_key():
    """No key / transport error → verdict is None, rules keep their answer."""
    import research_person as R

    real = R.jev_same_person
    R.jev_same_person = lambda contact, profile, timeout=20: None
    try:
        calls = []
        real_maigret = R.run_maigret

        def fake(handle, timeout=200, top_sites=300):
            calls.append(handle)
            return ({"Portfolio": {"url": "https://portfolio.example/solo",
                                   "fullname": "Rhea Ott", "location": "Chicago, IL",
                                   "bio": "", "blog_url": ""}},
                    {"tool_name": "maigret", "invoked_at": "", "input_type": "handle",
                     "input_value": handle, "status": "success",
                     "findings_count": 1, "error": None, "other_ids": []})

        R.run_maigret = fake
        try:
            res = R.research_person(
                "Rhea Ott", handles=["rheaott"], location_city="Chicago, IL",
                enable_search=False, enable_whois=False,
                enable_email_permutation=False, enable_company_domain=False,
                enable_company_pages=False, enable_github_emails=False,
                enable_targeted_site_search=False, enable_user_scanner=False,
                enable_github_user_search=False,
            )
        finally:
            R.run_maigret = real_maigret
    finally:
        R.jev_same_person = real

    # Single full-name match, JEV unavailable → rule verdict survives untouched.
    assert res["identity"]["level"] == "med", res["identity"]
    assert res["identity"]["jev_verdict"] is None


def test_jev_adjudicator_demotes_a_namesake():
    """A confident different_person verdict drops a single-source 'med' to 'low'."""
    import research_person as R

    real = R.jev_same_person
    R.jev_same_person = lambda contact, profile, timeout=20: {
        "type": "choice", "choice": "different_person", "confidence": 0.88,
        "probabilities": {"same_person": 0.08, "different_person": 0.88,
                          "insufficient_evidence": 0.04}}
    try:
        real_maigret = R.run_maigret

        def fake(handle, timeout=200, top_sites=300):
            return ({"Portfolio": {"url": "https://portfolio.example/namesake",
                                   "fullname": "Rhea Ott", "location": "Tokyo, Japan",
                                   "bio": "", "blog_url": ""}},
                    {"tool_name": "maigret", "invoked_at": "", "input_type": "handle",
                     "input_value": handle, "status": "success",
                     "findings_count": 1, "error": None, "other_ids": []})

        R.run_maigret = fake
        try:
            res = R.research_person(
                "Rhea Ott", handles=["rheaott"], location_city="Chicago, IL",
                enable_search=False, enable_whois=False,
                enable_email_permutation=False, enable_company_domain=False,
                enable_company_pages=False, enable_github_emails=False,
                enable_targeted_site_search=False, enable_user_scanner=False,
                enable_github_user_search=False,
            )
        finally:
            R.run_maigret = real_maigret
    finally:
        R.jev_same_person = real

    assert res["identity"]["level"] == "low", res["identity"]
    assert "JEV" in res["identity"]["reason"]
    assert res["identity"]["jev_verdict"]["choice"] == "different_person"


def test_jev_adjudicator_never_demotes_a_curated_profile():
    """The owner's own URL is not a third-party claim; JEV must not touch it."""
    import research_person as R

    real = R.jev_same_person
    called = []
    R.jev_same_person = lambda contact, profile, timeout=20: called.append(profile) or {
        "type": "choice", "choice": "different_person", "confidence": 0.99,
        "probabilities": {"different_person": 0.99}}
    try:
        res = R.research_person(
            "Rhea Ott", handles=[],
            known_urls=["https://www.linkedin.com/in/rhea-ott"],
            enable_search=False, enable_whois=False,
            enable_email_permutation=False, enable_company_domain=False,
            enable_company_pages=False, enable_github_emails=False,
            enable_targeted_site_search=False, enable_user_scanner=False,
            enable_github_user_search=False,
        )
    finally:
        R.jev_same_person = real

    assert res["identity"]["level"] in ("med", "low"), res["identity"]
    assert called == [], "JEV must not adjudicate a curated (owner-asserted) profile"


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_")]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    import sys
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python3 " + __file__.split('/')[-1] + " (run via pytest; no CLI options)")
        sys.exit(0)
