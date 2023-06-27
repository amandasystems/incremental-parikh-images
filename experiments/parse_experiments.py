#!/usr/bin/env python3

from collections import namedtuple
from enum import Enum, auto
import re

class Status(Enum):
    SAT = auto()
    UNSAT = auto()
    TIMEOUT = auto()
    MEMORY_OUT = auto()
    ERROR = auto()

Result = namedtuple("Result", ["backend", "instance", "status", "runtime"])

CONFIGS_RE = re.compile(r"\s([^\s]+)")

def status_from_str(status):
    if status == "t":
        return Status.TIMEOUT
    if status == "u":
        return Status.UNSAT
    if status == "s":
        return Status.SAT
    if status == "m":
        return Status.MEMORY_OUT
    if status == "e":
        return Status.ERROR
    
    raise ValueError(f"Unexpected status {status}")

def result_from_str(config_name, instance, res_str):
    status = status_from_str(res_str[0])
    runtime = float(res_str[1:]) if status in [Status.SAT, Status.UNSAT, Status.TIMEOUT] else float("inf")
    return Result(config_name, instance, status, runtime)

def parse_line(line, configurations):
    fields = line.rstrip().split("\t")
    instance = fields[0]
    return [result_from_str(config, instance, res_str) for config, res_str in zip(configurations, fields[1:])]
    
def parse_log(log):
    configurations = []
    with open(log) as fp :
        for line in fp:
            if line.startswith("CONFIGS"):
                configurations = CONFIGS_RE.findall(line)
            if line.startswith("RESULT"):
                for r in parse_line(line[len("RESULT "):], configurations):
                    yield r