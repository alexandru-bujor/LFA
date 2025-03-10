# Determinism in Finite Automata. Conversion from NDFA to DFA. Chomsky Hierarchy.

### Course: Formal Languages & Finite Automata
### Author: Bujor Alexandru

----

## Theory
Finite automata are abstract machines used to recognize patterns in input sequences, forming the basis for understanding regular languages in computer science. They consist of a finite set of states (Q), an input alphabet (Σ), a transition function (δ), a start state (q₀), and a set of accepting states (F). Automata process input symbols step-by-step, determining acceptance based on the final state reached.

* A **DFA** is represented as `{Q, Σ, q₀, F, δ}`. In a DFA, for each input symbol, the machine transitions to **one and only one** state. Every state must have a transition defined for each input symbol, ensuring a unique computational path.
* **NFA** is similar to DFA but includes additional features: It can transition to **multiple** states for the same input, and it allows null (ϵ) moves, where the machine can change states without consuming any input.

## Objectives:

1. Understand what an automaton is and what it can be used for.
2. Continuing the work in the same repository and the same project, the following need to be added:
    * a. Provide a function in your grammar type/class that could classify the grammar based on Chomsky hierarchy.
    * b. For this, you can use the variant from the previous lab.
3. According to your variant number (9), get the finite automaton definition and do the following tasks:
    * Implement conversion of a finite automaton to a regular grammar.
    * Determine whether your FA is deterministic or non-deterministic.
    * Implement some functionality that would convert an NDFA to a DFA.
    * Represent the finite automaton graphically (Optional, and can be considered as a bonus point).

## Implementation Description

### Task 2:

The classify_grammar method determines the Chomsky classification of a grammar based on its production rules.

* Type 3 (Regular Grammar): The method checks if each production conforms to the structure of a regular grammar, which allows either a terminal symbol or a non-terminal followed by a terminal, or a non-terminal followed by a non-terminal (but no other combinations).
* Type 2 (Context-Free Grammar): It ensures that the left-hand side of every production is a single non-terminal (which is a requirement for context-free grammars).
* Type 1 (Context-Sensitive Grammar): It verifies that for each production, the length of the right-hand side is greater than or equal to the left-hand side. This is the defining property of context-sensitive grammars.

If none of the conditions for Types 3, 2, or 1 hold, the grammar is classified as Type 0 (Unrestricted), which is the most general form in Chomsky's hierarchy.

```kotlin
fun classifyGrammar(grammar: Map<String, List<String>>): String {
    var isType3 = true
    var isType2 = true
    var isType1 = true

    for ((nonTerminal, productions) in grammar) {
        for (production in productions) {
            // Check for Regular Grammar (Type 3)
            if (!isRegularGrammar(production)) {
                isType3 = false
            }
            // Check for Context-Free Grammar (Type 2)
            if (production.length > 1 && production[0].isLowerCase()) {
                isType2 = false
            }
            // Check for Context-Sensitive Grammar (Type 1)
            if (production.length < nonTerminal.length) {
                isType1 = false
            }
        }
    }

    return when {
        isType3 -> "Type 3 (Regular Grammar)"
        isType2 -> "Type 2 (Context-Free Grammar)"
        isType1 -> "Type 1 (Context-Sensitive Grammar)"
        else -> "Type 0 (Unrestricted Grammar)"
    }
}

```
### Task 3:
The core of the implementation is a FiniteAutomaton class that encapsulates all the required functionality:
The finite automaton is defined with the following parameters for Variant 9:

* States: Q = {q0, q1, q2, q3}
* Alphabet: Σ = {a, b}
* Final States: F = {q3}
* Transitions:


    - δ(q0,a) = q1,
    - δ(q0,a) = q2,
    - δ(q1,b) = q1,
    - δ(q1,a) = q2,
    - δ(q2,a) = q1,
    - δ(q2,b) = q3.


* The method "is_deterministic()" checks if the FA has multiple transitions from the same state on the same input symbol:
  The automaton is non-deterministic because state q1 has two different transitions on the symbol 'b' (to both q2 and q3).
```kotlin
 fun isDeterministic(): Boolean {
        return transitions.values.all { it.size <= 1 }
    }
```
The method "to_regular_grammar()" implements the conversion of the finite automaton to a right-linear grammar:
For each transition, a production rule is created. If the destination state is a final state, an additional production is added that derives only the terminal symbol.
```kotlin
 fun toRegularGrammar(): Map<String, MutableList<String>> {
        val grammar = mutableMapOf<String, MutableList<String>>()

        for ((stateSymbol, destinations) in transitions) {
            val (state, symbol) = stateSymbol
            grammar.putIfAbsent(state, mutableListOf())

            for (dest in destinations) {
                if (dest in finalStates) {
                    grammar[state]!!.add(symbol.toString())
                    grammar[state]!!.add("$symbol$dest")
                } else {
                    grammar[state]!!.add("$symbol$dest")
                }
            }
        }

        if (startState in finalStates) {
            grammar.putIfAbsent(startState, mutableListOf())
            grammar[startState]!!.add("ε")
        }
        return grammar
    }

```

The subset construction algorithm is implemented in the "to_dfa()" method, which:

* Creates composite states representing sets of states from the original NDFA
* Computes transitions for each composite state on each symbol
* Identifies final states in the new DFA

The resulting DFA preserves all the behaviors of the original NDFA but ensures that each state has at most one transition for each input symbol.

```kotlin
      fun toDFA(): FiniteAutomaton {
    if (isDeterministic()) return this

    val dfaStates = mutableSetOf<Set<String>>()
    val dfaTransitions = mutableMapOf<Pair<Set<String>, Char>, Set<String>>()
    val dfaFinalStates = mutableSetOf<Set<String>>()

    val startClosure = setOf(startState)
    val unprocessedStates = mutableListOf(startClosure)
    dfaStates.add(startClosure)

    while (unprocessedStates.isNotEmpty()) {
        val currentState = unprocessedStates.removeAt(0)

        for (symbol in alphabet) {
            val nextState = currentState.flatMap { getTransitions(it, symbol) }.toSet()
            if (nextState.isNotEmpty()) {
                dfaTransitions[Pair(currentState, symbol)] = nextState
                if (nextState !in dfaStates) {
                    dfaStates.add(nextState)
                    unprocessedStates.add(nextState)
                }
            }
        }
    }

    for (state in dfaStates) {
        if (state.any { it in finalStates }) {
            dfaFinalStates.add(state)
        }
    }

    val stateMap = dfaStates.mapIndexed { index, state -> state to "q$index" }.toMap()
    val newTransitions = dfaTransitions.mapKeys { Pair(stateMap[it.key.first]!!, it.key.second) }
        .mapValues { stateMap[it.value]!! }

    return FiniteAutomaton(
        states = stateMap.values.toSet(),
        alphabet = alphabet,
        transitions = newTransitions.mapValues { setOf(it.value) },
        startState = stateMap[startClosure]!!,
        finalStates = dfaFinalStates.map { stateMap[it]!! }.toSet()
    )
}
```

The method visualize() uses Graphviz to create a graphical representation of the automaton:
The visualization follows conventions:

1. Regular states are represented as circles
2. Final states are represented as double circles
3. The start state has an incoming arrow
4. Transitions are represented as labeled arrows

```
   fun visualize(filename: String) {
        val dot = StringBuilder("digraph FiniteAutomaton {\n")
        dot.append("  rankdir=LR;\n")

        for (state in states) {
            val shape = if (state in finalStates) "doublecircle" else "circle"
            dot.append("  $state [shape=$shape];\n")
        }

        dot.append("  start [shape=none, label=\"\", width=0.0, height=0.0];\n")
        dot.append("  start -> $startState;\n")

        for ((key, dests) in transitions) {
            val (state, symbol) = key
            for (dest in dests) {
                dot.append("  $state -> $dest [label=\"$symbol\"];\n")
            }
        }

        dot.append("}")
        File("$filename.dot").writeText(dot.toString())
        println("Graph saved as $filename.dot. Use Graphviz to render it.")
    }
```

## Conclusion
The results highlight the relationship between finite automata and regular grammars, as well as the process of converting from non-deterministic to deterministic automata. This conversion is fundamental in compiler design and pattern matching algorithms. The implementation of the grammar classification function further demonstrates the relationship between formal languages and their corresponding automata, reinforcing the theoretical foundation of the Chomsky hierarchy.

## References
1. _Formal Languages and Finite Automata, Guide for Practical Lessons_ by COJUHARI Irina, DUCA Ludmila, FIODOROV Ion.
2. _Graphviz Documentation_: https://graphviz.readthedocs.io/
