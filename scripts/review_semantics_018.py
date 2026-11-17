"""Resolve the remaining confirmed conjunction and numeral duplications."""
import argparse
from semantic_review import ReviewBatch, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    b = ReviewBatch("semantic-review-018", "Final confirmed findings from the complete repeated-token and numeral-annotation scans. Preserve valid Turkish reduplications such as ayrı ayrı and bile bile.")
    if b.exists:
        validate()
        return
    for key in ["63:8:13", "42:13:17"]:
        assert b.before[key].startswith("ve ve ")
        b.change(key + "-duplicate-conjunction", {key: b.before[key][3:]}, "Remove one accidentally repeated ve. The Arabic source and English gloss contain one conjunction; the following noun, case and referent remain unchanged. Do not remove legitimate Turkish reduplications elsewhere.")
    b.phrase("5:12:9-twelve", [("on", "5:12:10"), (" ", None), ("iki", "5:12:9")], "The complete numeral-annotation scan found one further pair of duplicated explanatory views: iki (on iki) / on (on iki). Use complementary views of on iki, assigning two to the first Arabic token and ten to the second, just as at the already reviewed 7:160 locations. No numeric meaning is changed.")
    b.finish(args.apply)


if __name__ == "__main__":
    main()
