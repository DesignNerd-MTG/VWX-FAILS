"""Offline envelope checks, not a substitute for Vectorworks validation."""
from pathlib import Path
import unittest
import subprocess
import sys
import tempfile
from tools.rebuild_vsm import (
    END_FIELDS, MUTABLE_FIELDS, SOURCE_OFFSET, TRAILER_SIZE,
    extract_source, normalized_header, rebuild, u32,
)

ROOT = Path(__file__).resolve().parents[1]


class VSMPackagingTests(unittest.TestCase):
    def setUp(self):
        self.packages = sorted((ROOT / 'plug-ins').glob('*.vsm'))
        self.assertEqual(len(self.packages), 11)

    def test_all_sources_match_and_noop_rebuilds_are_identical(self):
        self.assertEqual({p.stem for p in self.packages},
                         {p.stem for p in (ROOT / 'src').glob('*.py')})
        for path in self.packages:
            with self.subTest(path=path.name):
                data = path.read_bytes()
                source = (ROOT / 'src' / (path.stem + '.py')).read_bytes()
                self.assertEqual(extract_source(data), source)
                self.assertEqual(rebuild(data, source), data)

    def test_growth_shrink_and_unicode_preserve_envelope(self):
        for path in self.packages:
            data = path.read_bytes()
            original = extract_source(data)
            for source in (b'pass\n', original + '\n# Unicode: café 🎭\n'.encode(),
                           b'#' + b'x' * 70000 + b'\npass\n'):
                with self.subTest(path=path.name, length=len(source)):
                    result = rebuild(data, source)
                    self.assertEqual(extract_source(result), source)
                    self.assertEqual(normalized_header(result), normalized_header(data))
                    self.assertEqual(result[-TRAILER_SIZE:], data[-TRAILER_SIZE:])
                    self.assertEqual(rebuild(result, original), data)
                    end = SOURCE_OFFSET + len(source)
                    for offset, relative in END_FIELDS.items():
                        self.assertEqual(u32(result, offset), end + relative)
                    for offset in (226, 248, 264, 272):
                        start = u32(result, offset)
                        self.assertTrue(result[start:start + 784].startswith(b'<svg '))
                        self.assertTrue(result[start:start + 784].endswith(b'</svg>\r\n'))

    def test_all_correlated_u32_fields_accounted_for(self):
        data = [p.read_bytes() for p in self.packages]
        ends = [SOURCE_OFFSET + len(extract_source(b)) for b in data]
        found = set()
        for offset in range(SOURCE_OFFSET - 3):
            differences = {u32(b, offset) - end for b, end in zip(data, ends)}
            if len(differences) == 1 and -SOURCE_OFFSET <= next(iter(differences)) <= TRAILER_SIZE:
                found.add(offset)
        self.assertEqual(found, set(MUTABLE_FIELDS))

    def test_cli_does_not_overwrite_an_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.py'
            output = Path(directory) / 'output.vsm'
            source.write_bytes(b'pass\n')
            output.write_bytes(b'keep me')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'tools' / 'rebuild_vsm.py'),
                 str(self.packages[0]), str(source), str(output)],
                capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b'keep me')

    def test_corruption_and_unknown_layout_rejected(self):
        data = self.packages[0].read_bytes()
        for offset in (0, 136, *MUTABLE_FIELDS, 300, len(data) - 1):
            broken = bytearray(data)
            broken[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                rebuild(bytes(broken), b'pass\n')
        for broken in (b'', data[:-1], data + b'\0'):
            with self.assertRaises(ValueError):
                extract_source(broken)
        with self.assertRaises(SyntaxError):
            rebuild(data, b'def broken(\n')
        with self.assertRaises(ValueError):
            rebuild(data, b'')


if __name__ == '__main__':
    unittest.main()
