#!/usr/bin/env python3

from re import A


initial_state = 0
accepting_states = {3}
transitions = [
    (0, "a", 1),
    (0, "b", 2),
    (1, "c", 1),
    (1, "a", 3),
    (2, "b", 0),
    (2, "c", 3),
]

states = sorted({
    initial_state,
    *accepting_states,
    *{s for s, _, _ in transitions},
    *{s for _, _, s in transitions},
})


def chunks(l, n):
    n = max(1, n)
    return (l[i : i + n] for i in range(0, len(l), n))


def subscript(x, s):
    return x + r"_{" + s + "}"


def fmt_transition(t):
    _from, label, to = t
    return r"\FromLabelTo{" + str(_from) + "}{" + label + "}{" + str(to) + "}"


alphabet = sorted({l for _, l, _ in transitions})
var = (
    {ch: subscript(r"\LetterVar", ch) for ch in alphabet}
    | {
        t: subscript(
            r"\TransitionVar",
            fmt_transition(t),
        )
        for t_id, t in enumerate(transitions)
    }
    | {s: subscript(r"\StateVar", str(s)) for s in states}
)

final_var = {s: subscript(r"\FinalStateVar", str(s)) for s in accepting_states}

automaton_symb = r"\Automaton"
defined_as = r":=\:"
align_here = "&"


def parikh_map_of(something):
    return r"\ParikhMap(" + something + ")"


def tex_env(name, contents):
    out = r"\begin{" + name + "}\n"
    out += contents
    out += "\n"
    out += r"\end{" + name + r"}"
    return out


def equation(contents):
    return tex_env("equation", contents)


def aligned(things):
    return tex_env("aligned", ("\\\\\n").join(things))


def cases(outcomes):
    return tex_env("cases", ("\\\\\n").join(outcomes))


def and_join(clauses):
    return r" \land ".join(clauses)


def or_join(clauses):
    return r" \lor ".join(clauses)


def sum_of(things):
    return 0 if not things else " + ".join(things)


def sub_of(things):
    return 0 if not things else " - ".join(things)


def sum_of_transitions(ch):
    return sum_of([var[t] for t in transitions if t[1] == ch])


def image_variables_consistent():
    return and_join([f"{var[ch]} = {sum_of_transitions(ch)}" for ch in alphabet])


def incoming(s):
    return [var[t] for t in transitions if t[2] == s]


def outgoing(s):
    return [var[t] for t in transitions if t[0] == s]


def flow(s):
    lhs = set(outgoing(s))
    rhs = set(incoming(s))
    lhs_simp = lhs - rhs
    rhs_simp = rhs - lhs
    return f"{sum_of(lhs_simp)} - {sub_of(rhs_simp)}"


def flow_preserved():
    def final_var_term(s):
        return f"{final_var[s]} +" if s in accepting_states else ""

    clauses = [
        f"{final_var_term(s)} {flow(s)} = {1 if s == initial_state else 0}"
        for s in states
    ]
    return [align_here + and_join(chunk) for chunk in chunks(clauses, 2)]


def transition_implies_distance():
    clauses = [implies(f"{var[t]} > 0", f"{var[t[2]]} > 0") for t in transitions]
    return [align_here + and_join(chunk) for chunk in chunks(clauses, 2)]


def distance_computation(q, q_prime):
    if q == initial_state:
        return f"{var[q_prime]} = 1" + r" \land "

    return ""


def implies(a, b):
    return a + r" \implies " + b


def parens(content):
    return r"\left(" + content + r"\right)"


def distance_inequalities():
    return [
        align_here
        + implies(
            f"{var[s]} > 0",
            or_join(
                [
                    *([f"{final_var[s]} = 1"] if s in accepting_states else []),
                    *[
                        parens(
                            and_join(
                                [
                                    f"{var[t[0]]} = {var[t[2]]} + 1",
                                    f"{var[t]} \\geq 1",
                                    f"{var[t[2]]} \\geq 1",
                                ]
                            )
                        )
                        for t in transitions
                        if t[0] == s
                    ],
                ]
            ),
        )
        for s in states
    ]


def final_vars_consistent():
    return and_join(
        [implies(f"{final_var[s]} > 0", f"{var[s]} > 0") for s in accepting_states]
    )


def main():
    return equation(
        aligned(
            [
                (
                    parikh_map_of(automaton_symb)
                    + defined_as
                    + "\n"
                    + align_here
                    + image_variables_consistent()
                ),
                (align_here + final_vars_consistent()),
                *flow_preserved(),
                *transition_implies_distance(),
                *distance_inequalities(),
            ]
        )
    )

print(main())