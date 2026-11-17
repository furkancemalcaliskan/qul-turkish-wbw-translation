"""Check notation and high-confidence spelling findings across every Turkish value.

This is a bounded orthographic audit, not a Turkish grammar parser or a claim
that all remaining words and translation choices are correct.
"""
import json
import re
from collections import Counter
from report_store import ROOT, STATE, VALIDATION, load, save
from semantic_review import digest


def main():
    turkish = load(ROOT / "turkish-wbw-translation.json")
    state = load(STATE)
    rules = {
        "square_delimiters": r"[\[\]]",
        "user_reported_agreement_and_possessive": r"gücümüzün yetmediğimiz|\bakitlerizi\b",
        "confirmed_misspellings": r"\b(?:şüket\w*|öc|gurup|deki|yanlız|yalnış|herkez)\b|ıyle|şartiyle",
        "incorrect_negative_future": r"mıyacak|mıyacağ|miyecek|miyeceğ",
        "accidental_lexical_concatenations": r"nutfesperm|alakaembriyo|sıkışanbulut|karıştıranortak|Semudkavmin|süseşya|kenthalkı|cumartesiyasak|gerçeki",
        "duplicate_conjunction": r"\bve\s+ve\b",
        "joined_concessive": r"\bolsalarda\b|\bolselerde\b",
        "joined_question_candidates": r"\b\w+m[ıiuü](?:s[ıiuü]n(?:[ıiuü]z)?|y[ıiuü]m|y[ıiuü]z)?\?",
    }
    findings = []
    for key, value in turkish.items():
        surface = value.replace("(", "").replace(")", "")
        for rule, pattern in rules.items():
            if re.search(pattern, surface):
                findings.append({"key": key, "rule": rule, "turkish": value})
    notation = state["batches"]["semantic-review-012"]
    for group in notation["groups"]:
        for key, before in group["before"].items():
            assert group["after"][key] == before.translate(str.maketrans("", "", "[]"))
    # Food nouns and legitimate Turkish reduplications must survive a strict scan.
    assert turkish["2:61:7"] == "yemeğ(e)"
    assert turkish["33:53:13"] == "yemeğ(e)"
    assert turkish["19:94:4"] == "bir bir"
    assert turkish["72:28:13"] == "bir bir"
    result = {
        "scope": "All current values scanned against the explicit bounded patterns below; findings require contextual review. Not exhaustive grammar or semantic certification.",
        "values_scanned": len(turkish),
        "turkish_sha256": digest(turkish),
        "patterns": rules,
        "findings": findings,
        "findings_by_rule": dict(Counter(row["rule"] for row in findings)),
        "square_delimiter_removal_values": notation["summary"]["changed_values"],
        "initial_delimiter_removal_preserved_contents_and_round_parentheses": True,
        "subsequent_boundary_and_spelling_batches": [name for name in state["batches"] if int(name.rsplit("-", 1)[1]) >= 13],
        "distinctions_checked": ["verbal yemeyi versus food-noun yemeği", "interrogative particle versus person suffix", "concessive da versus locative suffix", "legitimate reduplication versus duplicate conjunction", "source-context parentheses versus explanatory square delimiters"],
    }
    validation = load(VALIDATION)
    validation["turkish_spelling_follow_up"] = result
    save(VALIDATION, validation)
    print(json.dumps({"values_scanned": len(turkish), "findings": findings, "square_delimiters": sum("[" in value or "]" in value for value in turkish.values())}, ensure_ascii=False, indent=2))
    assert not findings, "Review the recorded candidates before claiming this bounded audit passed."


if __name__ == "__main__":
    main()
