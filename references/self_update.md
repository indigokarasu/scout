# Scout Self-Update Procedure

`scout.update` pulls the latest skill package from GitHub. Runs silently — no output unless the version changed or an error occurred.

## Steps

1. Read `source:` from SKILL.md frontmatter → extract `{owner}/{repo}` from URL
2. Read local version from SKILL.md frontmatter `metadata.version`
3. Fetch remote version:

```bash
gh api "repos/{owner}/{repo}/contents/SKILL.md" --jq '.content' | base64 -d | grep 'version:' | head -1 | sed 's/.*"\(.*\)".*/\1/'
```

4. If remote version equals local version → stop silently
5. Download and install:

```bash
TMPDIR=$(mktemp -d)
gh api "repos/{owner}/{repo}/tarball/main" > "$TMPDIR/archive.tar.gz"
mkdir "$TMPDIR/extracted"
tar xzf "$TMPDIR/archive.tar.gz" -C "$TMPDIR/extracted" --strip-components=1
cp -R "$TMPDIR/extracted/"* ./
rm -rf "$TMPDIR"
```

6. On failure → retry once. If second attempt fails, report the error and stop.
7. Output exactly: `I updated Scout from version {old} to {new}`

## What is preserved

- All journals under `{agent_root}/commons/journals/ocas-scout/`
- All data under `{agent_root}/commons/data/ocas-scout/`
- Local `config.json` (not overwritten by upstream default)
