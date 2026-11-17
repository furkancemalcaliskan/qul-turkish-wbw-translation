"""Conservative Turkish spelling, agreement and delimiter-boundary corrections."""
import argparse
import re
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b = ReviewBatch("semantic-review-013", "Strict spelling follow-up requested by the user: explicit agreement corrections, standard spelling of selected common nouns, and individually reviewed word boundaries after square-delimiter removal. Preserve lexical meaning, source keys and round-parenthesis allocation; no unrestricted apostrophe deletion.")
    if b.exists:
        validate()
        return
    planned, reasons = {}, {}

    def put(key, value, reason):
        planned[key] = value
        reasons.setdefault(key, []).append(reason)

    explicit = {
        "5:1:5": ("akitleri(nizi)", "Repair missing ni in the inherited optional second-person plural possessive ending: akitlerinizi. The Arabic contracts noun has no possessive suffix; keep the contextual nizi parenthesized."),
        "2:286:35": ("(gücümüzün yet)me(diği)", "The embedded subject is gücümüz, third-person singular, so the relative predicate is yetmediği, not yetmediğimiz. Preserve negative-morpheme foregrounding."),
        "2:286:36": ("gücümüzün yet(me)diği", "Match the third-person subject gücümüz: yetmediği. Do not change the first-person plural possessor of güç."),
        "2:282:44": ("(güç yetire)me(yecek)", "Correct the negative future vowel: yetiremeyecek, not yetiremiyecek; preserve the source-role split."),
        "2:282:45": ("güç yetire(me)yecek", "Correct the negative future vowel without changing capacity, tense or source allocation."),
        "17:24:7": ("ve de ki", "Separate the quotative conjunction ki from the imperative de; Arabic wa-qul means and say."),
        "51:29:8": ("bir kocakarı", "The established compound for an old woman is kocakarı; do not reinterpret this as a large wife."),
        "26:171:2": ("bir kocakarı", "Correct the compound spelling for the Arabic old-woman noun; lexical meaning is retained."),
        "24:35:18": ("(bir ağacın yağı)ndan", "Correct the indefinite genitive construction: bir ağacın yağı, not bir ağacının yağı. Preserve the explanatory oil context and ablative source contribution."),
        "24:35:19": ("bir ağacın yağı(ndan)", "Match the indefinite genitive construction in the paired source allocation."),
        "33:53:37": ("(gerçeği söylemek)ten", "Apply regular consonant lenition gerçek + i -> gerçeği; preserve the existing explanatory speech context."),
        "33:53:38": ("gerçeği söylemek(ten)", "Correct gerçeki to gerçeği in the same shared expression."),
        "4:24:5": ("(geçen cariyeler)", "Restore the word boundary in geçen cariyeler after removal of the old explanatory brackets; the source pronoun remains contextual."),
        "4:24:6": ("geçen (cariyeler)", "Restore the space after geçen. Keep the contextual noun parenthesized rather than joining it to the verb."),
        "38:24:10": ("(ortaklar)ın", "The removed brackets previously contained an alternative lexical gloss, not a suffix: karıştıran[ortak]lar. Retain ortaklar, matching Arabic al-khulata and English partners; do not concatenate synonymous glosses."),
        "38:24:11": ("ortaklar(ın)", "Use the same source-supported partners noun and preserve the genitive allocation."),
        "78:14:2": ("(sıkışan bulutlar)dan", "Restore the space between the participle and its explanatory noun; this is not a compound word."),
        "78:14:3": ("sıkışan bulutlar(dan)", "Restore the corresponding word boundary without changing the existing cloud description."),
        "27:45:3": ("(Semud kavmin)e", "Restore the proper-name/noun boundary in Semud kavmine; keep the source dative highlighted."),
        "27:45:4": ("Semud kavmin(e)", "Restore the same proper-name/noun boundary in the paired value."),
        "33:55:19": ("(bulunan köleleri)", "Separate the participle and explanatory noun after delimiter removal. The relative source contribution remains contextual."),
        "33:55:20": ("bulunan (köleleri)", "Separate bulunan from the contextual noun; preserve the existing contextual possessive ending."),
        "33:62:4": ("(geçen milletler)", "Separate the participle and explanatory noun; retain the relative source token as context."),
        "33:62:5": ("geçen (milletler)", "Restore the boundary between geçen and milletler; do not concatenate the explanatory noun."),
        "34:43:14": ("(ol)duğ(u tanrılar)dan", "Restore the boundary between the relative ending and contextual noun tanrılar; do not change the inherited predicate or ablative allocation."),
        "34:43:15": ("ol(duğ)u tanrılar(dan)", "Restore the corresponding word boundary in the same relative expression."),
        "27:72:8": ("(acele et)tiğ(iniz azabın)", "Separate the relative participle from the contextual noun; soften azap to azab- before its vowel suffix."),
        "27:72:9": ("acele et(tiğ)iniz azabın", "Restore the same noun boundary in the paired source allocation."),
        "20:87:9": ("(süs eşyası)ndan", "Restore the established noun phrase süs eşyası after removing explanatory brackets."),
        "20:87:10": ("süs eşyası(ndan)", "Restore the same noun-phrase boundary without changing its ablative ending."),
        "4:154:14": ("(cumartesi yasakları)nı", "Separate cumartesi and its contextual noun yasakları; do not create a new compound spelling."),
        "4:154:15": ("cumartesi yasakları(nı)", "Restore the same noun-phrase boundary and preserve source-role allocation."),
        "7:163:2": ("(kent halkının durumu)ndan", "Restore the boundary in kent halkı, retaining the previously supplied contextual halkının durumu."),
        "7:163:3": ("kent halkının durumu(ndan)", "Restore the same noun-phrase boundary in the paired allocation."),
        "2:191:5": ("(yer Mekke)den", "Separate the original noun and explanatory place name rather than producing yerMekke. Both source-supported and previously explanatory text remain present."),
        "2:191:6": ("yer Mekke(den)", "Restore the same explanatory place-name boundary; preserve the ablative source allocation."),
        "20:11:2": ("o (ateşin yanı)na gelince", "Separate the demonstrative o from the contextual noun phrase. Do not treat text concealed by parentheses as a lexical suffix."),
        "20:121:2": ("o (ağaç)tan", "Separate the demonstrative from the contextual noun while retaining the source ablative ending."),
        "3:163:1": ("O (insanlar)", "Separate the pronoun and contextual explanatory noun; the old O(insa)nlar split cut the noun internally and foregrounded a meaningless fragment."),
        "2:282:86": ("onun süresine", "Repair the pronoun in the possessive construction: onun süresine, not onu süresine. Arabic ajalihi and English its term both support a possessor."),
        "40:74:10": ("biz tapıyor", "The adjacent source tokens already express değilmişiz. In the complete construction biz ... tapıyor değilmişiz, an additional negative tapmıyor reverses the denial. Restore the positive verb stem while retaining the adjacent negative auxiliary allocation."),
    }
    for key, (value, reason) in explicit.items():
        put(key, value, reason)

    # Bracketed lexical alternatives must not be concatenated into invented words.
    for left, right, noun, suffix in [
        ("22:5:14", "22:5:15", "nutfe", "den"),
        ("35:11:6", "35:11:7", "nutfe", "den"),
        ("53:46:1", "53:46:2", "nutfe", "den"),
        ("40:67:7", "40:67:8", "nutfe", "den"),
        ("36:77:6", "36:77:7", "bir nutfe", "den"),
        ("22:5:17", "22:5:18", "alaka", "dan"),
        ("40:67:10", "40:67:11", "alaka", "dan"),
    ]:
        reason = "The old square brackets enclosed a lexical explanation, not an orthographic suffix. Retain the existing Arabic-derived noun nutfe/alaka, remove the duplicated alternative gloss sperm/embriyo, and preserve the ablative split. This avoids inventing nutfesperm/alakaembriyo or asserting a new biological interpretation."
        put(left, "(" + noun + ")" + suffix, reason)
        put(right, noun + "(" + suffix + ")", reason)
    put("80:19:1", "(nutfe)den", "Retain the original nutfe noun and remove the redundant former bracketed sperm explanation, consistently with the other individually listed nutfe contexts.")
    put("7:136:4", "(deniz)de", "Replace the mechanically joined yemm + su glosses with deniz, the meaning of Arabic al-yamm and the supplied English sea in this context; preserve the locative split.")
    put("7:136:5", "deniz(de)", "Use the same source-supported sea noun in the paired locative allocation.")

    # Reviewed, bounded spelling rules for common Turkish words, never proper names.
    roots = {"ni'met": "nimet", "mu'cize": "mucize", "la'net": "lanet", "mü'min": "mümin",
             "ita'at": "itaat", "du'a": "dua", "da'vet": "davet", "sa'at": "saat",
             "şefa'at": "şefaat", "rü'ya": "rüya", "ma'zeret": "mazeret", "sür'at": "sürat",
             "te'minat": "teminat", "neş'e": "neşe", "te'vil": "tevil", "ta'bir": "tabir",
             "vak'a": "vaka", "kıt'a": "kıta", "ma'nen": "manen", "cür'et": "cüret",
             "kat'iyyen": "katiyen", "men'et": "menet", "men'ed": "mened", "men'ol": "menol",
             "şeri'at": "şeriat", "bi'at": "biat", "şa'ir": "şair", "na'ra": "nara"}
    for key, before in b.before.items():
        value = planned.get(key, before)
        original = value
        for old, new in roots.items():
            value = value.replace(old, new)
        value = re.sub(r"\böc\b", "öç", value)
        value = value.replace("ıyle", "ıyla").replace("şartiyle", "şartıyla")
        value = re.sub(r"\bgurup\b", "grup", value)
        value = re.sub(r"\bhala\b", "hâlâ", value)
        value = value.replace("sözkonusu", "söz konusu").replace("kızkardeş", "kız kardeş")
        value = value.replace("ta'kibederek", "takip ederek")
        value = value.replace("va'adle", "vaatle").replace("va'aded", "vaded")
        value = value.replace("va'det", "vadet").replace("va'ded", "vaded")
        value = value.replace("va'di", "vaadi").replace("va'dler", "vaatler")
        value = re.sub(r"\bva'd\b", "vaat", value)
        value = value.replace("vaadet", "vadet").replace("vaaded", "vaded")
        value = value.replace("vaadde", "vaatte").replace("vaad edilen", "vadedilen").replace("vaad eder", "vadeder")
        if value != original:
            put(key, value, "Apply only the explicitly listed common-word spelling rules: standard Turkish loanword spellings rather than internal transcription apostrophes; öç, -ıyla, şartıyla, grup, hâlâ, söz konusu, kız kardeş, takip ederek, and vaat/vadet- inflection. Proper-name apostrophes and translation meaning are preserved. Each resulting value is recorded separately; loanword modernization is orthographic, not a new Arabic lexical interpretation.")
    b.references.append({"url": "https://sozluk.gov.tr/?ara=vadetmek", "use": "TDK spelling of vadetmek; not a Quran translation source."})
    for key, value in planned.items():
        b.change(key + "-spelling-follow-up", {key: value}, " ".join(reasons[key]))
    b.finish(args.apply)


if __name__ == "__main__":
    main()
