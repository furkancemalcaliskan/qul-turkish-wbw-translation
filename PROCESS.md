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

## 2026-11-16 — 04: Recheck remaining gaps and inspect initial alignment candidates

Regenerated the inventory after the ayah-number commit (`cf1e80d`). Results remain 6,890 missing word or phrase keys across 3,624 ayahs, with zero missing ayah-number keys. Both translation files remain byte-for-byte unchanged.

Inspected the first seven missing keys in numeric order against their complete local English/Turkish ayah context. Recorded candidate combined phrases, suffixes, and negative verb constructions in `reports/alignment-review.md`, including a separate spelling-review observation. These are preliminary alignment findings from the supplied files, not verified Arabic morphological analysis or an exhaustive classification. No translations were inserted or corrected.

## 2026-11-16 — 05: Contextual alignment of fused Turkish expressions

The user specified `(Rableri)nden` for `from` and `Rableri(nden)` for `their Lord`, and explicitly included negative verbs and subordinate clauses in this same operation and commit. The earlier tentative notation is superseded by `reports/suffix-notation.md`, which explains the convention for non-Turkish readers, why isolated endings are insufficient, the treatment of existing notes, and the limits of the review.

Baseline: `cf1e80d`, with 6,890 missing word/phrase keys. Reviewed local patterns cover noun cases, negative constructions, relative/nominal clauses, infinitives, temporal expressions, and selected multi-entry expressions. Existing explanatory parentheses become square brackets only in touched expressions. The written lexical material is preserved; the manifest records expression origins, including the corrected source-range assignment of two inherited expressions in `4:23`. English is untouched. Selected Arabic positional checks and Turkish grammar sources are linked in the notation document; no exhaustive Arabic morphological verification is claimed.

Result: 5,250 missing keys added, 5,288 existing values modified, and 5,228 contextual groups recorded. Turkish now has 82,025 entries. There remain 1,640 missing word/phrase keys across 1,265 ayahs. These are individually pending, and may include further suffix cases as well as zero equivalents, inherited wording problems, or absent meanings. This operation does not declare every suffix-related gap resolved. No ayah-number entries changed.

Reproduction from the fixed baseline data: run `python scripts/build_suffix_plan.py` (also prepares suffix candidates), `python scripts/prepare_verb_review.py`, `python scripts/prepare_clause_review.py`, `python scripts/prepare_case_supplement.py`, and `python scripts/prepare_complex_review.py`; then run `python scripts/assemble_contextual_alignment.py`, `python scripts/apply_contextual_alignment.py`, and `python scripts/audit_missing.py`. Intermediate candidate files are not the applied change list. The assembler reconciles overlap, records exclusions, and produces the authoritative `reports/contextual-alignment-changes.json` and CSV counterpart. The applier refuses unexpected working-tree content and can verify the already-applied result without changing its meaning.

Verification checks the full manifest against baseline values and expression origins, reconstructs each contextual view from its recorded roles, preserves every untouched pair, matches the exact requested example, excludes known ambiguous cases, preserves every ayah number, follows the actual reference key order, and verifies unchanged English bytes. The inventory independently checks duplicate keys, syntax, nonempty strings, and exact missing-key counts. `git diff --check` checks whitespace. These structural checks do not prove every linguistic judgment correct; the before/after log enables review and correction.

English SHA-256 remains `917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2`. Turkish changes from `d8e4a9d4444b4bd1fbd508c317ccb688147f375da0bd4987b316e135b6b7a4e3` to `94e871f2b1de1aae8c836ac5db4aa5a3f5c4a8c1699463bd00ba46ef93ac2770`. Exact results are also stored in `reports/contextual-alignment-validation.json`.
