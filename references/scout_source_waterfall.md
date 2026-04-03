# Scout Source Waterfall

## Intent

Research should exhaust free, low-friction sources before escalating. This reduces cost, respects rate limits, and ensures paid sources are used only when they add genuine value.

## Tier 1 — Public Sources (Automatic)

Sources: public web search, official websites, reputable news outlets, public filings (SEC, state registries), public social profiles (LinkedIn public view, Twitter/X, GitHub).

Behavior: runs automatically on every research request. No permission required.

Minimization: collect only what the goal requires. Do not harvest all available data.

### Parallel Search with Agent-Reach

Tier 1 now runs **agent-reach** in parallel with Tavily/DuckDuckGo web search:

- **Tavily**: General web search, news, official sites, documents
- **Agent-reach**: Platform-native search (Twitter/X, Reddit, LinkedIn, GitHub, Weibo, WeChat Articles, etc.)

Execution:
1. Query issued to Tavily (primary) AND agent-reach (platform search)
2. Results collected concurrently
3. Deduplication by URL and content hash
4. Merged into unified source pool

Benefits:
- Broader OSINT coverage across social platforms
- Platform-native content not indexed by general search
- No additional latency (parallel execution)

Fallback: If agent-reach fails or rate-limited, Tavily results are sufficient for Tier 1 completion.

## Tier 2 — Extended Sources (Config-Gated)

Sources: rate-limited APIs, business registries, extended public datasets, professional directories.

Behavior: runs only if `waterfall.enabled_tiers` includes 2 AND the Tier 1 results are insufficient for the goal.

Escalation criteria: Tier 1 produced fewer than 3 findings, or key identity questions remain unresolved.

## Tier 3 — Paid Sources (Permission-Gated)

Sources: paid OSINT providers, background check databases, premium data services.

Behavior: requires both config enablement AND explicit user permission grant recorded as a PermissionGrant.

Escalation criteria: Tier 1 and Tier 2 insufficient, and the research goal explicitly requires deeper investigation.

Hard stop: if no PermissionGrant exists, Tier 3 does not execute. The brief notes that further sources are available but not authorized.

## When to Stop

Stop escalating when:
- The research goal is satisfied
- Additional tiers are unlikely to add material value
- The time budget is exhausted
- The user has not granted permission for the next tier
