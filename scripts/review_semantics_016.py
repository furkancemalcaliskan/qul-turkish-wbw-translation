"""Separate interrogative particles and repair a confirmed missing consonant."""
import argparse
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b = ReviewBatch("semantic-review-016", "Review all joined interrogative particles detected after reconstructing Turkish surfaces without alignment parentheses. Separate mı/mi/mu/mü while retaining their person endings; repair şüket to şükret in the verified gratitude clause.")
    if b.exists:
        validate()
        return
    for first, second, stem, question in [
        ("67:3:15", "67:3:16", "görüyor", "musun"),
        ("69:8:1", "69:8:2", "görüyor", "musun"),
        ("61:10:4", "61:10:5", "size göstereyim", "mi"),
        ("47:18:1", "47:18:2", "bekliyorlar", "mı"),
        ("79:18:2", "79:18:3", "ister", "misin"),
        ("83:36:1", "83:36:2", "cezalandılar", "mı"),
        ("19:65:9", "19:65:10", "biliyor", "musun"),
        ("26:72:2", "26:72:3", "onlar sizi işitiyorlar", "mı"),
        ("26:93:4", "26:93:5", "size yardım ediyorlar", "mı"),
        ("19:98:6", "19:98:7", "hissediyor", "musun"),
        ("26:221:1", "26:221:2", "size haber vereyim", "mi"),
    ]:
        b.phrase(first + "-question-spacing", [(stem, second), (" ", None), (question, first), ("?", None)], "Turkish interrogative mı/mi/mu/mü is written separately from the preceding word; personal endings stay attached to the particle. Preserve the existing action, person, polarity and interrogative source allocation. The question mark is contextual punctuation, not a lexical translation.")
    values = {
        "90:8:1": "(biz ver)me(dik mi?)", "90:8:2": "biz ver(me)dik mi?",
        "39:71:15": "(gel)me(di mi?)", "39:71:16": "gel(me)di mi?",
        "56:62:5": "(düşünüp ibret al)maz (mısınız?)", "56:62:6": "düşünüp ibret al(maz mısınız?)",
        "56:70:5": "(şükret)mez (misiniz?)", "56:70:6": "şükret(mez misiniz?)",
    }
    for key, value in values.items():
        b.change(key + "-negative-question-spacing", {key: value}, "Separate the interrogative particle from the preceding negative verb while preserving the negative source contribution and existing person/tense. At 56:70, restore the missing r in şükret-, supported by Arabic tashkurun and English grateful; do not confuse gratitude with another action.")
    b.references.append({"url": "https://tdk.gov.tr/icerik/yazim-kurallari/soru-eki-mi-mi-mu-munun-yazilisi/", "use": "Turkish interrogative-particle orthography; source meanings are checked against immutable local Arabic/English."})
    b.finish(args.apply)


if __name__ == "__main__":
    main()
