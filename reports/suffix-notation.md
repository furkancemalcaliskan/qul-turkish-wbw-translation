# Contextual notation for Turkish suffix alignment

## Why a reference key can be missing

The English reference has separate entries for `from` (`2:5:4`) and `their Lord` (`2:5:5`). The Turkish file currently expresses their combined meaning as `Rablerinden` at `2:5:4`, leaving `2:5:5` absent. The English reference is the alignment authority and is never edited.

Turkish can express a relationship with an ending attached to a noun instead of a separate word. Here the English preposition `from` corresponds to an ending rather than a standalone Turkish word. Simply inserting the full Turkish phrase again would hide which part belongs to which source entry.

## Agreed display convention

The user specified this complementary pair:

| Key | English reference | Turkish display | How to read it |
| --- | --- | --- | --- |
| `2:5:4` | from | `(Rableri)nden` | The ending outside parentheses carries the relationship; the noun inside parentheses supplies readable context. |
| `2:5:5` | their Lord | `Rableri(nden)` | The noun outside parentheses carries this entry's meaning; the ending inside parentheses shows how it joins the preceding entry. |

For a reader who does not know Turkish: read these two entries as **one contextualized Turkish expression shown twice, with a different part emphasized each time**, not as two independent words to concatenate. Text outside parentheses is the contribution aligned to the current reference key. Text inside parentheses is context shared with the other entry. Concatenating the displays would incorrectly repeat the expression.

An ending-only display such as `-den` or `-dan` could label the grammatical contribution of `from`. However, an unattached ending is not a complete, independently readable translation of the expression. Its form and interpretation depend on the word it attaches to. The contextual notation keeps the actual word visible instead of presenting an isolated grammatical fragment. Preserve the spelling and suffix form of the existing translation during this alignment step; do not silently correct spelling or meaning at the same time.

## Applying the convention carefully

- Apply the pair only when the existing Turkish text contains the meanings of both adjacent source entries and their boundary can be identified.
- For example, `in` + `the earth` represented by `yeryüzünde` can be displayed as `(yeryüzü)nde` and `yeryüzü(nde)`.
- The boundary follows the existing written form. A connector consonant may be grouped with the case ending for display; this is an alignment convention, not a full morphological annotation system.
- Preserve the existing written expression, including inherited spelling. Reviewed multi-entry groups may move expressions between source positions; their origins and resulting positions must be recorded explicitly.
- Existing explanatory parentheses are converted to square brackets in touched expressions, retaining their text. Parentheses then consistently indicate alignment context. Untouched entries retain their original notation.
- Verbs, negation, relative clauses, independent words, and multi-entry phrases require separate structural rules. A missing key alone is not evidence of a suffix.
- Record every changed and added entry with its original value, English context, chosen boundary, and reason. Regenerate missing-key reports after applying changes.

This convention is now accepted for identifiable suffix-alignment cases. Other missing keys remain a separate linguistic review task. The initial inventory and initial alignment-review notes describe the state before this convention was applied.

## Negation, clauses, and larger expressions

The user explicitly included verbal negation and subordinate clauses in this operation. For example, the combined expression `inanmazlar` can expose negation as `(inan)maz(lar)` and the verb contribution as `inan(maz)lar`. The negative aorist cluster is shown together; this display does not assert that every highlighted cluster is a single linguistic morpheme. A relative expression such as `inananlar` can expose the relative/nominal contribution as `(inan)anlar` and its lexical predicate as `inan(anlar)`. Other clause types use their actual written endings, rather than applying noun-case rules to verbs.

With three source entries, each display highlights its own contribution and brackets the other contributions as context. Source-key roles and exact character spans are stored in the change manifest. Some source entries contribute multiple separated pieces. Connectors, changed stem forms, and conventional clusters follow the existing surface spelling; the displays are not dictionary headwords or a complete morphological parse.

An existing full phrase may need redistribution rather than a suffix split. In `4:23`, the inherited expressions `birleştiğiniz` and `evlerinizde bulunan` occupied the opposite source ranges. Their recorded origins are moved to the corresponding ranges before contextual views are generated. No new lexical wording is introduced by that correction.

## Evidence and limits

The supplied English and Turkish files are the primary alignment data. Local rules distinguish noun endings, negative forms, nominalizers, relatives, infinitives, and temporal constructions. Matching letters alone are insufficient: for example, the noun `Musa` must not be split as a conditional, and nominal `-ma/-me` must not automatically be called negation. Existing lexical corroboration and exclusions reduce these ambiguities but do not certify inherited translation accuracy.

Turkish grammatical references consulted: [TDK locative endings](https://tdk.gov.tr/icerik/yazim-kurallari/bulunma-durumu-eki-da-de-ta-tenin-yazilisi/), [TDK apostrophes](https://tdk.gov.tr/icerik/yazim-kurallari/kesme-isareti/), [TDK negative -mA](https://tdk.gov.tr/icerik/sikca-sorulan-sorular/olumsuzluk-eki-ma-yapim-eki-midir-yoksa-cekim-eki-midir/), and [MEB grammar material](https://ogmmateryal.eba.gov.tr/kitap/mebi-konu-ozetleri/tyt-turkce/tyt-turkce.pdf).

Selected Arabic positional checks used the Quranic Arabic Corpus: [2:5](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=5) for the requested example, [2:217](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=217) for an excluded ambiguous preposition, [4:23](https://corpus.quran.com/wordbyword.jsp?chapter=4&verse=23) for the expression swap, [7:198](https://corpus.quran.com/wordbyword.jsp?chapter=7&verse=198) for separate negative/verb positions despite repeated English wording, [17:111](https://corpus.quran.com/wordbyword.jsp?chapter=17&verse=111) for relative/negative/verb positions, and [46:33](https://corpus.quran.com/wordbyword.jsp?chapter=46&verse=33) for preposition/subordinator/verb positions. These checks cover selected examples, not every changed entry. English gloss anomalies are preserved in the immutable reference.

Remaining gaps are explicitly pending, not declared semantically absent or all unrelated to suffixes. They may include further fused expressions, zero equivalents, spelling problems, shifted phrases, or missing meanings requiring individual ayah review. In particular, `2:48:4` is excluded because the inherited wording requires lexical/voice review, and `2:217:3` cannot safely be assigned the neighboring locative ending.

## Extension: no independent surface identified

The broad continuation distinguishes an overt suffix from a function that has no independently identified surface in the retained Turkish wording. An entirely parenthesized display, such as `(su)`, supplies **context only**: there is no highlighted Turkish contribution for that source entry. The lexical entry is `su`. This is deliberately different from `(Rableri)nden`, whose visible ending is an overt contribution. No isolated ending or invented lexical word is inserted merely to make every key look nonempty.

This extension also applies when a source auxiliary is fused with another grammatical construction or expressed elsewhere in the clause. For example, `from` + `before` may be rendered by the inherited `daha önce`: the first view is `(daha önce)`, the second is `daha önce`. The first view must not be read as a second standalone translation to concatenate.

**A context-only display does not prove that the source meaning was adequately translated.** There may be a legitimate Turkish zero realization, a paraphrase, or an inherited omission. Every such key is recorded in `broad-linguistic-review.json` for semantic review. Filling its structural key is not the same as certifying its meaning. This distinction is part of the audit trail, not a claim that all remaining linguistic work has been completed.

Case forms are construction-dependent. The ending found in a Turkish paraphrase need not equal the usual dictionary translation of the English preposition. The log records the actual written form, while separate repairs identify cases where retaining that form would misrepresent the relationship. In particular, the broad batch resolves the previously deferred `2:217` example by replacing `ayında` with complementary views of `ay hakkında`; it does not relabel `-nda` as `about`.

Some English glosses combine or obscure source contributions. In [2:79](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=79), the reference labels the Arabic preposition `min` as `(is)`, followed by `from` for the location noun. The recorded Turkish views expose `katı` and `ndan`, retaining the copula as context; the English file remains untouched. In [2:60](https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=60), the two Arabic numeral components correspond to the existing Turkish `on iki` in reversed component order. Their contextual views identify the components rather than treating the first English gloss `(of)` as an ordinary preposition.

New lexical wording and repairs are explicitly marked `lexical_revision: true` in the broad manifest. For instance, an inherited isolated `-den` beside a missing noun becomes a complete contextual pair once the noun is supplied. These entries are also retained for semantic review. The earlier manifests remain historical; later manifest groups supersede their listed keys.

## Completion-stage refinements and repairs

The final inventory pass uses explicit expression specifications rather than a universal rule that every matching ending is a suffix. It can extend earlier groups with a displaced case ending, negative, relative marker, or postposition; the earlier recorded roles are retained where appropriate. Non-adjacent expression origins and larger phrase redistributions are recorded in `remaining-alignment-changes.json`.

An inherited parenthesis may already surround genuine grammatical material, such as `(ma)`, `(lar)`, or `(den)`. These are reinterpreted only in individually specified cases, with `origin_normalization` or an explicit repair reason. Other explanatory notes remain in square brackets. The Kâbe and köleler notes, for example, are preserved where their expressions are reassembled.

Completing a key sometimes requires a genuine correction. The previously deferred `2:48:4` is now supplied through complementary views of `yarar sağlamaz`, replacing an inherited punishment/passive expression that did not match the avail predicate. The contiguous displacement at `2:267:17–29` is corrected with explicit origin records, rather than copying the wrong neighboring values into the missing slots. Compound-name repairs include `Ruhu'l-Kudüs` and `Zülkarneyn`. The kinship rendering at `42:23` follows the supplied English reference and is explicitly marked as an interpretive repair; it is not presented as a ruling on all tafsir interpretations.

The combined `linguistic-review.json` carries current values and historical concerns forward. Every context-only view and every lexical/phrase revision is retained for further semantic scrutiny. Empty `alignment-pending.json` means that no structural keys are absent; it does not mean that semantic review has ended.
