---
title: |-
  Something something\
  Parikh Images
mathfont: texgyrepagella-math.otf
header-includes: |
    \usepackage{mathpartir}
    \usepackage{mymacros}
abstract: BLAH BLAH ABSTRACT
---

This is revision `!sh(git rev-parse --short HEAD)`.

# Introduction

## Motivating Example

- `(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*`, find a string of at
  least length 5: 3.75-time speedup!

## Parikh Images and String Equations {#sec:parikh}

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

Thus we would have $\psi(\left\{ab, abb\right\}) = \left\{\left[1, 1\right], \left[1, 2\right]\right\}$.

**Insight 1:** Another way of viewing the Parikh map is as a monoid homomorphism $p:\: \left(\Sigma^*, \cdot, \epsilon \right) \to (\mathbb{Z}^\Sigma, +, \vec{0})$, where $\cdot$ is the string concatenation operation, the objects of the right-hand-side monoid are character counts, and $+$ is standard vector addition. Note that while the left monoid does not commute, the right one does.

This viewpoint enables us to generalise the Parikh map further to arbitrary monoid morphisms $h:\: \Sigma^* \to M$ where $M$ is a commutative monoid. It then follows from the universal mapping property (**HELP**) that any such morphism $h$ can also be expressed in terms of the Parikh map, as $h' \circ p$. A useful example of such a morphism might be computing the length of a string, which could easily be recast in terms of the Parikh map by summing the individual character counts of the vector.

For solving purposes we are more interested in the *images* of these maps $p, h$, as they would allow us to derive the possible input values for a given (set of) outputs. Following [@generate-parikh-image], we define the Parikh Image of a DFA $\mathcal{A} =  \langle Q, \Sigma,\delta, I, F \rangle$ as:

$$
\begin{aligned}
\psi(\mathcal{A}) := 
& \bigwedge_{\alpha \in \Sigma}
c_\alpha = \sum_{\delta \in \delta} t_\delta  
\text{ where $\alpha \in \delta$}\\
&\bigwedge_{q \in Q} \left (\text{$1$ if $q \in I$} +
\sum_{\delta = q' \xrightarrow{} q} t_\delta 
- \sum_{\delta = q\xrightarrow{}q'} t_\delta \right) 
\text{ $\geq 0$ if $q \in F$, $= 0$ otherwise}\\
& \bigwedge_{\delta = q \xrightarrow{} q'} t_\delta > 0 
\implies z_q > 0 \\
& \bigwedge_{q \in Q, q \not \in F} z_q = 0 
\bigvee_{\delta = q \xrightarrow{} q'} 
z_q = z_{q'} + 1 \land t_\delta \geq 1 \land z_{q'} \geq 1\\
\end{aligned}
$$

where all variables $z_i, t_i$ are existentially quantified and the variables $c_\alpha$ make up the actual image.

In essence, the Parikh image of an automaton represents all possible paths through it modulo order. This fact is particularly useful for deciding negative inclusion in languages. For example, a string with a character count outside of the Parikh image of a language cannot be in that language. It is also useful for determining length constraints on strings whose possible values are represented by automata. Both of these applications are used in the Ostrich string solver [@ostrich], which we used in our experiments.

## Finding a Parikh Image is Optimally Path Profiling

- essentially, path profiling [@path_profiling][@optimally_profiling] discovers dependence relations in the flow equations (proof later)

- relationship to min-flow theorem
  (https://en.wikipedia.org/wiki/Dual_linear_program vs max-flow min-cut)

- relationship to TSP

# Efficient Parikh Image Computation

- TODO explain that the quantified transition variables are fine (follows from gauss-jordan elimination of system, only propagates coefficients of registers more or less), and it's the connectedness condition that kills us

A key observation is that for many interesting morphisms, we often do not need the entire image, but rather subsets of it. It therefore follows that generating the image lazily is useful.

- TODO what does Anthonys paper say about this? what happens when you relax a CFG to a regular language?

## Observations

- the problem breaks down into a flow analysis part (linear equations), and a cycle-detection part

- Flow rules are insufficient to ensure reachability of automata in the presence of cycles

- Any automaton where a cycle cannot become disconnected can be fully represented by the flow rules

- prove that a MST covers exactly the parts of the automata that cannot be determined by gauss-jordan-eliminating the flow equations // reduce the path profiling problem to finding a parikh image of some clever automaton modulo homomorphims

## Generating Quantifier-Free Presburger Formulae Lazily

Our approach, similar to other classic problem relaxations such as the one used for
solving the travelling salesperson problem in Concorde [@concorde], relaxes the
problem to finding paths through the automaton satisfying the quantifier-free
flow equations. We then lazily generate clauses to block disconnected components
by computing a min-cut between the disconnected states and the rest of the path.
These sub-problems are solved using our own solver, Princess [@princess], as an
oracle.

### Semantics

We assume a DFA $\Automaton = \Tuple{\States, \Alphabet, \Transitions, \Initial,
\Accepting}$ with $\NrTransitions$ transitions $\Transitions =
\Set{\EllipsisSequence{\Transitions}{\NrTransitions}}$ where we describe each
such transition $\Transitions_i$ from node $q$ to node $q'$ with label $\Label$ as
$\Transitions_i = \FromLabelTo{q}{\Label}{q'}$.

Treating $\Automaton$ as a graph with vertices $Q$ and edges $\delta$, we use
the term _separating cut_ of a set of _transitions_ $T =
\Set{\EllipsisSequence{\Transitions}{n}}, \SeparatingCut(T)$ to refer to any set
of transitions whose removal causes $T$ to be unreachable from any state in
$\Initial$, with the meaning that a transition is reachable iff its starting
node is. Note that if $T$ contains a transition $e =
\FromLabelTo{v}{\Label}{v'}$ such that $v \in \Initial$, $\SeparatingCut(T) =
\emptyset$.

With these preliminaries out of the way, we can define a predicate
$\PredicateInstance$ such that it is true exactly when:

- $h:\: \TransitionVec \rightarrow \PostTransitionVec$ is a morphism to a
  commutative monoid
- $\TransitionVec$ is a vector of terms such that each term correspond to a
  transition in $\Automaton$
- HELP: $h \circ p(\Automaton) = \PostTransitionVec$

\begin{mathpar}
  \inferrule*[left=Propagate, right=\textnormal{$C = \SeparatingCut(T)$}]
    {\AndComp
      {j \in \Naturals \SuchThat \Transitions_j \in T}
      {\TransitionVec{j} = 0} 
    \land \PredicateInstance \AndComp{i \in \Naturals \SuchThat \Transitions_i \in C}{\TransitionVec_i = 0} \land \SomeClause}
    {\PredicateInstance \AndComp{i \in \Naturals \SuchThat \Transitions_i \in C} 
    \TransitionVec_i = 0 \land \SomeClause}
    
  \inferrule*[left=Expand]
    {\FlowEq \AndComp{i \in \Naturals}{h(\TransitionVec_i) = \PostTransitionVec_i} \land \PredicateInstance \land \SomeClause}
    {\PredicateInstance \land \SomeClause}

  \inferrule*[left=Split]
  {\TransitionVec_i = 0 \land \PredicateInstance \land \SomeClause \\ | 
  \\ \TransitionVec_i \geq 0 \land \PredicateInstance \land \SomeClause}
    {\PredicateInstance{} \land \SomeClause}
   
\end{mathpar}

where $\FlowEq$ are the flow-balancing part of the Parikh image from [@sec:parikh]:

$$
\begin{aligned}
& \In(q) = \text{$1$ if $q \in I$} + \sum_{i \in \Naturals \SuchThat \Transitions_i = \FromLabelTo{*}{}{q}} \TransitionVec_i\\
& \Out(q) = \sum_{i \in \Naturals \SuchThat \Transitions_i = \FromLabelTo{q}{}{*}} \TransitionVec_i\\
& \FlowEq = \AndComp{q \in Q}{\In(q) - \Out(q)}
\text{ $\geq 0$ if $q \in F$, $= 0$ otherwise}
\end{aligned}
$$

#### An Example

### Soundness

### Completeness

![This is an enormous automaton.](img/automata.pdf){#fig:automata}

![This is a small automaton.](img/1.pdf){#fig:one}

# Use Cases

## Parikh Images of Symbolic Automata

- problem: unicode is really big

- describe symbolic automata

- a symbolic automata is an isomorphism on DFAs

# Evaluation

# References

::: {#refs}
:::

<!-- We will also extend this definition of a Parikh image to cost-enriched NFA:s (CEFA:s). A CEFA is an NFA enriched with a vector of mutually distinct registers $R = \left[r_1, \ldots, r_k\right]$ and a cost register update function $\eta: R \rightarrow \mathbb{Z}$ associated with each transition. For a CEFA, we write a transition $\langle q, a, q', \eta\rangle \in \delta$ as $q \xrightarrow{a, \eta} q'$. Note that we do not allow constraints involving registers to appear in transition constraints as that would push us solidly out of regular languages; they are solely expressed in terms of input characters $a \in \Sigma$ as with regular automata. -->

<!-- **Example**: a length-counting automaton would have a sole register $R = \left[r\right]$, a single, both accepting and initial, state $q$, and a single transition relation $q \xrightarrow{*, 1} q$, where each character would cause the $r$ to increment by one. -->

<!-- This definition allows us to construct a CEFA $\mathcal{C}$ for an arbitrary NFA $\mathcal{A}$ where we associate each letter $a \in \Sigma$ with a register  $r_a$ such that each transition $q \xrightarrow{a} q'$ becomes transitions $q \xrightarrow{a, r_a \mapsto 1} q'$ in $\mathcal{C}$, and otherwise let $\mathcal{C}$ copy $\mathcal{A}$. By this definition and our definition of the Parikh image above, $\psi(\mathcal{A}) = \psi(\mathcal{C})$  (**Q: do we want to mash the transitions together? Is this how the update function works?**). -->
