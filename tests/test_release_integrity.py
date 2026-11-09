"""Release inventory checks; no Vectorworks runtime is imported."""
import ast
import hashlib
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseIntegrityTests(unittest.TestCase):
    def test_source_syntax_and_pairing(self):
        sources = sorted((ROOT / "src").glob("*.py"))
        plugins = sorted((ROOT / "plug-ins").glob("*.vsm"))
        self.assertEqual(len(sources), 11)
        self.assertEqual({p.stem for p in sources}, {p.stem for p in plugins})
        for source in sources:
            with self.subTest(source=source.name):
                ast.parse(source.read_bytes(), filename=str(source))

    def test_manifest_covers_exact_release_bytes(self):
        manifest = (ROOT / "PACKAGE_MANIFEST.txt").read_text(encoding="utf-8")
        rows = re.findall(r"^((?:src|plug-ins)/.+)  ([a-f0-9]{64})$", manifest, re.M)
        paths = [path for path, _ in rows]
        expected = {str(p.relative_to(ROOT)) for folder, suffix in
                    (("src", "*.py"), ("plug-ins", "*.vsm"))
                    for p in (ROOT / folder).glob(suffix)}
        self.assertEqual(len(rows), 22)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(set(paths), expected)
        for path, expected_hash in rows:
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
                                 expected_hash)

    def test_notes_inventory_and_crlf_display_contract(self):
        path = ROOT / "src" / "99 CHUCKLES NOTES v1.0.4.py"
        source = path.read_text(encoding="utf-8")
        module = ast.parse(source)
        notes = next(ast.literal_eval(node.value) for node in module.body
                     if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "NOTES_TEXT"
                             for target in node.targets))
        self.assertLess(len(notes), 30000)
        self.assertNotIn("\r", notes)
        self.assertIn('NOTES_TEXT.replace("\\n", "\\r\\n")', source)
        self.assertIn("Package date: 2026-11-09", notes)
        expected = (("1", "2.7.1"), ("2", "5.0.1"), ("3", "1.0"),
                    ("4", "2.0"), ("5", "1.3"), ("6", "1.2.1"),
                    ("7", "1.5"), ("8", "1.2"), ("9", "1.0.2"),
                    ("10", "1.0"), ("99", "1.0.4"))
        version_list = notes.split("VERSION LIST\n", 1)[1]
        for number, version in expected:
            self.assertRegex(version_list,
                             r"(?m)^" + number + r"\s+.+\s+v" + re.escape(version) + r"$")


if __name__ == "__main__":
    unittest.main()
