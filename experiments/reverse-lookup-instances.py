#!/usr/bin/env python3

import sys

origin = dict()

with open("/Volumes/Storage/deduped-benchmarks/manifest.txt") as fp:
    for line in fp:
        new, old = line.split(": ")
        old = old.replace("/Volumes/Storage/parikh-plus/", "")
        old = "/".join(old.split("/")[:-1])
        origin[new] = old

for instance in sys.stdin:
    instance = instance.strip()
    print(origin[instance])
