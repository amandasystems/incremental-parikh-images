#!/usr/bin/env python3

import subprocess
import sys
import os
import time


TIMEOUT_S = 60
JVM_OPTS = [
    "-Xss20000k",
    "-Xmx2000m",
]


def z3(benchmark):
    return subprocess.Popen(
        ["/usr/bin/time", "z3", f"-T:{TIMEOUT_S}", benchmark],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def cvc(benchmark):
    return subprocess.Popen(
        ["/usr/bin/time", "cvc4", "--strings-exp", f"--tlimit={TIMEOUT_S * 1000}", benchmark],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def ostrich(benchmark):
    return subprocess.Popen(
        [
            "/usr/bin/time",
            "java",
            *JVM_OPTS,
            "-jar",
            os.path.expanduser("~/ostrich/target/scala-2.13/ostrich-assembly-1.3.jar"),
            "-stringSolver=ostrich.OstrichStringTheory:",
            "+quiet",
            f"-timeout={TIMEOUT_S * 1000}",
            benchmark,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def ostrich_catra(benchmark):
    return subprocess.Popen(
        [
            "/usr/bin/time",
            "java",
            *JVM_OPTS,
            "-jar",
            os.path.expanduser("~/ostrich/target/scala-2.13/ostrich-assembly-1.3.jar"),
            "-stringSolver=ostrich.cesolver.stringtheory.CEStringTheory:-ceaBackend=catra",
            "+quiet",
            f"-timeout={TIMEOUT_S * 1000}",
            benchmark,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

def poll_longer(proc):
    try:
        return proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        return None


def drain_all(processes):
    num_processes = len(processes)
    while True:
        finished = 0
        for p in processes:
            if poll_longer(p) == None:
                p.terminate()
                if poll_longer(p) == None:
                    p.kill()
            else:
                finished += 1
        if finished == num_processes:
            return

def time_of(res):
    stderr = res.stderr.read().strip()
    if not stderr:
        return None
    time = float(stderr.split()[0])
    return time if time else None


def improves(left, right):
    left = time_of(left)
    right = time_of(right)

    if right == None and left != None:
        return True

    if left and right:
        return left < right

    return False

def summarise_results(res):
    stdout = res.stdout.read().strip()

    if stdout:
        if "timeout" in stdout or "unknown" in stdout:
            return "t"
        else:
            code = f"{stdout}"
    else:
        code = "!"

    return f"{code}:{time_of(res)}"

def wait_all(benchmark):
    results = {
        "z3": z3(benchmark),
        "cvc4": cvc(benchmark),
        "ostrich": ostrich(benchmark),
        "ostrich_catra": ostrich_catra(benchmark),
    }

    while True:
        for solver, output in results.items():
            if poll_longer(output) != None:
                drain_all(results.values())
                return results


for benchmark in sys.argv[1:]:
    results = wait_all(benchmark)
    columns = [benchmark, *[f"{solver}={summarise_results(res)}" for solver, res in results.items()]]
    print(" || ".join(columns))
    with open("experiments.log", "a") as logfile:
        logfile.write(" || ".join(columns) + "\n")
