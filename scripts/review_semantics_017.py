"""Repair demonstrative/context boundaries and multiword numeral spelling."""
import argparse
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b = ReviewBatch("semantic-review-017", "Final targeted boundary review: demonstratives before contextual nouns, separated concessive da, and multiword Turkish numerals. Do not alter correctly segmented pronoun suffixes such as o(ndan).")
    if b.exists:
        validate()
        return
    values = {
        "28:7:6": "onu emzir",
        "13:11:1": "o (insan)ın vardır",
        "18:34:2": "o (adam)ın",
        "41:53:10": "o (Kur'an)'ın",
        "22:55:7": "o (Kur'an)'dan",
        "4:55:4": "ona",
        "3:88:2": "o (lanet)in içinde",
        "17:105:2": "biz o (Kur'an)'ı indirdik",
        "6:160:6": "o (getirdiği)nin",
        "3:172:1": "O (müminler) ki",
        "2:213:22": "o (Kitap hakkı)nda",
        "2:170:15": "(ol)salar da mı?",
        "2:170:16": "ol(salar da mı?)",
    }
    for key, value in values.items():
        reason = "Separate the demonstrative from its contextual noun and keep the noun whole instead of concealing only an arbitrary interior substring. The existing referent and grammatical case are retained. This does not change the meaning of correctly segmented o(ndan)/o(nun) pronouns elsewhere."
        if key in ("28:7:6", "4:55:4"):
            reason = "Use the ordinary source pronoun with its existing case: onu emzir / ona. Remove the intrusive explanatory child/book noun that had produced Oçocuğunu/OHakKitabına. The Arabic/English pronoun and its inherited antecedent remain; no new referent is asserted."
        if key.startswith("2:170:"):
            reason = "Concessive da is a separate word after the conditional plural olsalar. Preserve conditional, plural subject and rhetorical question; do not treat the conjunction as a locative suffix."
        b.change(key + "-demonstrative-boundary", {key: value}, reason)
    for first, second in [("7:160:2", "7:160:3"), ("7:160:18", "7:160:19")]:
        b.phrase(first + "-twelve", [("on", second), (" ", None), ("iki", first)], "Turkish multiword numerals are separated: on iki. Replace the duplicate iki (oniki)/on (oniki) explanatory views with complementary source allocations of the same single numeral. Arabic first token contributes two, second token ten; preserve both locations and the value twelve.")
    b.phrase("74:30:2-nineteen", [("on", "74:30:3"), (" ", None), ("dokuz", "74:30:2")], "Write the multiword numeral on dokuz with a space. Arabic first token contributes nine and the second ten; preserve the existing source allocation and numeric meaning nineteen.")
    b.finish(args.apply)


if __name__ == "__main__":
    main()
