"""Read original Arabic beside source English and current Turkish by location."""
import argparse
import json
import re
import sys

from audit_resources import MANIFEST, RESOURCES, ROOT, inventory, read

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("location", help="surah:ayah for the whole ayah, or surah:ayah:word for nearby words")
    parser.add_argument("--radius", type=int, default=2, help="Neighboring words around a specific word (default: 2)")
    args = parser.parse_args()
    assert re.fullmatch(r"[1-9]\d*:[1-9]\d*(?::[1-9]\d*)?", args.location), "Invalid location."
    assert args.radius >= 0
    baseline = read(MANIFEST)["files"]
    assert inventory() == baseline, "Resource hashes or inventory changed."
    arabic = read(RESOURCES / "arabic/qpc-hafs-word-by-word.json")
    english = read(RESOURCES / "english/english-wbw-translation.json")
    turkish = read(ROOT / "turkish-wbw-translation.json")
    parts = list(map(int, args.location.split(":")))
    chapter, verse = parts[:2]
    records = []
    for location, word in arabic.items():
        surah, ayah, position = map(int, location.split(":"))
        if (surah, ayah) != (chapter, verse):
            continue
        if len(parts) == 3 and abs(position-parts[2]) > args.radius:
            continue
        records.append({"location": location, "arabic": word["text"], "source_english": english.get(location),
                        "current_turkish": turkish.get(location),
                        "translation_location_present": location in english})
    assert records, "No matching Arabic locations."
    assert len(parts) == 2 or args.location in arabic, "Requested word location does not exist."
    assert inventory() == baseline, "Resource bytes changed during reading."
    records.sort(key=lambda record: int(record["location"].split(":")[2]))
    print(json.dumps(records, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
