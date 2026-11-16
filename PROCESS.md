# Process log

This file records changes and verification results for the Turkish word-by-word Quran translation. The English file is the reference and must remain unchanged. Baseline: `4503cdc` (`initial commit`). All documentation and code comments must be written in English.

## 2026-11-16 — 01: Reorder Turkish entries to match the reference

Request: align the Turkish file with the English reference order and formatting without changing any Turkish key/value pairs.

The reference is not in strictly numeric surah–ayah–word order. This operation follows the actual key order in the English file, skipping keys absent from the Turkish file. No entries were added.

Implementation: `python scripts/order_turkish.py`. The script preserves the original text of each Turkish entry line, changing only line placement and the required separator commas. Formatting remains consistent with the reference: UTF-8, two-space indentation, LF line endings, and one final newline.

Verification:

- All 70,539 Turkish key/value pairs are identical before and after the operation.
- Neither file contains duplicate keys.
- Every Turkish key exists in the reference.
- Turkish key order exactly matches the reference order filtered to existing Turkish keys.
- The English file is byte-for-byte unchanged.
- No spelling, grammar, meaning, or word alignment changes were made.
- Comparison against the baseline commit independently confirmed unchanged English bytes and Turkish key/value pairs.

SHA-256 records:

| File / stage | SHA-256 |
| --- | --- |
| English, before and after | `917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2` |
| Turkish, before | `53e03a9c5c3d1b130b9d7d7e7c4810ae9ce57d219465febcbc04ab571eb15d26` |
| Turkish, after | `fd57be551999620747bc0319287018c54b3330f54ccd612fb023546040b914f2` |

## Agreed principle for subsequent content review

Missing keys must not be filled by duplicating an existing translation. When Turkish suffixes allow multiple source words to be expressed as one Turkish word, that relationship must be reviewed and made visible to the reader. The user's example is `(sen)den (once)`. This example has not been applied to the translation or finalized as a universal notation standard. Notation will be applied after reviewing word alignment and ayah context; decisions and their rationale will be recorded here.

The initial inventory found 13,126 Turkish keys missing relative to the reference: 6,236 ayah-number entries and 6,890 other entries. These counts do not establish the number of missing translations: some meanings are already combined in a neighboring Turkish entry.

## 2026-11-16 — 02: Inventory missing Turkish keys

Request: compare the Turkish file with the English reference and identify missing entries.

Implementation: `python scripts/audit_missing.py`. Reports are written to `reports/`; neither translation file is modified. The inventory is sorted numerically for review, independently of the reference file's physical order.

Results: 13,126 missing keys, consisting of 6,236 ayah-number entries and 6,890 word or phrase entries. Word or phrase gaps affect 3,624 ayahs. There are no extra Turkish keys, duplicate keys, malformed keys, or empty/non-string values in either source.

Artifacts: `reports/missing-summary.json` records source hashes and counts by surah; `reports/missing-keys.csv` lists every missing key with neighboring Turkish context; `reports/missing-word-contexts.json` provides complete entry context for affected ayahs. `reports/README.md` explains interpretation and limitations.

Verification: missing and shared keys account for all reference entries; category totals match the missing-key total; both source files remain byte-for-byte unchanged. Source hashes match those recorded in step 01 after reordering.

All missing entries remain linguistically unreviewed. No suffix notation, translations, or ayah-number values were inserted. The reports identify structural gaps, not confirmed omissions of meaning.

## 2026-11-16 — 03: Add missing ayah-number entries

Request: copy missing parenthesized ayah numbers such as `(1)` and `(2)` exactly from the English reference. Suffix-related word alignment will be reviewed in a subsequent step.

Implementation: `python scripts/add_ayah_numbers.py`. Only absent keys whose English values match a parenthesized integer are eligible. Each added value is also checked against the ayah component of its key. Existing Turkish entry text is preserved, and the output follows the English reference key order. The English file is unchanged.

Result: 6,236 entries added, increasing the Turkish total from 70,539 to 76,775. All 70,539 existing key/value pairs are unchanged. Every added key/value pair exactly matches the reference. No missing ayah-number keys remain. The remaining 6,890 missing keys are word or phrase entries across 3,624 ayahs; no linguistic edits were made.

Audit trail: `reports/ayah-number-additions.json` lists every added pair and records SHA-256 hashes. Turkish SHA-256 changed from `fd57be551999620747bc0319287018c54b3330f54ccd612fb023546040b914f2` to `d8e4a9d4444b4bd1fbd508c317ccb688147f375da0bd4987b316e135b6b7a4e3`. English SHA-256 remains `917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2`.

The missing-key reports were regenerated with `python scripts/audit_missing.py` and their README updated to reflect the current state. An independent comparison against commit `36edf35` verifies the exact added-key set, preservation of all existing Turkish pairs, unchanged English bytes, reference order, and absence of remaining ayah-number gaps.
