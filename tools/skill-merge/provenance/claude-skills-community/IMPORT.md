# claude-skills-community Import

Source repository: https://github.com/alirezarezvani/claude-skills
Imported commit: 4a3c05b69e64f4925f7fc65c88890f614f79caf0
License: MIT, see LICENSE in this directory.
Import date: 2026-06-28

## Scope

Imported a first curated batch of generic, non-project-specific skills to reduce
coverage bias in the Portable Agent Workflow skill library.

The imported skills are stored under skills/<domain>/community/<skill>/.
community means third-party open-source material imported with provenance,
distinct from ours skills authored in this repository.

## Selection Rules

- Prefer generic business, operations, finance, product, project-management, and research-ops capabilities.
- Exclude router/index skills, one-off project wrappers, private/local context, and role-play-heavy executive personas.
- Keep source license and commit provenance.
- Normalize SKILL.md frontmatter to repository-compatible `name` and `description` fields.

## Imported Skills

| Domain | Skill | Source path |
|---|---|---|
| business-operations | capacity-planner | business-operations/skills/capacity-planner |
| business-operations | process-mapper | business-operations/skills/process-mapper |
| business-operations | knowledge-ops | business-operations/skills/knowledge-ops |
| business-operations | internal-comms | business-operations/skills/internal-comms |
| business-operations | procurement-optimizer | business-operations/skills/procurement-optimizer |
| business-operations | vendor-management | business-operations/skills/vendor-management |
| commercial-strategy | pricing-strategist | commercial/skills/pricing-strategist |
| commercial-strategy | deal-desk | commercial/skills/deal-desk |
| commercial-strategy | rfp-responder | commercial/skills/rfp-responder |
| commercial-strategy | partnerships-architect | commercial/skills/partnerships-architect |
| commercial-strategy | commercial-forecaster | commercial/skills/commercial-forecaster |
| commercial-strategy | channel-economics | commercial/skills/channel-economics |
| commercial-strategy | commercial-policy | commercial/skills/commercial-policy |
| finance | financial-analyst | finance/skills/financial-analyst |
| finance | saas-metrics-coach | finance/skills/saas-metrics-coach |
| product-management | product-discovery | product-team/skills/product-discovery |
| product-management | product-analytics | product-team/skills/product-analytics |
| product-management | experiment-designer | product-team/skills/experiment-designer |
| product-management | competitive-teardown | product-team/skills/competitive-teardown |
| product-management | roadmap-communicator | product-team/skills/roadmap-communicator |
| product-management | product-strategist | product-team/skills/product-strategist |
| product-management | code-to-prd | product-team/code-to-prd/skills/code-to-prd |
| product-management | research-summarizer | product-team/research-summarizer/skills/research-summarizer |
| project-management | meeting-analyzer | project-management/skills/meeting-analyzer |
| project-management | scrum-master | project-management/skills/scrum-master |
| project-management | senior-pm | project-management/skills/senior-pm |
| project-management | team-communications | project-management/skills/team-communications |
| research-ops | market-research | research-ops/skills/market-research |
| research-ops | product-research | research-ops/skills/product-research |
| research-ops | clinical-research | research-ops/skills/clinical-research |

## Second Import Batch · 2026-06-28

Imported commit: 4a3c05b69e64f4925f7fc65c88890f614f79caf0

Second batch goal: expand top-level coverage to at least 50 domains while keeping skills generic, licensed, and traceable.

Added 78 more MIT community skills across marketing, compliance, research, productivity, business growth, executive strategy, and markdown publishing domains.

Selection notes:

- Used OpenAI's Codex skills documentation and openai/skills repository as Codex skill ecosystem references; most curated OpenAI skills were already represented through the existing Codex source, and the openai/skills repository is now marked deprecated, so they were not duplicated.
- Continued using MIT `alirezarezvani/claude-skills` as the main import source for under-covered non-engineering domains.
- Excluded router/index skills, one-off command wrappers, private context, and most persona-heavy C-level advisor variants.
- Normalized imported SKILL.md frontmatter to `name` and `description`; license remains tracked by this provenance directory.

New domains added include SEO, content strategy, copywriting/editing, paid acquisition, email marketing, conversion optimization, growth experiments, brand strategy, app-store growth, launch management, marketing analytics, social media, video/webinar marketing, answer-engine optimization, AI governance compliance, privacy compliance, security compliance, medical regulatory, quality management, compliance programs, grant funding, patent intelligence, literature review, entity research, learning design, personal productivity, email productivity, handoff knowledge, customer success, revenue operations, sales enablement, executive strategy, change/org management, and markdown publishing.
