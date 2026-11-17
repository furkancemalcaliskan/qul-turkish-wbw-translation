"""Resolve confirmed old round-parenthesis lexical concatenations."""
import argparse
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b = ReviewBatch("semantic-review-019", "Resolve four confirmed boundary findings from the full spelling audit, including explanatory round parentheses inherited from the original data. Do not infer errors from mere substrings inside legitimate words such as vahyetmediğimiz.")
    if b.exists:
        validate()
        return
    b.change("23:14-alaka-inflection", {"23:14:4": "alakaya", "23:14:6": "alakayı"}, "Alaka and the former parenthesized embriyo were alternative lexical descriptions, not parts of one Turkish word. Retain the original Arabic-derived noun alaka; apply its dative alakaya and accusative alakayı according to the existing object/result construction. Do not attach the ending to an invented alakaembriyo stem or assert a new biological interpretation.")
    for key in ["41:17:2", "7:73:2"]:
        b.change(key + "-tribal-name-boundary", {key: b.before[key].replace("Semud(", "Semud (")}, "Restore the space between the proper name Semud and its contextual kavim noun; preserve all existing source content, suffixes and conjunctions. This is the same noun-phrase boundary as the already reviewed Semud kavmine construction.")
    b.finish(args.apply)


if __name__ == "__main__":
    main()
