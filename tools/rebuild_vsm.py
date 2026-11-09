#!/usr/bin/env python3
"""Re-embed Python in this repository's known, unencrypted VSM exports only.

This is NOT a general VSM writer or a Vectorworks export/compatibility test.
The layout was checked across all 11 exports at commit 25bb9df. Scanning
at every byte alignment found the source length and ten end-relative u32
fields below. The identical trailer contains four 784-byte SVG icons,
98 leading zero bytes, an 8-byte gap, and a 7-byte terminator. Preserve all
metadata (including original internal names/IDs) and trailer bytes exactly.
Unknown metadata/trailer layouts are rejected rather than guessed.

Usage: python tools/rebuild_vsm.py old.vsm final.py new.vsm
Existing outputs are never overwritten. Validate in Vectorworks on a copy.
"""
import argparse
import hashlib
from pathlib import Path
import struct

SOURCE_OFFSET = 2226
TRAILER_SIZE = 3249
# field byte offset: displacement from the end of the embedded source.
END_FIELDS = {148: 0, 152: 0, 226: 98, 234: 882, 248: 890,
              256: 1674, 264: 1674, 272: 2458, 280: 3242, 284: 3249}
MUTABLE_FIELDS = (140, *END_FIELDS)
TRAILER_HASH = '35114b5a625f056665a685b5e7d058e7814decd2f6e97933cf44fff4aa619d44'
# SHA-256 of original headers with only MUTABLE_FIELDS zeroed.
KNOWN_HEADERS = {
    '7caed13970096db2177385b4cc272f9fdb2f4e5b6b7f8a7e0249032c86cb8821',
    'f75864279ba0e77d1decee18f40730a15d3a8ad5216bb5fbb08cc70a21751f40',
    '48364362e3e0c597396777ecdc09e2c3c62d88c3fcef0b823fe8b35920612eef',
    'd16266127afbabf51a88b6a4275b6521c29bf3334fef43af0ec18eaf4e3ad24b',
    'f2ccf1ec0e6495cf1f6098bbaf96aed8f1850c357459fe06eea759b153e9eb4b',
    'b0394cf9aa97ed9e3d8a2e34159556047855a40421224ebff50d55bda2416254',
    '1d7322deec152953b481d7564acbd7af204f083b7a180da56a45e8de21147a4a',
    '294c53f3dd3174b448a0ff2bca3b25993b3fa41cccc8bf30a2bfb1b70994bcfa',
    '6b9c4864f18ab298e33761e7e80f1d8b356c1b19c0eeb86e4d6ead99c3040e6b',
    '793622412693c9c75946ec697737cb9f0157e97293541eb24703521cc5c7dbe8',
    '064ab52106b08d1cf18ec22f7d0cff0c8373adbc79abe32b4d1ccadcb3f7bb1f',
}


def u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def normalized_header(data):
    header = bytearray(data[:SOURCE_OFFSET])
    for offset in MUTABLE_FIELDS:
        header[offset:offset + 4] = bytes(4)
    return bytes(header)


def extract_source(data):
    """Validate the complete known envelope, then return the source bytes."""
    if len(data) < SOURCE_OFFSET + TRAILER_SIZE:
        raise ValueError('Truncated VSM')
    if hashlib.sha256(normalized_header(data)).hexdigest() not in KNOWN_HEADERS:
        raise ValueError('Unknown VSM metadata/layout; use a native Vectorworks export')
    end = SOURCE_OFFSET + u32(data, 140)
    if end + TRAILER_SIZE != len(data):
        raise ValueError('Source length / file size mismatch')
    for offset, relative in END_FIELDS.items():
        if u32(data, offset) != end + relative:
            raise ValueError(f'Invalid section pointer at byte {offset}')
    if hashlib.sha256(data[end:]).hexdigest() != TRAILER_HASH:
        raise ValueError('Unknown or damaged VSM trailer')
    return data[SOURCE_OFFSET:end]


def rebuild(data, source):
    old_source = extract_source(data)
    if not source:
        raise ValueError('Empty source')
    compile(source, '<embedded VSM source>', 'exec')
    end = SOURCE_OFFSET + len(source)
    if end + TRAILER_SIZE > 0xffffffff:
        raise ValueError('VSM exceeds 32-bit length limit')
    header = bytearray(data[:SOURCE_OFFSET])
    struct.pack_into('<I', header, 140, len(source))
    for offset, relative in END_FIELDS.items():
        struct.pack_into('<I', header, offset, end + relative)
    result = bytes(header) + source + data[SOURCE_OFFSET + len(old_source):]
    if extract_source(result) != source:
        raise ValueError('Rebuilt source did not round-trip')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('template', type=Path)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = rebuild(args.template.read_bytes(), args.source.read_bytes())
    with args.output.open('xb') as output:
        output.write(result)
    print(f'Wrote {args.output}: {len(result)} bytes. Native validation still required.')


if __name__ == '__main__':
    main()
