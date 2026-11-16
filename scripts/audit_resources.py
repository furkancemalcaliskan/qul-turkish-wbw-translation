"""Inspect immutable QUL sources; write audit records only outside resources."""
import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "resources"
MANIFEST = ROOT / "reports/resource-integrity.json"

def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate JSON key: {key}"
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)

def inventory():
    return {path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(RESOURCES.rglob("*")) if path.is_file()}

def rows(path, table):
    # Immutable, read-only SQLite avoids writes, journals, and WAL sidecars.
    with sqlite3.connect(path.resolve().as_uri()+"?mode=ro&immutable=1", uri=True) as connection:
        connection.execute("PRAGMA query_only=ON")
        assert connection.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        schema = connection.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
        assert schema, f"Missing table: {table}"
        columns = [row[1:3] for row in connection.execute(f'PRAGMA table_info("{table}")')]
        values = connection.execute(f'SELECT * FROM "{table}"').fetchall()
    return schema[0], columns, values

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initialize", action="store_true", help="Record the initial hashes if no manifest exists; never reset an existing manifest.")
    args = parser.parse_args()
    first = inventory()
    assert first, "No resource files found."
    if MANIFEST.exists():
        manifest = read(MANIFEST)
        assert first == manifest["files"], "Resource inventory or hashes changed; do not overwrite the baseline."
    else:
        assert args.initialize, "Initialize the resource integrity baseline explicitly."
        manifest = {"policy": "Immutable original QUL downloads. Never modify these files; update only release copies outside resources.",
                    "recorded_on": "2026-11-16", "files": first}
    en = read(RESOURCES / "english/english-wbw-translation.json")
    tr = read(RESOURCES / "turkish/turkish-wbw-translation.json")
    ar = read(RESOURCES / "arabic/qpc-hafs-word-by-word.json")
    assert all(re.fullmatch(r"[1-9]\d*:[1-9]\d*:[1-9]\d*", key) for key in en.keys() | tr.keys() | ar.keys())
    assert all(isinstance(value, str) and value for value in [*en.values(), *tr.values()])
    database_reports = {}
    for language, data in [("english", en), ("turkish", tr)]:
        path = RESOURCES / language / f"{language}-wbw-translation.db"
        schema, columns, values = rows(path, "word_translation")
        assert columns == [("surah_number", "INTEGER"), ("ayah_number", "INTEGER"), ("word_number", "TEXT"), ("text", "TEXT")]
        mapped = {}
        for surah, ayah, word, value in values:
            key = f"{surah}:{ayah}:{word}"
            assert key not in mapped
            assert isinstance(surah, int) and isinstance(ayah, int) and isinstance(word, str) and isinstance(value, str)
            mapped[key] = value
        assert mapped == data, f"JSON/SQLite mismatch: {language}"
        database_reports[language] = {"table": "word_translation", "schema": schema, "rows": len(values), "json_pairs_equal": True, "integrity_check": "ok"}
    schema, columns, values = rows(RESOURCES / "arabic/qpc-hafs-word-by-word.db", "words")
    assert [item[0] for item in columns] == ["id", "location", "surah", "ayah", "word", "text"]
    mapped = {}
    for identifier, location, surah, ayah, word, value in values:
        assert location not in mapped
        assert location == f"{surah}:{ayah}:{word}"
        mapped[location] = {"id": identifier, "location": location, "surah": str(surah), "ayah": str(ayah), "word": str(word), "text": value}
    assert mapped == ar, "Arabic JSON/SQLite mismatch."
    database_reports["arabic"] = {"table": "words", "schema": schema, "rows": len(values), "json_records_equal": True, "integrity_check": "ok"}
    initial_tr = json.loads(subprocess.check_output(["git", "show", "4503cdc:turkish-wbw-translation.json"], cwd=ROOT))
    assert tr == initial_tr
    initial_en = json.loads(subprocess.check_output(["git", "show", "4503cdc:english-wbw-translation.json"], cwd=ROOT))
    assert en == initial_en
    root_en = ROOT / "english-wbw-translation.json"
    root_en_equal = read(root_en) == en if root_en.exists() else None
    assert root_en_equal is not False
    assert not en.keys() - ar.keys()
    extras = []
    for key in sorted(ar.keys()-en.keys(), key=lambda item: tuple(map(int, item.split(":")))):
        surah, ayah, word = map(int, key.split(":"))
        previous = f"{surah}:{ayah}:{word-1}"
        extras.append({"location": key, "arabic": ar[key]["text"], "previous_location": previous,
                       "previous_arabic": ar[previous]["text"], "previous_english": en.get(previous),
                       "note": "The source English gloss combines after and what at the previous location. Preserve original keys and examine the two Arabic positions together; do not renumber or infer a missing Turkish key from this difference alone."})
    assert {item["location"] for item in extras} == {"2:181:4", "8:6:5", "13:37:9"}
    assert all(item["previous_english"] == "after what" for item in extras)
    assert inventory() == first, "Resource bytes changed during the read-only audit."
    if not MANIFEST.exists():
        MANIFEST.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    report = {"resource_hashes_unchanged": True, "resource_files": len(first), "database_checks": database_reports,
              "source_english_entries": len(en), "source_turkish_entries": len(tr), "source_arabic_entries": len(ar),
              "resource_turkish_equals_initial_pairs": True, "resource_english_equals_initial_pairs": True,
              "root_english_equals_source_pairs": root_en_equal, "arabic_only_locations": extras,
              "policy": "Resources are read-only. Publish updated root-level copies only after the linguistic work and release checks are complete."}
    (ROOT / "reports/resource-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["resource_hashes_unchanged", "resource_files", "source_english_entries", "source_turkish_entries", "source_arabic_entries"]}, indent=2))
    print("JSON/SQLite agreement and integrity checks passed for all three languages.")

if __name__ == "__main__":
    main()
