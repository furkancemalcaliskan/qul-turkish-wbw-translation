# Missing-key inventory

Generated with `python scripts/audit_missing.py`. Reports use numeric surah–ayah–word order for review; translation file order is unchanged.

| Measure | Count |
| --- | ---: |
| English entries | 83,665 |
| Turkish entries | 76,775 |
| Missing Turkish keys | 6,890 |
| Missing ayah-number keys | 0 |
| Missing word or phrase keys | 6,890 |
| Ayahs with missing word or phrase keys | 3,624 |
| Turkish keys absent from English | 0 |

- `missing-summary.json`: source SHA-256 hashes, totals, and counts by surah.
- `ayah-number-additions.json`: audit trail of the 6,236 ayah-number entries copied exactly from the English reference, with source hashes before and after the operation.
- `missing-keys.csv`: every missing key, its English value, and nearest existing Turkish entries on either side within the same ayah. Neighbors are context only, not confirmed alignment matches. All rows start as `not_reviewed`.
- `missing-word-contexts.json`: complete English/Turkish entry context for each ayah with a missing word or phrase key. A null Turkish value means the key is absent, not that its meaning is necessarily untranslated.

An English value consisting entirely of a parenthesized integer is classified as an ayah number. All other missing entries are classified as words or phrases. No linguistic classification or translation correction has been performed.

For example, `2:4:9` (English: `before you`) is absent, but the existing Turkish value at `2:4:8` is `senden önce`. Likewise, `2:5:5` (English: `their Lord`) is absent while `2:5:4` contains `Rablerinden`. These are candidates for alignment review, not instructions to duplicate text or confirmed corrections.

The inventory script does not modify either translation file. These reports were refreshed after adding the ayah-number entries. The inventory checks duplicate keys, key syntax, nonempty string values, count consistency, and preservation of both source files. It does not validate Quranic wording, grammar, or translation accuracy.
