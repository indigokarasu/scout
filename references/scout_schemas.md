# Scout Schemas

## ResearchRequest

```json
{
  "request_id": "string",
  "as_of": "string — ISO 8601",
  "subject": {
    "type": "string — person|company|org",
    "name": "string",
    "aliases": ["string"],
    "known_locations": ["string"],
    "known_handles": ["string"],
    "known_emails": ["string"],
    "known_phones": ["string"]
  },
  "goal": "string — what the research should determine",
  "constraints": {
    "time_budget_minutes": "number|null",
    "minimize_pii": "boolean — default true"
  }
}
```

## Finding

```json
{
  "finding_id": "string",
  "claim": "string — the factual claim",
  "confidence": "string — high|med|low",
  "source_refs": [
    {
      "url": "string",
      "retrieved_at": "string — ISO 8601",
      "quote": "string — supporting excerpt"
    }
  ]
}
```

## PermissionGrant

```json
{
  "grant_id": "string",
  "timestamp": "string — ISO 8601",
  "tier": "number — 2 or 3",
  "reason": "string",
  "granted_by": "string — user identifier",
  "scope": "string — this_request|session|ongoing"
}
```

## BriefRecord

```json
{
  "brief_id": "string",
  "request_id": "string",
  "rendered_at": "string — ISO 8601",
  "format": "string — markdown|pdf",
  "sections": ["string — section names included"],
  "finding_count": "number",
  "source_count": "number",
  "confidence_summary": "string"
}
```

## DecisionRecord

Extends shared DecisionRecord. Scout-specific types: tier_escalation, identity_resolution, finding_inclusion, finding_exclusion, pii_suppression, tool_selection, mcp_discovery.

## MCPDiscoveryRecord

```json
{
  "discovery_id": "string",
  "timestamp": "string — ISO 8601",
  "registry": "string — e.g. nothumansearch.ai",
  "query": "string",
  "servers_found": "number",
  "servers_connected": "number",
  "servers_used": [
    {
      "name": "string",
      "endpoint": "string",
      "capabilities": ["string"],
      "auth_type": "string — none|api_key|oauth",
      "person_osint_relevance": "number — 0-1"
    }
  ],
  "cache_hit": "boolean"
}
```

## PersonToolRecord

```json
{
  "tool_name": "string — e.g. theHarvester, maigret, holehe, h8mail, ghunt, phoneinfoga, emailrep",
  "invoked_at": "string — ISO 8601",
  "input_type": "string — handle|email|phone|name|domain",
  "input_value": "string",
  "status": "string — success|error|timeout|not_installed",
  "findings_count": "number",
  "error": "string|null"
}
```
