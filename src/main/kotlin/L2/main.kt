package L2

import java.awt.Desktop
import java.io.File
import javax.imageio.ImageIO
import javax.swing.ImageIcon
import javax.swing.JFrame
import javax.swing.JLabel
import javax.swing.JScrollPane

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
            .mapValues { setOf(stateMap[it.value]!!) }

        return FiniteAutomaton(
            states = stateMap.values.toSet(),
            alphabet = alphabet,
            transitions = newTransitions,
            startState = stateMap[startClosure]!!,
            finalStates = dfaFinalStates.map { stateMap[it]!! }.toSet()
        )
    }

    fun visualize(filename: String) {
        val dotFile = File("$filename.dot")
        val pngFile = File("$filename.png")

        // Generate DOT content
        val dot = StringBuilder("digraph FiniteAutomaton {\n")
        dot.append("  rankdir=LR;\n")

        for (state in states) {
            val shape = if (state in finalStates) "doublecircle" else "circle"
            dot.append("  \"$state\" [shape=$shape];\n")
        }

        dot.append("  start [shape=none, label=\"\", width=0.0, height=0.0];\n")
        dot.append("  start -> \"$startState\";\n")

        for ((key, dests) in transitions) {
            val (state, symbol) = key
            for (dest in dests) {
                dot.append("  \"$state\" -> \"$dest\" [label=\"$symbol\"];\n")
            }
        }

        dot.append("}")

        // Save DOT file
        dotFile.writeText(dot.toString())

        // Convert DOT to PNG using Graphviz
        try {
            val process = ProcessBuilder("dot", "-Tpng", dotFile.absolutePath, "-o", pngFile.absolutePath)
                .redirectErrorStream(true)
                .start()
            process.waitFor()
            if (!pngFile.exists()) {
                println("Graphviz is required to generate the graph image. Please install Graphviz and ensure 'dot' is in your PATH.")
                return
            }
        } catch (e: Exception) {
            println("Error running Graphviz: ${e.message}")
            return
        }

        // Display the image
        displayImage(pngFile)
    }

    private fun displayImage(imageFile: File) {
        val img = ImageIO.read(imageFile) ?: return
        val icon = ImageIcon(img)
        val label = JLabel(icon)
        val frame = JFrame()

        frame.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
        frame.title = "Finite Automaton Visualization"
        frame.contentPane.add(JScrollPane(label))
        frame.pack()
        frame.setLocationRelativeTo(null)
        frame.isVisible = true
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
    val grammar = fa.toRegularGrammar().mapValues { it.value.toList() }
    println(classifyGrammar(grammar))

    // Visualization of FA
    println("\nVisualizing Finite Automaton...")
    fa.visualize("fa_graph")

    // NDFA to DFA Conversion and Visualization
    if (!fa.isDeterministic()) {
        println("\nConverting NDFA to DFA...")
        val dfa = fa.toDFA()
        dfa.visualize("dfa_graph")
    }
}
