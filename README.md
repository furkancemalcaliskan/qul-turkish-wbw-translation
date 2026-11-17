# qul-turkish-wbw-translation

[English](README.md) · [Türkçe](README.tr.md)

Turkish Quran word-by-word translation

This independent project reviews, completes, and corrects the [Turkish word-by-word translation (#99)](https://qul.tarteel.ai/resources/translation/99/docs) distributed by [Tarteel AI’s Quranic Universal Library (QUL)](https://qul.tarteel.ai/). The intended destination is a contribution to QUL so developers can access reviewed, updated data. This repository provides transparency; it is not an approved or published QUL release.

**The initial flagged-record review is complete.** Initial release: [v1.0.0](https://github.com/furkancemalcaliskan/qul-turkish-wbw-translation/releases/tag/v1.0.0). QUL submission is pending. All **831 records** were assessed against Arabic and the English reference; none remains pending in that list. **487 records** were closed through reviews involving changes, and **344** through reasoned retention. These are not error counts: a decision may include adjacent words. This is not independent expert certification of every one of the 83,665 translations.

## Contribution policy

External contributions are currently closed: pull requests and translation proposals are not accepted. This repository is intended for public inspection of the process and release artifacts. The planned maintainer-led contribution to QUL is separate from accepting contributions here. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [v1.0.0 changelog](CHANGELOG.md).

## Sources and changes

The original English/Turkish JSON and SQLite files and QPC Hafs Arabic word resource under `resources/` were obtained from QUL. This credits QUL as provider without attributing all translation authorship or copyright ownership to Tarteel AI. All six originals remain untouched and are verified against the [SHA-256 manifest](reports/resource-integrity.json).

- Turkish was reordered/formatted against English without changing existing pairs during that stage.
- Missing ayah-number and word/phrase keys were completed, with contextual displays for Turkish suffixes and combined expressions.
- The spelling/grammar stage corrected **1,162 values**. After semantic review, notation cleanup and further spelling/grammar checks, **2,629 distinct values across 1,262 ayahs** differ from spelling/grammar commit `661144b`. These are not independent error counts; stage totals must not simply be added together.
- Uncertain meanings were assessed against original Arabic words and ayah context alongside English. Where multiple readings are possible, the chosen reading and its limits are recorded. Tools/AI assisted the work; no independent expert endorsement is claimed.

The subsequent follow-up removed square delimiters from 622 values. Relative to the previous completed review, this follow-up changes 1,522 distinct values in 940 ayahs, including both notation cleanup and spelling/grammar corrections.

## Notation

```json
{
  "2:5:4": "(Rableri)nden",
  "2:5:5": "Rableri(nden)"
}
```

In the example above, `(Rableri)nden` highlights the ablative contribution and `Rableri(nden)` the noun context. Both expose the same expression; do not concatenate the views. Outside parentheses is the selected contribution, inside is context. Current Turkish values contain no square brackets. Their old contents were initially preserved, then malformed joins and duplicate lexical explanations were reviewed individually. Round parentheses remain the shared-expression/context notation; ayah-number markers are unchanged. Allocation is functional rather than always morpheme-for-morpheme: Turkish verb valency and clause structure may determine the case or form. A fully parenthesized value is not automatically correct; an accepted zero surface needs its own recorded rationale.

## Transparency and output

Four reports hold the [summary](reports/README.md), [review state](reports/review-state.json), [validation results](reports/validation.json), and [source hashes](reports/resource-integrity.json). Current before/after changes, evidence, reasons, and pending records remain available. Earlier reports are in Git history; [PROCESS.md](PROCESS.md) identifies the relevant commits.

The root Turkish DB was updated from a copy of the original and matches all 83,665 reviewed JSON entries, preserving QUL's schema. The root Turkish JSON remains unchanged and pretty-printed. English is read directly from immutable `resources/english/`; its redundant root copy has been removed. Minified JSON and matching SQLite are built separately under `dist/`; all six original resources stay immutable. GitHub release assets are intended for download; their publication does not imply QUL acceptance. See the [resource/release policy](RESOURCE_POLICY.md) and [QUL contribution route](QUL_CONTRIBUTION.md).

## Licence information

The [resource #99 licence page](https://qul.tarteel.ai/resources/translation/99/licence) states that copyright information is unavailable. We record that uncertainty here. Attribution does not establish that the files are unlicensed or public domain; we do not assign our own licence to the downloaded originals.

## Download and data format

Download the minified JSON and SQLite from [release v1.0.0](https://github.com/furkancemalcaliskan/qul-turkish-wbw-translation/releases/tag/v1.0.0). The root JSON is the readable working copy; release JSON uses raw UTF-8 without formatting whitespace. Both contain the same location-to-string pairs. Do not use the old files under `resources/turkish/` as the corrected dataset; they are preserved original evidence.

SQLite table: `word_translation`.

| Column | Type |
| --- | --- |
| `surah_number` | `INTEGER` |
| `ayah_number` | `INTEGER` |
| `word_number` | `TEXT` |
| `text` | `TEXT` |

Locations are `surah:ayah:word`, starting at 1. Preserve the supplied identifiers; do not renumber them. Check `SHA256SUMS` after downloading. `release-manifest.json` records source/artifact hashes, build revision and dirty state; `RELEASE_NOTES.md` records release scope and limitations.

## Verify and build locally

Python 3.10+ and full Git history are required. The maintained tools use only the Python standard library. Run from the repository root:

```powershell
python scripts/audit_resources.py
python scripts/audit_missing.py
python scripts/semantic_review.py
python scripts/audit_turkish_spelling.py
python -m unittest discover -s tests -v
python scripts/build_release.py --version v1.0.0
```

The build writes minified JSON, equivalent SQLite, manifest, checksums and release notes under ignored `dist/`. It refuses a missing/stale root database. Only after an intentional reviewed JSON change, use `python scripts/build_release.py --update-root-db` to refresh that copy. Original resources are never writable inputs. Checks establish data integrity and recorded-change consistency, not independent linguistic certification.

## Repository maintenance

[CI](.github/workflows/release.yml) verifies branch/manual builds and creates a draft release for pushed `v*` tags. Release assets are published after successful verification. External pull requests do not trigger CI. Pull requests, issues, discussions and the wiki are disabled while outside contributions are closed.

All branches allow creation/updates only by the owner. Separate history rules block force pushes and branch deletion without a bypass. The maintained configurations are under [.github/rulesets/](.github/rulesets/); [CONTRIBUTING.md](CONTRIBUTING.md) states the contribution policy. Changes to these administrative settings are separate from QUL publication.
