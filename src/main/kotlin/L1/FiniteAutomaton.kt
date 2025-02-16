package org.example.L1

class FiniteAutomaton(
    val states: Set<String>,
    val alphabet: Set<Char>,
    val transitions: Map<Pair<String, Char>, String>,
    val startState: String,
    val finalStates: Set<String>
) {
    fun stringBelongsToLanguage(input: String): Boolean {
        var currentState = startState

        for (symbol in input) {
            val transition = transitions[currentState to symbol]
            if (transition == null) return false
            currentState = transition
        }

        return currentState in finalStates
    }
}
