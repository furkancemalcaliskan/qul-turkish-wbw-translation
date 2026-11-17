"""Reread delimiter boundaries and common-word orthographic consistency."""
import argparse
import re
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b = ReviewBatch("semantic-review-014", "Second reading of all distinct expressions formerly containing square brackets; repair duplicate appositions and agreement without adding a second annotation system. Complete selected capitalization-preserving common-word spelling corrections.")
    if b.exists:
        validate()
        return
    values = {
        "91:3:2": "(güneşi ortaya çıkar)dığında", "91:3:3": "güneşi ortaya çıkar(dığında)",
        "5:3:26": "ve (kısmet ara)ma(nız)", "5:3:27": "(ve) kısmet ara(ma)nız",
        "74:8:3": "(Sur)'a", "74:8:4": "Sur('a)",
        "69:11:6": "(akıp giden gemi)de", "69:11:7": "akıp giden gemi(de)",
        "28:12:7": "(size göstereyim) mi?", "28:12:8": "size göstereyim (mi?)",
        "28:12:9": "(halkını)", "28:12:10": "halkını",
        "3:30:16": "(onunla)", "3:30:18": "onun arasında",
        "11:37:5": "(bana hitap et)me", "11:37:6": "bana hitap et(me)",
        "11:57:7": "onunla",
        "38:58:2": "(o azaba benzer)", "38:58:3": "o azaba benzer",
        "18:90:13": "(güneşe) karşı", "18:90:14": "güneşe (karşı)",
        "16:99:3": "şeytanın",
        "17:108:5": "(vaadi)", "17:108:6": "vaadi",
        "2:256:21": "onun için",
        "5:11:11": "(uzat)ma(ya)", "5:11:12": "uzat(ma)ya",
        "24:22:7": "(bir şey verme)meye", "24:22:8": "bir şey verme(meye)",
        "2:237:23": "(sizin affet)me(niz)", "2:237:24": "sizin affet(me)niz",
        "2:265:9": "(kendileri)ndeki (imanı)", "2:265:10": "kendileri(ndeki imanı)",
        "4:176:15": "onundur",
        "4:176:22": "(mevcut) değil(se)", "4:176:23": "mevcut (değilse)", "4:176:24": "onun",
        "2:191:5": "(Mekke denilen yer)den", "2:191:6": "Mekke denilen yer(den)",
        "46:17:6": "siz bana vadediyor musunuz?",
        "19:11:4": "(mabet)ten", "19:11:5": "mabet(ten)",
        "3:96:4": "(mabet olarak) kurulan",
        "33:35:6": "taate devam eden erkekler", "33:35:7": "ve taate devam eden kadınlar",
        "4:155:14": "hayır fakat",
    }
    explanations = {
        "91:3": "The old onu [güneşi] apposition became two adjacent accusative objects. Keep the existing explicit sun referent once, with the same temporal/source split; no new pronoun interpretation is introduced.",
        "5:3": "The old bracketed şans was an alternative gloss for kısmet. Retain kısmet aramanız once, with the existing infinitive/source allocation; the following divining-arrows phrase is unchanged.",
        "74:8": "Remove the duplicate boruya apposition: Sur'a already expresses to the trumpet. Preserve the source relation and lexical noun separately.",
        "69:11": "Place the locative on the final noun of akıp giden gemide, not on the participle before a detached gemi. Preserve the existing sailing-ship description.",
        "28:12": "Separate the interrogative particle mi from the finite verb. Remove duplicate halkını aile apposition; bir ev halkını still expresses a household. The source preposition is absorbed by Turkish göstermek valency and remains a documented contextual view.",
        "3:30": "Remove duplicate pronoun/explanatory-noun appositions. Turkish kendisiyle onun arasında already coordinates the two terms through -yle; an extra ve is not required. The inherited referent is unchanged.",
        "11:37": "Remove the redundant explanatory dua from hitap dua etme. Arabic address Me and English address Me support bana hitap etme without an unrelated second object.",
        "11:57": "Retain onunla once instead of juxtaposing its earlier explanatory mesajla. The carried-message referent remains the preceding şeyi/gönderildiğim construction.",
        "38:58": "Use demonstrative o before the declined noun azaba: o azaba benzer. The old ona azaba combined two dative appositions incorrectly.",
        "18:90": "Retain the already explicit sun referent once instead of the juxtaposed ona güneşe; preserve the karşı source contribution.",
        "16:99": "Retain the explicit existing possessor şeytanın once, rather than juxtaposing two genitives onun şeytanın. Arabic/English pronoun referent remains Satan.",
        "17:108": "Vaadi and sözü were alternative noun glosses. Retain vaadi once; the source copula remains absorbed and contextual, not converted to a new independent claim.",
        "2:256": "Retain onun için from the source pronominal relation; remove the former explanatory kulpun genitive, which was ungrammatical before için. The handhold referent in the preceding words is unchanged.",
        "5:11": "Standardize the infinitive dative to uzatmaya and remove the detached explanatory saldırmaya duplicate. Arabic stretch and English stretch preserve the original action and the following hands object.",
        "24:22": "Use the standard negative infinitive dative vermemeye. Keep the inherited oath not to give and the existing distribution of infinitive versus lexical contribution.",
        "2:237": "Remove the detached explanatory erkekler before sizin affetmeniz; the explicit second-person plural possessor remains. This does not newly adjudicate the debated identity of the preceding marriage-knot holder.",
        "2:265": "Repair kendilerindekini imanı to kendilerindeki imanı: the accusative belongs to imanı, not its preceding modifier. Preserve the inherited inner-faith reading and expose -ndeki in the relation view.",
        "4:176": "Use grammatical pronouns onundur/onun and remove misplaced duplicate kız kardeşinin from the negative predicate; the female sibling antecedent is already explicit. Inheritance fractions and conditions are unchanged.",
        "2:191": "Link the inherited explanatory place name and noun grammatically as Mekke denilen yer instead of juxtaposing yer Mekke. Preserve both original referents and the ablative role.",
        "46:17": "Repair the inherited promise-question spelling and vowel harmony as vadediyor musunuz; retain the second-person plural addressee and present progressive aspect.",
        "19:11": "Standard Turkish common noun mabet takes the ablative mab et + ten (written mabetten), not the transcription ma'bedden; preserve the same place-of-worship meaning.",
        "3:96": "Normalize the common noun ma'bed to mabet without changing the established-house meaning.",
        "33:35": "Remove the transcription apostrophe from the common noun taat in its dative taate; the existing obedience meaning is unchanged.",
        "4:155": "Remove a stray terminal apostrophe after fakat; it is neither a proper-name suffix nor a quotation delimiter.",
    }
    for key, value in values.items():
        b.change(key + "-boundary-reread", {key: value}, explanations[key.rsplit(":", 1)[0]])
    for key, before in b.before.items():
        if key in values:
            continue
        value = before
        for old, new in [("Mü'min", "Mümin"), ("Ni'met", "Nimet"), ("Mu'cize", "Mucize"), ("Sa'at", "Saat"), ("mü'mi", "mümi")]:
            value = value.replace(old, new)
        # Explicitly observed back-vowel nouns had an inherited front-vowel spelling.
        value = value.replace("oklariyle", "oklarıyla")
        if value != before:
            b.change(key + "-capitalization-preserving-spelling", {key: value}, "Complete the same reviewed common-word orthographic rules while preserving uppercase initials, proper-name suffixes and round-parenthesis boundaries. Correct oklariyle to oklarıyla; this is not a lexical translation change.")
    b.finish(args.apply)


if __name__ == "__main__":
    main()
