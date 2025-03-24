import java.util.regex.Pattern

// -------------------------------
// Token Data Class
// -------------------------------
data class Token(val type: String, val value: String)

// -------------------------------
// Lexer Implementation
// -------------------------------
class Lexer {
    // DSL Keywords
    private val keywords = listOf(
        "network", "device", "module", "slot", "interface", "vlan", "route", "dhcp",
        "acl", "link", "coordinates", "power", "gateway", "dns", "bandwidth",
        "allow", "deny", "from", "to", "pool", "name", "desc", "cable",
        "length", "functional", "static", "ip", "mac"
    )

    // Regex Patterns
    private val patterns: List<Pair<String, Regex>> = listOf(
        "IPV4_ADDRESS" to Regex("""\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"""),
        "MAC_ADDRESS" to Regex("""\b[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\b"""),
        "STRING" to Regex(""""[^"]*""""),
        "NUMBER" to Regex("""\b\d+\b"""),
    ) + keywords.map { kw ->
        "KEYWORD_${kw.uppercase()}" to Regex("""\b$kw\b""")
    } + listOf(
        "ID" to Regex("""\b[a-zA-Z_][a-zA-Z0-9_-]*\b""")
    )

    fun tokenize(input: String): List<Token> {
        var pos = 0
        val tokens = mutableListOf<Token>()

        while (pos < input.length) {
            if (input[pos].isWhitespace()) {
                pos++
                continue
            }

            var matched = false
            for ((name, pattern) in patterns) {
                val matcher = pattern.find(input, pos)
                if (matcher != null && matcher.range.first == pos) {
                    tokens.add(Token(name, matcher.value))
                    pos = matcher.range.last + 1
                    matched = true
                    break
                }
            }

            if (!matched) {
                throw Exception("Unknown token at position $pos near '${input.substring(pos, minOf(pos + 10, input.length))}'")
            }
        }
        return tokens
    }
}

// -------------------------------
// Main Function Example
// -------------------------------
fun main() {
    val lexer = Lexer()
    val input = """
        device router1 interface eth0 ip 192.168.0.1
        mac 00ab.cd34.ef56 vlan 10 desc "Main uplink"
    """.trimIndent()

    val tokens = lexer.tokenize(input)
    tokens.forEach { println(it) }
}
