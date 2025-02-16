package org.example.L1

class Grammar(
    val nonTerminals: Set<String>,
    val terminals: Set<Char>,
    val productions: Map<String, List<String>>,
    val startSymbol: String
) {
    fun generateString(): String {
        var current = startSymbol
        val result = StringBuilder()

        while (current.any { it.isUpperCase() }) {
            val nonTerminal = current.first { it.isUpperCase() }.toString()
            val production = productions[nonTerminal]?.random() ?: ""
            current = current.replaceFirst(nonTerminal, production)
        }

        return current
    }

    fun toFiniteAutomaton(): FiniteAutomaton {
        val states = setOf("q0", "q1", "q2", "q3", "q4", "q5")
        val transitions = mutableMapOf<Pair<String, Char>, String>()

        // Adăugăm tranzițiile corespunzătoare
        transitions[Pair("q0", 'a')] = "q1"
        transitions[Pair("q0", 'b')] = "q1"
        transitions[Pair("q0", 'c')] = "q2"
        transitions[Pair("q0", 'd')] = "q3"
        transitions[Pair("q0", 'e')] = "q4"
        transitions[Pair("q1", 'a')] = "q1"
        transitions[Pair("q1", 'b')] = "q1"
        transitions[Pair("q1", 'c')] = "q2"
        transitions[Pair("q1", 'd')] = "q3"
        transitions[Pair("q1", 'e')] = "q4"
        transitions[Pair("q2", 'e')] = "q5"
        transitions[Pair("q2", 'd')] = "q3"
        transitions[Pair("q3", 'e')] = "q5"
        transitions[Pair("q3", 'f')] = "q3"
        transitions[Pair("q3", 'j')] = "q2"
        transitions[Pair("q4", 'e')] = "q4"
        transitions[Pair("q5", 'e')] = "q5"

        return FiniteAutomaton(states, terminals, transitions, "q0", setOf("q4", "q5"))
    }
}
