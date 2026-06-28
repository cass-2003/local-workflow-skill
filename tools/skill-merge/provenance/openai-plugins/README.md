# OpenAI Plugins Import

Imported from the public OpenAI Codex plugins example repository.

- Source repository: https://github.com/openai/plugins.git
- Source commit: 3fdeeb4970a1fa176ccabf873ae64fd6053cb2b0
- Import date: 2026-06-28
- Import scope: selected skills with explicit MIT-compatible license metadata or plugin-level MIT license.
- Local source layer: codex

## License handling

The root openai/plugins checkout does not include a repository-wide LICENSE file. This import only includes skills from plugin folders or skill frontmatter with explicit MIT license statements:

- plugins/expo/README.md declares MIT.
- plugins/render/README.md declares MIT and points to plugin-level LICENSE.
- plugins/supabase/skills/supabase-postgres-best-practices/SKILL.md declares MIT.
- plugins/airtable/skills/airtable-filters/SKILL.md and irtable-overview/SKILL.md declare MIT.

The per-skill license frontmatter field was removed during normalization because this repository's skill validator only accepts 
ame and description in SKILL.md frontmatter. License provenance is retained here.
