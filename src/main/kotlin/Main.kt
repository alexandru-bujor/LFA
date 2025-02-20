import kotlin.random.Random

class Grammar {
    // Variant 4 definition
    private val nonTerminals: Set<String> = setOf("S", "L", "D")
    private val terminals: Set<String> = setOf("a", "b", "c", "d", "e", "f", "j")
    private val productions: Map<String, List<String>> = mapOf(
        "S" to listOf("aS", "bS", "cD", "dL", "e"),
        "L" to listOf("eL", "fL", "jD", "e"),
        "D" to listOf("eD", "d")
    )
    private val startSymbol: String = "S"
    private val maxDepth: Int = 15

    private fun _derive(symbol: String, depth: Int = 0): String {
        if (depth > maxDepth) {
            return ""
        }

        if (symbol in terminals) {
            return symbol
        }

        val prodList = productions[symbol] ?: listOf("")
        val production = prodList.random()

        return production.map { _derive(it.toString(), depth + 1) }.joinToString("")
    }


    fun generateValidStrings(count: Int = 5): List<String> {
        val results = mutableSetOf<String>()
        while (results.size < count) {
            val candidate = _derive(startSymbol)
            if (candidate.isNotEmpty() && candidate.length <= maxDepth) {
                results.add(candidate)
            }
        }
        return results.toList()
    }


    fun toFiniteAutomaton(): FiniteAutomaton {

        val states = mutableSetOf<String>()
        nonTerminals.forEach { states.add("q_$it") }
        states.add("q_start")
        states.add("q_accept")


        val transitions = mutableMapOf<String, MutableMap<Char, String>>()
        for (state in states) {
            transitions[state] = mutableMapOf()
        }


        for (nt in nonTerminals) {
            val state = "q_$nt"
            val prodList = productions[nt] ?: emptyList()
            for (prod in prodList) {
                if (prod.isEmpty()) continue
                val symbol = prod[0]
                val nextState = if (prod.length > 1 && prod[1].toString() in nonTerminals) {
                    "q_${prod[1]}"
                } else {
                    "q_accept"
                }
                transitions[state]!![symbol] = nextState
            }
        }


        val startProdList = productions[startSymbol] ?: emptyList()
        for (prod in startProdList) {
            if (prod.isEmpty()) continue
            val symbol = prod[0]
            val nextState = if (prod.length > 1 && prod[1].toString() in nonTerminals) {
                "q_${prod[1]}"
            } else {
                "q_accept"
            }
            transitions["q_start"]!![symbol] = nextState
        }


        val alphabet = terminals.map { it[0] }.toSet()
        return FiniteAutomaton(states, alphabet, transitions, "q_start", setOf("q_accept"))
    }
}

class FiniteAutomaton(
    private val states: Set<String>,
    private val alphabet: Set<Char>,
    private val transitions: Map<String, MutableMap<Char, String>>,
    private val startState: String,
    private val acceptStates: Set<String>
) {

    fun accepts(inputString: String): Boolean {
        var currentState = startState
        for (char in inputString) {
            if (char !in alphabet) return false
            val trans = transitions[currentState] ?: return false
            if (!trans.containsKey(char)) return false
            currentState = trans[char]!!
        }
        return currentState in acceptStates
    }
}

fun main() {
    val grammar = Grammar()


    val generated = grammar.generateValidStrings(5)
    println("Generated Strings:")
    for (s in generated) {
        println("  $s")
    }


    val fa = grammar.toFiniteAutomaton()
    val testSamples = listOf(
        "aae", "bdde", "cd", "deL", "cf", "e", "af", "ad"
    )
    println("\nFinite Automaton Test Results:")
    for (test in testSamples) {
        val status = if (fa.accepts(test)) "valid" else "invalid"
        println("  '$test': $status")
    }
}