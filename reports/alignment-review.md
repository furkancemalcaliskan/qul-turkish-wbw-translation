# Initial alignment review

Date: 2026-11-16. Scope: local English/Turkish entry comparison only. No Arabic morphology source has been checked in this step. These findings identify candidates for later correction; no translation values or keys have been changed.

The regenerated inventory contains 6,890 missing word or phrase keys across 3,624 ayahs, with no missing ayah-number keys. The complete inventory is in `missing-keys.csv`; full affected-ayah context is in `missing-word-contexts.json`.

## First candidates in numeric order

| Missing key | English value | Existing Turkish context | Initial observation |
| --- | --- | --- | --- |
| `2:4:9` | before you | `2:4:8`: `senden önce` (English: from) | The phrase appears to cover both reference entries; the ablative suffix represents the relation expressed by `from`. Review splitting/notation without duplicating the phrase. |
| `2:5:5` | their Lord | `2:5:4`: `Rablerinden` (English: from) | The noun and suffixes appear combined in the preceding entry. Review alignment and spelling separately. |
| `2:6:9` | you warn them | `2:6:8`: `uyarmasan da` (English: not) | The verb and negation appear combined. This requires phrase-level review, not just a preposition/suffix rule. |
| `2:6:11` | they believe | `2:6:10`: `inanmazlar` (English: not) | The Turkish verb combines lexical meaning, negation, and person marking. |
| `2:9:6` | they deceive | `2:9:5`: `aldatamazlar` (English: and not) | The verb is already present in the neighboring value. The conjunction and modal meaning also need review before deciding how to align the entries. |
| `2:10:2` | their hearts | `2:10:1`: `onların kablerinde` (English: In) | A phrase appears combined in the preceding entry. The literal existing text contains `kablerinde`, which is also a spelling-review candidate; it has not been corrected. |
| `2:11:7` | the earth | `2:11:6`: `yeryüzünde` (English: in) | The noun and locative suffix appear combined in the preceding entry. |

These seven candidates are not an exhaustive linguistic classification of the 6,890 gaps. A missing key alone cannot distinguish a combined translation, an omitted meaning, a shifted alignment, or another error. The rest remain unreviewed. No universal suffix notation has been selected or applied.
