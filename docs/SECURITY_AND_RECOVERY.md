# Security and Recovery

## Data Classification

Allowed:

- report and field names;
- blank structural relationships;
- public API metadata;
- test status and non-secret error notes;
- approved model and lineage metadata.

Prohibited:

- screenshots or image files;
- screenshot/local evidence paths in new blueprints;
- full report rows, arbitrary values, or customer/vendor records;
- audit excerpts not generated under the issue-only, non-sensitive evidence
  policy;
- cookies, access tokens, API keys, passwords, or signed URLs;
- secrets copied into notes or test results.

## Hosted Controls

- GitHub Pages contains only the repository-approved, screenshot-free bundle.
- Atlas edits remain browser-local and are not silently uploaded.
- The executive portal is locked behind Zoho OAuth and allowed-workspace
  verification in Supabase.
- Supabase RLS blocks direct browser access to portal state tables.
- All Zoho and Supabase secrets remain server-side.
- Published mode is a UI read-only surface; do not treat it as a confidentiality
  boundary for content committed to GitHub.

## Recovery Layers

1. Version-controlled source blueprints reconstruct the baseline.
2. Browser-local state recovers in-progress work on the same profile.
3. JSON backup exports the current workspace for controlled transfer.
4. Git history recovers approved source and prior published baselines.
5. Supabase recovers only portal sessions and the URL-only handoff.

## Backup Procedure

1. Open the GitHub Pages workspace.
2. Select `Backup`.
3. Verify the JSON has the `documents` collection.
4. Store it in ABNAH's approved secure storage.
5. Do not commit the backup if internal notes make it unsuitable for source control.

## Restore Limitation

Automated import is intentionally not exposed in the UI because a bulk write can
overwrite reviewed state. Source blueprints remain the primary rebuild path and
backup JSON is reconciliation material.

## Incident Rule

If prohibited data is pasted into a note or test result, stop publication,
remove it from browser state and source, rotate any exposed secret, and purge it
from Git history according to company procedure. If it reached Supabase portal
configuration, remove it and rotate the affected backend secret.
