---
title: |-
  Something something\
  Parikh Images
---

This is revision `!sh(git rev-parse --short HEAD)`.

# Introduction

## Parikh Images and String Equations

- What is even a Parikh Image
- Why do we need it
- The role of Parikh Images in Ostrich
- Ostrich [@ostrich] in the bigger picture
- Other approaches:
  - Trau [@trau]
  - ARATHA [@minizinc-dse-js] solving framework using G-STRINGS, which uses dashed string representations
  - also cvc and z3 (word equations + heuristics??? I DON'T KNOW)

## Relationship to Path Profiling

- essentially, path profiling discovers dependence realtions in the flow equations.


## Observations

- Flow rules are insufficient to ensure reachability of automata in the presence of cycles

- Any automaton where a cycle cannot become disconnected can be fully represented by the flow rules

# Efficient Parikh Image Computation

A method for generating a Presburger formula representing the Parikh Image of a
context-free grammar (CFG) was described in [@generate-parikh-image]. However,
this method would yield a formula containing quantifiers, which in many
practical cases are prohibitively time-consuming to eliminate.

## Generating Quantifier-Free Presburger Formulae Lazily

Our approach, similar to other classic relaxations such as the one used for
solving the travelling salesperson problem in Concorde [@concorde], relaxes the
problem to finding paths through the automaton satisfying the quantifier-free
flow equations. We then lazily generate clauses to block disconnected components
by computing a min-cut between the disconnected states and the rest of the path.
These sub-problems are solved using our own solver, Ostrich, as an oracle.

![This is an enormous automaton.](img/automata.pdf){#fig:automata}

![This is a small automaton.](img/1.pdf){#fig:one}

# References

::: {#refs}
:::
