import java.util.*
import kotlin.collections.HashMap
import kotlin.collections.HashSet

const val EPSILON = "ε"

class Grammar(
    var nonTerminals: MutableList<String>,
    val terminals: List<String>,
    var rules: MutableMap<String, MutableSet<String>>,
    val startSymbol: String = "S"
) {
    fun printRules() {
        for ((nonTerminal, productions) in rules) {
            println("$nonTerminal -> ${productions.joinToString(" | ")}")
        }
    }

    fun isCNF(): Boolean {
        for ((nonTerminal, productions) in rules) {
            for (production in productions) {
                if (production.isEmpty() || production.length > 2) {
                    return false
                }
                if (production.length == 1 && production !in terminals) {
                    return false
                }
                if (production.length == 2 && production.any { it.toString() in terminals }) {
                    return false
                }
            }
        }
        return true
    }

    fun eliminateEpsilonProductions() {
        val nullable = mutableSetOf<String>()

        // Find all nullable non-terminals
        for ((nonTerminal, productions) in rules) {
            if (productions.contains(EPSILON)) {
                nullable.add(nonTerminal)
            }
        }

        // Check for indirect nullable non-terminals
        var changes = true
        while (changes) {
            changes = false
            for ((nonTerminal, productions) in rules) {
                if (nonTerminal !in nullable) {
                    for (production in productions) {
                        if (production.all { it.toString() in nullable }) {
                            nullable.add(nonTerminal)
                            changes = true
                            break
                        }
                    }
                }
            }
        }

        // Eliminate epsilon-productions
        val newRules = mutableMapOf<String, MutableSet<String>>()
        for ((nonTerminal, productions) in rules) {
            val newProds = mutableSetOf<String>()
            for (production in productions) {
                if (production != EPSILON) {
                    newProds.addAll(expandNullableProd(production, nullable))
                }
            }
            newRules[nonTerminal] = newProds
        }

        rules = newRules
    }

    private fun expandNullableProd(production: String, nullable: Set<String>): Set<String> {
        val expansions = mutableListOf("")

        for (symbol in production) {
            val newExpansions = mutableListOf<String>()
            if (symbol.toString() in nullable) {
                for (expansion in expansions) {
                    newExpansions.add(expansion + symbol)
                    newExpansions.add(expansion)
                }
            } else {
                for (expansion in expansions) {
                    newExpansions.add(expansion + symbol)
                }
            }
            expansions.clear()
            expansions.addAll(newExpansions)
        }

        return expansions.filter { it.isNotEmpty() }.toSet()
    }

    fun eliminateRenaming() {
        var changes = true
        while (changes) {
            changes = false
            for (nonTerminal in nonTerminals.toList()) {
                val unitProductions = rules[nonTerminal]?.filter { it in nonTerminals }?.toList() ?: continue
                for (unit in unitProductions) {
                    val newProductions = rules[unit] ?: continue
                    if (newProductions.isNotEmpty()) {
                        rules[nonTerminal]?.addAll(newProductions)
                        rules[nonTerminal]?.remove(unit)
                        changes = true
                    }
                }
                rules[nonTerminal]?.removeAll(nonTerminals)
            }
        }
    }

    fun eliminateInaccessibleSymbols() {
        val accessible = mutableSetOf(startSymbol)
        var changes = true
        val oldRules = HashMap(rules)

        while (changes) {
            changes = false
            for (nonTerminal in accessible.toList()) {
                for (production in rules[nonTerminal] ?: continue) {
                    for (symbol in production) {
                        val symbolStr = symbol.toString()
                        if (symbolStr in nonTerminals && symbolStr !in accessible) {
                            accessible.add(symbolStr)
                            changes = true
                        }
                    }
                }
            }
        }

        nonTerminals = accessible.toMutableList()
        rules = oldRules.filterKeys { it in accessible }.toMutableMap()
    }

    fun eliminateNonProductiveSymbols() {
        val productive = mutableSetOf<String>()
        var changes = true

        // Initialize with non-terminals that have direct terminal productions
        for ((nonTerminal, productions) in rules) {
            if (productions.any { prod -> prod.all { it.toString() in terminals } }) {
                productive.add(nonTerminal)
            }
        }

        // Expand to find all productive symbols
        while (changes) {
            changes = false
            for (nonTerminal in nonTerminals) {
                if (nonTerminal !in productive) {
                    for (production in rules[nonTerminal] ?: continue) {
                        if (production.all { symbol ->
                                symbol.toString() in terminals || symbol.toString() in productive
                            }) {
                            productive.add(nonTerminal)
                            changes = true
                            break
                        }
                    }
                }
            }
        }

        nonTerminals = productive.toMutableList()

        val updatedRules = mutableMapOf<String, MutableSet<String>>()
        for (nt in productive) {
            val productiveRules = mutableSetOf<String>()
            for (production in rules[nt] ?: continue) {
                if (production.all { symbol ->
                        symbol.toString() in terminals || symbol.toString() in productive
                    }) {
                    productiveRules.add(production)
                }
            }
            updatedRules[nt] = productiveRules
        }

        rules = updatedRules
    }

    private fun createNewNonTerminal(): String {
        val alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZαβγδζηθικλμνξοπρστυφχψω"

        // Try single letters first
        for (letter in alphabet) {
            val symbol = letter.toString()
            if (symbol !in nonTerminals) {
                nonTerminals.add(symbol)
                return symbol
            }
        }

        // Then try combinations with numbers
        for (letter in alphabet) {
            for (num in 0..99) {
                val symbol = "$letter$num"
                if (symbol !in nonTerminals) {
                    nonTerminals.add(symbol)
                    return symbol
                }
            }
        }

        throw Error("Exhausted all possible non-terminal symbols")
    }

    fun convertToProperCNF() {
        val rhsToNonTerminal = mutableMapOf<String, String>()
        val oldNonTerminals = rules.keys.toList()

        val newRules = mutableMapOf<String, MutableSet<String>>()
        for (nonTerminal in oldNonTerminals) {
            newRules[nonTerminal] = mutableSetOf()
            for (production in rules[nonTerminal] ?: continue) {
                var currentProd = production

                // Handle productions with more than 2 symbols
                while (currentProd.length > 2) {
                    val firstTwoSymbols = currentProd.substring(0, 2)
                    val newNonTerminal = rhsToNonTerminal.getOrPut(firstTwoSymbols) {
                        val newNT = createNewNonTerminal()
                        newRules.getOrPut(newNT) { mutableSetOf() }.add(firstTwoSymbols)
                        newNT
                    }
                    currentProd = newNonTerminal + currentProd.substring(2)
                }
                newRules[nonTerminal]?.add(currentProd)
            }
        }

        // Handle mixed productions (terminals in productions of length 2)
        for ((nonTerminal, productions) in newRules.toList()) {
            val tempProductions = productions.toList()
            for (production in tempProductions) {
                if (production.length == 2 && production.any { it.toString() in terminals }) {
                    val newProduction = StringBuilder()
                    for (symbol in production) {
                        val symbolStr = symbol.toString()
                        if (symbolStr in terminals) {
                            val newNonTerminal = rhsToNonTerminal.getOrPut(symbolStr) {
                                val newNT = createNewNonTerminal()
                                newRules.getOrPut(newNT) { mutableSetOf() }.add(symbolStr)
                                newNT
                            }
                            newProduction.append(newNonTerminal)
                        } else {
                            newProduction.append(symbol)
                        }
                    }
                    productions.remove(production)
                    productions.add(newProduction.toString())
                }
            }
        }

        // Combine old and new rules
        val allNonTerminals = oldNonTerminals + (newRules.keys - oldNonTerminals.toSet())
        rules = allNonTerminals.associateWith { newRules[it] ?: mutableSetOf() }.toMutableMap()
    }

    fun toCNF(printSteps: Boolean = true) {
        if (isCNF()) return

        if (printSteps) {
            println("Original grammar:")
            printRules()
            println()
        }

        eliminateEpsilonProductions()
        if (printSteps) {
            println("1. After eliminating epsilon productions:")
            printRules()
            println()
        }

        eliminateRenaming()
        if (printSteps) {
            println("2. After eliminating renaming productions:")
            printRules()
            println()
        }

        eliminateInaccessibleSymbols()
        if (printSteps) {
            println("3. After eliminating inaccessible symbols:")
            printRules()
            println()
        }

        eliminateNonProductiveSymbols()
        if (printSteps) {
            println("4. After eliminating non-productive symbols:")
            printRules()
            println()
        }

        convertToProperCNF()
        if (printSteps) {
            println("5. After converting to CNF:")
            printRules()
            println()
        }
    }
}

fun main() {
    // Variant 4 grammar
    val nonTerminals = mutableListOf("S", "A", "B", "C", "D")
    val terminals = listOf("a", "b", "c")
    val rules = mutableMapOf(
        "S" to mutableSetOf("aB", "bA", "A"),
        "A" to mutableSetOf("B", "AS", "bBAB", "b"),
        "B" to mutableSetOf("b", "bS", "aD", "c"),
        "D" to mutableSetOf("AA"),
        "C" to mutableSetOf("Ba")
    )

    val grammar = Grammar(nonTerminals, terminals, rules)
    println("Variant 4 Grammar:")
    grammar.printRules()
    println("\nConversion to CNF:")
    grammar.toCNF()

    println("\nFinal CNF Grammar:")
    grammar.printRules()
    println("\nIs in CNF? ${grammar.isCNF()}")
}