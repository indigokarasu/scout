#!/usr/bin/env python3
"""Scout person-research entrypoint (Tier 1 person OSINT).

The runnable implementation of the `scout.research.start` step described in
references/plans/contact-enrichment.plan.md. Given a name and whatever context
the address book already holds (email, org, occupation, city, and any profile
URLs the user hand-entered), it:

  1. USES known profile URLs as context. A URL already on the contact record
     is something the user typed, so it is recorded with provenance
     'contact_record', GitHub URLs are expanded via the structured users API,
     personal sites are cheaply title-fetched, and LinkedIn is recorded WITHOUT
     scraping (auth-walled). It does NOT by itself resolve identity — see (5).
     Getting that URL into weave is google_sync.py's job (it imports Google
     Contacts urls directly at 0.95); scout does not need to launder it
     through a corroboration gate it cannot honestly pass.
  2. Derives distinctive handle candidates from (a) explicit handles, (b) the
     slug of any known profile URL (linkedin.com/in/rheaott -> 'rheaott'),
     (c) the email local-part, and (d) name combinations — (d) only when the
     email handle is generic or absent.
  3. Runs Maigret (username -> 3000+ sites, with profile metadata) and Holehe
     (email -> which sites the address is registered on) from the isolated
     OSINT venv. Holehe needs only the email and runs even when no handle
     candidate survives.
  4. Enriches GitHub hits via the structured users API.
  5. CORROBORATES identity across sources: a profile only counts if its
     reported full name agrees with the contact's name (scout's normalizer).
     This is the discriminator that accepts 'wrenkeeley' -> Wren Keeley and
     rejects a common handle like 'geekgirl' whose profiles name other people.
     Seeding a handle from a known URL does NOT weaken this gate — a maigret
     hit on a URL-derived handle still has to pass the name test.

     Corroboration requires an INDEPENDENT anchor, and two cases are therefore
     explicitly NOT corroboration:
       * a handle MANUFACTURED from the contact's name (name_handle_variants).
         The pivot and the check would be the same signal, so any namesake
         passes trivially. Those hits are returned with circular_anchor=True
         and zero corroboration weight; the raw measurement is kept under
         name_shared_tokens_raw / family_present_raw.
       * a hand-entered URL on its own. It is an assertion about which account
         belongs to the contact, not verification of what some third-party
         profile says. Alone it yields identity 'low' (below the write gate);
         combined with one name-corroborated site it yields 'high'.
     A curated URL whose FETCHED name names someone else is marked
     name_conflict and is excluded from anchors and enrichment entirely.
  6. FALLS BACK to a capped SearXNG name+org / name+occupation search when the
     handle pivot corroborates nothing. Those results are returned as
     UNVERIFIED CANDIDATES only. They never raise the identity level and never
     produce enrichment.
  7. Emits scout Findings (finding_id / claim / confidence / source_refs) plus
     structured enrichment fields, each with provenance.

Enrichment fields are drawn ONLY from structured sources (GitHub API company /
location, profile blog_url, pronouns parsed from bios, hand-entered URLs).
Free-text bios and search snippets are surfaced as evidence with quotes —
never regex-scraped into employer fields (that was the old failure mode).
Confidence gates whether the caller writes.

Website selection is ranked, not first-wins: personal domain > github blog >
professional profile (LinkedIn/Crunchbase) > portfolio (Behance/Dribbble/
Medium) > consumer social (Snapchat/TikTok/Duolingo/Chess) last.

Stdlib + subprocess only. Network egress happens inside maigret/holehe, the
GitHub API call, the optional page-title fetch, and the local SearXNG query.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _normalize import normalize_name, token_overlap_ratio  # noqa: E402

OSINT_VENV = os.environ.get("SCOUT_OSINT_VENV", "/root/.hermes/tools/osint-venv")
MAIGRET_BIN = f"{OSINT_VENV}/bin/maigret"
HOLEHE_BIN = f"{OSINT_VENV}/bin/holehe"

# Pinned to 127.0.0.1 on purpose: 'localhost' can resolve to ::1 on this box
# and the SearXNG container only listens on IPv4 (cf. the Wikipedia IPv6 case).
SEARXNG_URL = os.environ.get("SCOUT_SEARXNG_URL", "http://127.0.0.1:8888/search")

# Hard caps so a fallback search cannot multiply into ~990 outbound sweeps.
MAX_SEARCH_QUERIES = 3
MAX_SEARCH_CANDIDATES = 12
MAX_SEARCH_VERIFY = 6   # candidates actually fetched and name-checked
MAX_MAIGRET_HANDLES = 3

GENERIC_EMAIL_LOCALS = {
    "info", "support", "webmaster", "admin", "hello", "contact", "noreply",
    "no-reply", "privacy", "sales", "press", "office", "mail", "team", "help",
    "jobs", "careers", "abuse", "postmaster", "security", "billing", "service",
    "feedback", "newsletter",
}
# NOTE: a common-but-personal handle (e.g. 'geekgirl') is NOT blocklisted —
# cross-source name corroboration is what rejects it: maigret will find many
# 'geekgirl' profiles, but none reporting the contact's name, so identity
# resolves to 'none' and nothing is written. That is the real discriminator,
# not a hardcoded denylist.

# Enrichment fields we are willing to write from structured sources.
_PRONOUN_RE = re.compile(
    r"\b(she/her|he/him|they/them|she/they|he/they|ze/zir|xe/xem)\b", re.I
)

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)

# --------------------------------------------------------------------------
# Profile-URL parsing
# --------------------------------------------------------------------------
# host suffix -> (platform label, path regex capturing a username, maigret_ok)
_URL_HANDLE_RULES = (
    ("linkedin.com", "LinkedIn", r"^/in/([^/?#]+)", True),
    ("github.com", "GitHub", r"^/([A-Za-z0-9][A-Za-z0-9\-]*)/?$", True),
    ("gitlab.com", "GitLab", r"^/([A-Za-z0-9][A-Za-z0-9._\-]*)/?$", True),
    ("twitter.com", "Twitter", r"^/([A-Za-z0-9_]+)/?$", True),
    ("x.com", "Twitter", r"^/([A-Za-z0-9_]+)/?$", True),
    ("instagram.com", "Instagram", r"^/([A-Za-z0-9_.]+)/?$", True),
    ("medium.com", "Medium", r"^/@([A-Za-z0-9_.\-]+)/?$", True),
    ("tiktok.com", "TikTok", r"^/@([A-Za-z0-9_.]+)/?$", True),
    ("dribbble.com", "Dribbble", r"^/([A-Za-z0-9_\-]+)/?$", True),
    ("behance.net", "Behance", r"^/([A-Za-z0-9_\-]+)/?$", True),
    ("keybase.io", "Keybase", r"^/([A-Za-z0-9_]+)/?$", True),
    ("reddit.com", "Reddit", r"^/u(?:ser)?/([A-Za-z0-9_\-]+)", True),
    ("about.me", "AboutMe", r"^/([A-Za-z0-9_.\-]+)/?$", True),
    # Handle exists but is not a maigret username (domain-shaped / numeric).
    ("bsky.app", "Bluesky", r"^/profile/([^/?#]+)", False),
    ("facebook.com", "Facebook", r"^/([A-Za-z0-9_.]+)/?$", False),
    ("crunchbase.com", "Crunchbase", r"^/person/([^/?#]+)", False),
    ("scholar.google.com", "GoogleScholar", r"", False),
    ("orcid.org", "ORCID", r"", False),
)

# Website-ranking host classes. Unknown host => treated as a personal domain.
_PROFESSIONAL_HOSTS = {
    "linkedin.com", "crunchbase.com", "angel.co", "wellfound.com", "xing.com",
    "researchgate.net", "orcid.org", "scholar.google.com", "stackoverflow.com",
    "github.com", "gitlab.com", "keybase.io",
}
_PORTFOLIO_HOSTS = {
    "behance.net", "dribbble.com", "medium.com", "substack.com",
    "artstation.com", "deviantart.com", "vimeo.com", "about.me", "carrd.co",
    "read.cv", "contra.com", "wordpress.com", "blogspot.com", "ghost.io",
    "hashnode.dev", "dev.to", "notion.site", "cargo.site", "squarespace.com",
}
_CONSUMER_SOCIAL_HOSTS = {
    "snapchat.com", "tiktok.com", "picsart.com", "duolingo.com", "chess.com",
    "instagram.com", "facebook.com", "pinterest.com", "twitter.com", "x.com",
    "reddit.com", "tumblr.com", "spotify.com", "last.fm", "twitch.tv",
    "steamcommunity.com", "vk.com", "myspace.com", "roblox.com", "discord.com",
    "t.me", "telegram.me", "youtube.com", "soundcloud.com", "flickr.com",
    "goodreads.com", "quora.com", "9gag.com", "imgur.com", "letterboxd.com",
    "strava.com", "untappd.com", "venmo.com", "cash.app", "bsky.app",
}

# Ordering knobs for website selection (lower is better).
_HOST_RANK_PERSONAL = 0
_HOST_RANK_PROFESSIONAL = 2
_HOST_RANK_PORTFOLIO = 3
_HOST_RANK_CONSUMER = 4
_KIND_RANK = {"curated": 0, "github_blog": 1, "profile_blog": 2, "profile_url": 3}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _host_of(url):
    try:
        host = urllib.parse.urlparse(url).netloc.lower()
    except Exception:  # noqa: BLE001
        return ""
    host = host.split("@")[-1].split(":")[0]
    if host.startswith("www."):
        host = host[4:]
    return host


def _host_matches(host, suffix):
    return host == suffix or host.endswith("." + suffix)


def _host_class(host):
    """0 personal / 2 professional / 3 portfolio / 4 consumer-social."""
    if not host:
        return _HOST_RANK_PERSONAL
    for s in _CONSUMER_SOCIAL_HOSTS:
        if _host_matches(host, s):
            return _HOST_RANK_CONSUMER
    for s in _PORTFOLIO_HOSTS:
        if _host_matches(host, s):
            return _HOST_RANK_PORTFOLIO
    for s in _PROFESSIONAL_HOSTS:
        if _host_matches(host, s):
            return _HOST_RANK_PROFESSIONAL
    return _HOST_RANK_PERSONAL


def rank_website_candidate(url, kind="profile_url"):
    """Sort key for a website candidate — LOWER is better.

    Ranking (requirement): personal domain > github blog > professional
    profile > portfolio > consumer social. Consumer-social URLs (Snapchat,
    Duolingo, Chess.com, Picsart) must never beat a real site.
    """
    return (_host_class(_host_of(url)), _KIND_RANK.get(kind, 3))


def pick_website(candidates):
    """candidates: iterable of (url, kind, source_url). Returns best or None."""
    best = None
    best_key = None
    for idx, cand in enumerate(candidates):
        url = (cand[0] or "").strip()
        if not url:
            continue
        kind = cand[1] if len(cand) > 1 else "profile_url"
        key = rank_website_candidate(url, kind) + (idx,)
        if best_key is None or key < best_key:
            best_key = key
            best = cand
    return best


def parse_profile_url(url):
    """Classify a URL from the contact record.

    Returns {url, platform, handle, maigret_ok, kind} or None for junk.
    kind is 'profile' for a recognised platform, 'website' otherwise.
    """
    url = (url or "").strip()
    if not url:
        return None
    if not re.match(r"^https?://", url, re.I):
        if re.match(r"^[\w.-]+\.[A-Za-z]{2,}(/|$)", url):
            url = "https://" + url
        else:
            return None
    host = _host_of(url)
    if not host or "." not in host:
        return None
    try:
        path = urllib.parse.urlparse(url).path or "/"
    except Exception:  # noqa: BLE001
        return None

    for suffix, platform, pattern, maigret_ok in _URL_HANDLE_RULES:
        if not _host_matches(host, suffix):
            continue
        handle = ""
        if pattern:
            m = re.match(pattern, path)
            if m:
                handle = urllib.parse.unquote(m.group(1)).strip().strip("/")
        return {"url": url, "platform": platform, "handle": handle,
                "maigret_ok": bool(maigret_ok and handle), "kind": "profile"}

    return {"url": url, "platform": "Website", "handle": "",
            "maigret_ok": False, "kind": "website"}


def _handle_ok(handle, min_len=5):
    if not handle:
        return False
    if not re.fullmatch(r"[A-Za-z0-9._\-]+", handle):
        return False
    if handle.isdigit():
        return False
    return len(re.sub(r"[._\-]", "", handle)) >= min_len


def _slug_variants(handle):
    """Handle plus useful rewrites: squashed, and LinkedIn's -<id> stripped."""
    out = []
    h = (handle or "").strip().lower()
    if not h:
        return out

    def _add(v):
        if v and v not in out:
            out.append(v)

    _add(h)
    # LinkedIn slugs often carry a disambiguating id: 'john-smith-1a2b3c4'.
    trimmed = re.sub(r"-[0-9a-f]{6,}$", "", h)
    if trimmed != h:
        _add(trimmed)
    for v in list(out):
        _add(re.sub(r"[._\-]", "", v))
    return out


def handles_from_urls(urls):
    """maigret-usable handle candidates derived from known profile URLs."""
    out = []
    for u in urls or []:
        parsed = parse_profile_url(u)
        if not parsed or not parsed["maigret_ok"]:
            continue
        for v in _slug_variants(parsed["handle"]):
            if _handle_ok(v) and v not in out:
                out.append(v)
    return out


def _email_local(email):
    email = (email or "").strip().lower()
    if "@" not in email:
        return ""
    return email.split("@", 1)[0].split("+", 1)[0]


def email_handle_variants(email):
    """Distinctive handle candidates from an email local part.

    Generic / short locals yield [] — probing 'info' manufactures wrong people.
    """
    local = _email_local(email)
    if not local or len(local) < 5 or local in GENERIC_EMAIL_LOCALS:
        return []
    variants = [local]
    squashed = re.sub(r"[._-]", "", local)
    if squashed != local and len(squashed) >= 5 and squashed not in variants:
        variants.append(squashed)
    return variants


def _split_name(name, name_given="", name_family=""):
    given = (name_given or "").strip()
    family = (name_family or "").strip()
    if not (given and family):
        toks = [t for t in re.split(r"\s+", (name or "").strip()) if t]
        toks = [re.sub(r"[^A-Za-z0-9\-']", "", t) for t in toks]
        toks = [t for t in toks if t]
        if len(toks) >= 2:
            given = given or toks[0]
            family = family or toks[-1]
    given = re.sub(r"[^A-Za-z0-9]", "", given).lower()
    family = re.sub(r"[^A-Za-z0-9]", "", family).lower()
    return given, family


def name_handle_variants(name, name_given="", name_family=""):
    """Candidate handles built from the contact's name.

    These are only CANDIDATES — the same cross-source name-corroboration gate
    still decides whether any resulting profile counts. Used when the email
    handle is generic or absent (see research_person).
    """
    given, family = _split_name(name, name_given, name_family)
    if not given or not family:
        return []
    # Deliberately short: each surviving candidate costs a full maigret sweep
    # (~200s). first+last and first.last carry almost all the yield; last+first
    # and the underscore form are noise.
    raw = [
        f"{given}{family}",
        f"{given}.{family}",
        f"{given[0]}{family}",
    ]
    out = []
    for v in raw:
        if _handle_ok(v) and v not in out:
            out.append(v)
    return out


def _run(cmd, timeout):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    except FileNotFoundError as e:
        return 127, "", str(e)


def run_maigret(handle, timeout=200, top_sites=300):
    """Return {site_name: {url, fullname, location, bio, blog_url}} for CLAIMED
    profiles of `handle`. Second value is a PersonToolRecord."""
    rec = {"tool_name": "maigret", "invoked_at": _now(), "input_type": "handle",
           "input_value": handle, "status": "error", "findings_count": 0,
           "error": None}
    if not Path(MAIGRET_BIN).exists():
        rec["status"] = "not_installed"
        rec["error"] = f"{MAIGRET_BIN} missing"
        return {}, rec

    outdir = tempfile.mkdtemp(prefix="maigret_")
    cmd = [MAIGRET_BIN, handle, "--no-recursion", "--no-progressbar",
           "--top-sites", str(top_sites), "--timeout", "8",
           "--json", "simple", "--folderoutput", outdir]
    code, _out, err = _run(cmd, timeout)
    report = Path(outdir) / f"report_{handle}_simple.json"
    if code == 124:
        rec["status"] = "timeout"
    if not report.exists():
        rec["error"] = (err or "no report")[:200]
        return {}, rec

    try:
        data = json.loads(report.read_text())
    except Exception as e:  # noqa: BLE001
        rec["error"] = f"parse: {e}"
        return {}, rec

    profiles = {}
    for site, info in data.items():
        st = info.get("status")
        if not isinstance(st, dict) or st.get("status") != "Claimed":
            continue
        ids = st.get("ids", {}) if isinstance(st.get("ids"), dict) else {}
        profiles[site] = {
            "url": info.get("url_user", ""),
            "fullname": (ids.get("fullname") or "").strip(),
            "location": (ids.get("location") or "").strip(),
            "bio": (ids.get("bio") or "").strip(),
            "blog_url": (ids.get("blog_url") or ids.get("url") or "").strip(),
        }
    rec["status"] = "success"
    rec["findings_count"] = len(profiles)
    return profiles, rec


def run_holehe(email, timeout=120):
    """Return (list of sites the email is registered on, PersonToolRecord)."""
    rec = {"tool_name": "holehe", "invoked_at": _now(), "input_type": "email",
           "input_value": email, "status": "error", "findings_count": 0,
           "error": None}
    if not Path(HOLEHE_BIN).exists():
        rec["status"] = "not_installed"
        rec["error"] = f"{HOLEHE_BIN} missing"
        return [], rec
    code, out, err = _run([HOLEHE_BIN, email, "--only-used", "--no-color"], timeout)
    if code == 124:
        rec["status"] = "timeout"
        return [], rec
    sites = []
    # A real hit line is "[+] <domain>". Guard against progress-bar / legend
    # text ("[x] Rate limit", "Email used") leaking into the site list: keep
    # only single tokens that look like domains.
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("[+]"):
            continue
        token = line[3:].strip()
        if " " in token or "." not in token:
            continue
        sites.append(token)
    rec["status"] = "success"
    rec["findings_count"] = len(sites)
    return sites, rec


def github_api_fields(handle, timeout=8):
    """Structured identity fields from api.github.com/users/<handle>, or {}."""
    url = f"https://api.github.com/users/{handle}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "hermes-scout/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return {}
            d = json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception:  # noqa: BLE001
        return {}
    if not isinstance(d, dict) or "login" not in d or d.get("message"):
        return {}
    out = {}
    if d.get("name"):
        out["fullname"] = d["name"].strip()
    company = (d.get("company") or "").strip().lstrip("@")
    if company:
        out["org"] = company
    if d.get("location"):
        out["location"] = d["location"].strip()
    if d.get("blog"):
        out["blog_url"] = d["blog"].strip()
    if d.get("bio"):
        out["bio"] = d["bio"].strip()
    return out



def fetch_page_text(url, timeout=10, max_bytes=300_000):
    """Title + visible text of a page, for NAME CORROBORATION ONLY.

    Deliberately not an extractor: the text is used to answer "does this page
    name the contact?" and never to mine field values, so there is nothing for
    a regex to mis-attribute into an employer.
    """
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(max_bytes).decode("utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        return "", ""
    m = _TITLE_RE.search(raw)
    title = ""
    if m:
        title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()[:200]
    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return title, body[:20000]




# Roles that make a <title> tail a plausible job title rather than a tagline.
_ROLE_WORDS = (
    "leader", "director", "manager", "engineer", "designer", "founder",
    "co-founder", "ceo", "cto", "coo", "cfo", "head", "principal", "lead",
    "architect", "developer", "analyst", "consultant", "writer", "editor",
    "producer", "researcher", "scientist", "professor", "advisor", "strategist",
    "president", "officer", "partner", "owner", "specialist", "coordinator",
    "photographer", "illustrator", "artist", "therapist", "attorney", "counsel",
)
_TITLE_SEP = re.compile("\\s+[|\u2013\u2014\u00b7:]+\\s+|\\s+-\\s+")
_HREF_RE = re.compile("href\\s*=\\s*[\"\']([^\"\']+)[\"\']", re.I)
_DESC_RE = re.compile("(?is)<meta[^>]+name=[\"\']description[\"\'][^>]+content=[\"\']([^\"\']+)")
_OGTITLE_RE = re.compile("(?is)<meta[^>]+property=[\"\']og:title[\"\'][^>]+content=[\"\']([^\"\']+)")
# Template placeholders, never real addresses.
_PLACEHOLDER_EMAILS = {"user@domain.com", "you@example.com", "name@email.com",
                       "email@example.com", "your@email.com", "info@domain.com"}


def mine_personal_site(url, name, timeout=12, max_bytes=400_000):
    """Harvest a contact's OWN site, once it is confirmed to name them.

    A link the subject publishes on their own site is an assertion BY them, so
    profile links found here are accepted without a separate name match —
    unlike a link found on a third party's page. That is why this runs only
    after the site has corroborated the contact's name.

    The <title> tail is read as a job title only when it actually looks like
    one; prose is otherwise left alone, because mining arbitrary text for an
    employer is what previously produced nonsense values.
    """
    out = {"links": [], "occupation": None, "tagline": None, "emails": []}
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(max_bytes).decode("utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        return out

    seen = set()
    site_host = _host_of(url)
    for m in _HREF_RE.finditer(raw):
        u = m.group(1).split("#")[0].split("?")[0].strip()
        if not u.startswith("http") or _host_of(u) == site_host:
            continue
        parsed = parse_profile_url(u)
        if not parsed or not parsed.get("handle"):
            continue
        key = (parsed["platform"], (parsed["handle"] or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out["links"].append(parsed)

    tm = _TITLE_RE.search(raw)
    title = ""
    if tm:
        title = re.sub("\\s+", " ", re.sub("<[^>]+>", " ", tm.group(1))).strip()
    if not title:
        om = _OGTITLE_RE.search(raw)
        if om:
            title = re.sub("\\s+", " ", om.group(1)).strip()
    if title:
        name_toks = set(normalize_name(name).split())
        for part in [x.strip() for x in _TITLE_SEP.split(title) if x.strip()]:
            if set(normalize_name(part).split()) & name_toks:
                continue                        # this fragment is the name
            low = part.lower()
            if any(w in low for w in _ROLE_WORDS) and 3 < len(part) <= 70:
                out["occupation"] = part
                break

    dm = _DESC_RE.search(raw)
    if dm:
        tag = re.sub("\\s+", " ", dm.group(1)).strip()
        if 3 < len(tag) <= 200:
            out["tagline"] = tag

    for em in set(re.findall("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", raw)):
        low = em.lower()
        if low in _PLACEHOLDER_EMAILS:
            continue
        if low.endswith((".png", ".jpg", ".svg", ".css", ".js")):
            continue
        if low.split("@")[1] in ("example.com", "domain.com", "email.com"):
            continue
        out["emails"].append(low)
    return out


def gravatar_profile(email, timeout=10):
    """Gravatar profile for an email address, or None.

    Gravatar is keyed on the md5 of the address itself, so a hit is bound to
    THIS email rather than inferred from a name — stronger provenance than any
    name match. The displayName is often just a handle, so it is reported but
    never trusted as the person's real name.
    """
    if not email or "@" not in email:
        return None
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    try:
        req = urllib.request.Request(
            "https://www.gravatar.com/%s.json" % h,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
    except Exception:  # noqa: BLE001
        return None
    entry = (d.get("entry") or [{}])[0]
    if not entry:
        return None
    name = (entry.get("displayName")
            or (entry.get("name") or {}).get("formatted") or "").strip()
    return {
        "display_name": name,
        "location": (entry.get("currentLocation") or "").strip(),
        "bio": (entry.get("aboutMe") or "").strip(),
        "accounts": [a.get("url") for a in (entry.get("accounts") or []) if a.get("url")],
        "urls": [u.get("value") for u in (entry.get("urls") or []) if u.get("value")],
        "profile_url": entry.get("profileUrl") or "",
    }


def email_domain_site(email):
    """A personal-domain email is a website hiding in plain sight.

    'anna@annastillwell.com' -> https://annastillwell.com. Returns None for
    consumer/webmail and obvious corporate shared domains, where the domain
    says nothing about which individual owns the mailbox.
    """
    if not email or "@" not in email:
        return None
    dom = email.split("@", 1)[1].strip().lower().rstrip(".")
    if not dom or "." not in dom:
        return None
    if dom in FREEMAIL_DOMAINS:
        return None
    return "https://" + dom


FREEMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "hotmail.com",
    "outlook.com", "live.com", "msn.com", "aol.com", "icloud.com", "me.com",
    "mac.com", "proton.me", "protonmail.com", "gmx.com", "mail.com",
    "fastmail.com", "zoho.com", "yandex.com", "qq.com", "163.com", "126.com",
    "comcast.net", "sbcglobal.net", "verizon.net", "att.net", "cox.net",
    "aim.com", "earthlink.net", "juno.com", "mailinator.com", "example.com",
}


def fetch_page_title(url, timeout=10, max_bytes=200_000):
    """Cheapest possible read of a personal site: just the <title>. '' on any
    failure. Deliberately NOT a scraper — no body text is extracted, so there
    is nothing for a regex to mis-attribute into an employer field."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(max_bytes).decode("utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        return ""
    m = _TITLE_RE.search(raw)
    if not m:
        return ""
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()
    return title[:200]


def searxng_search(query, limit=5, searxng_url=None, retries=1, timeout=15):
    """Query the local SearXNG. Returns [{url,title,content}] — [] on failure.

    Unlike weave's copy this does NOT raise: scout degrades to "no candidates"
    rather than failing a whole contact when the container is bouncing. 429 is
    treated as fail-fast (no retry) so a 990-contact run cannot hammer it.
    """
    base = (searxng_url or SEARXNG_URL).rstrip("/")
    if not base.endswith("/search"):
        base = base + "/search"
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": limit})
    url = f"{base}?{params}"
    for attempt in range(retries + 1):
        if attempt:
            time.sleep(1.5 * (2 ** (attempt - 1)))
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAgent/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            return [
                {"url": i.get("url", ""), "title": i.get("title", ""),
                 "content": i.get("content", "")}
                for i in (data.get("results") or [])[:limit]
            ]
        except urllib.error.HTTPError as e:  # noqa: PERF203
            if getattr(e, "code", 0) == 429:
                return []
        except Exception:  # noqa: BLE001
            continue
    return []


def build_search_queries(name, name_given="", name_family="", org="",
                         occupation="", location_city=""):
    """Name+org / name+occupation queries, most specific first."""
    name = (name or "").strip()
    if not name:
        return []
    org = (org or "").strip()
    occupation = (occupation or "").strip()
    city_head = (location_city or "").split(",")[0].strip()

    # The bare quoted name goes FIRST, always. Qualifying a distinctive full
    # name with an employer measurably degraded results on the available
    # engines: the qualified query returned only unrelated popular pages while
    # the bare name returned the person's actual profiles. Qualified variants
    # still run afterwards to help common names.
    queries = [f'"{name}"']
    if org:
        queries.append(f'site:linkedin.com/in "{name}" {org}')
        queries.append(f'"{name}" {org}')
    if occupation:
        queries.append(f'"{name}" {occupation}' + (f" {org}" if org else ""))
    if not org and not occupation:
        queries.append(f'site:linkedin.com/in "{name}"'
                       + (f" {city_head}" if city_head else ""))
        if city_head:
            queries.append(f'"{name}" {city_head}')
    out = []
    for q in queries:
        q = re.sub(r"\s+", " ", q).strip()
        if q and q not in out:
            out.append(q)
    return out


def _name_agreement(contact_name, profile_fullname):
    """(shared_token_count, family_present) between contact and a profile name."""
    if not profile_fullname:
        return 0, False
    ratio, shared = token_overlap_ratio(contact_name, profile_fullname)
    fam = (normalize_name(contact_name).split() or [""])[-1]
    fam_present = bool(fam) and fam in normalize_name(profile_fullname).split()
    return shared, fam_present


def _name_confirms(contact_name, profile_fullname):
    """Strict 'this profile's own name IS the contact's name'.

    Used ONLY to decide whether a FETCHED name confirms a hand-entered URL, and
    deliberately stricter than _name_agreement: the family names must be equal
    AND the given name has to appear too, so 'Peggy Smith' never confirms a URL
    filed under 'John Smith'. It is also free of token_overlap_ratio's >=4-char
    filter, which makes short family names ('Mun') invisible.
    """
    a = normalize_name(contact_name).split()
    b = normalize_name(profile_fullname).split()
    if not a or not b:
        return False
    if a[-1] != b[-1]:
        return False
    return len(set(a) & set(b)) >= min(2, len(a), len(b))


# --------------------------------------------------------------------------
# Known-URL short circuit
# --------------------------------------------------------------------------
def expand_known_urls(name, known_urls):
    """Turn hand-entered contact URLs into profile records.

    Cheap fetches only: GitHub via its users API, an unknown host via <title>.
    LinkedIn is auth-walled and is recorded WITHOUT any fetch attempt.
    Returns (profile_records, website_candidates, tool_records).

    Only real sites/blogs become website candidates. A profile page is not the
    person's website — it is surfaced through known_profiles / social_profiles
    instead, so nothing writes a LinkedIn URL into a `website` field.
    """
    profiles, websites, tools = [], [], []
    seen = set()
    for raw in known_urls or []:
        parsed = parse_profile_url(raw)
        if not parsed:
            continue
        key = parsed["url"].rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        pending_websites = []

        prof = {
            "site": parsed["platform"],
            "handle": parsed["handle"],
            "url": parsed["url"],
            "fullname": "",
            "location": "",
            "bio": "",
            "blog_url": "",
            "provenance": "contact_record",
            "curated": True,
            "kind": parsed["kind"],
            "handle_origin": "known_url",
        }

        if parsed["platform"] == "GitHub" and parsed["handle"]:
            rec = {"tool_name": "github_api", "invoked_at": _now(),
                   "input_type": "handle", "input_value": parsed["handle"],
                   "status": "success", "findings_count": 0, "error": None}
            gh = github_api_fields(parsed["handle"]) or {}
            if not gh:
                rec["status"] = "error"
                rec["error"] = "no data"
            for k in ("fullname", "org", "location", "blog_url", "bio"):
                if gh.get(k):
                    prof[k] = gh[k]
            rec["findings_count"] = len([k for k in gh if gh.get(k)])
            tools.append(rec)
            if prof.get("blog_url"):
                pending_websites.append((prof["blog_url"], "github_blog", prof["url"]))
        elif parsed["platform"] == "LinkedIn":
            # Auth-walled. Record the anchor; never scrape. A LinkedIn profile
            # is NOT a website candidate.
            prof["fetch_skipped"] = "auth_walled"
        elif parsed["kind"] == "website":
            rec = {"tool_name": "page_title", "invoked_at": _now(),
                   "input_type": "url", "input_value": parsed["url"],
                   "status": "success", "findings_count": 0, "error": None}
            title = fetch_page_title(parsed["url"]) or ""
            if title:
                prof["title"] = title
                rec["findings_count"] = 1
            else:
                rec["status"] = "error"
                rec["error"] = "no title"
            tools.append(rec)
            pending_websites.append((parsed["url"], "curated", parsed["url"]))
        # Any other recognised platform is a profile page, not a website.

        shared, fam = _name_agreement(name, prof.get("fullname", ""))
        prof["name_shared_tokens"] = shared
        prof["family_present"] = fam
        # This disagreement used to be measured here and then never consulted.
        # A hand-entered URL whose fetched profile names SOMEONE ELSE is
        # evidence AGAINST the URL, so it contributes nothing downstream.
        prof["name_conflict"] = bool(prof.get("fullname") and shared == 0 and not fam)
        if not prof["name_conflict"]:
            websites.extend(pending_websites)
        profiles.append(prof)
    return profiles, websites, tools


# --------------------------------------------------------------------------
# Entrypoint
# --------------------------------------------------------------------------
def research_person(name, email="", employer="", handles=None, phone="",
                    maigret_timeout=200, top_sites=300, *,
                    org="", occupation="", location_city="",
                    known_urls=None, name_given="", name_family="",
                    enable_search=True, searxng_url=None,
                    max_search_queries=MAX_SEARCH_QUERIES):
    """Run the Tier-1 person pipeline. Returns a structured research result.

    The first seven parameters keep their original positional order so existing
    callers — notably weave_enrich.scout_research_contact — keep working. All
    new context is keyword-only.
    """
    org = (org or employer or "").strip()
    employer = employer or org
    occupation = (occupation or "").strip()
    location_city = (location_city or "").strip()
    known_urls = [u for u in (known_urls or []) if u]

    result = {
        "subject": {"name": name, "email": email, "employer": employer,
                    "phone": phone, "org": org, "occupation": occupation,
                    "location_city": location_city,
                    "known_urls": list(known_urls)},
        "as_of": _now(),
        "tools": [],
        "profiles": [],
        "known_profiles": [],
        "search_candidates": [],
        "findings": [],
        "enrichment": {},
        "identity": {"level": "none", "corroborating_sites": [],
                     "curated_sites": [], "reason": ""},
    }

    # Known phone is an identity anchor already on file. PhoneInfoga (carrier/
    # line-type/region) is not installed here; record the anchor and note it so
    # a later run with the tool can enrich it rather than silently ignoring it.
    if phone:
        result["findings"].append({
            "finding_id": "PH001",
            "claim": f"Contact has a phone number on file ({phone}).",
            "confidence": "high",
            "source_refs": [{"url": "contact_record", "retrieved_at": _now(),
                             "quote": phone}],
        })

    # ---- Holehe first: it needs only the email. The old code hid it behind
    # the handle-quality gate below, so a generic/absent handle suppressed a
    # tool that never depended on a handle at all.
    if email:
        sites, rec = run_holehe(email)
        result["tools"].append(rec)
        if sites:
            result["findings"].append({
                "finding_id": "H001",
                "claim": f"Email {email} is registered on: {', '.join(sites)}.",
                "confidence": "med",
                "source_refs": [{"url": f"holehe:{email}", "retrieved_at": _now(),
                                 "quote": ", ".join(sites)}],
            })

    # ---- Known-URL short circuit: ground truth the user hand-entered.
    curated_profiles, website_candidates, curated_tools = expand_known_urls(
        name, known_urls)
    result["tools"].extend(curated_tools)
    result["known_profiles"] = [
        {"site": p["site"], "url": p["url"], "handle": p["handle"],
         "kind": p["kind"], "provenance": "contact_record",
         "fullname": p.get("fullname", "")}
        for p in curated_profiles
    ]
    for kidx, prof in enumerate(curated_profiles, start=1):
        result["findings"].append({
            "finding_id": f"K{kidx:03d}",
            "claim": (f"{prof['site']} URL on the contact record: {prof['url']}"
                      + (f" (names '{prof['fullname']}')" if prof.get("fullname") else "")),
            "confidence": "high",
            "source_refs": [{"url": "contact_record", "retrieved_at": _now(),
                             "quote": prof["url"]}],
        })

    # ---- Handle candidates: explicit, then URL slugs, then email, then name.
    handle_candidates = []
    handle_origin = {}

    def _seed(values, origin):
        for v in values:
            v = (v or "").strip()
            if not v or v in handle_origin:
                continue
            handle_candidates.append(v)
            handle_origin[v] = origin

    _seed(list(handles or []), "explicit")
    _seed(handles_from_urls(known_urls), "known_url")
    email_variants = email_handle_variants(email)
    _seed(email_variants, "email")
    if not email_variants:
        # Generic or absent email local — fall back to name combinations. Same
        # corroboration gate applies; these are only extra things to test.
        _seed(name_handle_variants(name, name_given, name_family), "name")

    maigret_handles = [h for h in handle_candidates if _handle_ok(h)][:MAX_MAIGRET_HANDLES]

    # ---- Maigret across each handle candidate; collect claimed profiles.
    all_profiles = {}  # site -> profile (curated wins, then first handle)
    for prof in curated_profiles:
        all_profiles.setdefault(prof["site"], prof)

    for handle in maigret_handles:
        profiles, rec = run_maigret(handle, timeout=maigret_timeout,
                                    top_sites=top_sites)
        result["tools"].append(rec)
        for site, prof in profiles.items():
            prof["site"] = site
            prof["handle"] = handle
            prof["provenance"] = "maigret"
            prof["curated"] = False
            prof["kind"] = "profile"
            # A handle seeded from a known URL does NOT make its maigret hits
            # trustworthy — record where the handle came from and let the name
            # gate below decide, exactly as for any other handle.
            prof["handle_origin"] = handle_origin.get(handle, "explicit")
            # GitHub structured enrichment.
            if site.lower() == "github":
                gh = github_api_fields(handle)
                for k in ("fullname", "org", "location", "blog_url", "bio"):
                    if gh.get(k) and not prof.get(k):
                        prof[k] = gh[k]
            all_profiles.setdefault(site, prof)

    if not maigret_handles:
        result["identity"]["reason"] = "no distinctive handle to anchor on"

    # ---- Corroboration: which profiles agree with the contact's name?
    corroborating = []
    fnc = 0  # full-name (given+family) corroborations
    curated_anchors = []
    for site, prof in all_profiles.items():
        shared, fam = _name_agreement(name, prof.get("fullname", ""))

        # A handle MANUFACTURED from the contact's own name cannot corroborate
        # that name: pivot and check are the same signal, so every namesake
        # passes. Report zero corroboration to consumers (weave_enrich filters
        # on name_shared_tokens / family_present) and keep the raw measurement
        # under *_raw for audit.
        if prof.get("provenance") == "maigret" and prof.get("handle_origin") == "name":
            prof["circular_anchor"] = True
            prof["name_shared_tokens_raw"] = shared
            prof["family_present_raw"] = fam
            prof["corroboration_note"] = (
                "handle derived from the contact's name — name agreement here "
                "is circular, not independent evidence")
            shared, fam = 0, False

        prof["name_shared_tokens"] = shared
        prof["family_present"] = fam

        if prof.get("curated") and prof.get("kind") == "profile":
            # Curated URL whose FETCHED name names someone else: the URL is
            # wrong, so it anchors nothing and sources nothing.
            if prof.get("name_conflict"):
                pass
            else:
                curated_anchors.append(prof)

        if shared >= 2:
            corroborating.append(prof)
            fnc += 1
        elif fam:
            corroborating.append(prof)
        if prof.get("blog_url") and not prof.get("name_conflict") and not prof.get("circular_anchor"):
            website_candidates.append(
                (prof["blog_url"],
                 "github_blog" if site.lower() == "github" else "profile_blog",
                 prof.get("url", "")))
        result["profiles"].append(prof)

    corr_sites = [p["site"] for p in corroborating]
    curated_sites = [p["site"] for p in curated_anchors]
    # A hand-entered URL whose FETCHED name is the contact's name: the URL and
    # the third-party profile are two independent things that agree, which is
    # real corroboration (unlike the URL existing on its own).
    curated_confirmed = [p for p in curated_anchors
                         if p.get("fullname") and _name_confirms(name, p["fullname"])]

    if fnc >= 2:
        level = "high"
        reason = f"{fnc} sites match full name"
    elif curated_anchors and (fnc >= 1 or curated_confirmed):
        level = "high"
        n_conf = fnc or len(curated_confirmed)
        reason = (f"profile URL on file ({', '.join(curated_sites)}) plus "
                  f"{n_conf} name-corroborated site(s)")
    elif fnc == 1 or len(corroborating) >= 2:
        level = "med"
        reason = (f"{fnc} site(s) match full name, "
                  f"{len(corroborating)} match family name")
    elif len(corroborating) == 1:
        level = "low"
        reason = "1 site matches family name only"
    elif curated_anchors:
        # A hand-entered URL is an assertion about which ACCOUNT belongs to the
        # contact. On its own it verifies nothing about what any third-party
        # profile says, so it stays BELOW the write gate (min_identity='med')
        # rather than promoting the whole result to 'high'. The URL itself is
        # still returned in known_profiles/curated_sites, and google_sync
        # imports the address-book URL into weave directly.
        level = "low"
        reason = (f"profile URL on file ({', '.join(curated_sites)}); "
                  "no independent corroboration")
    else:
        level = "none"
        reason = (result["identity"]["reason"]
                  or "no profile corroborated the contact name")

    result["identity"] = {
        "level": level,
        "corroborating_sites": corr_sites,
        "curated_sites": curated_sites,
        "anchor": "contact_record" if (curated_anchors and fnc < 2) else "name_corroboration",
        "reason": reason,
    }

    # ---- Findings: one per corroborating profile (provenance for identity).
    fid = 1
    for prof in corroborating:
        parts = []
        if prof.get("location"):
            parts.append(f"location={prof['location']}")
        if prof.get("org"):
            parts.append(f"org={prof['org']}")
        quote = prof.get("bio") or prof.get("fullname") or ""
        result["findings"].append({
            "finding_id": f"P{fid:03d}",
            "claim": (f"{prof['site']} profile of handle '{prof['handle']}' "
                      f"names '{prof.get('fullname','?')}'"
                      + (f" ({'; '.join(parts)})" if parts else "")),
            "confidence": "high" if prof.get("name_shared_tokens", 0) >= 2 else "med",
            "source_refs": [{"url": prof["url"], "retrieved_at": _now(),
                             "quote": quote[:300]}],
        })
        fid += 1

    # ---- Name+org search fallback: ONLY when nothing corroborated, and never
    # allowed to raise the identity level. Output is candidate evidence for a
    # human/LLM verification pass, per the 2026-08-14 fail-closed rebuild.
    # ---- Gravatar: the email's own profile. Keyed on md5(email), so a hit
    # belongs to this address by construction. Location and linked accounts are
    # taken; displayName is NOT written as the person's name because it is
    # frequently just a handle.
    grav = gravatar_profile(email) if email else None
    if grav and (grav["location"] or grav["accounts"] or grav["urls"] or grav["bio"]):
        result["profiles"].append({
            "site": "Gravatar", "handle": "", "url": grav["profile_url"] or "",
            "fullname": grav["display_name"], "location": grav["location"],
            "bio": grav["bio"], "blog_url": (grav["urls"] or [""])[0],
            "provenance": "gravatar", "curated": False, "kind": "profile",
            "handle_origin": "email_hash",
        })
        result["findings"].append({
            "finding_id": "GR001",
            "claim": ("Gravatar profile registered to %s%s" % (
                email, (" — location: " + grav["location"]) if grav["location"] else "")),
            "confidence": "high",
            "source_refs": [{"url": grav["profile_url"] or "https://gravatar.com",
                             "retrieved_at": _now(),
                             "quote": (grav["bio"] or grav["location"] or "")[:300]}],
        })
        if grav["location"]:
            result["enrichment"].setdefault("location_city", grav["location"])
            result["enrichment"].setdefault("location_city_source", "gravatar")
            result["enrichment"].setdefault("location_city_confidence", 0.8)
        for u in (grav["accounts"] + grav["urls"]):
            parsed = parse_profile_url(u)
            if parsed and not any((p.get("url") or "").rstrip("/") == u.rstrip("/")
                                  for p in result["profiles"]):
                result["profiles"].append({
                    "site": parsed["platform"], "handle": parsed["handle"],
                    "url": u, "fullname": "", "location": "", "bio": "",
                    "blog_url": "", "provenance": "gravatar_linked",
                    "curated": False, "kind": parsed["kind"],
                    "handle_origin": "gravatar",
                })
        # An email-anchored profile is real corroboration of the ADDRESS, which
        # is what the contact record actually asserts.
        if level == "none":
            level = "med"
            result["identity"]["level"] = level
            result["identity"]["reason"] = "gravatar profile registered to the contact's email"

    # ---- Email-domain probe: a non-freemail address often IS the person's
    # website ('anna@annastillwell.com' -> annastillwell.com). The local part
    # can be too short to be a handle while the DOMAIN identifies them exactly,
    # so this runs before falling back to search.
    if level not in ("high", "med"):
        site = email_domain_site(email)
        if site and site.rstrip("/").lower() not in {
                (p.get("url") or "").rstrip("/").lower() for p in result["profiles"]}:
            title, body = fetch_page_text(site)
            if title or body:
                shared, fam = _name_agreement(name, title + " " + body)
                if shared >= 2:
                    result["profiles"].append({
                        "site": "Website", "handle": "", "url": site,
                        "fullname": title[:120], "location": "", "bio": "",
                        "blog_url": site, "provenance": "email_domain",
                        "curated": False, "kind": "website",
                        "handle_origin": "email_domain",
                        "name_shared_tokens": shared, "family_present": fam,
                    })
                    result["findings"].append({
                        "finding_id": "ED001",
                        "claim": f"Email domain resolves to a site naming the contact: {title or site}",
                        "confidence": "high",
                        "source_refs": [{"url": site, "retrieved_at": _now(),
                                         "quote": title[:300]}],
                    })
                    result["enrichment"].setdefault("website", site)
                    result["enrichment"].setdefault("website_source", site)
                    result["enrichment"].setdefault("website_confidence", 0.9)

                    # The site is confirmed to be theirs, so mine it: the links
                    # a person publishes about themselves are the highest-grade
                    # signal available, better than anything inferred.
                    mined = mine_personal_site(site, name)
                    for parsed in mined["links"]:
                        if any((p.get("url") or "").rstrip("/") ==
                               parsed["url"].rstrip("/") for p in result["profiles"]):
                            continue
                        result["profiles"].append({
                            "site": parsed["platform"], "handle": parsed["handle"],
                            "url": parsed["url"], "fullname": "", "location": "",
                            "bio": "", "blog_url": "",
                            "provenance": "self_published",
                            "curated": False, "kind": parsed["kind"],
                            "handle_origin": "personal_site",
                        })
                    if mined["links"]:
                        result["findings"].append({
                            "finding_id": "PS001",
                            "claim": ("Contact's own site links %d profile(s): %s"
                                      % (len(mined["links"]),
                                         ", ".join(p["platform"] for p in mined["links"]))),
                            "confidence": "high",
                            "source_refs": [{"url": site, "retrieved_at": _now(),
                                             "quote": title[:300]}],
                        })
                    if mined["occupation"]:
                        result["enrichment"].setdefault("occupation", mined["occupation"])
                        result["enrichment"].setdefault("occupation_source", site)
                        result["enrichment"].setdefault("occupation_confidence", 0.85)
                    if mined["tagline"]:
                        result["enrichment"].setdefault("bio_summary", mined["tagline"])
                        result["enrichment"].setdefault("bio_summary_source", site)
                        result["enrichment"].setdefault("bio_summary_confidence", 0.8)
                    for em in mined["emails"][:2]:
                        if em != (email or "").lower():
                            result["findings"].append({
                                "finding_id": "PS002",
                                "claim": "Additional email published on own site: %s" % em,
                                "confidence": "med",
                                "source_refs": [{"url": site, "retrieved_at": _now(),
                                                 "quote": em}],
                            })
                    level = "med" if level == "none" else level
                    result["identity"]["level"] = level
                    result["identity"]["reason"] = (
                        "email domain is a personal site naming the contact")

    if enable_search and level not in ("high", "med"):
        queries = build_search_queries(name, name_given, name_family, org,
                                       occupation, location_city)[:max_search_queries]
        seen_urls = {p.get("url", "").rstrip("/").lower() for p in result["profiles"]}
        cid = 1
        for q in queries:
            if len(result["search_candidates"]) >= MAX_SEARCH_CANDIDATES:
                break
            rec = {"tool_name": "searxng", "invoked_at": _now(),
                   "input_type": "query", "input_value": q,
                   "status": "success", "findings_count": 0, "error": None}
            try:
                hits = searxng_search(q, limit=10, searxng_url=searxng_url)
            except Exception as e:  # noqa: BLE001
                hits = []
                rec["status"] = "error"
                rec["error"] = str(e)[:200]
            for h in hits:
                u = (h.get("url") or "").strip()
                if not u or u.rstrip("/").lower() in seen_urls:
                    continue
                seen_urls.add(u.rstrip("/").lower())
                parsed = parse_profile_url(u)
                result["search_candidates"].append({
                    "candidate_id": f"SC{cid:03d}",
                    "query": q,
                    "url": u,
                    "title": h.get("title", ""),
                    "snippet": (h.get("content") or "")[:300],
                    "platform": parsed["platform"] if parsed else "Website",
                    "status": "unverified_candidate",
                    "verified": False,
                })
                cid += 1
                if len(result["search_candidates"]) >= MAX_SEARCH_CANDIDATES:
                    break
            rec["findings_count"] = len(hits)
            result["tools"].append(rec)

        # VERIFY the candidates instead of discarding them. Collecting URLs and
        # never opening them is why contacts with no email but a known employer
        # ("someone at Netflix") failed: the search found them and the result
        # was thrown away. Fetching is cheap and the bar is unchanged — a
        # candidate is promoted only if the PAGE ITSELF names the contact, the
        # same corroboration standard applied to every other profile.
        verified_n = 0
        for cand in result["search_candidates"][:MAX_SEARCH_VERIFY]:
            title, body = fetch_page_text(cand["url"])
            if not (title or body):
                continue
            hay = (title + " " + body)
            shared, fam = _name_agreement(name, hay)
            org_ok = bool(org) and org.strip().lower() in hay.lower()
            if shared < 2 and not (fam and org_ok):
                continue   # page does not name the contact -> stays unverified
            cand["status"] = "verified_candidate"
            cand["verified"] = True
            cand["verified_by"] = ("full name on page" if shared >= 2
                                   else "family name + employer on page")
            parsed = parse_profile_url(cand["url"])
            result["profiles"].append({
                "site": (parsed["platform"] if parsed else "Website"),
                "handle": (parsed["handle"] if parsed else ""),
                "url": cand["url"],
                "fullname": title[:120],
                "location": "",
                "bio": "",
                "blog_url": "",
                "provenance": "name_search",
                "curated": False,
                "kind": (parsed["kind"] if parsed else "website"),
                "handle_origin": "search",
                "name_shared_tokens": shared,
                "family_present": fam,
                "org_present": org_ok,
            })
            verified_n += 1

        for cand in result["search_candidates"]:
            if cand.get("verified"):
                result["findings"].append({
                    "finding_id": cand["candidate_id"],
                    "claim": (f"Search result names the contact ({cand['verified_by']}): "
                              f"{cand['title'] or cand['url']}"),
                    "confidence": "med",
                    "source_refs": [{"url": cand["url"], "retrieved_at": _now(),
                                     "quote": (cand["title"] or cand["snippet"])[:300]}],
                })
            else:
                result["findings"].append({
                    "finding_id": cand["candidate_id"],
                    "claim": ("UNVERIFIED CANDIDATE (web search, name not "
                              f"corroborated): {cand['title'] or cand['url']}"),
                    "confidence": "low",
                    "unverified": True,
                    "source_refs": [{"url": cand["url"], "retrieved_at": _now(),
                                     "quote": cand["snippet"]}],
                })

        # Re-derive identity now that search may have produced corroboration.
        if verified_n:
            _sp = [p for p in result["profiles"]
                   if p.get("provenance") == "name_search" and p.get("verified") is not False]
            _full = sum(1 for p in _sp if p.get("name_shared_tokens", 0) >= 2)
            if _full >= 2:
                level, reason = "high", f"{_full} search result(s) name the contact"
            elif _full == 1 or any(p.get("family_present") and p.get("org_present")
                                   for p in _sp):
                level, reason = "med", (f"{verified_n} search result(s) corroborate "
                                        "the contact by name" +
                                        (" and employer" if org else ""))
            result["identity"]["level"] = level
            result["identity"]["reason"] = reason
        if result["search_candidates"]:
            result["identity"]["reason"] = (
                f"{reason}; {len(result['search_candidates'])} unverified "
                "search candidate(s) returned — NOT promoted")

    # ---- Enrichment fields — ONLY from corroborated or hand-entered profiles.
    if level in ("high", "med"):
        enr = {}
        conf = 0.75 if level == "high" else 0.6
        # Verified social presence IS enrichment — a confirmed identity with no
        # employer still yields the person's real profiles. Do not discard them.
        social = {}
        sourced = list(curated_anchors) + [p for p in corroborating
                                           if p not in curated_anchors]
        for prof in sourced:
            site = prof["site"]
            # Per-PROFILE confidence, not the result-wide level: a family-name-
            # only match must not inherit 'high' just because some other source
            # (or a hand-entered URL) lifted the overall level.
            if prof.get("curated"):
                pconf = 0.8
            elif prof.get("name_shared_tokens", 0) >= 2:
                pconf = conf
            else:
                pconf = min(conf, 0.6)
            if prof.get("url") and site not in social:
                social[site] = prof["url"]
            if prof.get("org") and "org" not in enr:
                enr["org"] = prof["org"]
                enr["org_source"] = prof["url"]
                enr["org_confidence"] = pconf
            if prof.get("location") and "location_city" not in enr:
                enr["location_city"] = prof["location"]
                enr["location_city_source"] = prof["url"]
                enr["location_city_confidence"] = pconf
            if "pronouns" not in enr and prof.get("bio"):
                m = _PRONOUN_RE.search(prof["bio"])
                if m:
                    enr["pronouns"] = m.group(1).lower()
                    enr["pronouns_source"] = prof["url"]
                    enr["pronouns_confidence"] = 0.85

        # Website: RANKED, not first-wins. personal domain > github blog >
        # professional profile > portfolio > consumer social.
        cands = list(website_candidates)
        for prof in sourced:
            # Only a real site counts as a website candidate. A profile page
            # (LinkedIn, GitHub, Snapchat...) belongs in social_profiles; the
            # `website` predicate must not be filled with one.
            if prof.get("url") and prof.get("kind") == "website":
                cands.append((prof["url"], "curated" if prof.get("curated")
                              else "profile_url", prof["url"]))
        best = pick_website(cands)
        if best and _host_class(_host_of(best[0])) in (
                _HOST_RANK_PERSONAL, _HOST_RANK_PORTFOLIO):
            enr["website"] = best[0]
            enr["website_source"] = best[2] or best[0]
            enr["website_confidence"] = (
                0.8 if best[1] in ("curated", "github_blog") else conf)

        if social:
            enr["social_profiles"] = social
            enr["social_profiles_confidence"] = conf
        # MERGE, never replace: the gravatar and email-domain probes above
        # already recorded findings (location, website) that this block does
        # not re-derive. Assigning the dict outright silently dropped them.
        for _k, _v in enr.items():
            result["enrichment"][_k] = _v

    return result


def main():
    ap = argparse.ArgumentParser(description="Scout person research (Tier 1)")
    ap.add_argument("--name", required=True)
    ap.add_argument("--email", default="")
    ap.add_argument("--employer", default="")
    ap.add_argument("--org", default="", help="employer/org from the contact record")
    ap.add_argument("--occupation", default="")
    ap.add_argument("--location-city", default="")
    ap.add_argument("--name-given", default="")
    ap.add_argument("--name-family", default="")
    ap.add_argument("--phone", default="")
    ap.add_argument("--handles", default="", help="comma-separated known handles")
    ap.add_argument("--url", action="append", default=[],
                    help="known profile/website URL (repeatable)")
    ap.add_argument("--urls", default="", help="comma-separated known URLs")
    ap.add_argument("--no-search", action="store_true",
                    help="disable the SearXNG name+org fallback")
    ap.add_argument("--top-sites", type=int, default=300)
    ap.add_argument("--maigret-timeout", type=int, default=200)
    ap.add_argument("--json", action="store_true", help="emit JSON only")
    a = ap.parse_args()

    urls = list(a.url) + [u.strip() for u in a.urls.split(",") if u.strip()]

    res = research_person(
        a.name, a.email, a.employer,
        handles=[h.strip() for h in a.handles.split(",") if h.strip()],
        phone=a.phone,
        maigret_timeout=a.maigret_timeout, top_sites=a.top_sites,
        org=a.org, occupation=a.occupation, location_city=a.location_city,
        known_urls=urls, name_given=a.name_given, name_family=a.name_family,
        enable_search=not a.no_search,
    )
    if a.json:
        print(json.dumps(res))
        return 0
    idn = res["identity"]
    print(f"# {a.name}  <{a.email or 'no email'}>")
    print(f"identity: {idn['level']}  ({idn['reason']})")
    print(f"anchor: {idn.get('anchor', '-')}")
    print(f"corroborating sites: {', '.join(idn['corroborating_sites']) or 'none'}")
    print(f"contact-record URLs: {', '.join(idn.get('curated_sites') or []) or 'none'}")
    if res["enrichment"]:
        print("enrichment:")
        for k, v in res["enrichment"].items():
            if k.endswith(("_source", "_confidence")):
                continue
            if isinstance(v, dict):
                print(f"  {k}:")
                for kk, vv in v.items():
                    print(f"    {kk}: {vv}")
            else:
                print(f"  {k} = {v}")
    if res["search_candidates"]:
        print(f"unverified search candidates ({len(res['search_candidates'])}):")
        for c in res["search_candidates"]:
            print(f"  [{c['candidate_id']}] {c['platform']}: {c['url']}")
    print(f"findings: {len(res['findings'])}; profiles: {len(res['profiles'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
