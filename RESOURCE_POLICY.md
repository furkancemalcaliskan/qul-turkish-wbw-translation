# Original QUL resources and release contract

The files under `resources/` are original downloads supplied by the user from Tarteel AI's Quranic Universal Library (QUL). They are immutable reference material. Read them only. Do not edit, reformat, minify, normalize, replace, migrate, or update them. Never open their SQLite databases in writable mode. Release artifacts must be separate files outside `resources/`.

The initial SHA-256 hashes and byte sizes of all six files are recorded in [reports/resource-integrity.json](reports/resource-integrity.json). Run `python scripts/audit_resources.py` before and after work involving these sources. A mismatch must fail verification; do not reset the baseline to make a mismatch pass. `--initialize` can create a missing manifest but refuses to reset an existing one. Source inventory additions require explicit review rather than silently replacing the existing inventory.

The root `.gitattributes` file disables Git text normalization for `resources/**` so repository storage and Windows checkouts preserve these original bytes. The working translation JSON files explicitly use LF line endings. Before committing source files, verify that the staged Git blobs also match the resource SHA-256 manifest; a working-tree-only hash check is not sufficient to verify repository storage.

## Source roles

| Source | Records | Role |
| --- | ---: | --- |
| `resources/english/english-wbw-translation.json` and `.db` | 83,665 each | Original English translation reference; the root English JSON has identical loaded key/value pairs and different formatting bytes. |
| `resources/turkish/turkish-wbw-translation.json` and `.db` | 70,539 each | Original Turkish baseline; the JSON has identical loaded pairs to the initial Git commit. Preserve these original errors and gaps as historical evidence. |
| `resources/arabic/qpc-hafs-word-by-word.json` and `.db` | 83,668 each | Original Arabic words, joined to translations by `surah:ayah:word`. Consult these when evaluating uncertain Turkish meanings and grammatical roles. |

The Arabic source is not a replacement translation. Read the original word and its neighboring Arabic context, then assess the proposed Turkish wording, source grammar, pronouns, tense, negation, and case relationships. English is a reference, not sufficient evidence for resolving every ambiguity. Record the actual Arabic locations consulted and distinguish spelling-only changes from interpretive changes. Preserve the agreed contextual-suffix notation and explanations in English documentation.

Arabic JSON values are records containing `id`, `surah`, `ayah`, `word`, `location`, and `text`; the numeric components in JSON are strings. Its SQLite table is `words (id INTEGER, location TEXT, surah INTEGER, ayah INTEGER, word INTEGER, text TEXT)`. Use `location` to join datasets, not Arabic `id` or row order. Keep the original Arabic text, including its marks, unchanged.

`python scripts/read_arabic_context.py 2:5:4 --radius 1` prints nearby original Arabic, source English, and the current root Turkish translation. Pass `2:5` to read a whole ayah. The helper checks source hashes and writes no files. Missing translation locations are displayed explicitly instead of silently shifting positions.

## Known location differences

Every English reference location exists in the Arabic source. The Arabic source additionally contains `2:181:4`, `8:6:5`, and `13:37:9`, each with `مَا`. At each preceding location, the English reference combines `بَعۡدَ` and this following word in the gloss `after what`. Both original translation and script datasets remain unchanged. Inspect both Arabic positions together in these cases; do not renumber later words or infer that the Turkish file needs a new key solely from the three-record count difference. The exact neighboring records are in [reports/resource-audit.json](reports/resource-audit.json).

## Final release contract

The user has specified the eventual release layout. It is deferred until linguistic work and final verification are finished:

1. Keep all original files under `resources/` byte-for-byte unchanged.
2. Keep the updated Turkish translation at root as `turkish-wbw-translation.json`, minified for release. Minification must preserve all reviewed key/value pairs, including the retained ayah-number entries. Preserve the flat location-to-string object; do not add metadata or Arabic records to it.
3. Copy the original Turkish SQLite database to root as `turkish-wbw-translation.db`, then update only that root copy from the reviewed Turkish JSON. The original database under `resources/turkish/` must remain unchanged.
4. Preserve QUL's `word_translation` table and columns: `surah_number INTEGER`, `ayah_number INTEGER`, `word_number TEXT`, and `text TEXT`. Word positions start at 1. Keep the existing location identifiers, including source gaps; do not renumber them. Ensure one row per translation key, string word numbers, no duplicate location triples, and exact JSON/SQLite value agreement after updating and adding missing rows.
5. Remove the root `english-wbw-translation.json` at the final stage, after active tools and checks have been adapted to read the immutable English source in `resources/`. Retain both original English resource files. Do not remove the working English reference prematurely while existing historical scripts still use it.
6. Verify JSON/SQLite integrity, unchanged resource hashes, exact translation agreement, and the intended final file layout before the final release commit. The current Turkish reference key set has 83,665 entries; changing that contract requires a separately documented decision.

This preserves the [QUL word-by-word translation format](https://qul.tarteel.ai/resources/translation/99/docs): individual word meanings addressed by location, supplied as a flat JSON object and an equivalent SQLite translation table. Arabic remains a separate reference joined by location. No release deletion, minification, database update, or commit was performed when this policy was recorded.
