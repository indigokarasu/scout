# Scout Person-Specific OSINT Sources

Curated list of person-specific OSINT tools and APIs, organized by capability.
Updated: 2026-11-22. Sources reviewed from jivoi/awesome-osint, cipher387/API-s-for-OSINT,
soxoj/awesome-osint-mcp-servers, christinminor459/OnionClaw (README unreachable this cycle;
last known state retained), plus APIs-for-OSINT people/email/phone/face sections.

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
| **Castrick** | Web (castrickclues.com) | Multi-platform | ~30s | Find social media accounts with email, username, and phone number. |
|| **Predicta Search** | Web (predictasearch.com) | Multi-platform | ~30s | Search for social accounts with email and phone. |
|| **CheckUser** | Web (checkuser.vercel.app) | Username search | ~15s | Quick username search across social networks. |
|| **IDCrawl** | Web (idcrawl.com/username) | Username search | ~20s | Search for a username in popular social networks. |
|| **Name Chk** | Web (namechk.com) | Username/domain | ~15s | Check 30+ domains and 90+ social media account platforms. |
|| **Name Checkr** | Web (namecheckr.com) | Username/domain | ~15s | Checks domain and username across many platforms. |
|| **Name Checkup** | Web (namecheckup.com) | Username availability | ~15s | Check username availability across all social media and platforms. |
|| **NameKetchup** | Web (nameketchup.com) | Username/domain | ~15s | Checks domain name and username in popular social media/platforms. |
|| **Snoop** | `pip install snoop` | Nickname search | ~45s | Search for a nickname on the web (OSINT world). |
|| **Cupidcr4wl** | `pip install cupidcr4wl` | Username + phone | ~30s | Crawls adult content platforms for targeted accounts or persons. |
|| **Helix** | GitHub (thalha-a9/helix) | 8,000+ sites | ~60s | Checks a username on 8,000+ sites, re-verifies every hit live against impossible usernames, and graphs how the accounts connect. |
|| **TraceFind** | Web (tracefind.info) | Thousands of sites | ~30s | Scans thousands of sites for username presence. |
|| **Threat Actor Username Search** | Web (threatactorusernames.com) | 3M+ threat-actor usernames | ~15s | Search where known criminal and bot usernames post and operate online. |
|| **User Search** | Web (usersearch.org) | 3,000+ sites | ~60s | Username, email, phone number or picture across social networks, dating sites, forums, crypto forums, chat sites and blogs. |
|| **TwexAPI Twitter Viewer** | Web (twexapi.io) | X (Twitter) | ~15s | View a public X profile and its latest posts without logging in or creating an account. |
|| **Osintgram** | GitHub (Datalux/Osintgram) | Instagram | ~60s | Interactive shell for OSINT analysis of any Instagram account by nickname. |
|| **insto** | GitHub (subzeroid/insto) | Instagram | ~60s | OSINT CLI/REPL: profile, media, followers, dossier, geo-fingerprint; token-based (HikerAPI), no IG account needed. |
|| **2Chat** | Web (2chat.co/tools/whatsapp-checker) | WhatsApp | ~15s | Check whether a phone number is on WhatsApp. |
|| **Telerecon** | GitHub (sockysec/Telerecon) | Telegram | ~60s | Reconnaissance framework for researching and investigating Telegram. |
|| **Teleteg** | Web (teleteg.com) | Telegram | ~30s | Telegram search engine and channel catalog; 10 results on the free plan. |
|| **Tme-s** | GitHub (axmaier/tme-s) | Telegram | ~30s | Reads public Telegram channels via logged-out t.me/s previews; no API key, phone number, or account. |

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
|| **OSINT Industries** | API (osint.industries) | Email/phone/search | Freemium | Powerful OSINT platform for investigators. Search emails, phone numbers, other selectors. Free for non-profits. |
|| **FachaAPI** | API (api.facha.dev) | Temp email detection | Yes | Check if an email domain is a temporary/disposable email domain. |
|| **Email Permutator** | Web (polished.app/email-permutator) | Email generation | Yes | Generate potential email addresses for a contact by permutating name patterns. |
|| **EmailHippo** | Web (tools.verifyemailaddress.io) | Verification platform | Freemium | Email address verification platform — checks if address exists. |
|| **Snov.io** | Web/API (snov.io/email-finder) | Email finder | Freemium | Find email addresses on any website. API + chrome extension. |
|| **Toofr** | Web (toofr.com) | Email finder | Freemium | Find anyone's email address in seconds. |
|| **Peepmail** | Web (samy.pl/peepmail) | Email discovery | Yes | Discover business email addresses for users, even if not publicly shared. |
|| **Email Extractor** | Web (99tools.net/email-extractor) | Bulk extraction | Yes | Browser-based utility to extract email addresses from bulk text or raw data. |
|| **Blacklist Checker** | Web (blacklistchecker.com) | Blacklist check | Yes | Checks 100+ email blacklists in seconds. |
|| **Email Address Validator** | Web (email-validator.net) | Deliverability | Yes | Deliverability, bounce reduction, fraud prevention. |
|| **Email Format** | Web (email-format.com) | Format patterns | Yes | Finds the email address formats used by different companies. |
|| **Gitrecon** | GitHub (atiilla/gitrecon) | GitHub scan | Yes | Node.js tool scanning GitHub repositories for exposed emails and names. |
|| **Hunter** | Web (hunter.io) | Email finder | Freemium | Finds email addresses by domain and connects them to people. |
|| **MailTester** | Web (mailtester.com) | Email discovery | Yes | Hunt for emails and improve deliverability. |
|| **OpenLeads** | GitHub (Samyrrrrrr990/openleads) | People + work email | Yes | CLI finding people and work emails from OpenStreetMap, GitHub, OpenAlex, SEC EDGAR and team pages; labels each address found/pattern/guessed; no API keys. |
|| **ThatsThem** | Web (thatsthem.com) | Reverse email lookup | Freemium | Reverse email lookup. |
|| **Verify Email** | Web (verify-email.org) | Verification | Yes | Email verification — checks whether an address exists. |
|| **Kiprio Disposable Email** | Web (kiprio.com/v1/disposable-email/) | Disposable check | Yes | Checks whether an email domain is temporary/disposable; no auth required. |
|| **Kiprio Email Validate** | Web (kiprio.com/v1/email-validate/) | Validation | Yes | MX record checks, disposable-domain detection, typo suggestions. |
|| **GitLeak** | Web (gitleak.io) | Yes | GitHub OSINT: extracts hidden email addresses, commit timezones and activity patterns via .patch metadata. [Tier 1] |
|| **OSINTEye** | GitHub (atiilla/OsintEye) | Yes | WPF desktop app for GitHub intelligence, social media reconnaissance and subdomain discovery. [Tier 1] |
|| **VoilaNorbert** | Web (voilanorbert.com/api/) | Paid | Find anyone's contact information for lead research and talent acquisition. From $49/month. [Tier 3] |
|| **looot** | API (looot.ai) + MCP | Paid, no free tier | Work email and phone lookup, email verification, company and people enrichment; pay-per-call API and MCP server. Prepaid balance from $5. [Tier 3] |

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
|| **GetContact** | API (getcontact.com) | Phone identity | Paid | Find info about user by phone number. |
|| **Plivo** | API (plivo.com/lookup) | Carrier/line type | Freemium | Determine carrier, number type, format, and country. From $0.04/request. |
|| **EmobileTracker** | Web (emobiletracker.com) | Phone tracking | Freemium | Track mobile number, location on Google Map, owner name, country, telecom provider. |
|| **FreeCarrierLookup** | Web (freecarrierlookup.com) | Carrier lookup | Yes | Returns carrier name, wireless/landline, email-to-SMS gateways for US/CA numbers. |
|| **InMobPrefix** | GitHub (hstsethi/in-mob-prefix) | India prefix data | Yes | Dataset, charts, models about mobile phone number prefixes in India. |
|| **Phone Validator** | Web (phonevalidator.com) | Phone lookup | Freemium | Accurate phone lookup, particularly good against Google Voice numbers. |
|| **Spy Dialer** | Web (spydialer.com) | Voicemail + owner | Freemium | Get voicemail of a cell phone & owner name lookup. |
|| **Sync.ME** | Web (sync.me) | Caller ID | Freemium | Caller ID and spam blocker app with reverse lookup. |
|| **USPhoneBook** | Web (usphonebook.com) | Reverse phone lookup | Freemium | Reverse phone and address lookups. |
|| **SearchPeopleFREE** | Web (searchpeoplefree.com/phone-lookup) | Phone/address lookup | Free | Reverse name, address, email, or phone lookup. |
|| **Reverse Phone Lookup** | Web (reversephonelookup.com) | Phone lookup | Freemium | Carrier, region, service provider, and switch information. |

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
| **Search4faces** | API (search4faces.com/api.html) | Face detection + bounding boxes | Paid | Detect and locate human faces within an image. $21/1000 requests. |
| **Face++** | API (faceplusplus.com) | Face search by image | Paid | Search for people in social networks by facial image. From $0.03/call. |
| **BetaFace** | API (betafaceapi.com) | Face analysis + search | Freemium | Scan images/URLs, find faces, verify and identify. 50 images/day free. |
|| **Bing Images Search API** | API (bing.com/apis/bing-image-search-api) | Reverse image | Freemium | 1,000 free requests/month; reverse image search with thumbnails, full-size URLs and image metadata. |
|| **Google Reverse images search API** | GitHub (SOME-1HING/google-reverse-image-api) | Reverse image | Free | Unofficial Node.js/Express API for Google reverse image search by image URL. |
|| **Dupli Checker** | Web | Yes | Reverse image search by upload, URL, or keyword. [Tier 1] |
|| **Faceagle** | Web | Limited free | Face recognition search engine. [Tier 2] |
|| **GeoSpyer** | GitHub (atiilla/geospy) | Yes | Python tool using Graylark's AI geo-location service to uncover where photos were taken. [Tier 1] |
|| **KartaVision** | Web | Yes | Search engine for KartaView imagery; natural-language and image search. [Tier 1] |
|| **Lenso.ai** | Web | Limited free | Reverse image search with facial recognition — find people, similar images, identical places. [Tier 2] |
|| **PicTriev** | Web | Yes | Face search engine. [Tier 1] |
|| **PimEyes** | Web | Paid | Online face search engine finding pictures containing given faces across the Internet. [Tier 3] |
|| **ChronoVerify** | Web | Free web tool | EXIF/XMP reader, C2PA Content Credentials validation, classical pixel forensics with a typed verdict. [Tier 2] |
|| **GeoSpy** | Web | Limited free | AI-based image OSINT: geolocate where a photo was taken. [Tier 2] |
|| **ProfileImageIntel** | Web | Yes | Social media and WhatsApp profile image tool: find when a profile image was uploaded. [Tier 1] |
|| **TinEyeAPI** | API (services.tineye.com/TinEyeAPI) | Paid | Reverse image search API: verify images, track usage, check uniqueness. From $200/5,000 searches. [Tier 2] |
|| **Picarta** | API (picarta.ai/api) | Yes | Estimate the location where a photo was taken from visual content. 100 requests/day free. [Tier 1] |
|| **Oceanir** | API (docs.oceanir.ai) | Paid | Estimate photo locations from visual content without GPS metadata. Paid credits; API access reviewed. [Tier 2] |

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
| **FinalNotes** | Web (finalnotes.page) | Obituary research | Yes | Guide for finding obituary records, preserving source trails, turning obituary clues into sourced family-history stories. |
| **LERS Portal Directory** | Web (ministryofcyberaffairs.com) | Law-enforcement data requests | Yes | Directory of platform law-enforcement data-request portals (WhatsApp, Google, Apple, Telegram, TikTok, Binance). |
| **OSINTNova** | Web (app.osintnova.com) | AI-powered OSINT | Freemium | AI-powered platform for advanced digital investigations and intelligence analysis. |
| **AnalyzeID** | Web | Identity analysis | Freemium | Identity analysis and verification platform. |
|| **192 (UK)** | Web (192.com) | People search | Freemium | Search by person, business, or address in the UK; limited free info, premium upsell. |
|| **411 (US)** | Web (411.com) | People search | Freemium | Person, phone number, address, and business search; limited free info, premium upsell. |
|| **Black Book Online** | Web (blackbookonline.info) | Public records | Yes | Free nationwide directory of public record lookups. |
|| **Canada411** | Web (canada411.ca) | People search | Yes | Person, phone number, and business search in Canada. |
|| **Family Search** | Web (familysearch.org) | Genealogy | Yes | Popular free genealogy site; registration required. |
|| **Federal Bureau of Prisons Inmate Locator (US)** | Web (bop.gov) | Inmate search | Yes | Federal inmates incarcerated from 1982 to the present. |
|| **Offendersearch** | Web (offendersearch.app) | Offender registries | Yes | All 58 US state, territory and tribal sex-offender registries in one query; public API + MCP server. |
|| **recap-cli** | GitHub (NPCmillionaire/recap-cli) | Court dockets | Yes | Free CLI to search and download U.S. federal court dockets from the RECAP archive (CourtListener); free API token required. |
|| **UK Phone Book** | Web (ukphonebook.com/) | People search | Freemium | UK people search similar to 192.com. |
|| **VerifiedHer** | Web (verifiedher.com) | Creator registry | Yes | Free registry of online creators and influencers with sourced real / AI persona / unverified verdicts. |
|| **White Pages (US)** | Web (whitepages.com) | People search | Freemium | Limited free info, premium data upsell. |
|| **Genderize.io** | API (genderize.io) | Name analysis | Yes | Gender likelihood and name popularity from a first name; 1,000 names/day free. |
|| **Agify.io** | API (agify.io) | Name analysis | Yes | Predicts age from a name; 1,000 names/day free. |
|| **Nationalize.io** | API (nationalize.io) | Name analysis | Yes | Predicts nationality from a name; 1,000 names/day free. |
|| **Geocreepy** | Web | Yes | Geolocates social media check-ins and posts; maps where a person has been. [Tier 1] |
|| **Mail.Ru Social Network Search** | Web | Yes | Russian social network search — find profiles across the Mail.Ru ecosystem. [Tier 1] |
|| **SocialBlade** | Web | Limited free | YouTube/Twitch/Instagram/TikTok creator statistics, subscriber and view counts, rankings. [Tier 2] |
|| **ExportData** | Web | Limited free | Data export tool for historical tweets, followers & followings, and historical trends. [Tier 2] |
|| **Foller.me** | Web | Limited free | Twitter/X account analysis: activity, word clouds, friends, maps. [Tier 2] |
|| **MyTweetAlerts** | Web | Limited free | Custom email alerts based on Twitter search queries. [Tier 2] |
|| **TweetAPI Twitter ID Finder** | Web | Yes | Find the user ID behind a Twitter username or profile link, or look up the current username for an ID. [Tier 1] |
|| **the-endorser** | GitHub (eth0izzle/the-endorser) | Yes | Draw out relationships between people on LinkedIn via endorsements and skills. [Tier 1] |
|| **LinkedInDumper** | GitHub (l4rm4nd/LinkedInDumper) | Yes | Script to dump/scrape/extract company employee info from LinkedIn. [Tier 1] |
|| **GroupDa** | Web | Yes | Search Telegram channels by category, country, and language. [Tier 1] |
|| **Maltego Telegram** | GitHub (vognik/maltego-telegram) | Yes | Rich set of entities and transforms for OSINT on Telegram with Maltego. [Tier 1] |
|| **TgramSearch** | Web | Yes | Convenient search for Telegram channels; structured catalog of 700,000+ channels. [Tier 1] |
|| **Telepahty** | GitHub (proseltd/Telepathy-Community) | Yes | Archives Telegram chats and analyzes communication patterns within groups and channels. [Tier 1] |
|| **Telegago** | Web | Yes | Google Custom Search for finding public and private Telegram channels and chats. [Tier 1] |
|| **Telegram-Archive** | GitHub (GeiserX/Telegram-Archive) | Yes | Self-hosted backup of a Telegram account's chats and media with local web viewer and search. [Tier 1] |
|| **TeleSearch** | Web | Yes | Search and find Telegram channels, groups, bots, and games. [Tier 1] |
|| **TeleTracker** | GitHub (tsale/TeleTracker) | Yes | Python scripts for investigating Telegram channels; gather channel information. [Tier 1] |
|| **tg-chat-dump** | GitHub (renkagod/tg-chat-dump) | Yes | Archives a whole Telegram group/channel/forum into searchable SQLite and per-topic JSONL files. [Tier 1] |
|| **TGScope** | Web | Yes | Search engine and catalog of 3M+ public Telegram channels by topic, language, size; event pages mentioning people. [Tier 1] |
|| **TGScope Channel Creation Date** | Web | Yes | Tells when a Telegram channel or supergroup was created from username, t.me link, or numeric ID. [Tier 1] |
|| **TGStat** | Web | Limited free | OSINT platform analyzing Telegram channels, groups, metrics, trending activity. [Tier 2] |
|| **TOsint** | GitHub (drego85/tosint) | Yes | Telegram OSINT: extract information from Telegram bots and channels. [Tier 1] |
|| **OSINT-Steam** | Web | Yes | Open-source tool returning public info from Steam profiles: friends list, possible locations. [Tier 1] |
|| **Steam-OSINT** | GitHub (matiash26/steam-osint) | Yes | Open-source OSINT tool for mutual friends analysis on Steam, supporting full friend lists. [Tier 1] |
|| **GHNames** | Web | Yes | GitHub lookup: username history, associated emails, deleted repositories. [Tier 1] |
|| **github_monitor** | GitHub (misiektoja/github_monitor) | Yes | Real-time tracking of GitHub users' activity: profile and repository changes, email alerts, CSV logging. [Tier 1] |
|| **GithubRecon** | Web | Yes | Lookup GitHub users by username or email and gather associated data. [Tier 1] |
|| **Dolphin Radar** | Web | 1 free view | Instagram Post Viewer: view posts, stories, profiles from public accounts. [Tier 2] |
|| **IGDetective** | Web | Limited free | Anonymous Instagram investigation: story viewer, follower tracker, profile viewer, optional Story Archive. [Tier 2] |
|| **instagram_monitor** | GitHub (misiektoja/instagram_monitor) | Yes | Real-time tracking of Instagram users' activity and profile changes; email alerts, CSV logging, story downloads. [Tier 1] |
|| **Osintgraph** | GitHub (XD-MHLOO/Osintgraph) | Yes | Maps a target's Instagram data and relationships in Neo4j for social network analysis. [Tier 1] |
|| **Toutatis** | GitHub (megadose/toutatis) | Yes | Extract information from Instagram accounts: emails, phone numbers, and more. [Tier 1] |
|| **GetTikVideo** | Web | Yes | Full-size profile picture and latest public videos from a TikTok profile link, no account needed. [Tier 1] |
|| **TikTokStalker** | Web | Yes | Lookup information about TikTok users and content. [Tier 1] |
|| **Arctic Shift** | GitHub (ArthurHeitmann/arctic_shift) | Yes | Access and interact with large dumps of Reddit data via API and web interface. [Tier 1] |
|| **Pushshift API** | Web | Yes | API for historical Reddit data: posts, comments, metadata for research. [Tier 1] |
|| **Pullpush** | Web | Yes | Indexing and retrieval of Reddit content; useful for finding deleted/removed posts and comments. [Tier 1] |
|| **REDARCS** | Web | Yes | Reddit archives 2005-2023. [Tier 1] |
|| **RedditMetis** | Web | Limited free | Reddit user analysis tool: summary and statistics for an account, top posts, user activity. [Tier 2] |
|| **Universal Scammer List** | Web | Yes | List of malicious Reddit accounts from /r/universalscammerlist; minimizes scam damage. [Tier 1] |
|| **Дезертир** | Web | Yes | VKontakte OSINT application. [Tier 1] |
|| **Barkov.net** | Web | Yes | VKontakte OSINT tools. [Tier 1] |
|| **VK5** | Web | Yes | VKontakte search and OSINT utilities. [Tier 1] |
|| **VK.watch** | Web | Yes | VKontakte profile and content lookup. [Tier 1] |
|| **Groupio** | Web | Yes | Find and search WhatsApp groups. [Tier 1] |
|| **Ancestry** | Web | Free trial with credit card | Premium genealogy and family history data. [Tier 3] |
|| **Classmates** | Web | Free accounts | High-school-focused people search; create profile and view other members. [Tier 2] |
|| **CrunchBase** | Web | Limited free | Business information database with executive and founder data. [Tier 2] |
|| **Fold3 (US Military Records)** | Web | Limited free | Search U.S. military records; premium access requires subscription. [Tier 2] |
|| **InfoTracer** | Web | Paid | People search across public records. [Tier 3] |
|| **Mugshots** | Web | Yes | Arrest photos and booking records. [Tier 1] |
|| **Reunion** | Web | Limited free | People search with limited free info, premium upsell. [Tier 2] |
|| **SearchBug** | Web | Limited free | People search; limited free info, premium data upsell. [Tier 2] |
|| **The National Archives (UK)** | Web | Yes | Search UK national archives. [Tier 1] |
|| **HiCreators** | API (hicreator.ai/api-docs) | Paid | API collecting info about X, YouTube, Instagram and TikTok influencers. From $59/month. [Tier 3] |
|| **SocialData API** | API (socialdata.tools) | Paid | Unofficial Twitter API: scrape tweets by user, hashtag or keyword, and user profiles. $0.20 per 1,000 results. [Tier 2] |
|| **xdataapi.io** | API + MCP | Paid | Read-only public X data: profiles, tweets, threads, followers, search. MCP server and SDKs. $0.06-$0.125 per 1,000 items; 5,000 free credits. [Tier 2] |
|| **DataXAPI** | API + MCP | Paid | Public posts, comments, accounts, search and hot lists from Douyin, Xiaohongshu, WeChat, Weibo, Bilibili, Zhihu, Kuaishou, TikTok, X, YouTube, Instagram, Reddit; Meta and Google ad libraries. Pay per call from $0.0003; up to 333 calls free. [Tier 2] |

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
| **HIB Ransomed** | Web (haveibeenransom.com) | Ransomware leak check | Yes | Check if data has been leaked in ransomware incidents. |
| **HEROIC.NOW** | Web (heroic.com) | Dark web leak scan | Freemium | Scan identities for dark web data leaks. Free tier available. |
| **IKnowYour.Dad** | Web (iknowyour.dad) | Breach search engine | Yes | Data breach search engine. |
|| **BreachDirectory.com** | API (breachdirectory.com) | Breach search | Free | Search domain in data breach databases. |
|| **LeekLookup** | API (leak-lookup.com) | Multi-field breach search | Freemium | Search domain, email, fullname, IP, phone, password, username in leaks. 10 requests free. |
|| **LeakPeek** | API (leakpeek.io) | Leak database search | Paid | Search in leak databases. $9.99/4 weeks unlimited. |
|| **Psdmp.ws** | API (psbdmp.ws/api) | Pastebin search | Freemium | Search pastebin dumps. $9.95/10,000 requests. |
|| **BreachDirectory.org** | API (rapidapi.com/rohan-patra/api/breachdirectory) | Breach search | Freemium | Search domain, email, fullname, IP, phone, password, username in breaches. 50 req/mo free. |
|| **CheckLeaked** | Web/API (checkleaked.cc) | Breach search | Freemium | Email, username, or phone breach check showing sources; free searches, developer API and chat bots. |
|| **Hudson Rock** | Web (cavalier.hudsonrock.com/docs) | Infostealer search | Yes | Search whether a domain, email address, or username was compromised in global infostealer campaigns. |

**Scout workflow integration:**
- h8mail + HIBP run in parallel when email is known.
- LeakCheck/LeakIX as Tier 2 escalation.
- IntelX as Tier 3 (paid for full results).

---

## 7. Dark Web (Person-Specific)

Search for a person's data on dark web markets, leak boards, paste sites, and forums.

| Tool | Type | Free | Notes |
|------|------|------|-------|
| **OnionClaw** | Tor dark web search + fetch + pipeline | Yes (needs Tor) | 18 dark web search engines, .onion fetching, circuit rotation, Robin-based LLM pipeline. Based on SICRY engine. Most complete dark web OSINT toolkit available. |
| **Robin** | AI dark web search | Yes (needs Tor + LLM) | Searches dark web engines via Tor, uses LLM to filter. Overlaps with OnionClaw; use Robin when you already have it configured, OnionClaw when starting fresh. |
| **Ahmia** | Web (ahmia.fi) | .onion search | Yes | Clearnet gateway to Tor search. Accessible via SearXNG if `.onion` indexing is enabled. |
| **Onion Lookup** | API (onion.ail-project.org) | .onion metadata | Yes | Check existence of Tor hidden services and retrieve associated metadata. |
| **Darksearch.io** | API (darksearch.io/apidoc) | .onion search | Free | Search by websites in .onion zone. |
|| **Aleph Open Search** | Web (open-search.aleph-networks.eu) | Dark web search | Yes | Dark web search engine indexing .onion content. |

**OnionClaw details:**
- 18 verified-live dark web search engines: Ahmia, OnionLand, Amnesia, Torland, Excavator, Onionway, Tor66, OSS, Torgol, TheDeepSearches, DuckDuckGo-Tor, Ahmia-clearnet, plus 6 additional SICRY-based engines
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
| **Voidly** | @voidly/mcp-server (npm) | Censorship intelligence | Free | 116 tools across 119+ countries. Query OONI/IODA/CensoredPlanet evidence, check domain blocking, ISP risk scores, ML shutdown forecasts. No API key. |
| **BGPT MCP** | bgpt.pro/mcp | Scientific paper search | Freemium | Structured full-text evidence: methods, sample sizes, results, limitations. Free tier: 50 results. |
| **Helium MCP** | heliumtrades.com/mcp-page | News bias scoring | Freemium | 37-dimensional news bias scoring across 216 sources, market data, ML options pricing. |
| **DataNexus MCP** | smithery.ai | Public records intelligence | Freemium | 55 tools across 7 domains: domain recon, patent search, US government contracts, regulatory filings, nonprofit data, CVE/SBOM, professional license verification. No API key required for free tier. |
| **ZoomEye MCP** | zoomeye-ai/mcp_zoomeye | Network asset info | Freemium | Query ZoomEye for network asset info. 7-day free trial, requires API key. |
|| **Consensus OSINT** | OSINT-Experts-Society/Consensus-OSINT | Person lookups | Free | Local MCP server for username, email, phone and web-page lookups; 7 tools with structured, paginated results. `consensus mcp --transport stdio`. |
|| **OSINT Tools MCP** | frishtik/osint-tools-mcp-server | Person lookups | Free | Wraps Sherlock, Blackbird, Maigret, Holehe, Ghunt, theHarvester and SpiderFoot behind one MCP server; installs the underlying CLIs itself. |
|| **OSINT Toolbox MCP** | renkagod/osint-toolbox-mcp | Person lookups | Free | Runs 12 OSINT tools locally: Sherlock, Maigret, Blackbird, Holehe, Ghunt, theHarvester, SpiderFoot, subfinder, dnsrecon, dnstwist, PhoneInfoga, ExifTool, plus WHOIS/DNS/crt.sh/Wayback. No API keys. |
|| **LinkedIn MCP** | eliasbiondo/linkedin-mcp-server | Person lookups | Free | LinkedIn people, company and job search with structured profile data; uses your own session cookie, no API key. |
|| **Clearfront** | scottmartinanderson/clearfront | Footprint scan | Free | Self-OSINT footprint scanner: 30 tools incl. username enumeration, email/breach checks, domain/IP recon, EXIF/GPS; evidence graph with confidence ratings. `pip install clearfront`. |
|| **Darknet MCP** | badchars/darknet-mcp-server | Dark web + breach | Free | 66 tools: ransomware victim listings, stealer logs, HIBP, IntelX, Tor .onion fetching, exit-node checks; many keyless. |
|| **Arcmira** | arcmira.com / mcp.arcmira.com/mcp | SOCMINT: public statements across indexed YouTube videos with transcript passages and source timestamps. Requires sign-in or API key. Free tier + paid plans. [Tier 2] |
|| **TwitterAPIs MCP** | TwitterAPIs/twitterapis-mcp | X (Twitter) data: tweet search, user profiles, followers, timelines, account monitoring — 68 read tools without an X developer account. Pay per call ($0.0008, $0.50 starter credit). [Tier 2] |
|| **TweetAPI MCP** | tweetapi/tweetapi-mcp | Read-only Twitter data: tweet search, profiles, About this account (location, username history), followers, lists, communities, Spaces. OAuth or TweetAPI key. [Tier 2] |
|| **BulkTranscripts** | pratie/bulktranscripts-mcp | YouTube channel uploads, in-channel topic search, full transcripts as clean text — poll a subject's channel. 30 free credits/shared IP, then paid packs. [Tier 2] |
|| **LinkMCP** | app.linkmcp.io | LinkedIn research and automation through your own account: profile/company lookup, people search, work email and mobile lookup. Free trial, plans from $19/month. [Tier 3] |
|| **Kooperativa.io** | kooperativa-team/kooperativa-mcp | Enrich and search professional profiles and companies: work history, headcount by seniority, hiring signals, job changes. API key, 7-day free trial. [Tier 2] |
|| **TubeText YouTube Transcripts** | LMSlay/tubetext-mcp | YouTube transcripts (videos, Shorts, playlists, channels, Whisper fallback), channel stats and Social Blade history. Apify OAuth; free monthly credit. [Tier 2] |
|| **GetYouTubeTranscript** | getyoutubetranscript.com | Full YouTube transcripts, in-channel search, channel/video lists; polling latest uploads is free. OAuth or API key; 100 free credits. [Tier 2] |
|| **LurkAPI** | lurkapi.com | Public profiles, posts, comments, video transcripts, ad library from TikTok, Instagram, YouTube, Reddit, X, LinkedIn and 10+ platforms without logging in. 89 tools. OAuth or API key; 100 free credits. [Tier 2] |
|| **SandBase CLI** | sandbaseai/cli | Local MCP bridge for social/web OSINT: X, YouTube, Reddit, TikTok, Instagram, Xiaohongshu, Weibo, Bilibili, page scraping. Browser OAuth. [Tier 2] |
|| **ReadGZH** | sweesama/readgzh | Full text of public WeChat Official Account articles as Markdown (title, account, publish time); keyword search and per-account listing. API key; anonymous shared-IP limits. [Tier 2] |
|| **FilingFirehose** | filingfirehose.com/mcp | Hosted SEC EDGAR MCP for any US ticker: 8-K body-text parsing, 10-K/10-Q/S-3/13D reads, forensic risk scoring, cyber-incident tracking. Free public endpoints; paid from $9/month. [Tier 2] |
|| **OpenSOSData** | OpenSOSData/opensosdata-mcp | US business entity search across all 53 Secretary of State jurisdictions; 33M-entity index. First 10 lookups free, then $0.0314 each. [Tier 2] |
|| **Fylings** | HeyZod/fylings-mcp | African company intelligence across 18+ national registries: company search, beneficial ownership, contract awards, sanctions screening. Free, no API key. [Tier 1] |
|| **Reestri** | apify.com/reestri | Public company registers of Georgia and Armenia: NAPR lookup, person-to-companies search, Armenian beneficial-owner declarations. Pay per lookup. [Tier 3] |
|| **Auregistre** | auregistre.fr/api | Dated history of a French company by SIREN from BODACC gazette: name/seat/capital changes, insolvency, filed accounts, grants, state aid. No key, no account. [Tier 1] |
|| **open-data-mcp** | markatdataandbeyond/open-data-mcp | EU VAT (VIES) + LEI, French Sirene, Nordic registries, TED tenders, PubMed, ClinicalTrials.gov, NHTSA VIN recalls. No API key for basic tools. [Tier 1] |
|| **TinyRex MCP** | emirmrkaljevic/tinyrex-mcp | Official company registers (France, Norway, Finland, UK), GLEIF LEI, SEC EDGAR filings, US NPI registry (healthcare providers), EU/US/UK/NL tender portals. Runs on your Apify token. [Tier 2] |
|| **Crunchbase Company API** | alphaosint.com/sources/crunchbase-company-api | Unofficial Crunchbase wrapper: funding rounds, investors, headcount range, founders and key people. Apify account required. [Tier 3] |
|| **cvrradar** | cvrradar.dk | Danish CVR register: search by name/CVR/domain/email, people and roles with dates, ownership graph, annual accounts, bankruptcies. Free API key. [Tier 1] |
|| **Equibles** | daniel3303/Equibles | Who owns and trades a US public company: SEC full-text search, Form 4 insider trades, 13F holders, congressional trades. Free tier 100 requests/day. [Tier 2] |
|| **Edgrapi** | edgrapi.com | SAM.gov opportunities, USAspending awards, Grants.gov, House STOCK Act trades, SEC EDGAR filings as flat JSON. 19 read-only tools. 50 free credits, then $10/month. [Tier 2] |
|| **EU & Nordic Open Data MCP** | itulo/eu-nordic-open-data-mcp | Official EU/Nordic records: EU sanctions, TED tenders, VIES VAT, GLEIF LEI, Finnish PRH, Norwegian Brreg, safety recalls. 49 tools. No key except optional Fingrid. [Tier 1] |
|| **Open Data Actors MCP** | Mamoo85/open-data-actors-mcp | Sanctions screening, SEC Form D, new business filings, FMCSA carrier census, WARN layoffs, city agendas, WHOIS/DNS/SSL. Apify token, pay-per-result. [Tier 2] |
|| **National ID & Tax ID Validator** | soxoj/national-id-mcp | Validate/decode national IDs, tax, company, VAT, passport, MRZ numbers: 222 types across 108 countries. Structure/checksum only, no registry query. Free. [Tier 1] |
|| **Sanctions Screening MCP** | cyanheads/sanctions-screening-mcp-server | Screen names against consolidated OFAC, EU, UK, UN sanctions lists; resolve companies to GLEIF LEIs; local SQLite/FTS5 index, offline matching. Free, no API key. [Tier 1] |
|| **ThreatCluster** | Jam0k/Threat-Intelligence-MCP | Clustered incident records from 20,000+ sources, validated IOCs, CVE lookup, ransomware leak-site victims. Free API key: 100 credits/day. [Tier 2] |
|| **XposedOrNot** | XposedOrNot/XposedOrNot-API | Data breach lookups for emails and domains: breaches an address appears in, full breach history, public catalog, domain exposure counts. Read-only, no passwords. Free, no API key. [Tier 1] |
|| **osint-agent-skills** | frangelbarrera/osint-agent-skills | 23 MCP tools: DNS, Shodan InternetDB, crt.sh, Wayback CDX, GitHub code search, OTX, HIBP, Etherscan, Mastodon. Zero-dependency Node.js server. Free. [Tier 1] |
|| **Claudii Exploratores** | SOsintOps/claudii-exploratores | OSINT suite: 898 curated tools across 24 categories (people, usernames, email, domains, IP, phones, companies) as Claude Agent Skill and MCP server. Free (alpha). [Tier 1] |
|| **Iris** | iriscan.app/mcp | Wallet attribution on Solana, EVM, Bitcoin, Tron: funding sources, money flows, labels from 640,000+ known addresses, mixer/bridge traces. 10 free analyses, then 3/day. [Tier 2] |
|| **Tanod** | tanod.dev | Pre-transaction risk verdict, OFAC SDN crypto-address screening, token/transaction/ENS lookups, RDAP/DNS/IP. 200+ tools. Small free daily tier, then x402. [Tier 1] |
|| **Bridge Watch** | LakeSky/bridge-watch | On-chain address intelligence on Base: resolve EVM addresses against 104,209 labeled entities (exchanges, bridges, contracts). Free anonymous tier, then x402. [Tier 2] |

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
