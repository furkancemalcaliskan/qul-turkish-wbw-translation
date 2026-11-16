"""Explicit construction repairs discovered during the grammar review."""
from alignment_common import render

def construction_cases():
    groups = []
    def add(before, parts, reason):
        members = list(before)
        groups.append({"members": members, "before": before,
                       "parts": [{"text": text, "role": role} for text, role in parts],
                       "after": {key: render([{"text": text, "role": role} for text, role in parts], key) for key in members},
                       "reason": reason})
    for verse, first, noun, ending in [
        ("50:7", 8, "çift", "ten"), ("31:10", 24, "çift", "ten"),
        ("27:23", 6, "şey", "den"), ("28:75", 2, "ümmet", "ten"),
        ("27:83", 3, "ümmet", "ten"),
    ]:
        relation, quantifier, head = [f"{verse}:{first+i}" for i in range(3)]
        add({relation: "her-"+ending, quantifier: "her", head: noun+ending},
            [("her", quantifier), (" ", "context"), (noun, head), (ending, relation)],
            "Replace an isolated, incorrectly attached suffix with complementary views of the retained quantified ablative phrase.")
    add({"97:3:4": "bin-dan", "97:3:5": "bin", "97:3:6": "ay"},
        [("bin", "97:3:5"), (" ", "context"), ("ay", "97:3:6"), ("dan", "97:3:4")],
        "Attach the comparative ablative to the head of bin ay rather than the numeral alone.")
    add({"7:20:15": "(-tan)", "7:20:16": "şu", "7:20:17": "ağaç(tan)"},
        [("şu", "7:20:16"), (" ", "context"), ("ağaç", "7:20:17"), ("tan", "7:20:15")],
        "Give the existing ablative an explicit demonstrative-noun context without duplicating the expression.")
    for verse, first, left, right in [("23:20", 3, "Tur-i", "Sina"), ("48:25", 5, "Mescid-i", "Haram")]:
        relation, first_name, second_name = [f"{verse}:{first+i}" for i in range(3)]
        add({relation: left+"-dan", first_name: left, second_name: right+"'dan"},
            [(left, first_name), (" ", "context"), (right, second_name), ("'dan", relation)],
            "Attach the proper-name ablative after the complete compound; preserve the inherited compound-name spelling.")
    add({"53:59:1": "bu-den mi?", "53:59:2": "bu", "53:59:3": "söze"},
        [("bu", "53:59:2"), (" ", "context"), ("söz", "53:59:3"), ("den", "53:59:1"), (" mi?", "53:59:1")],
        "Restore the ablative and interrogative in bu sözden mi; Arabic 53:59:1 includes the question particle and preposition. The old dative söze conflicts with that construction.")
    add({"21:75:5": "-Salihler-den idi", "21:75:6": "ve Nuh'u da-Salihler"},
        [("salihler", "21:75:6"), ("den idi", "21:75:5")],
        "Remove displaced ve Nuh'u da, which already correctly opens 21:76:1 and is absent from the source wording of 21:75. Preserve the retained salihlerden idi predicate in complementary views.")
    add({"26:86:4": "-dandır", "26:86:5": "(sapıklar)dan(dır)", "26:86:6": "sapıklar(dan)dır"},
        [("sapıklar", "26:86:6"), ("dan", "26:86:5"), ("dır", "26:86:4")],
        "Give the copular and ablative source positions distinct contributions to the retained sapıklardandır expression. This repairs display ownership; it does not adjudicate the inherited tense interpretation of Arabic kana.")
    groups.append({"members": ["16:99:3"], "before": {"16:99:3": "o(şeyta)nın"},
                   "after": {"16:99:3": "onun [şeytanın]"},
                   "reason": "Repair the malformed possessor pronoun and complete its inherited explanatory noun. Use square brackets for the explanation, keeping alignment parentheses distinct."})
    add({"80:18:1": "hangi-den?", "80:18:2": "(hangi)", "80:18:3": "hangi"},
        [("hangi", "80:18:2"), (" ", "context"), ("şey", "80:18:3"), ("den", "80:18:1")],
        "Restore the missing lexical head şey at Arabic shay'in / English thing, retain hangi for the interrogative, and attach the ablative to the complete phrase. Hangi supplies the question meaning without standalone punctuation in these fragments.")
    add({"22:28:13": "yürüyen-dan", "22:28:14": "yürüyen", "22:28:15": "hayvanların"},
        [("yürüyen", "22:28:14"), (" ", "context"), ("hayvanlar", "22:28:15"), ("dan", "22:28:13")],
        "Repair the incomplete genitive as an ablative phrase governed by min, retaining the inherited lexical paraphrase yürüyen hayvanlar. This is a case/display repair, not certification of that paraphrase's lexical precision.")
    add({"46:28:5": "başka-tan", "46:28:6": "başka", "46:28:7": "Allah'tan"},
        [("Allah", "46:28:7"), ("'tan", "46:28:5"), (" ", "context"), ("başka", "46:28:6")],
        "Redistribute Allah'tan başka across min / duni / Allah, preserving Turkish word order and avoiding a suffix incorrectly attached to başka.")
    add({"39:47:13": "kötü-dan (kurtulmak için)", "39:47:14": "kötü", "39:47:15": "azabı"},
        [("kötü", "39:47:14"), (" ", "context"), ("azap", "39:47:15"), ("tan", "39:47:13"), (" [kurtulmak için]", "context")],
        "Correct the case-governed phrase as kötü azaptan and preserve the inherited explanatory purpose wording in square brackets. The source positions are min / su'i / al-adhabi; the inherited adjective paraphrase is retained rather than replaced with a new lexical interpretation.")
    add({"2:112:15": "ve yoktur", "2:112:16": "onlara", "2:112:17": "üzülmek"},
        [("ve ", "2:112:15"), ("onlar", "2:112:16"), (" ", "context"), ("üzül", "2:112:17"), ("mez", "2:112:15"), ("ler", "2:112:17")],
        "Replace the malformed existential/infinitive construction with the negative finite predicate ve onlar üzülmezler. The source has conjunction/negation, subject hum, and plural finite yahzanuna, not a dative subject or an infinitive: https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=112.")
    groups.append({"members": ["79:24:3"], "before": {"79:24:3": "sizi Rabbinizim"},
                   "after": {"79:24:3": "sizin Rabbinizim"},
                   "reason": "Restore the genitive possessor sizin before Rabbinizim. Preserve the valid first-person predicative ending -im; do not replace it with the superficially similar genitive Rabbinizin."})
    return groups
