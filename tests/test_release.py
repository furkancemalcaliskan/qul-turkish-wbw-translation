"""Exercise release data-loss, schema, Unicode and protected-path failure modes."""
import hashlib
import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_release import TABLE_SQL, ROOT, build_database, compact, ensure_output_directory, read_database, validate_translation, verify_artifacts
from audit_resources import read


class ReleaseTests(unittest.TestCase):
    def test_update_add_and_preserve_source_schema_and_unicode(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source = folder / "source.db"
            with closing(sqlite3.connect(source)) as connection, connection:
                connection.execute(TABLE_SQL)
                connection.executemany("INSERT INTO word_translation VALUES (?,?,?,?)", [(1, 1, "1", "eski"), (1, 1, "2", "korunan")])
            before = hashlib.sha256(source.read_bytes()).digest()
            reviewed = {"1:1:1": "(Rableri)nden", "1:1:2": "korunan", "1:1:3": "şükür", "1:1:4": "(1)"}
            target = folder / "turkish-wbw-translation.db"
            build_database(source, target, reviewed)
            self.assertEqual(read_database(target), reviewed)
            self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), before)
            output = compact(reviewed)
            self.assertIn("şükür".encode("utf-8"), output)
            self.assertNotIn(b"\n", output)
            self.assertEqual(json.loads(output), reviewed)
            (folder / "turkish-wbw-translation.json").write_bytes(output)
            verify_artifacts(folder, reviewed)
            with self.assertRaises(ValueError):
                build_database(source, folder / "invalid.db", {"1:1:1": "would lose a row"})

    def test_duplicate_database_locations_and_schema_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.db"
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute(TABLE_SQL)
                connection.executemany("INSERT INTO word_translation VALUES (1,1,'1',?)", [("a",), ("b",)])
            with self.assertRaises(ValueError):
                read_database(path)
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("CREATE TABLE metadata (text TEXT)")
            with self.assertRaises(ValueError):
                read_database(path)

    def test_translation_contract_rejects_missing_order_marker_and_notation_errors(self):
        data = read(ROOT / "turkish-wbw-translation.json")
        english = read(ROOT / "resources/english/english-wbw-translation.json")
        validate_translation(data, english)
        missing = data.copy()
        missing.pop(next(iter(missing)))
        with self.assertRaises(ValueError):
            validate_translation(missing, english)
        with self.assertRaises(ValueError):
            validate_translation(dict(reversed(list(data.items()))), english)
        for key, value in [("1:1:1", "[new notation]"), ("1:1:1", "(broken"), ("1:1:5", "wrong marker")]:
            altered = data.copy()
            altered[key] = value
            with self.assertRaises(ValueError):
                validate_translation(altered, english)

    def test_release_cannot_overwrite_working_or_reference_directories(self):
        for path in [ROOT, ROOT.parent, ROOT / "resources/turkish", ROOT / "reports", ROOT / "scripts/output", ROOT / ".git/output"]:
            with self.assertRaises(ValueError):
                ensure_output_directory(path)
        self.assertEqual(ensure_output_directory(ROOT / "dist"), ROOT / "dist")


if __name__ == "__main__":
    unittest.main()
