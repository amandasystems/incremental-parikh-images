---
title: |-
  Something something\
  Parikh Images
---

This is revision `!sh(git rev-parse --short HEAD)`.

# Introduction

## Motivating Example

- `(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*`, find a string of at
  least length 5: 3.75-time speedup!

## Parikh Images and String Equations

Formally, the _Parikh map_ over a context-free language $\Sigma = \left\{a_1, \ldots, a_k \right\}$ is defined as in [@kozen]:

$$
\begin{aligned}
& \psi: \Sigma^* \rightarrow \mathbb{N}^k \\
& \psi(s) = \left[\#a_1(s), \#a_2(s), \ldots, \#a_k(s)\right]
\end{aligned}
$$

That is, $\psi(s)$ is a vector of the number of occurrences of each character in the language for a given string $s$. For example, for  $\Sigma = \left \{ a, b\right\}$, we would have $\psi(abb) = \left[1, 2\right]$.

We define the image of this map, the _Parikh image_, of some subset of the language $A \subseteq \Sigma^*$ as:

$$
\psi(A) = \left\{ \psi(x) | x \in A \right\}
$$

Thus we would have $\psi(\left\{ab, abb\right\}) = \left\{\left[1, 1\right], \left[1, 2\right]\right\}$. Mixing notations slightly, we allow a Presburger formula to describe an infinite Parikh image by describing a relationship between the occurrences of each character in the language. For our example above, we would have $\psi(\Sigma^*) = \left[x, y\right]$ with no further restrictions on $x$ and $y$, since we can have any number of $a$:s and $b$:s and their occurrences are independent.

We will analogously extend this definition of the Parikh map and its image to cost-enriched NFA:s. Specifically, we will define the Parikh Image over a register automaton $\mathcal{A}$ to be:

$$
a
$$

In essence, the Parikh image of an automaton represents all possible paths through it modulo order. This fact is particularly useful for deciding negative inclusion in languages (a string with a character count outside of the Parikh image of a language obviously cannot be in that language), and for determining length constraints on their outputs. Both of these applications are used in the Ostrich string solver [@ostrich].

- TODO define register-enriched NFA

## Relationship to Path Profiling

- essentially, path profiling [@path_profiling][@optimally_profiling] discovers dependence relations in the flow equations
- TODO determine the relationship between path profiling's optimisation (cut out
  the MST) and the flow equations. Is it equal to gauss-jordan elimination?
- relationship to min-flow theorem
  (https://en.wikipedia.org/wiki/Dual_linear_program vs max-flow min-cut)

## Observations

- Flow rules are insufficient to ensure reachability of automata in the presence of cycles
- Any automaton where a cycle cannot become disconnected can be fully represented by the flow rules
- TODO can I prove that?

# Efficient Parikh Image Computation

A method for generating a Presburger formula representing the Parikh image of a
context-free grammar (CFG) was described in [@generate-parikh-image]. However,
this method would yield a formula containing quantifiers, which may be
expensive to eliminate. A key observation is that for our use case, we often do not need the entire image, but rather subsets of it. It therefore follows that generating the image lazily is useful.

- TODO what does Anthonys paper say about this? what happens when you relax a CFG to a regular language?

## Generating Quantifier-Free Presburger Formulae Lazily

Our approach, similar to other classic problem relaxations such as the one used for
solving the travelling salesperson problem in Concorde [@concorde], relaxes the
problem to finding paths through the automaton satisfying the quantifier-free
flow equations. We then lazily generate clauses to block disconnected components
by computing a min-cut between the disconnected states and the rest of the path.
These sub-problems are solved using our own solver, Princess [@princess], as an
oracle.

### Semantics

### Soundness

### Completeness

![This is an enormous automaton.](img/automata.pdf){#fig:automata}

![This is a small automaton.](img/1.pdf){#fig:one}

# References

::: {#refs}
:::
