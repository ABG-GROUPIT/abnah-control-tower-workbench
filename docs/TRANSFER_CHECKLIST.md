# Transfer Checklist

## Repository

- [ ] No screenshots or other image files are present.
- [ ] No credentials, tokens, cookies, full rows, arbitrary report values, or
  private exports are present. Any Control Tower excerpts are compiler-generated,
  issue-only, non-sensitive, and limited to one per finding type.
- [ ] P2/P4 source blueprints are under the correct page/section.
- [ ] Generated files were rebuilt rather than edited manually.
- [ ] `schema-pack/manifest.json` matches the generated contracts.
- [ ] `npm run data:validate` passes.
- [ ] `npm run typecheck` passes.
- [ ] `npm run lint` passes.
- [ ] `npm test` passes.

## Hosted Working State

- [ ] All intended drafts are saved.
- [ ] In-review reports have an assigned reviewer outside the tool if needed.
- [ ] Published mode shows only approved revisions.
- [ ] A current authenticated workspace backup was exported.
- [ ] Backup JSON is stored in approved secure storage.
- [ ] D1 project/binding ownership and deployment credentials are transferred separately.

## Knowledge Handoff

- [ ] New developer has read `README.md` and `docs/ARCHITECTURE.md`.
- [ ] New AI agent starts with `AGENT_HANDOFF.md` and the manifest.
- [ ] Structural reviewers understand `docs/STRUCTURAL_SCHEMA_METHOD.md`.
- [ ] Status meanings and unavailable reports are explained.
- [ ] Public API candidates are clearly separated from ABNAH UAT verification.
- [ ] Inventory/consumption and vendor/procurement priorities are stated.
- [ ] KPI and lineage contracts remain empty until approval.

## Clean Copy

Transfer source code and schema pack. Exclude machine-specific build/runtime folders such as `node_modules/`, `dist/`, `build/`, and `.wrangler/`. Run `npm install` and regenerate contracts in the receiving environment.

## Acceptance

The receiving developer should be able to select any report by stable ID, understand its current schema state, modify an irregular blank table without code changes, trace revision status, distinguish documented APIs from tested APIs, and explain why no KPI mapping has been invented.
