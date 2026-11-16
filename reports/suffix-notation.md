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
