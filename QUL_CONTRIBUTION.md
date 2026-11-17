# Contributing the Turkish WBW corrections to QUL

Research date: 2026-11-16. This records the published contribution guidance and a proposed handoff for this project. It is not evidence of maintainer approval, accepted licensing terms, a submission, or publication. The user subsequently resumed the Arabic-led work: the initial 831-record flag queue is now reviewed with its limits documented in the reports. Final release packaging and external submission remain pending.

## Verified public guidance

- [Contribute Data](https://qul.tarteel.ai/docs/contribute-data): improving existing translation data is in scope. Most data contributions use the QUL CMS, with review before publication. The page recommends community Discord coordination for larger contributions and explicitly says the documentation is still being expanded.
- [QUL CMS](https://qul.tarteel.ai/cms): the public entry point redirects to sign-in and offers account creation. Public documentation does not establish whether a newly created account can edit Turkish resource #99, what permissions are required, or how a bulk WBW replacement is imported.
- [Contribution workflow](https://qul.tarteel.ai/docs/contributing): the repository/issue tracker is [TarteelAI/quranic-universal-library](https://github.com/TarteelAI/quranic-universal-library). Dataset issue reports should identify the resource URL, format, exact locations, expected/actual values, and a minimal example. The documented fork/branch/PR instructions cover repository contributions; they do not establish that a SQLite/JSON replacement should be committed directly to that application repository.
- [Turkish WBW #99 documentation](https://qul.tarteel.ai/resources/translation/99/docs): this particular package uses word locations, a flat JSON location-to-string object, and the `word_translation` SQLite schema. The generic translation tutorial also discusses ayah-level packages; retain the WBW package's own contract for this contribution.
- [Turkish WBW #99 licence tab](https://qul.tarteel.ai/resources/translation/99/licence): the page states that copyright information is unavailable. The bilingual README records this uncertainty and credits QUL as source provider. No dataset licence is inferred from the application repository's code licence or assigned to the downloaded originals. Attribution and licence questions can be included in the maintainer discussion.

Official community entry point: [QUL Discord](https://t.zip/discord?utm_campaign=qul&utm_source=github), linked from the contribution guide. The observed redirect was to `https://discord.gg/uXDndvM8RJ`; no authenticated community access or message was attempted.

## Proposed project-specific route

The steps below are recommendations for this project, not additional requirements claimed to appear in the QUL documentation.

1. Coordinate the planned correction of existing Turkish WBW resource #99 with the maintainers. Use a focused [dataset issue](https://github.com/TarteelAI/quranic-universal-library/issues), Discord, or both, linking a reviewable project summary when available. Describe the work as corrections/completion of the existing dataset and distinguish new contextual notation and interpretive revisions from spelling fixes. An initial coordination discussion can happen before the dataset is ready; label the work unfinished.
2. Ask whether the preferred destination is an update to #99, a new version/resource, or CMS review tasks. Confirm the team's bulk-import format, permissions, reviewer expectations, handling of ayah markers, and acceptance of the complementary-parenthesis convention. Include a small example such as `(Rableri)nden` / `Rableri(nden)` and explain how it behaves in word-level tooltips. Also clarify data provenance, author attribution, redistribution, and licence terms.
3. Finish the Arabic-led review, document uncertain or disputed choices, and complete release verification. Make the limits of automated/AI-assisted work and any human linguistic review transparent. Do not present pending records as fully reviewed or claim an independent expert endorsement that has not occurred.
4. Prepare a versioned handoff package: minified root Turkish JSON; matching root Turkish SQLite; a before/after ledger keyed by location; reasons and Arabic/English evidence; the English notation guide; reproducible verification commands/results; and source/final checksums. Preserve all original resources byte-for-byte under the existing policy. Prepare a concise summary of additions, corrections, semantic choices, and remaining limitations.
5. Provide the package through the maintainer-confirmed route. The public GitHub project supplies provenance, history, and review evidence; CMS/maintainer review supplies QUL's publication path. No public guide found in this research specifies a self-service bulk upload that automatically replaces #99.
6. After acceptance, compare the published JSON/SQLite key/value pairs with the reviewed release. Ask for a resource update note and a clear current download/version reference so developers can identify the corrected data. Existing application copies and caches will still need their owners to update; publication alone does not replace previously downloaded files.

## Suggested issue contents

- Resource: `https://qul.tarteel.ai/resources/translation/99/docs`.
- Formats: WBW JSON and SQLite, preserving the location/schema contract.
- Scope and status: completion, spelling/grammar corrections, Arabic-led semantic review, and the exact review status.
- Two or three minimal location-specific before/after examples, with Arabic evidence and rationale.
- Repository/release links when ready, source hashes, and validation results.
- Explicit questions about updating #99, bulk import, reviewer access, notation, attribution, and dataset redistribution/licensing.

The [resource guide template](https://qul.tarteel.ai/docs/resource-guide-template) is a template for QUL documentation pages, not a dataset-upload form. A documentation PR can describe an agreed workflow later; it does not itself establish publication of the corrected dataset.

No issue, PR, Discord message, account registration, upload, repository publication, or release was performed during this research. The pending semantic batch remains uncommitted at the user's request; commit completed work when the agreed review stage is finished.
