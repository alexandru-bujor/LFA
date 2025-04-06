fun generateValidStrings(): Triple<List<String>, List<String>, List<String>> {
    // 1. (S|T)(U|V)W*Y+24
    val firstPart = mutableListOf<String>()
    for (firstLetter in listOf('S', 'T')) {
        for (secondLetter in listOf('U', 'V')) {
            for (wCount in 0..5) {
                for (yCount in 1..5) {
                    val wPart = "W".repeat(wCount)
                    val yPart = "Y".repeat(yCount)
                    val combo = "$firstLetter$secondLetter$wPart${yPart}24"
                    firstPart.add(combo)
                }
            }
        }
    }

    // 2. L(M|N)O^3P*Q(2|3)
    val secondPart = mutableListOf<String>()
    for (letter in listOf('M', 'N')) {
        for (pCount in 0..2) {
            val pPart = "P".repeat(pCount)
            for (digit in listOf('2', '3')) {
                val combo = "L${letter}OOO${pPart}Q$digit"
                secondPart.add(combo)
            }
        }
    }

    // 3. R*S(T|U|V)W(X|Y|Z)^2
    val thirdPart = mutableListOf<String>()
    val xyzPairs = mutableListOf<String>()
    for (c1 in listOf('X', 'Y', 'Z')) {
        for (c2 in listOf('X', 'Y', 'Z')) {
            xyzPairs.add("$c1$c2")
        }
    }

    for (rCount in 0..5) {
        val rPart = "R".repeat(rCount)
        for (middleLetter in listOf('T', 'U', 'V')) {
            for (pair in xyzPairs) {
                val combo = "${rPart}S${middleLetter}W$pair"
                thirdPart.add(combo)
            }
        }
    }

    return Triple(firstPart, secondPart, thirdPart)
}

fun sequenceProcessing(string: String): String {
    val explanation = mutableListOf<String>()
    var idx = 0

    // Step 1: (S|T)
    if (string.isEmpty() || string[0] !in listOf('S', 'T')) {
        return "Does not match step 1"
    }
    explanation.add("Step 1: Matched '${string[0]}' as (S|T)")
    idx++

    // Step 2: (U|V)
    if (idx >= string.length || string[idx] !in listOf('U', 'V')) {
        return "Does not match step 2"
    }
    explanation.add("Step 2: Matched '${string[idx]}' as (U|V)")
    idx++

    // Step 3: W*
    var wCount = 0
    while (idx < string.length && string[idx] == 'W') {
        wCount++
        idx++
    }
    explanation.add("Step 3: Matched 'W' repeated $wCount times")

    // Step 4: Y+
    var yCount = 0
    while (idx < string.length && string[idx] == 'Y') {
        yCount++
        idx++
    }
    if (yCount < 1) {
        return "Does not match step 4"
    }
    explanation.add("Step 4: Matched 'Y' repeated $yCount times")

    // Step 5: 24
    if (idx + 2 <= string.length && string.substring(idx, idx + 2) == "24") {
        explanation.add("Step 5: Matched '24'")
        idx += 2
    } else {
        return "Does not match step 5"
    }

    // Final check
    if (idx == string.length) {
        explanation.add("String fully matched expression 1!")
    } else {
        explanation.add("String has extra chars beyond the pattern.")
    }

    return explanation.joinToString("\n")
}

fun main() {
    val (p1, p2, p3) = generateValidStrings()

    println("===== Expression 1 matches =====")
    for (s in p1.take(10)) { // First 10 elements
        println(s)
    }
    println("Total count: ${p1.size}")

    println("\n===== Expression 2 matches =====")
    for (s in p2.take(10)) // First 10 elements
        println(s)
    println("Total count: ${p2.size}")

    println("\n===== Expression 3 matches =====")
    for (s in p3.take(10)) // First 10 elements
        println(s)
    println("Total count: ${p3.size}")

    println("\n===== Bonus point test string =====")
    println("Enter test string for expression 1 (e.g., SUWWYY24):")
    val testString = readLine() ?: ""
    println(sequenceProcessing(testString))
}