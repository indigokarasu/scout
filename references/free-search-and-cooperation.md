# Free Search Sources & Skill Cooperation

### Free search sources (SearXNG)

SearXNG is a free meta-search engine. To improve people-search coverage, enable these free engines in `/opt/searxng/settings.yml`:
- bing, google, brave, qwant, yahoo, naver, seznam

Avoid duckduckgo (CAPTCHA-blocked) and startpage (not available). Use the curated engine list in `weave_enrich.searxng_search` to query only these engines.

### Sift free extraction sources

The Sift phase (`fetch_page`) uses multiple free extraction fallbacks:
- Direct HTTP with rotating user agents
- Google cache (`webcache.googleusercontent.com`)
- Wayback Machine (`web.archive.org`)
- Jina Reader (`r.jina.ai`)

This improves content extraction from auth-walled or JS-heavy sites without paid APIs.


## Optional skill cooperation

Sherlock (handle expansion), Sift (web search), Look (reverse image), Weave (social graph, read-only), Chronicle (Signals), native-mcp/mcporter (MCP servers), RapidAPI (social enrichment — see below).

