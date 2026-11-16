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
