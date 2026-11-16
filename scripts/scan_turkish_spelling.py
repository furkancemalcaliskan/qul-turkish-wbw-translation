"""Inventory spelling candidates without changing either translation."""
import collections
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "turkish-wbw-translation.json").read_text(encoding="utf-8"))
patterns = [
    r"(?<![\w'])\b(?:yanlız|yalnış|herkez|birşey\w*|herşey\w*|hiç bir|pekçok|bir çok|bir kaç|süphesiz|şübhe\w*|muhakkakki|tabiiki|yada|havyan\w*|Rabbler\w*)\b|Rabb'",
    r"\s{2,}|^\s|\s$",
    r"\b\w*(?:ğğ|ıı|üü|şş|çç|jj|vvv)\w*",
]
for pattern in patterns:
    print("PATTERN", pattern)
    for key, value in data.items():
        if re.search(pattern, value):
            print(key, value)
words = collections.Counter(re.findall(r"[^\W\d_]+", " ".join(data.values())))
rare = sorted(word for word, count in words.items() if count == 1)
(ROOT / "reports/spelling-scan-vocabulary.txt").write_text("\n".join(rare) + "\n", encoding="utf-8")
print("RARE WORDS", len(rare))
