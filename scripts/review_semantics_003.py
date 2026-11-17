"""Review explicitly selected anterior-time and copular constructions."""
import argparse
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    batch = ReviewBatch("semantic-review-003", "Explicit anterior-time expressions and selected general divine-attribute copulas, assessed by construction rather than isolated English words.")
    if batch.exists:
        validate()
        return
    retained_min = "3:4:1 3:164:21 4:164:5 6:28:7 6:84:9 6:158:27 7:155:15 7:173:6 8:71:7 10:74:16 11:109:14 12:6:18 12:64:10 15:27:3 19:7:10 19:9:10 28:12:4 28:48:18 30:4:6 33:15:5 34:53:4 40:34:4 40:67:24 51:46:3".split()
    for key in retained_min:
        assert batch.en[key].strip().lower() in {"from", "before", "before (this)"}
        batch.decide(key, "Min qabl is an anterior-time expression in this local clause. The inherited daha önce / [bundan] önce / öteden beri wording conveys anteriority; Turkish has no independent overt ablative on önce. Retain the context-only min view rather than inventing önceden as if it always had the same construction. This decision concerns the time relation, not all adjacent inherited wording.", retained=True)
    # The temporal expression in 4:136 does not name earlier recipients.
    batch.change("4:136-earlier-revelation", {"4:136:15": "(daha önce)", "4:136:16": "daha önce"},
                 "Min qablu means before/previously, not to those before. Remove the unsupported recipient plural/dative in daha öncekilere; the preceding book is the object of revelation.")
    batch.decide("4:136:15", "Restore anterior time without inventing earlier recipients; the min itself remains context-only because daha önce needs no separate suffix.")
    for left, right, pronoun, reason in [
        ("10:16:15", "10:16:16", "bu", "The attached pronoun points to this revelation in the preceding speech; retain it as bundan önce rather than an entirely unanchored daha önce."),
        ("17:107:11", "17:107:12", "bu", "The attached pronoun refers to this Quran, before which knowledge was granted. Bundan önce retains the pronominal anchor without claiming a new recipient."),
        ("27:42:11", "27:42:12", "on", "Qabliha explicitly contains a feminine pronominal complement. Ondan önce retains that source pronoun without deciding whether the comparison is to her person or her arrival."),
        ("30:49:8", "30:49:9", "bu", "The repeated min qablihi refers back to the sending-down event. Bundan önce preserves its pronominal anchor; it does not create a new period unrelated to the preceding clause."),
    ]:
        # 'on' is the oblique Turkish pronoun stem; 'bu' retains a demonstrative anchor.
        batch.phrase(left + "-pronoun", [(pronoun, right), ("ndan" if pronoun == "bu" else "dan", left), (" önce", right)], reason)
        batch.decide(left, reason)
    for left, right, stem, reason in [
        ("39:55:10", "39:55:11", "size gel", "An yatiyakum is a positive coming-to-you complement under before, not a separate negative predicate."),
        ("42:47:5", "42:47:6", "gel", "An yatiya is positive arrival under before. Turkish gelmeden önce is a temporal nominal construction, not a denial that the day will come."),
        ("58:3:13", "58:3:14", "birbirlerine dokun", "An yatamassa is dual reciprocal touching. Retain reciprocity and expose nominalization before the anterior-time expression."),
        ("58:4:9", "58:4:10", "birbirlerine dokun", "The repeated an yatamassa again has dual reciprocal scope; preserve it consistently with the preceding ayah."),
    ]:
        nominal, case = ("me", "den") if stem.endswith("gel") else ("ma", "dan")
        batch.phrase(left + "-temporal-nominal", [(stem, right), (nominal, left), (case, right)], reason + " The -ma/-me is a Turkish nominalizer; the temporal ablative is supplied by the wider before construction.")
        min_key = left.rsplit(":", 1)[0] + ":" + str(int(left.split(":")[-1]) - 2)
        batch.decide(min_key, reason + " Min qabl remains naturally expressed by önce without a second invented ablative.")
        for key in [left, right]:
            if any(entry["key"] == key and entry["status"] == "requires_semantic_review" for entry in batch.state["queue"]):
                batch.decide(key, reason)
    batch.change("48:23-earlier-time-spacing", {"48:23:6": "(öteden beri)", "48:23:7": "öteden beri"},
                 "Retain the established anterior-time idiom for min qabl, correcting its word spacing. No new case suffix is invented for min.")
    batch.decide("48:23:6", "Retain the contextual anterior-time interpretation while correcting the spacing of öteden beri.")
    # Each mapping was read alongside the original kana and its actual predicate.
    copulas = [
        ("4:1:26", "4:1:28", "gözetleyici", "dir"),
        ("4:17:17", "4:17:19", "bilen", "dir"),
        ("4:23:52", "4:23:53", "çok bağışlayan", "dır"),
        ("4:29:21", "4:29:23", "çok merhametli", "dir"),
        ("4:32:24", "4:32:27", "bilen", "dir"),
        ("4:33:15", "4:33:19", "şahit", "tir"),
        ("4:86:11", "4:86:15", "hesaplayan", "dır"),
        ("4:92:57", "4:92:59", "bilen", "dir"),
        ("4:94:36", "4:94:39", "haberdar", "dır"),
        ("4:96:5", "4:96:7", "bağışlayan", "dır"),
        ("4:104:19", "4:104:21", "bilen", "dir"),
        ("4:111:8", "4:111:10", "bilen", "dir"),
        ("4:127:38", "4:127:40", "bilen", "dir"),
        ("4:128:26", "4:128:29", "haberdar", "dır"),
        ("4:131:29", "4:131:31", "hiçbir şeye muhtaç olmayan", "dır"),
        ("4:134:11", "4:134:13", "işiten", "dir"),
        ("4:148:11", "4:148:13", "işiten", "dir"),
        ("17:25:10", "17:25:12", "bağışlayan", "dır"),
        ("17:30:9", "17:30:11", "haberdar", "dır"),
        ("17:96:8", "17:96:10", "haberdar", "dır"),
        ("19:47:8", "19:47:10", "çok lütufkâr", "dır"),
        ("33:2:9", "33:2:12", "haberdar", "dır"),
        ("33:54:8", "33:54:11", "bilen", "dir"),
        ("33:55:26", "33:55:30", "şahit", "tir"),
        ("35:45:23", "35:45:25", "gören", "dir"),
        ("48:11:33", "48:11:37", "haberdar", "dır"),
    ]
    for kana, predicate, stem, suffix in copulas:
        pieces = []
        if batch.ar[kana]["text"].startswith("و"):
            pieces.append(("ve ", kana))
        pieces += [(stem, predicate), (suffix, kana)]
        reason = "Here kana supports a general divine-attribute predication, not a past-only state that has ceased. Turkish expresses that predication with the nominal copula -dır/-dir; expose it at kana instead of copying an unrelated subject or prepositional phrase."
        if stem == "haberdar":
            reason += " Khabir describes awareness; haberdardır avoids the inherited haber almak wording suggesting acquisition of new information."
        if "muhtaç" in stem:
            reason += " Ghani is freedom from need, made explicit rather than a potentially financial sense of zengin."
        batch.phrase(kana + "-predication", pieces, reason)
        batch.decide(kana, reason)
    batch.change("48:11-what-you-do", {"48:11:35": "(yap)tık(larınızdan)", "48:11:36": "yap(tık)larınız(dan)"},
                 "Bima tamaluna is what you do, second-person plural, governed by awareness. Replace the inherited olduklarınızı / yapıyorlar mismatch with yaptıklarınızdan, in the haberdar construction.")
    # These adjacent constructions were explicitly seen but need their own decisions.
    batch.finish(args.apply)


if __name__ == "__main__":
    main()
