# Original QUL resources and release contract

The files under `resources/` are original downloads supplied by the user from Tarteel AI's Quranic Universal Library (QUL). They are immutable reference material. Read them only. Do not edit, reformat, minify, normalize, replace, migrate, or update them. Never open their SQLite databases in writable mode. Release artifacts must be separate files outside `resources/`.

The initial SHA-256 hashes and byte sizes of all six files are recorded in [reports/resource-integrity.json](reports/resource-integrity.json). Run `python scripts/audit_resources.py` before and after work involving these sources. A mismatch must fail verification; do not reset the baseline to make a mismatch pass. `--initialize` can create a missing manifest but refuses to reset an existing one. Source inventory additions require explicit review rather than silently replacing the existing inventory.

The root `.gitattributes` file disables Git text normalization for `resources/**` so repository storage and Windows checkouts preserve these original bytes. The working translation JSON files explicitly use LF line endings. Before committing source files, verify that the staged Git blobs also match the resource SHA-256 manifest; a working-tree-only hash check is not sufficient to verify repository storage.

## Source roles

| Source | Records | Role |
| --- | ---: | --- |
| `resources/english/english-wbw-translation.json` and `.db` | 83,665 each | Original English translation reference; the removed root English JSON had identical loaded key/value pairs and different formatting bytes; tools now read this immutable resource directly. |
| `resources/turkish/turkish-wbw-translation.json` and `.db` | 70,539 each | Original Turkish baseline; the JSON has identical loaded pairs to the initial Git commit. Preserve these original errors and gaps as historical evidence. |
| `resources/arabic/qpc-hafs-word-by-word.json` and `.db` | 83,668 each | Original Arabic words, joined to translations by `surah:ayah:word`. Consult these when evaluating uncertain Turkish meanings and grammatical roles. |

The Arabic source is not a replacement translation. Read the original word and its neighboring Arabic context, then assess the proposed Turkish wording, source grammar, pronouns, tense, negation, and case relationships. English is a reference, not sufficient evidence for resolving every ambiguity. Record the actual Arabic locations consulted and distinguish spelling-only changes from interpretive changes. Preserve the agreed contextual-suffix notation and explanations in English documentation.

Arabic JSON values are records containing `id`, `surah`, `ayah`, `word`, `location`, and `text`; the numeric components in JSON are strings. Its SQLite table is `words (id INTEGER, location TEXT, surah INTEGER, ayah INTEGER, word INTEGER, text TEXT)`. Use `location` to join datasets, not Arabic `id` or row order. Keep the original Arabic text, including its marks, unchanged.

`python scripts/read_arabic_context.py 2:5:4 --radius 1` prints nearby original Arabic, source English, and the current root Turkish translation. Pass `2:5` to read a whole ayah. The helper checks source hashes and writes no files. Missing translation locations are displayed explicitly instead of silently shifting positions. Current audit results are consolidated under `resources` in `reports/validation.json`.

## Known location differences

Every English reference location exists in the Arabic source. The Arabic source additionally contains `2:181:4`, `8:6:5`, and `13:37:9`, each with `مَا`. At each preceding location, the English reference combines `بَعۡدَ` and this following word in the gloss `after what`. Both original translation and script datasets remain unchanged. Inspect both Arabic positions together in these cases; do not renumber later words or infer that the Turkish file needs a new key solely from the three-record count difference. The exact neighboring records are under `resources.arabic_only_locations` in [reports/validation.json](reports/validation.json).

## Final release contract

Keep the root Turkish working JSON pretty and build separate release artifacts. The user has now authorized removal of the redundant root English JSON; tools must read the immutable English resource directly:

1. Keep all original files under `resources/` byte-for-byte unchanged.
2. Keep the updated root `turkish-wbw-translation.json` pretty-printed for review. Produce `dist/turkish-wbw-translation.json` as raw UTF-8 with compact separators, no BOM and no trailing newline, matching the original resource JSON serialization. Preserve every reviewed key/value pair, physical reference order and ayah-number entry. Keep release metadata outside the flat translation object.
3. Copy the original Turkish SQLite database to root as `turkish-wbw-translation.db`, then update only that root copy from the reviewed Turkish JSON. The original database under `resources/turkish/` must remain unchanged.
4. Preserve QUL's `word_translation` table and columns: `surah_number INTEGER`, `ayah_number INTEGER`, `word_number TEXT`, and `text TEXT`. Word positions start at 1. Keep the existing location identifiers, including source gaps; do not renumber them. Ensure one row per translation key, string word numbers, no duplicate location triples, and exact JSON/SQLite value agreement after updating and adding missing rows.
5. The redundant root English JSON has been removed. Read the immutable English reference under resources/english/ directly. CI and local packaging must not alter the working Turkish JSON or any original resource. Build the release SQLite independently from a new copy of the immutable Turkish source and verify its exact data agreement with both working JSON and the updated root DB. SQLite byte identity across different SQLite versions is not required; schema, storage types, locations and text must agree.
6. Verify JSON/SQLite integrity, unchanged source/working JSON hashes, exact translation agreement and the final artifact layout. The current Turkish reference key set has 83,665 entries; changing that contract requires a separately documented decision. Keep the updated root DB versioned; ignore generated `dist/` output and SQLite runtime sidecars.

This preserves the [QUL word-by-word translation format](https://qul.tarteel.ai/resources/translation/99/docs): individual word meanings addressed by location, supplied as a flat JSON object and an equivalent SQLite translation table. Arabic remains a separate reference joined by location. `python scripts/build_release.py --update-root-db` prepares the verified root DB and local artifacts; later `python scripts/build_release.py` refuses a missing/stale root DB and builds release copies only. The CI workflow builds artifacts on branch/PR/manual runs and creates a draft GitHub release only for a pushed `v*` tag. Creating a local package does not publish data to QUL or GitHub.

## Current Turkish notation

Current working/release Turkish values must not contain square-bracket delimiters. Preserve round parentheses used for shared-expression/source-context views and preserve the reference ayah-number markers. Removing old explanatory delimiters must not create concatenated lexical alternatives or change a suffix accidentally; assess such boundaries explicitly against the Arabic/English context. Historical review records retain exact earlier values, including obsolete notation. This rule does not authorize editing any original resource.
