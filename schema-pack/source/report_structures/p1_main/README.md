# P1 Structural Schema Ledger

This folder is the portable, screenshot-free source of truth for P1 Enterprise report structures. Local screenshots were used only as evidence during reconstruction and are not stored, referenced, or shipped here.

## Completion Snapshot

| Section | Active | Captured | Active unavailable | Archived placeholders |
| --- | ---: | ---: | ---: | ---: |
| Sales Analysis | 23 | 23 | 0 | 0 |
| Settlements | 6 | 6 | 0 | 0 |
| Discounts & Offers | 11 | 10 | 1 | 1 |
| Tax Analysis | 5 | 5 | 0 | 0 |
| Performance | 15 | 15 | 0 | 2 |
| Misc | 25 | 17 | 8 | 2 |
| **Total** | **85** | **76** | **9** | **5** |

Including archived placeholders, P1 contains 90 catalogue entries: 76 captured and 14 unavailable. There are no `partial` or `pending` P1 reports.

## What Is Encoded

- One JSON blueprint per usable report output.
- Exact visible header order and table count.
- Merged parent headers, row groups, context blocks, and separate tables where present.
- Generic repeating groups for dynamic dates, categories, sources, sections, meal periods, order types, and similar runtime members.
- Explicit status overrides with reasons when no result schema was available.

The first five sections contain 59 reviewed blueprints reconstructed from the complete local evidence set. Seven captured Misc blueprints have now been reviewed against the first Misc evidence batch; 10 captured Misc blueprints remain `needs_review` until separately checked.

### Misc Review Batch 1

Reviewed reports: Budget DSR Report, Cashier Report, Entp Day Report, Super Categories DSR, Whatsapp Message Report, Item Recipe Report, and Shift Report.

This batch is routed to P1 Misc because its report catalogue and enterprise report definitions belong to `p1_main/06_misc`. It must not be copied into the similarly named P2 report sections.

## Folder Rules

1. Do not add screenshots, screenshot filenames, local paths, or sample report values.
2. Edit an individual report JSON rather than generated workspace files.
3. Keep a dynamic member as a pattern unless its label is a stable report header.
4. Use `_status.json` only for unavailable or archived catalogue entries and include a reason.
5. Run `npm run data:workspace` and `npm run data:validate` after every source change.

The generated presentation contract lives at `schema-pack/generated/workspace.json`. The validation baseline prevents OCR-derived `partial` states from replacing these reviewed structures.
