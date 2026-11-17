"""Remove square-bracket delimiters, preserving every enclosed character."""
import argparse
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    batch = ReviewBatch("semantic-review-012", "User-requested notation policy: remove square-bracket characters only; preserve their contents and every existing round parenthesis. This mechanical change makes no new semantic claim.")
    if batch.exists:
        validate()
        return
    for key, value in batch.before.items():
        if "[" in value or "]" in value:
            after = value.translate(str.maketrans("", "", "[]"))
            batch.change(key + "-square-delimiters", {key: after}, "Remove only U+005B and U+005D under the explicit user instruction. Enclosed text, spacing, punctuation and round-parenthesis source allocation are unchanged; do not turn explanatory material into a new alignment parenthesis.")
    batch.finish(args.apply)


if __name__ == "__main__":
    main()
