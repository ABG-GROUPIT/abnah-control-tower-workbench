# Workspace Operations

## Editing

Discovery opens a single report workspace. Tabs separate data points, table structure, API tests, notes, settings, and history. Changes are local in the browser until `Save draft` succeeds.

Any edit to an in-review or published document returns the working copy to draft.

## Review and Publication

1. Save the draft.
2. Submit it for review.
3. Review exact labels, structure, availability, and notes.
4. Publish or return to draft.

Only the current in-review revision can transition to published. Published mode is read-only.

## Conflicts

GitHub Pages does not merge edits across browsers. Export a backup before
handoff, nominate one source editor for each schema batch, and reconcile
approved changes into source control. Git conflicts are resolved during review,
not inside the browser workspace.

## Archive

Archive is a soft state. Archived reports are hidden from the default navigator but remain searchable when `Show archived` is enabled. Use it for unknown duplicates and obsolete custom records; do not erase discovery history.

## Backup

The top-bar `Backup` action returns:

- all current browser documents;
- current workflow status, version, and timestamp metadata.

Backups do not include screenshots, credentials, or external local files.

There is no one-click restore UI. Keep source blueprints current, and treat the
backup as recovery/transfer material for controlled reconciliation.

## Local Development

Local development and GitHub Pages both use browser-local drafts. The secured
executive portal has no development bypass; it requires the Supabase/Zoho flow.

## Operational Limits

- 2 MB request body per report save.
- 50 tables per report.
- 500 rows and 500 columns per table.
- 100,000 cells per report.
- 100 revision metadata records returned in the History tab.

Split a report into meaningful tables rather than increasing limits without review.
