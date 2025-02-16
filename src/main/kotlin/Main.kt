package org.example
import org.example.L1.Grammar

fun main() {
    val grammar = Grammar(
        setOf("S", "A", "B"),
        setOf('a', 'b'),
        mapOf(
            "S" to listOf("aA", "aB"),
            "A" to listOf("bA", "aB"),
            "B" to listOf("aA", "b")
        ),
        "S"
    )

    println("Cuvinte generate de gramatică:")
    repeat(5) { println(grammar.generateString()) }

    val fa = grammar.toFiniteAutomaton()
    println("Testare DFA:")
    println("e" to fa.stringBelongsToLanguage("e"))
    println("aaaa" to fa.stringBelongsToLanguage("aaaa"))
}