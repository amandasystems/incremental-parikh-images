#!/usr/bin/env python3

from pathlib import Path
import sys
import sys

def classify_file(fp):
    present = []
    for line in fp:
        if "str.len" in line:
            present.append("str.len")
        if "str.replace" in line:
            present.append("str.replace")
        if "str.indexof" in line:
            present.append("str.indexof")
        if "str.substr" in line:
            present.append("str.substr")

    return present

files = []
for file in sys.stdin:
    file = Path(file.strip())
    with file.open() as fp:
        try:
            files.append((file, classify_file(fp)))
        except UnicodeDecodeError:
            continue

for file, constraints in sorted(files, key=lambda f: len(f[1])):
    print("\t".join([str(file), ",".join(constraints)]))
