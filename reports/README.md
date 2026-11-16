# Missing-key inventory

Generated with `python scripts/audit_missing.py`. Reports use numeric surah–ayah–word order for review; translation file order is unchanged.

| Measure | Count |
| --- | ---: |
| English entries | 83,665 |
| Turkish entries | 83,665 |
| Missing Turkish keys | 0 |
| Missing ayah-number keys | 0 |
| Missing word or phrase keys | 0 |
| Ayahs with missing word or phrase keys | 0 |
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
- `alignment-pending.json`: the current missing-key list, now empty. Semantic review is tracked separately in `linguistic-review.json`.
- `suffix-candidates.json`, `verb-candidates.json`, and `*-alignment-plan.json`: intermediate baseline-based candidate/review outputs. A `proposed` status here does not mean applied. Only the authoritative change manifest defines the committed changes; overlapping proposals, exclusions, and deferred candidates are reconciled during assembly.

This step adds 5,250 keys and changes 5,288 existing values in 5,228 shared-expression groups. It preserves inherited lexical spelling, apart from recorded expression redistribution and display delimiters. Selective Arabic checks and local linguistic review do not constitute complete translation certification.

The continuation batch is recorded separately in `continued-alignment-changes.json`: 77 additional keys, 180 modified existing values, and 77 groups, based on commit `033d895`. Expanded groups supersede the earlier displays for their listed members; the original manifest remains the historical audit record. Run `python scripts/continue_alignment.py` to reproduce or verify this batch, followed by `python scripts/audit_missing.py` to regenerate the structural inventory. The earlier applier targets its historical baseline and should not be rerun over later work.

## Broad continuation

The broad batch added 1,021 keys and modified 1,013 existing values in 1,010 groups. This covered approximately 65% of the 1,563 gaps present at its start. Its baseline is `033d895` plus the recorded 77-key continuation, reconstructed without overwriting that earlier audit trail.

- `broad-alignment-changes.json`: historical broad-batch manifest, including exact before/after values, expression parts, zero-surface keys, lexical-revision flags, and reasons.
- `broad-alignment-changes.csv`: flattened review table for the same changes.
- `broad-alignment-validation.json`: independent structural verification and final hash.
- `broad-linguistic-review.json`: historical follow-up list from the broad batch, which ended with 542 missing keys. Consult `linguistic-review.json` for current values and combined review history.

There are 521 context-only views with no independently identified Turkish surface. These are explicitly recorded, not assumed to be certified zero equivalents. The notation guide explains how to distinguish them from overt suffixes. Thirty groups introduce lexical wording or repair a case/phrase; the rest preserve the inherited written material, apart from documented display normalization and redistribution. Structural completion is not a certification of the entire Turkish translation.

The broad batch was reproduced with `python scripts/complete_broad_alignment.py --apply`, then `python scripts/validate_broad_alignment.py` and `python scripts/audit_missing.py`. Its applier/validator targets that historical state and intentionally refuses later Turkish edits.

## Completion of the missing-key inventory

The latest batch adds all 542 remaining keys and modifies 616 existing values in 526 groups. Forty-four groups record lexical, spelling, compound, or phrase repairs explicitly. The Turkish and English files now have exactly the same 83,665 keys in the same reference order, with all 6,236 ayah-number entries preserved.

- `remaining-alignment-changes.json`: authoritative latest changes, source roles, expression origins, original values, resulting displays, reasons, zero-surface flags, and revision flags.
- `remaining-alignment-changes.csv`: flattened before/after table for every listed entry.
- `remaining-alignment-validation.json`: independent reconstruction and final structural checks.
- `linguistic-review.json`: combined semantic-review history for 831 present keys, including their current values and whether each currently has a context-only display. Of these, 693 currently have no independently identified overt surface; the remainder have lexical/phrase repair history or earlier zero-surface concerns. This is a focused follow-up list, not an exhaustive certification or error inventory of the entire translation.

There are 172 context-only views in the latest batch, including six newly added keys. The other new keys expose lexical or grammatical contributions. A complete key set does not prove that all source meanings, spelling, grammar, or alignment choices are correct. Context-only entries and interpretive repairs remain visibly queued for semantic review.

Reproduce or verify the current state with `python scripts/finish_remaining_alignment.py --apply`, `python scripts/validate_remaining_alignment.py`, and `python scripts/audit_missing.py`. The preparation script reconstructs its fixed baseline from the committed file plus the previous two manifests and refuses unexpected working-tree changes. Its explicit cases are in `remaining_special_cases.py` and `remaining_final_cases.py`. Earlier manifests and validation results remain historical; later groups supersede their listed source keys.
