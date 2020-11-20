---
title: |-
  Something something\
  Parikh Images
mathfont: texgyrepagella-math.otf
header-includes: |
    \usepackage{mathpartir}
    \usepackage{mymacros}
abstract: We contribute a novel understanding of how Parikh maps can be combined with arbitrary commutative monoid morphisms to efficiently represent a wide range of logics on automata and automata-like structures. Cases studied as examples include epistemic logic and string-length constraints in a string constraint solver. Moreover, we show how this formulation can be efficiently implemented in a theorem prover for succinct formulations of SEVERAL CONSTRAINTS on strings. Finally, we show that this implementation in addition to being Z BETTER also offers X PERFORMANCE improvements on Y real-world instances.
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
\begin{cases}
\geq 0 & \text{if $q \in I$} \\
= 0 & \text{ otherwise}
\end{cases}\\
& \bigwedge_{\delta = q \xrightarrow{} q'} t_\delta > 0 
\implies z_{'q} > 0 \\
& \bigwedge_{q, q' \in Q} z_{q'} > 0 
\implies 
\begin{cases}
\bigvee\limits_{\delta = q \xrightarrow{} q'} z_{q'} = z_{q} + 1 \land t_\delta > 0 \land z_{q} > 0 & \text{if $q \not\in  I$} \\
z_{q'} = 1 \land t_\delta > 0& \text{if $q \in I$}
\end{cases}
\end{aligned}
$$

where all variables $z_i, t_i$ are existentially quantified and the variables $c_\alpha$ make up the actual image.

FIXME: this formalisation is _WRONG_ and I do not know how to fix it

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

We assume an NFA $\Automaton = \Tuple{\States, \Alphabet, \Transitions, \Initial,
\Accepting}$ with $\NrTransitions$ transitions $\Transitions =
\Set{\EllipsisSequence{\Transitions}{\NrTransitions}}$ where we describe each
such transition $\Transitions_i$ from node $q$ to node $q'$ with label $\Label \in \Alphabet$ as
$\Transitions_i = \FromLabelTo{q}{\Label}{q'}$.

Treating $\Automaton$ as a graph with vertices $Q$ and edges $\delta$, we use
the term _separating cut_ of a set of _transitions_ $T =
\Set{\Transitions_i, \ldots, \Transitions_n}, \SeparatingCut(T)$ to refer to any set
of transitions whose removal causes $T$ to be unreachable from any state in
$\Initial$, with the meaning that a transition is reachable iff its starting
node is. Note that if $T$ contains a transition $e =
\FromLabelTo{v}{\Label}{v'}$ such that $v \in \Initial$, $\SeparatingCut(T) =
\emptyset$.

We will follow the notation of [@generate-parikh-image] and simultaneously talk
about $\Automaton$ as a graph and an automaton. Moreover, we will continuously
refer to the subgraph produced by keeping only the transitions/edges whose
corresponding variables in $\TransitionVec$ are positive ($> 0$). An edge will
be called *selected* if it is in this subgraph. An edge that is known to be zero
will conversely be called *deselected*. An edge whose corrsponding term has no
known status is called unknown. Formally, we define these as follows:

\begin{definition}
$\Selected(x)(\SomeClause)$ means that $x > a$ for some $a \geq 0$ is a clause
in $\SomeClause$.
\end{definition}

\begin{definition}
$\Deselected(x)(\SomeClause)$ means that $x = 0$ or $x < a$ for some $a \leq 1$
is a clause in $\SomeClause$.
\end{definition}

\begin{definition}
$\Unknown(x)(\SomeClause)$ means that neither $\Selected(x)(\SomeClause)$ nor
$\Selected(x)(\SomeClause)$ holds.
\end{definition}


With these preliminaries out of the way, we can define a predicate
$\PredicateInstance$ such that it is true exactly when:

- $h:\: \Alphabet^* \rightarrow M$, a morphism to a commutative product monoid 
   $M = \prod_{i} M_i$
- $\TransitionVec$ is a vector of terms such that each term correspond to a
  transition in $\Automaton$. We use the notation $x_t$ to refer to transition
  $t \in \Transitions$'s corresponding term.

\begin{mathpar}
  \inferrule*[left=Propagate, right=\textnormal{$C = \SeparatingCut(T)$, $\exists t \in T \::\: \lnot \Selected(t)$}]
    {\AndComp
      {\Transitions_t \in T}
      {\TransitionVec_{\Transitions_t} = 0} 
    \land \PredicateInstance \land \AndComp{\Transitions_c \in C}{\TransitionVec_{\Transitions_c} = 0} \land \SomeClause}
    {\PredicateInstance \land \AndComp{\Transitions_c \in C}{\TransitionVec_{\Transitions_c} = 0} \land \SomeClause}
    
  \inferrule*[left=Expand, right=\textnormal{(Only once)}]
    {\FlowEq \land \AndComp{i \in 1,\ldots,t}{h(\TransitionVec_i) = \PostTransitionVec_i} \land \PredicateInstance \land \SomeClause}
    {\PredicateInstance \land \SomeClause}

  \inferrule*[left=Split, right=\textnormal{if $\Unknown(\TransitionVec_i)(\SomeClause)$}]
  {\TransitionVec_i = 0 \land \PredicateInstance \land \SomeClause \\ | 
  \\ \TransitionVec_i > 0 \land \PredicateInstance \land \SomeClause}
    {\PredicateInstance{} \land \SomeClause}
    
\inferrule*[left=Subsume, right=\textnormal{if \KnownConnected}]
  {\SomeClause}
  {\PredicateInstance{} \land \SomeClause}
   
\end{mathpar}

where $\FlowEq$ are the flow-balancing part of the Parikh image from [@sec:parikh]:

$$
\begin{aligned}
& \In(q) = \text{$1$ if $q \in I$} + \sum_{i \in 1,\ldots,t \SuchThat \Transitions_i = \FromLabelTo{*}{}{q}} \TransitionVec_i\\
& \Out(q) = \sum_{i \in 1,\ldots,t \SuchThat \Transitions_i = \FromLabelTo{q}{}{*}} \TransitionVec_i\\
& \FlowEq = \AndComp{q \in Q}{\In(q) - \Out(q)}
\text{ $\geq 0$ if $q \in F$, $= 0$ otherwise}
\end{aligned}
$$

and $\KnownConnected$ corresponds to the following, corresponding to guaranteed
connectedness (or, conversely, the non-existence of cuts disagreeing with $\TransitionVec$):
$$
\forall{C, T}\: C = \SeparatingCut(T) \implies \forall{i} \: \Transitions_i \in T \land \TransitionVec_i > 0 \implies \forall{j} \: \Transitions_j \in C \implies \TransitionVec_j = 0
$$

Additionally, we assume the existence of a rule \PresburgerClose{},
corresponding to a sound and complete solver for Presburger formulae.

The $\Propagate{}$ rule allows us to propagate connectedness across
$\Automaton$. It states that we are only allowed to "use" transitions attached
to a reachable state, and is necessary to ensure connectedness in the presence
of cycles. \textsc{Expand} expands the predicate into its most basic rules; one
set of linear equations connecting $\TransitionVec$ and $\PostTransitionVec$,
and the linear flow equations of the standard Parikh image formulation.

Finally, $\Split{}$ allows us to branch on the proof tree by first trying to
exclude a contested edge from a potential solution and then concluding that it
must be included.

A decision procedure for our predicate in a tableau-based automated theorem
prover would start by expanding the predicate using the $\Expand{}$ rule. For
many instances of the predicate, this would be enough to induce subsumption; as
as long as the DFA contains no loops that could be disconnected from a minimum
spanning tree (MST) of the automaton.

- FIXME: is subsume really correct? We need at least the mapping equations, don't we?
- FIXME: what happens to Expand under this formulation of h, h'? How do we map h into this?
- FIXME add precondition that the separating cut is of deselected edges so that
  it is guaranteed to terminate
- FIXME introduce and formalise the selected/deselected edges terminology
- FIXME we will assume a sound, complete and terminating decision procedure for
  presburger arithmetic such that we can determine the selectedness status of an
  edge (formalise!)


#### An Example

HELP

### Soundness
- TODO there is nothing said here about $\PostTransitionVec$

We assume that we have an instance of the predicate $\PredicateInstance$, along
with some arbitrary other clauses $\SomeClause$. For our decision procedure to
be sound would mean to preserve satisfiability. Any valuation function that
satisfies a formula before evaluating one of the rules would also be a valuation
of the result of applying the rule.

Structurally, an assignment to $\TransitionVec$ (which can be partial) can be
outside of the Parikh image of $\Automaton$ only if it is not part of a valid
derivation of $\Automaton$. A derivation can be outside of the automaton only if:

1. The selected graph contains at least one transition $\DeadTransition$ that
   participates in no path from an accepting to a final state. This corresponds
   to an impossible combination of productions in the automaton.
2. There is some state $q \not\in F$ with incoming $\Vector{\delta_{in}}$ and
   outgoing transitions $\Vector{\delta_{out}}$ such that it is part of an
   unbalanced path, in effect $\sum{\Vector{\delta_{in}}} \neq
   \sum{\Vector{\delta_{out}}}$. This corresponds to an unbalanced production.

\begin{lemma}
\Propagate{} preserves satisfiability. 
\end{lemma}
\begin{proof}

Assume that we have a valuation $\Valuation$ where $\Assignment$ that satisfies
an initial formula $\SomeClause$, where the clauses $\SomeClause'$ is
$\SomeClause$ without the predicate we are expanding.

If we have applied $\Propagate$, there must be a separating cut $C =
\SeparatingCut(T)$ such that $\forall c \in C \Deselected(c)(\SomeClause')$. In
that case, the predicate would add a clause $x_i = 0$ for each term $x_i$ in
$\TransitionVec$ associated with a term $t_i \in T$, effectively asserting
$\Deselected(t_i)$.

The only way for this to contradict the valuation is if it contains an
assignment where $\AssignsTo{x_{c_1}}{0}, \ldots, \AssignsTo{x_{c_n}}{0}$ for
all transitions $c_1, \ldots, c_n \in C$, while at the same time
$\AssignsTo{x_t}{a}$ for some transition $t \in T$ and some value $a > 0$.
However, such an assignment would not constitute a path from an initial to an
accepting state, and therefore cannot be in the Parikh image. Therefore, the
additional constraints must be satisfied by any valuation also satisfying the
definition of the Parikh predicate, and therefore cannot exclude any valid
valuation. Therefore it follows that $\Propagate$ must preserve satisfiability.
\end{proof}

\begin{lemma}
\Expand{} preserves satisifiability.
\end{lemma}
\begin{proof}
Assume that we have a valuation $\Valuation$ that satisfies an initial formula
$\SomeClause$, where the clauses $\SomeClause'$ is $\SomeClause$ without the
predicate we are expanding. To prove that $\Expand$ preserves satisfiability,
assume with the goal of reaching contradiction that some application of
$\Expand$ would close the proof.

$\Expand$ only adds the equations in $\FlowEq$. For it to close the proof, at
least one of the flow equations must not be satisified, i.e. there must be some
state $q \not\in \Accepting$ such that $\sum\In(q) \neq \sum\Out(q)$ under $v$.
However, this \Fudge{contradicts the semantics of the predicate as it would mean
an unbalanced production would be a member of the Parikh image}. Therefore it
follows that $\Expand$ preserves satisfiability.
\end{proof}

\begin{lemma}
\Split{} preserves satisfiability.
\end{lemma}
\begin{proof}
It follows trivially that $\Split$ preserves staisfiability immediately from
arithmetic axioms; a positive integer is either 0 or greater than 0. Therefore,
if a formula is satisifiable, at least one of its splits has to be for any given
term.
\end{proof}

\begin{lemma}
\Subsume{} preserves satisfiability.
\end{lemma}
\begin{proof}
Assume there exists a satisfying valuation $\Valuation{}$ that satisfies a formula
$\SomeClause$. In that case, if we apply $\Subsume{}$ to $\SomeClause$ it
follows trivially that satisfiability is preserved, as the rule only removes a
predicate.
\end{proof}

\begin{theorem}
The decision procedure is preserves satisfiability.
\end{theorem}
\begin{proof}
As all the rules preserve satisfiability, so must the decision procedure.
\end{proof}

### Termination

We prove termination by showing that the number of transition terms
($\TransitionVec$) that are unknown is decreasing monotonically with each rule
application. Initially, the worst-case number of unknown terms is $n =
|\TransitionVec|$, i.e. all terms are unknown.

\Expand is evaluated precisely once, which means that it is automatically
guaranteed to terminate. It will also at worst not increase $n$.

\Split can always be applied when there are unknown terms, and will always
eliminate that unknown term in each split. Therefore, it will monotonically
decrease the number of unknown terms.

\Propagate can be executed whenever there is a term in $T$ not currently known
to be selected. This means that there are two options. Either it can close the
proof by materialising finitely many contradicting deselecting statements for a
selected transition in $T$, effectively terminating the proof procedure
immediately with a contradiction. Or it can propagate selectedness to an unknown
transition term, thereby reducing the number of transition terms. Therefore, the
rule can be executed only finitely many times.

\Subsume, finally, will be applied only once, after which none of the other
rules can be applied to that predicate. It will be applicable if there are no
unknown transitions left and the known transitions are guaranteed to not
contradict the predicate. If they did, one of the other rules would be able to
execute, generating a contradiction.

It therefore follows that these rules always allows us to always make progress
towards reducing the number of unknown terms for each predicate in a formula.


### Completeness

We have something sound and terminating; it is enough to show that we can always
apply a rule. Initially, if we have no predicate instances left, we can close
the proof with \PresburgerClose.

If there is a predicate instance and all of its transition terms are known, we
can either close the proof by applying \Expand (if it has not been applied
before) or \Propagate to derive a contradiction, or remove the predicate using
the $\Subsume$ rule if neither of them can be applied.

If there is at least one unknown transition term, we can always apply at least \Split
to attempt a proof by cases, removing the unknown term.

It follows therefore that because we can always make monotonic progress towards
a solution, and because the decision procedure is sound, it is also complete.

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
