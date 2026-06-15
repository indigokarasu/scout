# Scout Person-Specific OSINT Sources

Curated list of person-specific OSINT tools and APIs, organized by capability.
Updated: 2026-06-14. Sources reviewed from jivoi/awesome-osint, laramies/theHarvester,
apurvsinghgautam/robin, cipher387/API-s-for-OSINT, soxoj/awesome-osint-mcp-servers,
and christinminor459/OnionClaw.

## Selection criteria

- **Person-specific**: Must directly help identify, locate, or characterize a person
- **Lawful**: Only publicly available data, no access control bypass
- **Callable**: Can be invoked via CLI, API, or MCP from Scout's runtime
- **Free tier preferred**: Free or freemium; paid-only sources go in Tier 3

---

## 1. Username Enumeration

Find accounts belonging to a person across platforms.

| Tool | Install | Scope | Speed | Notes |
|------|---------|-------|-------|-------|
| **Sherlock** | `pip install sherlock` | 400+ sites | ~30s | Already integrated. First-pass username checker. |
| **Maigret** | `pip install maigret` | 3000+ sites | ~60s | Deeper than Sherlock. Collects profile text, metadata. Use as second pass when Sherlock returns thin results. |
| **WhatsMyName** | Web API / `pip install whatsmyname` | 600+ sites | ~20s | Lightweight. Good for quick validation of a known username. |
| **Holehe** | `pip install holehe` | 100+ sites | ~30s | Email-based username discovery. Checks which sites an email is registered on via password-reset flows. |
| **NexFil** | `pip install nexfil` | 350+ sites | ~30s | Fast, lightweight username checker. |
| **Blackbird** | `pip install blackbird` | 600+ sites | ~45s | Includes AI-based profile matching to reduce false positives. |
| **Social Analyzer** | `pip install social-analyzer` | 1000+ sites | ~120s | Slowest but broadest. Use for high-value targets when other tools return thin results. |
| **Trace** | Web (trace.manus.space) | 600+ sites | ~30s | Also handles email, phone, name. Includes breach detection and AI risk scoring. |
| **Antisocial** | `pip install antisocial` | 500+ sites | ~45s | Three-tier verification (API → browser → HTTP). Reduces false positives to ~5%. |
| **SherlockEye** | Web (sherlockeye.io) | OSINT by username | ~30s | Public data linked to usernames across web sources. |
| **Digital Footprint Check** | Web (digitalfootprintcheck.com) | 100+ sites | ~20s | Free username checker across hundreds of sites. |
| **Seekr** | `pip install seekr` | Multi-source | ~60s | All-in-one OSINT toolkit with web UI. Username checking + note taking. |
| **User Searcher** | Web (user-searcher.com) | 2000+ sites | ~60s | Free username search across 2000+ websites. |

**Scout workflow integration:**
- Step 5 (handle expansion) already runs Sherlock. Add Maigret as a second-pass
  when Sherlock returns < 3 verified profiles.
- Run Holehe when an email address is known (discovers usernames the person uses).
- Social Analyzer is a Tier 2 escalation (slow, broad).

---

## 2. Email Investigation

Discover accounts, breaches, and metadata linked to an email address.

| Tool | Install | Type | Free | Notes |
|------|---------|------|------|-------|
| **Holehe** | `pip install holehe` | Account discovery | Yes | Checks 100+ sites via password-reset. |
| **h8mail** | `pip install h8mail` | Breach hunting | Yes | Searches 20+ breach databases locally. Supports chasing related emails. |
| **HaveIBeenPwned** | API (hibp-api-key) | Breach check | Yes (rate-limited) | Canonical breach database. API key required for domain search. |
| **EmailRep** | API (emailrep.io) | Reputation/risk | Yes (no key, rate-limited) | Returns risk score, associated profiles, breach exposure. |
| **LeakCheck** | API (leakcheck.io) | Breach search | Freemium | 7.5B+ entries. Search by email, username, domain. |
| **DeHashed** | API (dehashed.com) | Breach search | Freemium | Aggregated breach data. |
| **Ghunt** | `pip install ghunt` | Google account | Yes | Investigates Google emails — finds Google Maps reviews, Photos, YouTube channel. |
| **Gyrecon** | `pip install gyrecon` | GitHub email | Yes | Scans GitHub for exposed emails and names in commits. |
| **Epieos Tools** | Web (tools.epieos.com) | Email OSINT | Yes | Collection of free OSINT tools for email investigations (Google, Skype, etc.). |
| **MailAccess** | `pip install mailaccess` | Multi-platform + breach | Yes | Checks 800+ platforms, HIBP, infostealer logs. Cross-platform identity graph with confidence scoring. |
| **LeakRadar** | API (leakradar.io) | Stealer log scan | Freemium | Scans compromised emails/domains in infostealer logs. Real-time alerts. |
| **Minerva OSINT** | Web (minervaosint.com) | Email search | Yes | Aggregates data on a target email from 100+ websites. |
| **IntelBase** | API (intelbase.is) | Email forensics | Freemium | Reverse email lookup + email data enrichment. |
| **user-scanner** | `pip install user-scanner` | Email/site check | Yes | Scans a given email across popular sites, games, and retrieves registration info. |
| **EVA** | API (eva.pingutil.com) | Email verification | Yes | Measures email deliverability and quality. |
| **Mailboxlayer** | API (mailboxlayer.com) | Email verification | Freemium | 100 requests free, 5000/month — $14.49. Simple REST API. |
| **EmailCrawlr** | API (emailcrawlr.com) | Domain email search | Freemium | 200 requests free. Find all emails associated with a domain. |
| **Kickbox** | API (open.kickbox.com) | Email verification | Yes | Free email verification API. |
| **Reacher** | API (reacher.email) | Real-time verification | Yes | Rust-based, 100% open-source email verification API. |

**Scout workflow integration:**
- When an email is known: run Holehe (account discovery) + h8mail (breach check) in parallel.
- Ghunt is high-value for Google emails — reveals Maps reviews, Photos, YouTube.
- EmailRep for quick risk scoring without API key.

---

## 3. Phone Number Investigation

Identify the owner and metadata of a phone number.

| Tool | Install | Type | Free | Notes |
|------|---------|------|------|-------|
| **PhoneInfoga** | `pip install phoneinfoga` | Phone OSINT | Yes | Carrier, location, line type. Uses free sources (Google, Numverify, OVH). |
| **Numverify** | API (numverify.com) | Validation/lookup | 250 req/mo free | Global phone validation, 232 countries. |
| **Twilio Lookup** | API (twilio.com) | Carrier/location | Free credits | Carrier, caller name, line type. ~$0.01/lookup. |
| **Truecaller** | API (truecaller.com) | Identity | Freemium | Global reverse phone lookup. |
| **Veriphone** | API (veriphone.io) | Validation/carrier | Yes | 1000 requests/month free. Phone validation and carrier lookup. |
| **Infobel** | API (infobel.com) | Contact search | Freemium | 164M+ records across 73 countries. Phone + person + address lookup. |
| **GetContact** | API (getcontact.com) | Phone identity | Paid | Find info about user by phone number. |

**Scout workflow integration:**
- PhoneInfoga is the default (free, no API key, pip-installable).
- Numverify as fallback for international numbers.
- Twilio when caller name is needed (paid, Tier 2).

---

## 4. Face Search & Image

Link a face to online profiles and identities.

| Tool | Type | Free | Notes |
|------|------|------|-------|
| **FaceCheck.ID** | Face-to-profile | Freemium | Searches social media by face. |
| **Socialcatfish** | Face + name search | Freemium | 200B+ records. Face, name, email, phone, username. |
| **Surfface** | Face-to-social | Freemium | Links faces to social media profiles. |
| **Social Links API** | Face + email + phone | Paid | Individual/company profiling, social media tracking, dark web monitoring. Face search API. |
| **MRISA** | Reverse image | Yes (self-hosted) | Google reverse image search API. |
| **PicImageSearch** | Reverse image aggregator | Yes (self-hosted) | Aggregates Google, Yandex, Bing, TinEye. |

**Scout workflow integration:**
- Face search is Tier 2 (requires image input, not always available).
- When a photo is available: run FaceCheck.ID + Socialcatfish in parallel.
- Reverse image (MRISA/PicImageSearch) when profile photos are found.

---

## 5. People Search & Public Records

Find people by name, address, or other attributes.

| Tool | Type | Free | Notes |
|------|------|------|-------|
| **theHarvester** | `pip install theHarvester` | Names, emails, subdomains | Yes | 40+ sources. Gathers names/emails from public data. |
| **OpenSanctions** | API (opensanctions.org) | Sanctions/PEP | Yes | Sanctions lists, politically exposed persons. |
| **FamilyTreeNow** | Web | Genealogy/public records | Yes | Addresses, phone numbers, relatives. No registration. |
| **VoterRecords** | Web | Voter records | Yes | 100M+ US voter records. |
| **PeekYou** | Web | People search | Freemium | Aggregates public profiles. |
| **Pipl** | API | Identity | Paid | Professional identity resolution. Tier 3. |
| **Spokeo** | Web | People search | Paid | Tier 3. |
| **BeenVerified** | Web | Background check | Paid | Tier 3. |
| **Apollo.io** | Web/API | B2B contact finder | Freemium | Free B2B phone & email finder. 1200 credits/year free. |
| **ContactOut** | API | Professional contact | Paid | Find emails & phone for 300M professionals. Tier 3. |
| **Judyrecords** | Web | US court records | Yes | Nationwide search of 400M+ US court cases. |
| **UniCourt** | Web | US court records | Freemium | Nationwide search of 100M+ US court cases. |
| **VineLink** | Web | US inmate search | Yes | Inmate search linked to US correctional facilities. |
| **California Justice Watch** | Web/API/MCP | CA judicial records | Yes | District attorneys, public defenders, judges, misconduct records. Free MCP server. |
| **BuscaPaginasBlancas** | `pip install buscablancas` | Spanish white pages | Yes | OSINT tool for Spanish contact info extraction. |
| **ITP Infotrack** | Web | People/vehicle/property | Freemium | US people, vehicle, property lookup. |
| **ZabaSearch** | Web | People search | Yes | Free US people search (name, phone, address). |

**Scout workflow integration:**
- theHarvester is a Tier 1 default — run it on every person research request
  (pass the name/email/domain to gather associated data).
- OpenSanctions check is automatic (sanctions/PEP screening).
- FamilyTreeNow and VoterRecords for US-based subjects.
- Pipl/Spokeo/BeenVerified are Tier 3 (paid, require permission).

---

## 6. Breach & Leak Search

Find compromised credentials and leaked personal data.

| Tool | Type | Free | Notes |
|------|------|------|-------|
| **h8mail** | `pip install h8mail` | Multi-breach search | Yes | Local search across 20+ breach databases. |
| **HaveIBeenPwned** | API | Breach database | Yes (rate-limited) | Canonical source. |
| **LeakCheck** | API | Breach search | Freemium | 7.5B+ entries. |
| **LeakIX** | API (leakix.net) | Exposed data | Freemium | Exposed databases, leaks. |
| **IntelX** | API (intelx.io) | Dark web + leaks | Freemium | Pastes, leaks, dark web. |
| **InfoStealers** | Web (infostealers.info) | Infostealer logs | Yes | Darknet-exposed infostealer logs. |
| **Leaker** | `pip install leaker` | Multi-breach CLI | Yes | Passive leak enumeration across 10 breach databases simultaneously. |
| **OsintCat** | API (osintcat.net) | Email breach check | Yes | Fast breach lookup across multiple databases. Simple API. |
| **StealSeek** | Web (stealseek.io) | Breach search | Yes | Search and analyze data breaches. |
| **Venacus** | API (venacus.com) | Breach monitoring | Freemium | Search for data breaches and get notified of new compromises. |
| **NOX** | GitHub (nox-project/nox-framework) | Deep breach analysis | Yes | Recursive async framework for deep breach analysis and identity pivoting. |
| **CredenShow** | Web (credenshow.com) | Compromised credentials | Freemium | Identify compromised credentials before others do. |

**Scout workflow integration:**
- h8mail + HIBP run in parallel when email is known.
- LeakCheck/LeakIX as Tier 2 escalation.
- IntelX as Tier 3 (paid for full results).

---

## 7. Dark Web (Person-Specific)

Search for a person's data on dark web markets, leak boards, paste sites, and forums.

| Tool | Type | Free | Notes |
|------|------|------|-------|
| **OnionClaw** | Tor dark web search + fetch + pipeline | Yes (needs Tor) | 12 dark web search engines, .onion fetching, circuit rotation, Robin-based LLM pipeline. Most complete dark web OSINT toolkit available. |
| **Robin** | AI dark web search | Yes (needs Tor + LLM) | Searches dark web engines via Tor, uses LLM to filter. Overlaps with OnionClaw; use Robin when you already have it configured, OnionClaw when starting fresh. |
| **Ahmia** | Web (ahmia.fi) | .onion search | Yes | Clearnet gateway to Tor search. Accessible via SearXNG if `.onion` indexing is enabled. |

**OnionClaw details:**
- 12 verified-live dark web search engines: Ahmia, OnionLand, Amnesia, Torland, Excavator, Onionway, Tor66, OSS, Torgol, TheDeepSearches, DuckDuckGo-Tor, Ahmia-clearnet
- `search.py` — multi-engine search with dedup
- `fetch.py` — fetch any .onion page through Tor
- `renew.py` — rotate Tor circuit (new identity)
- `pipeline.py` — full Robin pipeline: refine → search → filter → scrape → LLM synthesis
- Requires: Tor running (SOCKS 9050), Python 3.10+, `requests[socks] beautifulsoup4 python-dotenv stem`
- Install: `git clone https://github.com/JacobJandon/OnionClaw` then `pip install -r requirements.txt`
- LLM key optional — search and fetch work without one

**Scout workflow integration:**
- OnionClaw is the **preferred dark web tool** (replaces Robin as first-choice).
- Dark web search is Tier 2+ (specialized, requires Tor, not always necessary).
- Run when: research goal involves credential leaks, breach data, dark web forum presence, or ransomware victim listings.
- `scout.sources.discover --query "dark web credential leak"` surfaces OnionClaw.
- Person-relevant queries: `"john.doe@company.com" site:onion`, `"John Doe" leak`, `"CompanyName" breach dump`.

---

## 8. theHarvester — Detailed Module List

theHarvester is the single most impactful addition. It aggregates 40+ sources:

**Search engines:** Baidu, Brave, DuckDuckGo, Google, Mojeek, Yahoo
**Security/cert:** Censys, Certspotter, crt.sh, CriminalIP, FullHunt, ProjectDiscovery
**DNS:** DNSDumpster, RapidDNS, SubdomainCenter, SubdomainFinderC99, THC
**Threat intel:** FOFA, Hunter.how, LeakIX, Netlas, ONYPHE, OTX, SecurityTrails, Shodan, ThreatMiner, VirusTotal, ZoomEye
**People/email:** Hunter, HaveIBeenPwned, RocketReach, Tomba, IntelX
**Breach:** DeHashed, LeakLookup
**Other:** BuiltWith, Dymo, PentestTools, SecurityScorecard, URLscan, Venacus, Windvane

**Usage pattern for Scout:**
```bash
# Gather everything about a person's domain/email
theHarvester -d example.com -b all -l 500

# Search by person name (via search engines)
theHarvester -d linkedin.com -b bing,google -l 200 -q "John Doe"
```

---

## 9. MCP-Wrapped OSINT Servers

These are MCP servers that can be connected via the `native-mcp` skill or `mcporter`:

| MCP Server | Source | Person Capability |
|------------|--------|-------------------|
| **Maigret MCP** | BurtTheCoder/mcp-maigret | Username enumeration |
| **Shodan MCP** | BurtTheCoder/mcp-shodan | IP/email infrastructure |
| **VirusTotal MCP** | BurtTheCoder/mcp-virustotal | Domain/URL/email reputation |
| **DNSTwist MCP** | BurtTheCoder/mcp-dnstwist | Typosquatting detection |
| **ContrastAPI** | UPinar/contrastapi | 49 security/OSINT tools |
| **OSINT Toolkit MCP** | pulsemcp.com | WHOIS, Nmap, DNS, typosquatting |
| **CompanyScope MCP** | Stewyboy1990/companyscope-mcp | Company + person intelligence |
| **OpenRegistry MCP** | sophymarine/openregistry | 27 corporate registries |
| **Not Human Search** | nothumansearch.ai | MCP server discovery (8600+ servers) |
| **Xquik** | Xquik-dev/x-twitter-scraper | X (Twitter) data extraction, 40+ REST API endpoints, real-time monitoring |
| **Expose Team** | expose.team | AI-powered OSINT, credit-based ($8+/mo) |
| **Checko MCP** | Nymaxxx/checko-mcp | Russian company/individual verification (EGRUL/EGRIP), paid |
| **StockScope** | Stewyboy1990/companyscope-mcp | SEC EDGAR financial intelligence, free |
| **AnySite** | anysite.io | Structured data from 115+ endpoints across 40+ platforms (LinkedIn, Instagram, X, Reddit, YouTube, GitHub, Amazon) — 7-day free trial, then paid |
| **Bright Data MCP** | brightdata/brightdata-mcp | Real-time web search, scraping, structured data from 60+ sources (LinkedIn, TikTok, Google Maps, etc.) — free tier 5,000 req/mo |
| **US Business Data MCP** | avabuildsdata/mcp-us-business-data | Secretary of State business registrations (17 US states), building permits (400+ cities), Yellow Pages — paid |
| **OpenOSINT** | OpenOSINT/OpenOSINT | AI-powered OSINT agent with interactive REPL, MCP server, and CLI — free tier available |
| **TWZRD Agent Intel** | intel.twzrd.xyz | Blockchain OSINT for AI agent trust scoring (Solana wallet history, transaction patterns) — free preflight + paid signed receipts |
| **The Stall** | the-stall.intuitek.ai | Multi-tool blockchain OSINT: OFAC sanctions screening (19k+ SDN), wallet risk scoring, agent KYA trust scoring — pay-per-call via x402 USDC on Base |

**Scout workflow integration:**
- See `scout_mcp_discovery.md` for the dynamic discovery mechanism.
- MCP servers are loaded at runtime via the native MCP client.
- Not Human Search is the meta-discovery engine — use it to find new OSINT MCP servers.

---

## Source Priority Matrix

For a typical person research request, run in this order:

1. **theHarvester** (domain/email gathering) — always
2. **Sherlock** (username check) — if handles known
3. **Maigret** (deep username) — if Sherlock returns < 3
4. **Holehe** (email → accounts) — if email known
5. **h8mail** (breach check) — if email known
6. **Ghunt** (Google account) — if Gmail address
7. **PhoneInfoga** (phone OSINT) — if phone known
8. **EmailRep** (email risk) — if email known
9. **OpenSanctions** (sanctions) — always
10. **FaceCheck.ID** (face search) — if photo available
11. **Social Analyzer** (broad username) — Tier 2 escalation
12. **OnionClaw** (dark web) — Tier 2+ if Tor available, when leaks/breach data relevant
13. **Robin** (dark web) — alternative to OnionClaw if already configured
