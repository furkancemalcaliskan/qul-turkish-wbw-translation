# Missing-key inventory

Generated with `python scripts/audit_missing.py`. Reports use numeric surah–ayah–word order for review; translation file order is unchanged.

| Measure | Count |
| --- | ---: |
| English entries | 83,665 |
| Turkish entries | 82,025 |
| Missing Turkish keys | 1,640 |
| Missing ayah-number keys | 0 |
| Missing word or phrase keys | 1,640 |
| Ayahs with missing word or phrase keys | 1,265 |
| Turkish keys absent from English | 0 |

- `missing-summary.json`: source SHA-256 hashes, totals, and counts by surah.
- `ayah-number-additions.json`: audit trail of the 6,236 ayah-number entries copied exactly from the English reference, with source hashes before and after the operation.
- `missing-keys.csv`: every missing key, its English value, and nearest existing Turkish entries on either side within the same ayah. Neighbors are context only, not confirmed alignment matches. All rows start as `not_reviewed`.
- `missing-word-contexts.json`: complete English/Turkish entry context for each ayah with a missing word or phrase key. A null Turkish value means the key is absent, not that its meaning is necessarily untranslated.

An English value consisting entirely of a parenthesized integer is classified as an ayah number. All other missing entries are classified as words or phrases. This inventory is structural; the contextual-alignment artifacts below record the separate linguistic work.

The initial examples and seven initial findings in `alignment-review.md` describe the pre-alignment state. In the current file, `2:5:4` is `(Rableri)nden` and `2:5:5` is `Rableri(nden)`.

The inventory script does not modify either translation file. These reports were refreshed after contextual alignment. The inventory checks duplicate keys, key syntax, nonempty string values, count consistency, and preservation of both source files. It does not validate Quranic wording, grammar, or translation accuracy.

## Contextual-alignment artifacts

- `suffix-notation.md`: reader convention, grammatical scope, sources, exclusions, and limitations.
- `contextual-alignment-changes.json`: authoritative applied manifest, including source roles, exact boundaries, expression origins, reasons, and before/after values for every group.
- `contextual-alignment-changes.csv`: flattened entry-level change log for review.
- `contextual-alignment-validation.json`: resulting file hash and verification result.
- `alignment-pending.json`: all 1,640 remaining missing keys, with preliminary reasons and baseline neighboring context. These still require individual review; further fused expressions may remain.
- `suffix-candidates.json`, `verb-candidates.json`, and `*-alignment-plan.json`: intermediate baseline-based candidate/review outputs. A `proposed` status here does not mean applied. Only the authoritative change manifest defines the committed changes; overlapping proposals, exclusions, and deferred candidates are reconciled during assembly.

This step adds 5,250 keys and changes 5,288 existing values in 5,228 shared-expression groups. It preserves inherited lexical spelling, apart from recorded expression redistribution and display delimiters. Selective Arabic checks and local linguistic review do not constitute complete translation certification.
