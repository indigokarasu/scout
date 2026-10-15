# Scout self-update procedure

`scout.update` pulls the latest package from the `source:` URL in `SKILL.md` frontmatter. It is scheduled daily at 00:00 (`0 0 * * *`) and preserves journals/data across updates.

- Runs silently; output only appears when the version changed or an error occurred.
- Refresh background-task registrations after a successful update if the package shape changed.
- For debugging failures: run `scripts/update.sh` manually and inspect the git fetch/pull output and any install step errors.