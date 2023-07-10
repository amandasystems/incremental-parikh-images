#!/usr/bin/env python3

from collections import namedtuple
from enum import Enum, auto
from pandas import DataFrame
import pandas
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
                    
def adjust_categories(runtimes):
    runtimes['backend'] = runtimes['backend'].astype("category")
    runtimes['status'] = runtimes['status'].astype("category")
    runtimes['status'] = runtimes['status'].cat.set_categories(
        [Status.SAT, Status.UNSAT, Status.TIMEOUT, Status.MEMORY_OUT, Status.ERROR], 
        ordered=True)
    return runtimes
                    
def log2df(log):
    return adjust_categories(DataFrame(parse_log(log)))


def solved_after(seconds, known_solved):
    df = known_solved[known_solved['runtime'] < seconds]\
        .groupby('backend')\
        .size()\
        .reset_index()
    df['after'] = seconds
    df = df.rename(columns = {0: 'nr solved'})
    return df

def prepare_cactus_plot(runtimes, timeout_s, step_size):
    known_solved = runtimes[runtimes['status'] < Status.TIMEOUT]
    return (runtimes.instance.unique().size, 
            pandas.concat([solved_after(i * step_size, known_solved) for i in range(int(timeout_s / step_size) + 1)], axis=0))


LINE_RE = re.compile(
    r"^==== (?P<instance>.*?): (?P<status>sat|unsat|timeout.*ms|memory-out) run: (?P<runtime>.+)s parse: .*====$"
)

ERROR_RE = re.compile("^==== (?P<instance>.*?) error: (?P<message>.*)====?$")



def catra_status_from_str(status):
    if "timeout" in status:
        return Status.TIMEOUT
    if status == "unsat":
        return Status.UNSAT
    if status == "sat":
        return Status.SAT
    if status == "memory-out":
        return Status.MEMORY_OUT
    if "error" in status:
        return Status.ERROR
    
    raise ValueError(f"Unexpected status {status}")
    

def parse_catra_line(backend, line):
    match = LINE_RE.match(line)
    if match:
        status = catra_status_from_str(match.group("status"))
        runtime = (
            float(match.group("runtime"))
            if status not in [Status.TIMEOUT, Status.MEMORY_OUT]
            else float("inf")
        )
        return Result(backend, match.group("instance"), status, runtime)
    match = ERROR_RE.match(line)
    if not match:
        return None
    # It's an error
    return Result(backend, match.group("instance"), Status.ERROR, float("inf"))

def parse_catra_log(logfile, backend):
    with open(logfile) as fp:
        return adjust_categories(DataFrame([result for line in fp if (result := parse_catra_line(backend, line))]))
