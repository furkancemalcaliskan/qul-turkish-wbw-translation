# Process and review record

This project corrects QUL Turkish word-by-word data while preserving original sources. Documentation/comments are in English except the explicitly bilingual root README. The initial 831-record semantic flag queue is reviewed; local packaging is verified; external publication and submission are pending. This is AI-assisted review with recorded interpretive limits, not independent expert certification of every translation.

## History

| Commit | Stage |
| --- | --- |
| 4503cdc | Initial English/Turkish working files; 70,539 Turkish keys. |
| 36edf35 | Reorder/format Turkish without changing existing pairs. |
| cf1e80d | Add ayah numbers and inventory translation gaps. |
| 033d895 | First contextual alignment of suffixes, fused expressions, negation and clauses. |
| c9dac12 | Complete reference-key coverage and document alignment changes. |
| 661144b | Correct 1,162 spelling/grammar values; preserve original QUL resources and establish policies. |

Historical reports and retired stage-specific tools remain in their commits:

```powershell
git log --oneline
git show 661144b:reports/spelling-changes.json
git show c9dac12:reports/remaining-alignment-changes.json
```

Use historical tools only from a matching historical checkout. Their retired outputs are not maintained in the current tree.

## Report consolidation - 2026-11-17

At the user's request, 44 step-specific reports were consolidated into four files: reports/README.md, resource-integrity.json, review-state.json and validation.json. The then-uncommitted first semantic batch, all 20 before/after changes and source evidence, and all 831 queue-history records were preserved before removing standalone reports. Translation and source bytes were unchanged by that documentation cleanup itself; the subsequent semantic work below intentionally changes root Turkish only. The historical cleanup checksum remains identified under consolidation in validation.json.

New semantic batches are sections of review-state.json, not separate report files. report_store.py maintains consolidated sections. The bilingual README records provenance, notation, contribution goals, source-licence uncertainty and exact review scope. No licence was assigned to the downloaded originals.

## Arabic-led review and second reading - 2026-11-17

The first batch had already changed 20 values in four ayahs and resolved two semantic flags before this resumed review. Batches 002-009 then assessed all 829 remaining flags. Batch 010 reread the work, corrected draft inflection and completed explicitly identified adjacent lexical/syntactic follow-ups. Batch 011 corrected 28 explicitly identified spelling/inflection values, including eating imperatives and the 4:3 future-negative form. Prior drafts remain in the ordered, hash-linked ledger rather than being silently rewritten.

| Batch | Recorded value changes in that batch | Newly resolved initial flags | Reassessed flags |
| --- | ---: | ---: | ---: |
| 001 | 20 | 2 | 0 |
| 002 | 99 | 55 | 0 |
| 003 | 74 | 64 | 0 |
| 004 | 127 | 112 | 0 |
| 005 | 167 | 130 | 0 |
| 006 | 164 | 140 | 0 |
| 007 | 208 | 139 | 0 |
| 008 | 184 | 120 | 0 |
| 009 | 106 | 69 | 0 |
| 010 | 79 | 0 | 12 |
| 011 | 28 | 0 | 0 |
| 012 | 622 | 0 | 0 |
| 013 | 787 | 0 | 0 |
| 014 | 63 | 0 | 0 |
| 015 | 90 | 0 | 0 |
| 016 | 30 | 0 | 0 |
| 017 | 19 | 0 | 0 |
| 018 | 4 | 0 | 0 |
| 019 | 4 | 0 | 0 |

Current queue: 487 reviewed_with_changes, 344 reviewed_retained, 0 pending. These statuses describe reviews/constructions, including adjacent corrections, not 487 individually erroneous keys. The current net difference from 661144b is **2,629 distinct values across 1,262 ayahs**. This resumed work changed **2,609 values across 1,258 ayahs** relative to the already applied first batch. Batch totals are not unique error counts and must not simply be added together.

Every batch records source Arabic/English by location, complete consulted ayah contexts, before/after values, reasons and source-role allocations. The 2:23 and 2:36 deferrals from the first batch were resolved in 002. Later identified follow-ups were revisited in 010, including scripture-confirmation idioms, resentment versus revenge, generic accountability pronouns, destructive-wind roles, fainting, and the seven specifically selected Throne/istiva clauses. Arabic human-maturity, plant-growth and istawa-ila constructions were not swept into that lexical comparison.

Selected readings and their alternatives remain explicit. Examples include love/food pronouns, 4:135 syntax, negated nearness, nearest/lower land, contextual partitives, raising/sending and technical istiva terminology. Keeping a technical term does not uniquely settle its theological interpretation. Complete context storage is evidence, not a claim that every unmodified word in an ayah was exhaustively certified.

## Notation and scope

Outside parentheses is the selected source contribution; inside is shared context. Do not concatenate complementary views. Current Turkish values contain no square brackets. The historical ledger preserves earlier notation as evidence; round parentheses remain the shared-expression/context notation. Allocation is functional rather than always morpheme-for-morpheme: Turkish verb valency, noun compounds, rhetorical questions and negative-exception transformations can require a different construction from the isolated English gloss.

A fully parenthesized value is not automatically correct. Accepted zero surfaces have explicit reasons, such as anterior time without a separate ablative, prepositions absorbed by Turkish verb valency, or a negative-exception restriction expressed by only. Conversely, no suffix was invented just to make every function word visually nonempty. Semantic decisions remain distinguished from incidental spelling repairs.

Primary local evidence is the user's immutable QUL Arabic and English resources. Published comparisons are linked within the batches and report summary. Some QAC page requests returned different verse headings and some official pages exposed no readable text; those attempts are explicitly not claimed as verification. No external messages, submission or publication occurred.

## Maintained workflow

```powershell
python scripts/audit_resources.py
python scripts/audit_missing.py
python scripts/semantic_review.py
python scripts/read_arabic_context.py 2:5
```

semantic_review.py replays the ordered ledger from commit 661144b and validates the exact current result. review_semantics_002.py through review_semantics_019.py preserve the explicit curated decisions. Their --apply modes require the expected state; rerunning an already recorded batch validates rather than duplicates history or rolls data back. review_semantics_001.py is the guarded historical first-batch applier and refuses to replace later batches. validate_semantic_review_001.py remains a compatibility verification command and delegates to the complete ledger once later batches exist.

Verification checks exact before/after chains and untouched values, original Arabic/English provenance and complete recorded contexts, foreground roles, all 83,665 keys in reference order, 6,236 unchanged ayah markers, delimiters, canonical UTF-8/LF JSON, unique keys and queue history including reassessments. Source checks open immutable read-only SQLite and verify all six hashes and JSON/SQLite agreement. Technical checks establish integrity and reproducibility, not linguistic correctness or independent scholarly approval.

Current Turkish SHA-256: 9076b351f661aaac319af263c3c241b0f2a00490622624bd9321e3fa49a482c7. Root English SHA-256: 917a0fb15244cfd84ab3492172d33418225a682e92d74f529c32df96a0f5f7f2.

## Sources and future release

RESOURCE_POLICY.md defines immutable originals, the three Arabic-only location exceptions and the final output contract. QUL_CONTRIBUTION.md records the contribution route. Resource #99 reports unavailable copyright information; attribution does not itself establish a data licence.

Historical plan at the end of the semantic-review stage (superseded by the separate-packaging instruction below): minify root Turkish JSON, update a root copy of Turkish SQLite, and remove root English. Preserve originals and QUL's flat JSON/SQLite contract. No release, database update, external publication or commit occurred in this resumed semantic review. Unrelated .vscode files remain outside the work.

## Notation and strict spelling follow-up (2026-11-17)

The user rejected square-bracket annotations and reported two remaining errors. Batches 012-019 address this follow-up. Relative to the result of 011, 1,522 distinct values in 940 ayahs changed. These are location counts, including notation-only changes, not independent linguistic errors.

Batch 012 removed only the square-delimiter characters from 622 values, preserving their contents, spacing and round parentheses exactly at that stage. Later batches reread all distinct affected expressions. They repaired glued lexical alternatives, word boundaries and duplicate appositions separately, with explicit Arabic/English evidence. Original Arabic-derived nutfe/alaka nouns were retained instead of concatenating their old explanatory sperm/embriyo glosses or newly adjudicating biological interpretation. Historical before/after records intentionally retain old brackets. Current Turkish values must contain none.

The reported 2:286:35-36 construction now reads gücümüzün yetmediği: the embedded subject is gücümüz, not biz. At 5:1:5, akitleri(zi) became akitleri(nizi); the contextual second-person possessive remains parenthesized because the Arabic contracts noun itself has no possessive ending. Other confirmed changes include şüket -> şükret, öc -> öç, -ıyle -> -ıyla, interrogative-particle spacing, duplicate ve, and complementary on iki/on dokuz views. Selected common loanwords were normalized to standard Turkish spelling without internal transcription apostrophes; proper-name suffixes were preserved.

Explicit verbal -mağa/-meğe locations were modernized to -maya/-meye. This is a spelling modernization, not a claim that every older form was a semantic error. In 49:12 the action is yemeyi; the food-noun forms yemeğ(e) at 2:61:7 and 33:53:13 remain untouched. Legitimate reduplications such as ayrı ayrı, bile bile and bir bir were retained.

audit_turkish_spelling.py scans all 83,665 values for the documented bounded patterns, checks the exact initial delimiter-only operation, and records results inside validation.json. A broad substring candidate also matched the valid vahyetmediğimiz; its pattern was narrowed to the actual gücümüzün yetmediğimiz construction after contextual review. Approximate vocabulary comparisons and repetition scans identify candidates, not automatic correction authority. The audit is not a full Turkish grammar parser or proof of error-free translation.

Orthographic reference: [TDK vadetmek](https://sozluk.gov.tr/?ara=vadetmek). Quranic meanings remain grounded in the immutable local Arabic and English sources.

## Separate release packaging (2026-11-17)

After the completed review commit 188ff1e, the user requested a final data check, a root copy of the Turkish source database updated from reviewed JSON, and CI packaging without rewriting either working JSON. This supersedes the earlier root-minification/English-removal plan. All four existing data/review audits passed; no translation value changed in this packaging stage.

The root DB was copied from the original Turkish SQLite, updated by existing row identifiers and extended with missing locations. Only the copy is writable. The original table definition, column types and zero user/application versions are retained. The root DB has 83,665 unique locations and exactly matches reviewed JSON, including 6,236 ayah markers.

build_release.py builds independent JSON/SQLite files in dist/, verifies protected-input hashes and exact data agreement, and emits checksums, a provenance manifest and English release notes. JSON uses the original resources' raw UTF-8 compact serialization without a trailing newline. Temporary files are staged outside protected directories and a verified root DB is replaced atomically only with --update-root-db. Normal builds reject a stale/missing root DB instead of silently changing it. The manifest distinguishes the build revision and dirty state; generated outputs are not versioned.

Release tests cover update/addition without source mutation, Unicode serialization, source-row loss, duplicate locations, schema drift, reference order, ayah markers, forbidden notation and protected-output paths. Real-data integration checks verify the complete JSON/root-DB/release-DB agreement and repeat-build stability. CI runs the same checks and builds downloadable artifacts; only pushed v* tags trigger creation of a draft GitHub release. No remote repository was configured at this stage, so no hosted CI run, tag push, GitHub release or QUL upload was performed.

Personal editor settings, local environment files, Python caches, generated dist/build output and SQLite sidecars are ignored. The reviewed root database remains versioned.

## Remove redundant root English copy

The user subsequently authorized deletion of only the root english-wbw-translation.json. All active checks, historical helper entry points and packaging now read resources/english/english-wbw-translation.json directly. Historical initial-English comparisons check parsed pairs against Git; original source bytes remain protected by the immutable resource manifest. Earlier statements about preserving both root JSON files describe the preceding stage and are superseded for the English copy only. No Turkish JSON/DB or original-resource values were changed by this cleanup. Release packaging and tests were rerun without the root English file.

## v1.0.0 preparation

Repository name: qul-turkish-wbw-translation; intended owner: furkancemalcaliskan. Prepared a bilingual README, English changelog, closed external-contribution policy and maintainer CODEOWNERS. CI accepts branch/tag pushes and manual runs, not external pull-request events. Release metadata identifies the project and repository. The local release commit and annotated v1.0.0 tag are prepared before the user's push. No source or Turkish translation values changed.

The user will push the repository. GitHub rulesets and feature settings must be applied through gh after the initial branch exists remotely; they were not claimed as enabled by these documentation files. No remote repository creation, push, ruleset update or publication was performed during local preparation.

## README separation and hosted publication

The user authorized README cleanup, push, release publication and repository rulesets. README.md is now English-only apart from its language-navigation label and quoted Turkish data; README.tr.md is the Turkish companion. Both contain their own verification/build instructions. The English report summary remains separate. Earlier bilingual-README statements describe the previous layout.

Repository features were updated through gh: pull requests, issues, discussions and wiki are disabled. Two active branch rulesets cover all branches: Owner-only branch updates (27486724), with only user 83654279 allowed to bypass creation/update restrictions; and Preserve branch history (27486751), with no bypass for deletion or non-fast-forward updates. Their exact payloads and feature settings are committed under .github/. No translation, original resource or SQLite content changed. The unpublished local v1.0.0 tag is advanced to the documentation-complete release commit before its first remote push; no published tag is rewritten. CI-generated artifacts are verified before publication.
