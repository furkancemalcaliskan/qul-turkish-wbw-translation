"""Build QUL-compatible release copies without rewriting working JSON or resources."""
import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path

from audit_resources import MANIFEST, RESOURCES, inventory, read
from report_store import ROOT

TABLE_SQL = "CREATE TABLE word_translation (surah_number INTEGER, ayah_number INTEGER, word_number TEXT, text TEXT)"
JSON_NAME = "turkish-wbw-translation.json"
DB_NAME = "turkish-wbw-translation.db"
PROJECT = "qul-turkish-wbw-translation"
REPOSITORY = "https://github.com/furkancemalcaliskan/qul-turkish-wbw-translation"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_database(path):
    """Never open a reference or inspected database in writable mode."""
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        connection.execute("PRAGMA query_only=ON")
        check(connection.execute("PRAGMA integrity_check").fetchall() == [("ok",)], "SQLite integrity check failed")
        schema = connection.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name").fetchall()
        check(schema == [("table", "word_translation", TABLE_SQL)], "Unexpected QUL SQLite schema")
        check(connection.execute("PRAGMA user_version").fetchone() == (0,), "Unexpected database user_version")
        check(connection.execute("PRAGMA application_id").fetchone() == (0,), "Unexpected database application_id")
        result = {}
        for surah, ayah, word, text in connection.execute("SELECT surah_number,ayah_number,word_number,text FROM word_translation"):
            check(type(surah) is int and type(ayah) is int and type(word) is str and type(text) is str, "Wrong SQLite storage types")
            key = f"{surah}:{ayah}:{word}"
            check(key not in result, f"Duplicate database location: {key}")
            result[key] = text
        return result
    finally:
        connection.close()


def validate_translation(data, english):
    check(list(data) == list(english) and len(data) == 83665, "Turkish reference keys/order differ")
    for key, value in data.items():
        check(bool(re.fullmatch(r"[1-9]\d*:[1-9]\d*:[1-9]\d*", key)), f"Invalid location: {key}")
        check(isinstance(value, str) and bool(value) and value == value.strip(), f"Invalid translation: {key}")
        check("[" not in value and "]" not in value, f"Forbidden square delimiter: {key}")
        level = 0
        for char in value:
            if char == "(":
                level += 1
            elif char == ")":
                level -= 1
            check(level >= 0, f"Unbalanced parenthesis: {key}")
        check(level == 0, f"Unbalanced parenthesis: {key}")
    markers = {key: value for key, value in english.items() if re.fullmatch(r"\(\d+\)", value)}
    check(len(markers) == 6236 and all(data[key] == value for key, value in markers.items()), "Ayah-number markers differ")


def compact(data):
    # Original QUL JSON uses raw UTF-8, no separator whitespace and no newline.
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def build_database(source, destination, data):
    """Copy the original, then update existing rows and insert missing locations."""
    original = read_database(source)
    check(not original.keys() - data.keys(), "Source DB has locations absent from reviewed JSON")
    shutil.copyfile(source, destination)
    connection = sqlite3.connect(destination)
    try:
        with connection:
            rowids = {f"{surah}:{ayah}:{word}": rowid for rowid, surah, ayah, word in connection.execute("SELECT rowid,surah_number,ayah_number,word_number FROM word_translation")}
            updates, inserts = [], []
            for key, text in data.items():
                surah, ayah, word = key.split(":")
                if key in original:
                    if original[key] != text:
                        updates.append((text, rowids[key]))
                else:
                    inserts.append((int(surah), int(ayah), word, text))
            connection.executemany("UPDATE word_translation SET text=? WHERE rowid=?", updates)
            connection.executemany("INSERT INTO word_translation (surah_number,ayah_number,word_number,text) VALUES (?,?,?,?)", inserts)
    finally:
        connection.close()
    check(read_database(destination) == data, "Built SQLite does not exactly match reviewed JSON")


def verify_artifacts(directory, data):
    check((directory / JSON_NAME).read_bytes() == compact(data), "Release JSON is not the canonical minified UTF-8 object")
    check(read(directory / JSON_NAME) == data, "Release JSON values differ")
    check(read_database(directory / DB_NAME) == data, "Release database values differ")


def ensure_output_directory(path):
    """Keep generated files outside sources, reports and the repository root."""
    path = path.resolve()
    check(path != ROOT, "Release output must not be the repository root")
    for protected in [RESOURCES, ROOT / "reports", ROOT / "scripts", ROOT / "tests", ROOT / ".git", ROOT / ".github"]:
        check(path != protected and protected not in path.parents and path not in protected.parents, f"Protected output directory: {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--version", default="snapshot")
    parser.add_argument("--update-root-db", action="store_true", help="Atomically replace only the root Turkish database with the verified copy.")
    args = parser.parse_args()
    check(bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}", args.version)), "Invalid release version")
    output = ensure_output_directory(args.output_dir)
    originals = inventory()
    check(originals == read(MANIFEST)["files"], "Original resource inventory/hash mismatch")
    protected = [ROOT / JSON_NAME]
    working_hashes = {path.name: sha(path) for path in protected}
    data = read(ROOT / JSON_NAME)
    english = read(RESOURCES / "english/english-wbw-translation.json")
    validate_translation(data, english)
    recorded = read(ROOT / "reports/validation.json").get("semantic_review", {})
    check(recorded.get("turkish_sha256") == working_hashes[JSON_NAME], "Run semantic_review.py to verify the current reviewed JSON first")
    root_db = ROOT / DB_NAME
    if not args.update_root_db:
        check(root_db.exists() and read_database(root_db) == data, "Root database is absent/stale; run with --update-root-db after reviewing the JSON")
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".qul-release-", dir=output.parent) as temporary:
        staging = Path(temporary)
        (staging / JSON_NAME).write_bytes(compact(data))
        build_database(RESOURCES / "turkish" / DB_NAME, staging / DB_NAME, data)
        verify_artifacts(staging, data)
        check(inventory() == originals, "Original resources changed during packaging")
        check(all(sha(path) == working_hashes[path.name] for path in protected), "Working JSON changed during packaging")
        if args.update_root_db:
            # Stage in the root filesystem so replacement is atomic on Windows too.
            handle, temp_name = tempfile.mkstemp(prefix=".turkish-wbw-", suffix=".tmp", dir=ROOT)
            os.close(handle)
            try:
                shutil.copyfile(staging / DB_NAME, temp_name)
                os.replace(temp_name, root_db)
            finally:
                Path(temp_name).unlink(missing_ok=True)
        check(read_database(root_db) == data, "Root SQLite/JSON agreement failed")
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=normal"], cwd=ROOT, text=True).strip())
        artifact_hashes = {name: sha(staging / name) for name in [JSON_NAME, DB_NAME]}
        manifest = {
            "project": PROJECT, "repository": REPOSITORY,
            "version": args.version, "git_revision": revision, "working_tree_dirty": dirty,
            "reference_keys": len(data), "ayah_markers": 6236,
            "working_json_sha256": working_hashes[JSON_NAME],
            "root_database_sha256": sha(root_db),
            "artifacts": {name: {"sha256": value, "bytes": (staging / name).stat().st_size} for name, value in artifact_hashes.items()},
            "original_resources": originals,
            "verification": {"json_sqlite_exact_agreement": True, "root_sqlite_exact_agreement": True, "qul_schema_preserved": True, "source_and_working_json_unchanged": True},
            "review_scope": "Recorded Arabic/English-led review and spelling/grammar follow-ups; not independent expert certification or an approved QUL publication.",
        }
        (staging / "release-manifest.json").write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        notes = f"""# {PROJECT}: {args.version}

Independent correction/completion of QUL Turkish WBW resource #99.
Repository: {REPOSITORY}
External contributions are currently closed; see CONTRIBUTING.md.

- {len(data):,} word-location entries, including 6,236 reference ayah markers.
- Minified UTF-8 flat JSON and exactly matching SQLite word_translation data.
- Original QUL schema and all immutable source downloads preserved.
- Parentheses show shared expressions/context; square delimiters are excluded.
- Build revision: {revision}; working tree dirty: {str(dirty).lower()}.

Read README.md, PROCESS.md and reports/ in the repository for provenance,
before/after decisions, notation, selected readings and verification limits.
This is not an approved QUL publication or independent expert certification.
The source licence page states that copyright information is unavailable;
attribution does not establish public-domain status or grant a dataset licence.

Source: https://qul.tarteel.ai/resources/translation/99/docs
Licence information: https://qul.tarteel.ai/resources/translation/99/licence
"""
        (staging / "RELEASE_NOTES.md").write_bytes(notes.encode("utf-8"))
        names = [JSON_NAME, DB_NAME, "release-manifest.json", "RELEASE_NOTES.md"]
        (staging / "SHA256SUMS").write_bytes("".join(f"{sha(staging / name)}  {name}\n" for name in names).encode("ascii"))
        for name in names + ["SHA256SUMS"]:
            os.replace(staging / name, output / name)
    verify_artifacts(output, data)
    check(inventory() == originals and all(sha(path) == working_hashes[path.name] for path in protected), "Protected input changed")
    print(json.dumps({"output_directory": str(output), "entries": len(data), "root_database_updated": args.update_root_db, "working_json_unchanged": True, "resources_unchanged": True, "artifact_hashes": artifact_hashes}, indent=2))


if __name__ == "__main__":
    main()
