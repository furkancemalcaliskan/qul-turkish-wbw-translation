# Review summary

The initial list of **831 flagged records has been reviewed** against the original Arabic and supplied English: **487 reviewed_with_changes**, **344 reviewed_retained**, **0 pending**. A changed review can concern the construction or adjacent words; these statuses are not counts of individually erroneous keys. Retained flags have explicit functional/idiomatic reasons, not automatic approval because they have a nonempty string.

Current Turkish has **83,665 reference keys**, no missing/extra keys and all **6,236 ayah markers**. All six original QUL resources are unchanged; the redundant root English copy was removed after the user authorized it. Relative to spelling/grammar commit `661144b`, semantic review changes **2,629 distinct values in 1,262 ayahs**. The original source Turkish remains the untouched 70,539-key baseline.

## Four maintained reports

| File | Purpose |
| --- | --- |
| [README.md](README.md) | This human-readable summary. |
| [resource-integrity.json](resource-integrity.json) | Fixed paths, sizes and SHA-256 hashes of the six originals. |
| [review-state.json](review-state.json) | All queue history and nineteen ordered semantic batches, with complete source contexts, before/after values, reasons, source-role allocations, selected readings and reassessments. |
| [validation.json](validation.json) | Latest resource/structure/full-ledger checks; historical first-batch verification and consolidation snapshots are explicitly identified. |

Earlier stage-specific reports remain in Git. New work updates these four files rather than creating one report per batch. Full technical checks and the exact translation hash are in validation.json under semantic_review.

## What the review covered

- Missing or displaced relative, negation, tense, case and pronoun contributions; Turkish suffixes and combined expressions were read as whole constructions.
- Valid functional zeros: min qabl can be natural daha önce without a separate source ending, and negative-exception restriction can be Turkish only without a second negative.
- Lexical errors found in the read clauses, including reversed sky/earth locations, incorrect recipient/object roles, sidr confused with cedar, favor confused with gratitude, and orphan terminology.
- A second reading corrected draft conditional harmony, noun-compound morphology and duplicate determiners. Those earlier drafts remain visible in the ordered ledger rather than being silently replaced.
- Identified follow-ups in 2:23, 2:36, 5:46, 5:48, 9:74, 17:36, 17:69, 33:19 and the seven explicitly selected Throne clauses were revisited. The technical Turkish istiva term is retained without an expanded physical-sitting or encirclement claim.

## Interpretive limits

This is an AI-assisted review of the flagged constructions and explicitly recorded adjacent findings, **not a word-by-word certification of the entire Quran by an independent scholar**. Complete ayah contexts are evidence; storing them does not mean every unmodified word was exhaustively adjudicated. Initial queue completion does not prove that an unflagged error cannot remain.

Chosen readings and alternatives are recorded where relevant: pronouns in love/food expressions, negated-nearness constructions, the syntax of 4:135, nearest/lower land, contextual partitives, raising/sending, and technical istiva terminology. A retained reading is not a claim that every traditional interpretation is identical. English is a reference, not an overriding authority where the Arabic or Turkish frame differs.

Outside parentheses is the selected contribution; inside is shared context. Do not concatenate complementary views. Current Turkish values prohibit square brackets. Historical before/after records retain them for exact replay; they do not prescribe the current notation. This is functional allocation, not always literal morpheme identity: scope, Turkish valency, rhetorical questions and negative-exception transformations are explained in the ledger.

Published comparisons include [2:236](https://quran.com/al-baqarah/236), [34:16](https://quran.com/saba/16), [41:24](https://quran.com/fussilat/24), [45:11](https://quran.com/al-jathiyah/11), [10:3](https://quran.com/yunus/3) and [93:2](https://quran.com/ad-duhaa/2). The original local Arabic/English remains the primary location evidence; failed or wrong-verse web retrievals are not presented as verification.

See the bilingual [README](../README.md) and English [PROCESS.md](../PROCESS.md) for scope, history and commands. The root SQLite copy and separate local release artifacts are prepared and verified; hosted CI, release publication and QUL submission have not occurred. The working Turkish JSON remains unchanged; English is read from its immutable resource. Packaging results are recorded under release_packaging in validation.json.

## Subsequent notation and spelling review

Batches 012-019 implement the user-requested prohibition of square delimiters and stricter spelling/grammar follow-up. The first operation removes only delimiters from 622 values; later individually recorded corrections repair malformed joins and duplicate explanations. In total this follow-up changes 1,522 distinct values across 940 ayahs relative to batch 011. See PROCESS.md for the subject-agreement, possessive-ending, question-spacing, numeral and verbal/food-noun distinctions. The original 831-record semantic queue statistics describe that historical list, not a count of these later orthographic corrections.

Run python scripts/audit_turkish_spelling.py for the bounded whole-file orthographic scan. Its results are stored in validation.json; no additional report files are created. Current notation permits round parentheses for shared expressions/context, with the reference ayah markers preserved. Historical ledger entries retain their original delimiters for reproducibility.
