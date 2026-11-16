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

## 2026-11-16 — 06: Continue with multi-entry temporal and quantifier groups

Request: continue filling the remaining keys. Baseline: `033d895`, 1,640 missing keys. This bounded batch adds 77 keys and changes 180 existing values in 77 recorded groups. There are now 82,102 Turkish entries and 1,563 remaining missing keys across 1,215 ayahs. Remaining cases are still pending; this is not a claim that all combined expressions have been resolved.

The main issue is a relation whose overt Turkish ending appears on a later noun or nominal clause, while the postposition or quantifier occupies the relation's original key. For example, the existing `sonra` and `imanınızdan` become three complementary views of `imanınızdan sonra`: `(imanınız)dan (sonra)` for `from`, `(imanınızdan) sonra` for `after`, and `imanınız(dan sonra)` for the noun. Clause groups already processed in step 05 retain their inner relative/nominal roles; only the outer ablative ending is reassigned to the preceding relation. This prevents overwriting established inner alignment when expanding the group.

Additional explicitly inspected groups cover locative `her mescidde`, `her defasında`, `her vadide`, four dative expressions containing `Allah'adır`, and the oath expression `Allah adına`. The dative and divine name are highlighted separately; the copula stays shared context. Written forms such as `vasiyyet`, `fetihden`, and `Nuh'dan` are retained for a later spelling review. No lexical spelling corrections or new Turkish lexical wording are introduced.

Selected positional evidence: [2:109](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=109) distinguishes `min`, `ba'd`, and the following noun/clause; [30:3](https://corpus.quran.com/wordbyword.jsp?chapter=30&verse=3) confirms separate preposition and temporal noun positions even when both English glosses say `after`. These are selected checks, not exhaustive Arabic verification of every group.

Review of the provisional output excluded ten cases where the following entry itself stands for `that`/`what` without a recorded clause decomposition. Assigning a whole predicate to that subordinator would conceal another missing lexical entry. For example, `58:3:13–14` needs a joint analysis of `temaslarından` and the following absent predicate; it is left unchanged. The `ondan sonra` candidate is also deferred as part of that joint subordinator review.

Implementation and verification: `python scripts/continue_alignment.py`, then `python scripts/audit_missing.py`. The continuation script reads a fixed committed baseline, refuses unexpected Turkish edits, checks unchanged English bytes, verifies every expression against its recorded origins, preserves untouched pairs and all ayah numbers, and writes in reference order. It checks representative exact output strings and a deferred regression case. `reports/continued-alignment-changes.json` stores every before/after pair and boundary; the earlier manifest is retained as historical evidence. The pending list is filtered and its neighboring Turkish context refreshed to match the current file. The inventory independently verifies duplicate keys, nonempty strings, counts, and exact remaining-key coverage.

English SHA-256 is unchanged. Turkish SHA-256 changes from `94e871f2b1de1aae8c836ac5db4aa5a3f5c4a8c1699463bd00ba46ef93ac2770` to `698d10cc1eb8599834ae09cddd1bc387363205c7684ff9e7c676ecfad6e30fd9`.

## 2026-11-16 — 07: Broad continuation of the remaining inventory

Request: work through most remaining gaps in a broader pass rather than another small batch. The starting state is step 06: 1,563 missing keys. Added 1,021 keys (about 65% of that inventory), modified 1,013 existing values, and recorded 1,010 groups. Turkish now has 83,123 entries; 542 word/phrase keys remain absent across 466 ayahs. All ayah numbers and English bytes are unchanged.

The work combines corpus-supported noun forms, explicitly inspected boundaries, postpositions, negative and interrogative constructions, temporal idioms, multi-entry predicates, numerals, and selected lexical additions. Every applied group records its baseline values, English glosses, exact Turkish parts and source roles, resulting displays, category, and rationale. Thirty groups introduce lexical wording or repair inherited wording/case and are marked as such; these are not passed off as preservation-only operations.

The display convention is extended to context-only entries where no independent overt Turkish contribution has been identified: the entire phrase is parenthesized. For example, `(daha önce)` for the source preposition does not invent an ending when only the temporal phrase `daha önce` is present. There are 521 such views. They are flagged for further semantic review because an absent overt form could reflect a legitimate Turkish construction, a paraphrase, or an inherited omission. They count as structurally present keys, not certified complete translations. The English notation guide explains this distinction for non-Turkish readers; `reports/broad-linguistic-review.json` preserves the follow-up work separately from the missing-key inventory.

Selected concrete changes:

- Redistribution of complete noun/predicate expressions from function-word keys to their lexical positions, with overt grammatical contributions highlighted where identifiable.
- Explicit negative, temporal, and clause boundaries for multi-entry expressions, preserving previously established roles where relevant.
- Completion of missing lexical nouns beside inherited isolated `-den/-dan`, replacing unattached fragments with contextual noun/ending views.
- In `75:12`, move `o gün` to its own source position, restore the Lord reference, and repair genitive `Rabbinin` to dative `Rabbine` for `To`.
- In `2:217`, replace `ayında` with complementary views of `ay hakkında`; the inherited locative must not be mislabeled as the preposition `about`.
- In `2:60`, expose the two components of `on iki` according to their Arabic numeral positions, despite the reference's first gloss `(of)`.
- In `2:79` and related local constructions, distinguish Arabic `min` and the following location noun even when the English gloss labels the first entry `(is)`. English is retained verbatim.
- In `2:143:13`, explicitly interpret the inherited `(ma)` as the actual negative ending and retain all letters, rather than converting this particular grammatical annotation into an explanatory note.

Selected primary positional checks: [2:60](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=60), [2:79](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=79), [2:109](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=109), [30:3](https://corpus.quran.com/wordbyword.jsp?chapter=30&verse=3), [41:24](https://corpus.quran.com/wordbyword.jsp?chapter=41&verse=24), and [2:48](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=48). These are selected checks, not an exhaustive Arabic validation of the batch. `2:48:4` remains absent because its inherited lexical/voice issue is not resolved by a suffix split. Other complex inherited problems, including the extended phrase displacement in `2:267` and corrupted compound wording around `16:102`, remain review work rather than being silently filled from an English lookup table.

Preparation: `python scripts/complete_broad_alignment.py` writes the proposed manifest without applying it. Local review corrected false candidate splits such as `haya + ta` in `hayata`, `g + ün` in `iki gün`, final `en` inside `gelmezden`, and possessive versus connector consonants. Explicit overrides record reviewed boundaries for ambiguous forms instead of pretending matching letters always prove a morpheme. Apply with `python scripts/complete_broad_alignment.py --apply`.

Independent verification: `python scripts/validate_broad_alignment.py` reconstructs the starting state from the committed file plus the previous continuation manifest, checks every before/after value and source role, verifies untouched pairs and every ayah number, checks duplicate keys, nonempty strings, reference order, balanced/noncrossing delimiters, exact JSON formatting, representative boundary regressions, final SHA-256, and the exact pending-key set. It also compares English bytes against the initial commit. `python scripts/audit_missing.py` independently regenerates the structural inventory; `git diff --check` checks whitespace. All passed. These tests establish structural scope and reproducibility, not complete semantic correctness.

Turkish SHA-256 changes from `698d10cc1eb8599834ae09cddd1bc387363205c7684ff9e7c676ecfad6e30fd9` to `5b1ecd2180fa24cfba291b0a60b66791ebb1c846c45bd10b0caac16ca476fc72`. English SHA-256 remains `917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2`. The user's unrelated `.vscode/` files are outside this operation.

## 2026-11-16 — 08: Complete the remaining structural key inventory

Request: continue with the remaining entries. Starting state: 542 absent keys after step 07. This operation adds all 542, modifies 616 existing values, and records 526 groups. English and Turkish now have the same 83,665 keys in the exact reference order. There are no missing, extra, or duplicate keys; all 6,236 ayah-number values are unchanged. The English file is byte-for-byte identical to the initial commit.

Work proceeded through explicit local expression specifications, then larger phrase/position checks. The preparation script writes a reviewable manifest without changing translations unless called with `--apply`. It reconstructs the fixed input from `033d895` plus the continuation and broad manifests, and checks their before/after provenance. Existing content outside the authoritative update set is preserved. This stage records every added or modified entry with its English value, prior Turkish value, resulting display, expression origins, boundary roles, category, and rationale.

Preservation-only groups are checked against their original written material. Cases involving grammatical parentheses are explicitly normalized, while explanatory text is retained in square brackets. Larger constructions include front/possessive/case phrases, min/ba'd/nominal clauses, passive relatives, exception/negative constructions, compounds, and pronouns whose Turkish form appears on a later predicate. Matching letter sequences alone are not treated as morphological proof. Final review corrected examples where the exceptive negative had been confused with a past/nominal ending, or a source copula had been confused with a pronoun gloss.

Forty-four groups are explicitly marked as revisions rather than preservation-only operations. These include spelling/spacing or annotation repairs, restored lexical heads, compound completion, and interpretive phrase repairs. Material examples:

- `2:48:3–4`: replace the inherited punishment/passive expression `cezalandırılmaz` with complementary views of `yarar sağlamaz` for the negative avail predicate.
- `2:267:17–29`: correct the contiguous displacement of spending, taking, exception, location-reference, knowledge-command, Allah, self-sufficiency, and praise expressions. Existing expressions are moved using recorded origins; necessary finite/reference wording is supplied explicitly. The closing praise entry is no longer absent or placed under self-sufficiency.
- `6:48:1–2`: repair malformed `biz gönderimeyi` as the finite negative `biz göndermeyiz` and expose its negative ending.
- `16:102:3–4` and `18:94:2–3`: complete the corrupted Holy Spirit and vocative-name compounds as contextual views of `Ruhu'l-Kudüs` and `ey Zülkarneyn`.
- `4:135:23–27`: redistribute the existing prohibition and complements into a coherent Turkish instruction without inventing an extra negative that would reverse its force. The source purpose marker is context-only in this retained paraphrase.
- `5:41:29–31`: replace unsupported `bazısının` and complete the placement-after expression. This follows the reference's temporal gloss and is explicitly flagged for semantic review as an interpretive phrase repair.
- `42:23:16–18`: restore the love/kinship vocabulary of the English reference and remove the inherited parenthetical Allah-directed gloss. This follows the requested reference rather than claiming to adjudicate all tafsir interpretations; the complete change remains queued for semantic review.
- `63:10:2–4`: remove the literal `0` placeholder and expose the case and nominal-clause contributions already present in the following expression.
- Selected direct spelling repairs include `milet` to `millet`, removal of the stranded `y` in `bir suy`, correction of `onlarıv`, and possessive agreement in `sizin ellerinizde`.

Primary positional checks consulted for this work: [QAC 4:135](https://corpus.quran.com/wordbyword.jsp?chapter=4&verse=135), [5:8](https://corpus.quran.com/wordbyword.jsp?chapter=5&verse=8), [16:102](https://corpus.quran.com/wordbyword.jsp?chapter=16&verse=102), [12:83](https://corpus.quran.com/wordbyword.jsp?chapter=12&verse=83), [11:108](https://corpus.quran.com/wordbyword.jsp?chapter=11&verse=108), [4:24](https://corpus.quran.com/wordbyword.jsp?chapter=4&verse=24), and [5:32](https://corpus.quran.com/wordbyword.jsp?chapter=5&verse=32). The last confirms the min/ajl/dhalika sequence despite the reference's imprecise `time` gloss; the existing causal Turkish idiom is retained. English glosses are not edited.

Selected Turkish sense comparisons used [Diyanet 4:135](https://kuran.diyanet.gov.tr/kuran?ayet=135&mode=kuran-meal&sure=4), [Diyanet 5:8](https://kuran.diyanet.gov.tr/mushaf/kuran-meal-2/maide-suresi-5/ayet-8/diyanet-isleri-baskanligi-meali-1), [Diyanet 42:23](https://kuran.diyanet.gov.tr/mushaf/kuran-meal-2/sura-suresi-42/ayet-23/diyanet-isleri-baskanligi-meali-1), [Diyanet 2:267](https://kuran.diyanet.gov.tr/kuran?ayet=266&mode=kuran-meal&sure=2), and [Diyanet 5:41](https://kuran.diyanet.gov.tr/mushaf/kuran-meal-2/maide-suresi-5/ayet-37/kuran-yolu-meali-5). These are selected sense/position checks, not exhaustive validation of every inherited or newly reviewed Turkish phrase.

There are 172 context-only displays in this batch: 166 at previously existing keys and six at newly added keys. They explicitly identify surfaces that have not been independently located in the retained Turkish construction. A filled key does not certify that its meaning is adequately represented. `reports/linguistic-review.json` consolidates current values and review history for 831 keys across the broad and completion stages, including 693 currently context-only displays. This focused queue preserves zero-versus-omission and lexical/interpretive concerns; it is not an exhaustive error inventory for the whole Quran translation. `reports/alignment-pending.json` is now empty because it tracks absent keys only.

Reproduction: `python scripts/finish_remaining_alignment.py --apply`, then `python scripts/validate_remaining_alignment.py`, then `python scripts/audit_missing.py`. The explicit review cases are in `scripts/remaining_special_cases.py` and `scripts/remaining_final_cases.py`. The preparer verifies unique group ownership, valid source roles, original expression material for preservation-only changes, and balanced/noncrossing delimiters. The independent validator reconstructs the entire batch, verifies its exact edit scope, all untouched pairs, complete reference key order, duplicate-free/nonempty values, every ayah number, canonical UTF-8/LF JSON formatting, final hash, and representative negative, compound, placeholder, and displacement regressions. The inventory independently confirms zero missing/extra keys. `git diff --check` passes. These checks establish structural integrity and traceability, not complete translation certification.

Artifacts: `remaining-alignment-changes.json` and CSV contain the authoritative latest before/after log; `remaining-alignment-validation.json` records verification. Earlier manifests and hashes remain historical. No commit was created in this stage; the user's unrelated `.vscode/` files remain untouched.

Turkish SHA-256 changes from `5b1ecd2180fa24cfba291b0a60b66791ebb1c846c45bd10b0caac16ca476fc72` to `3f92efca0d85727623920e99f37690c701d37341aa7a0a30b9979c1402329d45`. English SHA-256 remains `917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2`.

## 2026-11-16 — 09: Pre-commit verification of the completed alignment

Request: perform a quick check and commit the completed work if no blocking issue is found. The next phase is a full Turkish grammar and spelling review.

Re-ran `python scripts/validate_remaining_alignment.py`, `python scripts/audit_missing.py`, and `git diff --check`. All passed. Both files contain 83,665 keys, with no missing, extra, duplicate, or empty entries. Reference order, all 6,236 ayah-number entries, unchanged pairs, recorded before/after changes, expression provenance, representative boundary regressions, and canonical Turkish JSON formatting were verified. English remains byte-for-byte identical to the initial commit.

No structural or change-record inconsistency was found by these checks. This is a quick structural and process review, not a full grammar, spelling, or semantic review. The focused concerns in `reports/linguistic-review.json` remain open for subsequent review; complete key coverage does not resolve those concerns. Steps 06–08 and this verification are included in the commit `Complete Turkish word alignment and document review trail`. The unrelated `.vscode/` directory is excluded.

## 2026-11-16 — 10: Turkish spelling and grammar review

Request: check Turkish grammar and spelling and continue through the findings. Baseline: `c9dac12`. English remains immutable; documentation and comments are in English.

Scanned all 83,665 values for common misspellings, malformed character sequences, repeated/exterior whitespace, delimiter problems, numeric placeholders, and suspicious suffix punctuation. A rare-token vocabulary assisted inspection; it is not a dictionary or proof of error. Alignment fragments were reviewed through their complete expression: isolated `ağac` before a vowel must not be blindly changed to `ağaç`. Apostrophe-containing words such as `rü'yada` and `ta'kibederek` must not be altered by unrelated substring matches. Transliteration, capitalization, and circumflex choices were not globally standardized.

The ledger records 1,051 changed values and no added/removed keys: 999 spelling, spacing, inflection, or annotation-boundary corrections, four explicit placeholder/punctuation alignment repairs, and 48 values in 17 explicit construction-repair groups. These count display values, not independent lexical errors; one correction can affect several complementary views.

Examples: `herşey → her şey`, `havyanlar → hayvanlar`, `inanmışşızdır → inanmışızdır`, `kalbleri → kalpleri`, `meyvaları → meyveleri`, and separate auxiliaries in `azap etmek` and `cihat etmek`. Vowel harmony changes with the noun in `meyve`; a root-only substitution would incorrectly produce `meyveları`. Reviewed proper-name case endings receive apostrophes. Question-particle spacing, applicable vowel harmony, malformed inflections, and repeated spaces are corrected. Selected historical dative `-mağa/-meğe` spellings are modernized. Parentheses retain contextual source roles, including equal-length substitutions across boundaries: `(her mescid)de → (her mescit)te`, not `(her mescitt)e`. Explanatory notes use square brackets where explicitly repaired. Ordinary inherited punctuation is not removed wholesale.

Construction repairs are distinct from spelling substitutions in `scripts/spelling_construction_cases.py` and the manifest's `construction_groups`:

- Attach ablatives to the complete noun phrase in `bin ay`, `her çift`, `her şey`, `her ümmet`, and `şu ağaç`. Compound names keep their inherited spelling, with the case ending after the complete name.
- Repair `79:40:8`, whose existing value was `0`, together with `79:40:9`: `(kötü hevesler)den` / `kötü hevesler(den)`. Previous key-count checks missed this because the key existed. The new validator rejects bare numeric values. Repair the corrupted `Allah-;-tan` / `Allah-;` pair at `46:8:10–11` as complementary views of `Allah'tan`.
- Restore `şey` at `80:18:3`, where the inherited value repeated the interrogative instead of translating the lexical head. Repair the expression as `hangi şeyden`.
- Remove displaced `ve Nuh'u da` from `21:75:6`; that wording already correctly opens `21:76:1` and does not occur in the source wording of `21:75`. Retain `salihlerden idi` in complementary views.
- Repair case boundaries at `53:59:1–3`, the malformed possessor annotation at `16:99:3`, and copular versus ablative ownership at `26:86:4–6`. The latter preserves the inherited present-tense Turkish expression without adjudicating the tense interpretation of Arabic `kana`.
- Repair case/display boundaries at `22:28:13–15`, `46:28:5–7`, and `39:47:13–15`. Retain inherited lexical paraphrases and the explanatory purpose wording; these case repairs do not certify their lexical precision.

Spelling-rule reference: [TDK, separately written compounds](https://tdk.gov.tr/icerik/yazim-kurallari/ayri-yazilan-birlesik-kelimeler/). Selected Arabic positional checks: [79:40](https://corpus.quran.com/wordbyword.jsp?chapter=79&verse=40), [46:8](https://corpus.quran.com/wordbyword.jsp?chapter=46&verse=8), [21:75](https://corpus.quran.com/wordbyword.jsp?chapter=21&verse=75), [26:86](https://corpus.quran.com/wordbyword.jsp?chapter=26&verse=86), [53:59](https://corpus.quran.com/wordbyword.jsp?chapter=53&verse=59), [80:18](https://corpus.quran.com/wordbyword.jsp?chapter=80&verse=18), [22:28](https://corpus.quran.com/wordbyword.jsp?chapter=22&verse=28), [46:28](https://corpus.quran.com/wordbyword.jsp?chapter=46&verse=28), and [39:47](https://corpus.quran.com/wordbyword.jsp?chapter=39&verse=47). These are selected checks, not an exhaustive Arabic review.

Two construction concerns remain in `reports/grammar-construction-review.json`: `30:43:12` and `39:74:10`. Their isolated suffixes require choosing the complete clause and its source roles, not a reliable spelling-only substitution. Positions were checked at [30:43](https://corpus.quran.com/wordbyword.jsp?chapter=30&verse=43) and [39:74](https://corpus.quran.com/wordbyword.jsp?chapter=39&verse=74). They remain unchanged and open, not marked correct. The existing 831-key semantic queue also remains open; `reports/linguistic-review-current.json` refreshes its values/history without assuming spelling corrections resolve semantic concerns. These focused queues are not exhaustive error inventories. The corpus has not been certified free of all grammar, spelling, or meaning errors.

Artifacts: `reports/spelling-changes.json` and CSV contain the complete English gloss / before / after / reason ledger; `reports/spelling-validation.json` contains current verification. `reports/spelling-scan-vocabulary.txt` is a generated rare-token inspection aid. Earlier alignment manifests, validation results, and their hash-specific validators remain historical snapshots.

Reproduce with `python scripts/apply_turkish_spelling.py --apply`, then `python scripts/validate_turkish_spelling.py`, `python scripts/prepare_spelling_review_reports.py`, and `python scripts/audit_missing.py`. The applier reconstructs the fixed committed baseline and refuses changes outside its previous recorded output. The independent validator reconstructs the exact final file and checks untouched values, reference order, all 6,236 ayah markers, duplicate/empty keys, bare numeric placeholders, delimiter balance, shared-expression consistency, canonical UTF-8/LF formatting, and representative regression cases. English bytes match the initial commit. `git diff --check` passes. No commit has been created for this stage; `.vscode/` remains outside the work.

Turkish SHA-256 changes from `3f92efca0d85727623920e99f37690c701d37341aa7a0a30b9979c1402329d45` to `3fc17754d87d7d6e9b84e0132b6d6de8928ad15d3401ac1d4e024298eaadacc3`. English SHA-256 remains `917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2`.

## 2026-11-16 — 11: Second spelling and grammar review

Request: check again for remaining Turkish spelling and grammar errors. The starting file is the uncommitted result of step 10, with SHA-256 `3fc17754d87d7d6e9b84e0132b6d6de8928ad15d3401ac1d4e024298eaadacc3`. `reports/spelling-second-pass-start.json` freezes the 1,051 first-pass changed values over `c9dac12`, allowing that exact state to be reconstructed without an intermediate commit. Earlier step-10 counts and hashes are historical; the combined ledger and validator now describe the latest result.

This pass adds corpus-based candidate generation rather than relying only on the first pass's known-error patterns. Rare complete tokens were compared with frequently occurring tokens by insertion, deletion, substitution, and adjacent transposition. The scan produced 646 candidates occurring at most twice. A second scan covered tokens occurring three to ten times and produced 299 additional candidates. Short tokens, repeated misspellings, consonant alternations, question particles, proper-name case spelling, and neighboring clause grammar were also inspected. Candidate similarity does not establish an error: ordinary inflections, different words, names, capitalization variants, and old transliterations can be legitimate. In particular, `Rabbinizim` is a valid first-person predicate and `sinin` is a valid imperative; neither is replaced simply because it resembles another token.

The second-pass ledger records 115 changed values relative to step 10: 111 newly edited keys and four previously edited displays reformatted. Cumulative changes relative to `c9dac12` are 1,162 values, comprising 1,106 routine spelling/spacing/inflection corrections, four earlier placeholder/punctuation alignment repairs, and 52 values in 19 explicit construction-repair groups. There are no added or removed keys.

Reviewed corrections include `sonre → sonra`, `Alah → Allah` with its inflected forms, `soruyarlar → soruyorlar`, `muhakak / mukakkak → muhakkak`, `hakında → hakkında`, `işitendi / bilendi → işitendir / bilendir`, `seden → senden`, `eyetlerimizi → ayetlerimizi`, `arasıdan → arasından`, and `yoludan → yolundan`. Additional fixes cover missing short-word letters, question-particle spacing, apostrophes in selected names and pronouns, and consonant alternations. The `tat-` correction applies at word end or before a consonant; `tadın` and other vowel-initial inflections retain `d`, and already corrected `tattır-` forms remain intact. Selected language/nationality words use standard `Arapça`, `Araplar`, and `Arap` spelling/capitalization; this does not retranslate the inherited Bedouin gloss or certify its lexical precision.

Two explicit grammar repairs are recorded independently of spelling-only rules:

- `79:24:3`: `sizi Rabbinizim → sizin Rabbinizim`, repairing the possessor while retaining the valid first-person predicate.
- `2:112:15–17`: replace the malformed existential/dative/infinitive sequence with complementary views of `ve onlar üzülmezler`. The source has conjunction and negation, nominative `hum`, and a plural finite grief verb. This is supported by the supplied English reference and the [Arabic positional analysis of 2:112](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=112). Preserve the separate fear clause at `2:112:12–14`: its identical inherited strings `ve yoktur` and `onlara` do not make it a complementary display of the grief clause. The independent validator now explicitly distinguishes those two separately scoped constructions while still checking the actual shared-expression groups.

The first-pass editing routine had placed a newly inserted boundary space inside an opening parenthesis in four displays. These are now corrected without changing their words or focus: `28:19:13`, `21:22:8`, `3:58:6`, and `7:169:10`. Future boundary-space insertions occur outside the opening delimiter. Regression checks also cover `geldi (mi)?`, the correct `tattır-` spelling, retained `Rabbinizim`, and retained `sinin`.

Spelling/capitalization references: [TDK capitalization rules](https://tdk.gov.tr/icerik/yazim-kurallari/buyuk-harflerin-kullanildigi-yerler/) and the [Turkish Historical Society dictionary's spelling principles](https://sozluk.ttk.gov.tr/hakkinda/k%C4%B1lavuz). These references inform orthographic conventions; the supplied translation and local clause context determine which word was intended.

Artifacts: `spelling-second-pass-changes.json` and CSV record the exact step-10-to-step-11 delta, including the four reformatted prior edits. `second-review-candidates.json` and `second-review-repeated-candidates.json` are reproducible candidate inventories of the frozen first-pass input, not current error inventories or certifications of the unchanged candidates. `spelling-changes.json` and CSV remain the complete combined ledger. Current Turkish values are refreshed in `linguistic-review-current.json`; spelling or grammar repairs do not automatically resolve the existing 831-key semantic queue. The two previously flagged construction concerns, `30:43:12` and `39:74:10`, remain unchanged and open. This review is not an exhaustive linguistic certification of the entire translation; transliteration and all inherited punctuation were not globally standardized.

Current reproduction/verification: `python scripts/apply_turkish_spelling.py --apply`, `python scripts/prepare_spelling_review_reports.py`, `python scripts/prepare_second_spelling_review.py`, `python scripts/validate_turkish_spelling.py`, and `python scripts/audit_missing.py`. Candidate inventories are reproduced by `python scripts/scan_turkish_second_review.py` and its `--repeated` mode, which reconstruct the frozen first-pass input. The validator independently reconstructs both the combined edit set and the second-pass delta. Reference bytes, 83,665-key coverage/order, all 6,236 markers, untouched pairs, actual shared expressions, delimiter balance, placeholder absence, and canonical JSON formatting pass. The rule scan finds no further applicable approved substitutions. `git diff --check` passes. No commit is created in this step; unrelated `.vscode/` files remain untouched.

Turkish SHA-256 is now `4152ef58819ac81148c8f2a0c926c588259ec922aa3a677183de8d8a73d3622a`. English SHA-256 remains `917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2`.

## 2026-11-16 — 12: Register immutable QUL originals and the release contract

The user supplied original English and Turkish QUL JSON/SQLite downloads and an Arabic QPC Hafs word-by-word script under `resources/`. Instruction: read these files only; their SHA values must never change. Arabic is the original-language evidence for assessing uncertain Turkish wording. At the final stage, remove the root English JSON, minify the updated root Turkish JSON, and publish a matching updated Turkish SQLite database at root. The original Turkish database stays immutable: copy it to root and update only the copy. These final release mutations are deferred; this step does not modify translations, create a release database, remove files, or create a commit.

Read the supplied [QUL documentation](https://qul.tarteel.ai/resources/translation/99/docs) and inspected all six local sources. The original English JSON has exactly the same loaded pairs as the initial/root English reference. The original Turkish JSON has exactly the same loaded pairs as the initial Turkish Git commit. English JSON/SQLite agree on 83,665 records; Turkish JSON/SQLite agree on 70,539 records. The Arabic JSON/SQLite agree on 83,668 complete word records. SQLite integrity checks pass. Databases were opened with `mode=ro&immutable=1` and query-only mode; no writable source connections or sidecar files were created.

`reports/resource-integrity.json` records the initial path, byte size, and SHA-256 of every source file. `scripts/audit_resources.py` verifies this fixed inventory, JSON/SQLite correspondence, database schemas, original Git-pair agreement, and hashes before/after reading; it writes reports only outside `resources/`. Initialization cannot replace an existing baseline. A second audit confirmed all six hashes remained unchanged. Details and the future release layout are in `RESOURCE_POLICY.md`; verification results are in `reports/resource-audit.json`.

The Arabic source includes three locations absent from the English source: `2:181:4`, `8:6:5`, and `13:37:9`. All three are `مَا`; at the previous location the English gloss `after what` covers both Arabic words. This is an explicit source-alignment distinction, not a reason to shift later word positions or modify the originals. All existing English locations are present in Arabic. The audit records these exceptions and their neighbors for future linguistic checks.

`scripts/read_arabic_context.py` reads a location or ayah and shows original Arabic beside source English and the current root Turkish values, checking resource hashes without writing files. Verified it with `2:5:4`: the original Arabic preposition and following Lord/pronoun word align to the established `(Rableri)nden` / `Rableri(nden)` example. Future uncertain translations must be evaluated against the Arabic context, with the locations and rationale recorded; do not resolve them through automatic English substitutions alone.

The future root SQLite copy must preserve QUL's `word_translation (surah_number INTEGER, ayah_number INTEGER, word_number TEXT, text TEXT)` schema and exactly match the reviewed root Turkish JSON. No metadata or Arabic records will be inserted into the flat translation object. Active checks will be adapted to the source English path before removing the root English JSON. Resource hash verification remains mandatory through the eventual release commit.

## 2026-11-16 — 13: Final spelling-review checks and source-preservation commit

Request: run a final grammar/spelling check, correct any definite new errors, and commit the completed corrections together with the original resources and their policies. No additional definite spelling/grammar error was identified by this final pass. The approved correction scan has no remaining applicable substitutions. Re-ran the independent spelling/grammar reconstruction validator, the missing-key inventory, and the immutable resource audit. All passed. The Turkish file still has 83,665 entries and the recorded 1,162 changed values relative to `c9dac12`; all 6,236 ayah markers and the exact reference key order are preserved. English remains byte-for-byte unchanged from the initial commit. All three resource JSON/SQLite pairs agree, their databases pass integrity checks, and all six original SHA-256 values remain unchanged.

The two documented clause/alignment concerns at `30:43:12` and `39:74:10`, and the existing semantic-review queue, remain open. This commit records the reviewed corrections and source-preservation infrastructure; it does not assert that every inherited Turkish meaning or sentence has been certified error-free. The detailed ledgers and follow-up records are included.

Added `.gitattributes` to disable Git text normalization under `resources/**` and retain canonical LF bytes for the working translation JSON files. Pre-commit verification compares each staged source blob directly with the fixed resource hash manifest and verifies the staged Turkish hash against the correction ledger. `git diff --check` and the staged whitespace check pass. The commit is titled `Correct Turkish spelling and grammar and preserve original QUL resources`. Unrelated `.vscode/` files are excluded. Final release minification, root English removal, and creation of the updated root Turkish SQLite database remain deferred under `RESOURCE_POLICY.md`.
