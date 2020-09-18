---
title: |-
  Something something\
  Parikh Images
mathfont: texgyrepagella-math.otf
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

Thus we would have $\psi(\left\{ab, abb\right\}) = \left\{\left[1, 1\right], \left[1, 2\right]\right\}$. Mixing notations slightly, we allow a Presburger formula to describe an infinite Parikh image by describing a relationship between the occurrences of each character in the language. For our example above, we would have $\psi(\Sigma^*) = \left[x, y\right]$ with no further restrictions on $x$ and $y$, since we can have any number of $a$:s and $b$:s and their occurrences are independent. Furthermore, we will use the notation $\psi(\mathcal{A})$ to mean the Parikh image of the language recognised by a non-deterministic finite automaton (NFA) $\mathcal{A}$, really a tuple $\langle Q, \Sigma, \delta, I, F\rangle$, where $Q$ is a finite set of states, $\Sigma$ is a finite alphabet, $\delta \subseteq Q \times \Sigma \times Q$ is the transition relation, $I,F \subseteq Q$ are the set of initial and final states respectively. We also write a transition $(q, a, q') \in \delta$ as  $q \xrightarrow{a} q'$.

We will also extend this definition of a Parikh image to cost-enriched NFA:s (CEFA:s). A CEFA is an NFA enriched with a vector of mutually distinct registers $R = \left[r_1, \ldots, r_k\right]$ and and a cost register update function $\eta: R \rightarrow \mathbb{Z}$ associated with each transition. For a CEFA, we write a transition $\langle q, a, q', \eta\rangle \in \delta$ as $q \xrightarrow{a, \eta} q'$. Note that we do not allow constraints involving registers to appear in transition constraints (**DO WE WANT THIS?**); they are solely expressed in terms of input characters $a \in \Sigma$ as with regular automata.



**Example**: a length-counting automaton would have a sole register $R = \left[r\right]$, a single, both accepting and initial, state $q$, and a single transition relation $q \xrightarrow{*, 1} q$, where each character would cause the $r$ to increment by one.



Following [@generate-parikh-image], we define the Parikh Image of a CEFA $\mathcal{A} =  \langle Q, \Sigma, R, \delta, I, F \rangle$ as:

$$
\begin{aligned}
\psi(\mathcal{A}) := &\bigwedge_{i \in \{1, \ldots, k\}}
r_i = \sum_{\delta, \eta \in \delta} t_\delta \cdot \eta(i)  \\
&\bigwedge_{q \in S} \text{$1$ if $q \in I$} +
\sum_{\delta = q' \xrightarrow{} q} t_\delta 
- \sum_{\delta = q\xrightarrow{}q'} = 
\text{$1$ if $q \in F$, $0$ otherwise}\\
& \bigwedge_{\delta = q \xrightarrow{} q'} t_\delta > 0 
\implies z_q > 0 \\
& \bigwedge_{q \in S, q \not \in F} z_q = 0 
\bigwedge_{\delta = q \xrightarrow{} q'} 
z_q = q_{q'} + 1 \land t_\delta \geq 1 \land z_{q'} \geq 1\\
\end{aligned}
$$



This definition allows us to construct a CEFA $\mathcal{C}$ for an arbitrary NFA $\mathcal{A}$ where we associate each letter $a \in \Sigma$ with a register  $r_a$ such that each transition $q \xrightarrow{a} q'$ becomes transitions $q \xrightarrow{a, r_a \mapsto 1} q'$ in $\mathcal{C}$, and otherwise let $\mathcal{C}$ copy $\mathcal{A}$. By this definition and our definition of the Parikh image above, $\psi(\mathcal{A}) = \psi(\mathcal{C})$  (**Q: do we want to mash the transitions together? Is this how the update function works?**).

In essence, the Parikh image of an automaton represents all possible paths through it modulo order. This fact is particularly useful for deciding negative inclusion in languages. For example, a string with a character count outside of the Parikh image of a language cannot be in that language. It is also useful for determining length constraints on strings whose possible values are represented by automata. Both of these applications are used in the Ostrich string solver [@ostrich], which we used in our experiments.

- ## Relationship to Path Profiling

- essentially, path profiling [@path_profiling][@optimally_profiling] discovers dependence relations in the flow equations
- TODO determine the relationship between path profiling's optimisation (cut out
  the MST) and the flow equations. Is it equal to gauss-jordan elimination?
- relationship to min-flow theorem
  (https://en.wikipedia.org/wiki/Dual_linear_program vs max-flow min-cut)

## Observations

- Flow rules are insufficient to ensure reachability of automata in the presence of cycles
- Any automaton where a cycle cannot become disconnected can be fully represented by the flow rules
- TODO prove that?

# Efficient Parikh Image Computation

- TODO explain that the quantified transition variables are fine (follows from gauss-jordan elimination of system, only propagates coefficients of registers more or less), and it's the connectedness condition that kills us

A key observation is that for our use case, we often do not need the entire image, but rather subsets of it. It therefore follows that generating the image lazily is useful.

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

TODO define the semantics of the "parikh image predicate".

### Soundness

### Completeness

![This is an enormous automaton.](img/automata.pdf){#fig:automata}

![This is a small automaton.](img/1.pdf){#fig:one}

# Evaluation

# References

::: {#refs}
:::
