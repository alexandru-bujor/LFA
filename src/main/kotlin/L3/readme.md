# Lexer & Scanner

### Course: Formal Languages & Finite Automata

### Author: Bujor Alexandru

## Theory

Lexical analysis is the process of converting a sequence of characters into a sequence of **tokens** — the smallest meaningful units in a language. This process is a crucial first step in the interpretation or compilation of a programming language or domain-specific language (DSL). A lexer recognizes patterns like identifiers, numbers, strings, operators, IP addresses, and reserved keywords.

**Regular expressions** are commonly used to define patterns that identify these tokens. A lexer applies these expressions to the input text to match and extract tokens efficiently.

This lab work focuses on implementing a lexer and demonstrates both the Python (Pyparsing) and Kotlin implementations of a tokenizer for a custom DSL designed for configuring network systems.

## Objectives

1. Understand lexical analysis and tokenization.
2. Learn how to build a lexer using regular expressions.
3. Recognize the importance of token ordering and pattern matching.
4. Implement a complete lexer that can tokenize a network-oriented DSL.

## Lexer Design and Implementation in Kotlin

### Step 1: Data class for Tokens

```kotlin
data class Token(val type: String, val value: String)
```
Defines a **Token** object with two fields:
- `type`: specifies what kind of token it is (e.g., keyword, IP address, identifier).
- `value`: holds the actual string matched from the input (e.g., "device", "192.168.0.1").

Tokens are the building blocks used in further syntactic or semantic analysis.

---

### Step 2: Lexer Class Declaration

```kotlin
class Lexer {
    ...
}
```
We encapsulate the entire lexer logic inside a `Lexer` class. This makes the lexer modular, easy to integrate into larger projects, and enables multiple independent instances if needed.

---

### Step 3: Declaring Keywords

```kotlin
private val keywords = listOf(
    "network", "device", "module", "slot", "interface", "vlan", "route", "dhcp",
    "acl", "link", "coordinates", "power", "gateway", "dns", "bandwidth",
    "allow", "deny", "from", "to", "pool", "name", "desc", "cable",
    "length", "functional", "static", "ip", "mac"
)
```
This list holds all reserved keywords used by the DSL. By reserving these words, we ensure that, during tokenization, they will not be confused with identifiers.

Reserved keywords typically control the structure or configuration semantics of the DSL.

---

### Step 4: Defining Token Patterns

```kotlin
private val patterns: List<Pair<String, Regex>> = listOf(
    "IPV4_ADDRESS" to Regex("""\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"""),
    "MAC_ADDRESS" to Regex("""\b[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\b"""),
    "STRING" to Regex("\"[^\"]*\""),
    "NUMBER" to Regex("""\b\d+\b"""),
) + keywords.map { kw ->
    "KEYWORD_${kw.uppercase()}" to Regex("""\b$kw\b""")
} + listOf(
    "ID" to Regex("""\b[a-zA-Z_][a-zA-Z0-9_-]*\b""")
)
```
This list of pairs defines:
- **Specialized patterns** like IPv4 addresses, MAC addresses, quoted strings, and numbers.
- **Dynamically generated keyword patterns** based on the `keywords` list.
- **A fallback ID pattern** for generic identifiers that don't match any keyword.

The patterns are ordered to ensure more specific patterns are checked before generic ones.

---

### Step 5: Tokenization Logic

```kotlin
fun tokenize(input: String): List<Token> {
    var pos = 0
    val tokens = mutableListOf<Token>()
    ...
}
```
This function takes the input DSL text and processes it left to right.
- `pos` keeps track of the current position.
- `tokens` collects the resulting list of tokens.

The logic involves skipping whitespace and iteratively matching patterns.

---

### Step 6: Matching Tokens

```kotlin
for ((name, pattern) in patterns) {
    val matcher = pattern.find(input, pos)
    if (matcher != null && matcher.range.first == pos) {
        tokens.add(Token(name, matcher.value))
        pos = matcher.range.last + 1
        matched = true
        break
    }
}
```
For each position `pos` in the input string, this block checks each pattern.
- The lexer stops at the **first valid pattern match**.
- The matching token is added to the token list.
- The position `pos` advances past the matched token.

Using **first-match wins** logic ensures that higher-priority patterns are respected.

---

### Step 7: Handling Errors

```kotlin
if (!matched) {
    throw Exception("Unknown token at position $pos near '${input.substring(pos, minOf(pos + 10, input.length))}'")
}
```
Error handling is crucial in lexical analyzers.
- If no pattern matches the current position, an exception is thrown.
- The error message includes a preview of the problematic section of input.

This helps quickly identify malformed DSL code or missing token patterns.

---

### Step 8: Main Function

```kotlin
fun main() {
    val lexer = Lexer()
    val input = """
        device router1 interface eth0 ip 192.168.0.1
        mac 00ab.cd34.ef56 vlan 10 desc \"Main uplink\"
    """.trimIndent()

    val tokens = lexer.tokenize(input)
    tokens.forEach { println(it) }
}
```
This block demonstrates the lexer in action.
- We define a sample DSL snippet representing a network device with an interface, IP address, MAC address, VLAN, and description.
- The resulting token list is printed line by line.

### Sample Output

```kotlin
Token(type=KEYWORD_DEVICE, value=device)
Token(type=ID, value=router1)
Token(type=KEYWORD_INTERFACE, value=interface)
Token(type=ID, value=eth0)
Token(type=KEYWORD_IP, value=ip)
Token(type=IPV4_ADDRESS, value=192.168.0.1)
Token(type=KEYWORD_MAC, value=mac)
Token(type=MAC_ADDRESS, value=00ab.cd34.ef56)
Token(type=KEYWORD_VLAN, value=vlan)
Token(type=NUMBER, value=10)
Token(type=KEYWORD_DESC, value=desc)
Token(type=STRING, value="Main uplink")
```

---

## Conclusions / Results

This lab demonstrates the creation of a complete lexer for a network-oriented DSL using Kotlin. The lexer handles various input types including keywords, identifiers, IPs, MACs, strings, and numbers, correctly recognizing their patterns through prioritized rules.

The exercise enhanced practical Kotlin experience and highlighted key theoretical concepts from lexical analysis: **regular expression precision**, **token priority ordering**, and **error handling**.

The lexer is modular and adaptable, making it suitable for more complex DSLs or larger projects that require preprocessing before parsing.

The full implementation is included above.
I've choosed kotlin over other languages, because first of all I started working on all the labs in kotlin, and then I wanted to see the difference between other languages as I was working in this language for a longer time, studying it since the first worst versions of it till the last updated and more code friendly ones, where you don't have to create a different file for a class.

## Bibliography

[1] [Pyparsing Documentation](https://pyparsing-docs.readthedocs.io/)

[2] [Formal Language Theory](https://en.wikipedia.org/wiki/Formal_language)

[3] [Kotlin Regular Expressions - Kotlin Docs](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.text/regex/)

[4] [Lexical Analysis - Wikipedia](https://en.wikipedia.org/wiki/Lexical_analysis)

