package L2

import java.io.File

class FiniteAutomaton(
    val states: Set<String>,
    val alphabet: Set<Char>,
    val transitions: Map<Pair<String, Char>, Set<String>>,
    val startState: String,
    val finalStates: Set<String>
) {
    fun isDeterministic(): Boolean {
        return transitions.values.all { it.size <= 1 }
    }

    fun getTransitions(state: String, symbol: Char): Set<String> {
        return transitions[Pair(state, symbol)] ?: emptySet()
    }

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
}

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

fun isRegularGrammar(production: String): Boolean {
    // Regular grammar allows one terminal followed by a non-terminal or just a terminal
    return production.all { it.isLowerCase() } || (production.length == 2 && production[1].isUpperCase())
}

fun main() {
    val states = setOf("q0", "q1", "q2", "q3")
    val alphabet = setOf('a', 'b')
    val transitions = mapOf(
        Pair("q0", 'a') to setOf("q1", "q2"),
        Pair("q1", 'b') to setOf("q1"),
        Pair("q1", 'a') to setOf("q2"),
        Pair("q2", 'a') to setOf("q1"),
        Pair("q2", 'b') to setOf("q3")
    )
    val startState = "q0"
    val finalStates = setOf("q3")

    val fa = FiniteAutomaton(states, alphabet, transitions, startState, finalStates)

    // Regular Grammar
    println("Regular Grammar:")
    for ((nonTerminal, productions) in fa.toRegularGrammar()) {
        for (production in productions) {
            println("$nonTerminal → $production")
        }
    }

    // Grammar Classification
    println("\nGrammar Classification:")
    val grammar = mapOf(
        "q0" to listOf("aq1", "bq2"),
        "q1" to listOf("aq2", "bq1"),
        "q2" to listOf("aq1", "bq3"),
        "q3" to listOf("ε")
    )
    println(classifyGrammar(grammar))

    // NDFA to DFA Conversion
    if (!fa.isDeterministic()) {
        println("\nConverting NDFA to DFA...")
        val dfa = fa.toDFA()
        println("DFA states: ${dfa.states}")
        println("DFA transitions:")
        for ((key, dest) in dfa.transitions) {
            println("δ(${key.first}, ${key.second}) = $dest")
        }
        println("DFA final states: ${dfa.finalStates}")
        dfa.visualize("dfa_graph")
    }

    // Visualize the FA
    fa.visualize("fa_graph")
}
