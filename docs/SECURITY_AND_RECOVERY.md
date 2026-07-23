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

- Keep the site private to authorized users.
- R2 is disabled.
- D1 is the only configured runtime data binding.
- Hosted write and backup requests require the authenticated user email header.
- Published mode is a UI read-only surface; private hosting still controls who can read it.
- All save payloads are sanitized and bounded.

## Recovery Layers

1. Version-controlled source blueprints reconstruct the baseline.
2. D1 current records recover the latest working documents.
3. Immutable D1 revisions recover prior states and publication history.
4. Authenticated JSON backup exports current documents and all revisions for transfer.

## Backup Procedure

1. Open the private workspace as an authenticated editor.
2. Select `Backup`.
3. Verify the JSON has `documents` and `revisions` collections.
4. Store it in ABNAH's approved secure storage.
5. Do not commit the backup if internal notes make it unsuitable for source control.

## Restore Limitation

Automated import is intentionally not exposed in the UI because a bulk write can overwrite reviewed state. Restore should be performed by a developer after validating IDs, versions, and target environment. Until that utility is added, source blueprints remain the primary rebuild path and backup JSON is reconciliation material.

## Incident Rule

If prohibited data is pasted into a note or test result, stop publication, remove it in a new revision, rotate any exposed secret, and purge the affected hosted record through an administrator. Revision history is immutable by normal UI design, so secret exposure requires administrative database cleanup.
