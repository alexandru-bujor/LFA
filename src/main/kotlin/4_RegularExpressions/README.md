# Regular Expressions

### Course: Formal Languages & Finite Automata

### Author: Bujor ALexandru

## Theory

Regular expressions (regex) are a formal method for describing patterns in strings. They are used to search, match, and manipulate text in a wide variety of applications including lexical analysis, data validation, and text processing. In the context of formal languages, regular expressions describe regular languages and serve as the basis for designing finite automata.

## Objectives

1. Explain what regular expressions are and their practical applications.
2. Dynamically generate valid combinations of strings that conform to specified regular expressions.
3. Implement a solution that, given a regex (with unbounded parts limited to 5 repetitions), produces all valid strings.
4. **Bonus:** Develop a dynamic function to demonstrate, step by step, how a given string is processed by the regex—this function interprets the regex structure on the fly rather than relying on a static implementation.

## Regular Expressions

### Variant 4

For Variant 4, the following three complex regular expressions were considered:

1. **Expression 1:** `(S|T)(U|V)W*Y+24`  
   - **(S|T):** The first character is either `S` or `T`.
   - **(U|V):** The second character is either `U` or `V`.
   - **W\*:** Zero or more occurrences of `W` (limited to 5 repetitions).
   - **Y+:** At least one occurrence of `Y` (limited to 5 repetitions).
   - **24:** The literal substring `24` at the end.

2. **Expression 2:** `L(M|N)O^3P*Q(2|3)`  
   - **L:** A literal `L`.
   - **(M|N):** Either `M` or `N`.
   - **O^3:** Exactly three occurrences of `O`.
   - **P\*:** Zero or more occurrences of `P` (limited to 5 repetitions).
   - **Q:** A literal `Q`.
   - **(2|3):** Either `2` or `3`.

3. **Expression 3:** `R*S(T|U|V)W(X|Y|Z)^2`  
   - **R\*:** Zero or more occurrences of `R` (limited to 5 repetitions).
   - **S:** A literal `S`.
   - **(T|U|V):** Either `T`, `U`, or `V`.
   - **W:** A literal `w`.
   - **(X|Y|Z)^2:** Exactly two characters, each chosen from `x`, `y`, or `z`.

*An additional example (e.g. "O(P|Q|R)+2(3|4)") from another variant may be included.*

## Implementation

The implementation comprises two main parts:

### 1. Dynamic Regex Parsing and Generation

The first part is a set of functions that:
- **Parse:** Convert a regex string (from our restricted grammar) into a parse tree.  
  - `parse_expression`, `parse_atom`, and `sequence_to_node` handle concatenation, alternation, grouping, and quantifiers.
- **Generate:** Recursively traverse the parse tree to generate all strings that match the regex using `generate_from_tree`.
- **Interface:** The function `generate_valid_from_regex` takes any allowed regex string and returns the list of valid strings (ensuring repetition limits as specified).

```python
   def parse_expression(s, pos=0, stop_chars=set(')')):
       """
       Parses an expression with concatenation and alternation ('|').
       Returns a parse tree and the updated position.
       """
       alternatives = []
       sequence = []
       while pos < len(s) and s[pos] not in stop_chars:
           if s[pos] == '|':
               # When a '|' is encountered, finish the current sequence and start a new alternative.
               alternatives.append(sequence_to_node(sequence))
               sequence = []
               pos += 1  # Skip the '|' character.
           else:
               node, pos = parse_atom(s, pos)
               sequence.append(node)
       alternatives.append(sequence_to_node(sequence))
       if len(alternatives) == 1:
           return alternatives[0], pos
       else:
           return {"type": "alternation", "options": alternatives}, pos
```

- This function iterates over the regex string until it reaches a stopping character (by default, )).
- It uses a list called sequence to gather tokens (nodes) that are concatenated.
- When a '|' character is found, the current sequence is finished and saved as one alternative.
- Finally, if only one alternative exists, that node is returned; otherwise, an alternation node is built.

```python
def sequence_to_node(seq):
    """
    Combines nodes into a sequence node.
    Returns a single node if the list has one element.
    """
    if not seq:
        return {"type": "literal", "value": ""}
    if len(seq) == 1:
        return seq[0]
    return {"type": "sequence", "elements": seq}
```
- This helper function takes a list of nodes and combines them into a sequence.
- If the list is empty, it returns an empty literal node.
- If there is only one element, that element is returned directly; otherwise, a sequence node containing all elements is created.

```python
def parse_atom(s, pos):
    """
    Parses a single atom (either a group or a literal) and handles attached quantifiers.
    Supported quantifiers:
      - '*' for 0 to 5 repetitions.
      - '+' for 1 to 5 repetitions.
      - '^N' for exactly N repetitions.
    """
    if s[pos] == '(':
        pos += 1  # Skip '('
        node, pos = parse_expression(s, pos, stop_chars={')'})
        if pos >= len(s) or s[pos] != ')':
            raise Exception("Missing closing parenthesis")
        pos += 1  # Skip ')'
    else:
        start = pos
        while pos < len(s) and s[pos] not in set("()*+|^"):
            pos += 1
        literal = s[start:pos]
        node = {"type": "literal", "value": literal}

    if pos < len(s):
        if s[pos] == '*':
            node = {"type": "repeat", "node": node, "min": 0, "max": 5}
            pos += 1
        elif s[pos] == '+':
            node = {"type": "repeat", "node": node, "min": 1, "max": 5}
            pos += 1
        elif s[pos] == '^':
            pos += 1
            num_start = pos
            while pos < len(s) and s[pos].isdigit():
                pos += 1
            if num_start == pos:
                raise Exception("Expected number after '^'")
            number = int(s[num_start:pos])
            node = {"type": "repeat", "node": node, "min": number, "max": number}
    return node, pos
```

- This function examines the current character. If it is an opening parenthesis, it recursively calls parse_expression to parse the group.
- Otherwise, it reads literal characters until a special character is encountered.
- After reading the literal or group, it checks if a quantifier (*, +, or ^ followed by a number) is present and modifies the node accordingly, adding repetition bounds.

```python
def parse_regex(s):
    """
    Top-level parser that returns the full parse tree for the regex.
    """
    tree, pos = parse_expression(s, 0, stop_chars=set())
    if pos != len(s):
        raise Exception("Unexpected characters at end of regex")
    return tree

def generate_from_tree(node):
    """
    Recursively generates all strings matching the given parse tree node.
    """
    t = node["type"]
    if t == "literal":
        return [node["value"]]
    elif t == "sequence":
        result = [""]
        for elem in node["elements"]:
            new_result = []
            subs = generate_from_tree(elem)
            for prefix in result:
                for sub in subs:
                    new_result.append(prefix + sub)
            result = new_result
        return result
    elif t == "alternation":
        results = []
        for option in node["options"]:
            results.extend(generate_from_tree(option))
        return results
    elif t == "repeat":
        subs = generate_from_tree(node["node"])
        results = []
        for count in range(node["min"], node["max"] + 1):
            if count == 0:
                results.append("")
            else:
                temp = [""]
                for _ in range(count):
                    new_temp = []
                    for prefix in temp:
                        for sub in subs:
                            new_temp.append(prefix + sub)
                    temp = new_temp
                results.extend(temp)
        return results
    else:
        raise Exception("Unknown node type: " + t)

def generate_valid_from_regex(regex):
    """
    Given a regex string, returns all valid matching strings.
    """
    tree = parse_regex(regex)
    return generate_from_tree(tree)
```

- parse_regex is the top-level interface that converts the entire regex string into a parse tree.
- generate_from_tree recursively traverses the parse tree:
  - For a literal node, it returns its value.
  - For a sequence node, it concatenates all generated sub-strings.
  - For an alternation node, it combines the results from each option.
  - For a repeat node, it generates strings by repeating the node’s subpattern a number of times within the allowed bounds.
- Finally, generate_valid_from_regex ties these together by parsing the regex and then producing all valid strings.

### 2. Dynamic Step-by-Step (Sequence) Processing
For the bonus task, the function `dynamic_sequence_processing` dynamically processes a given test string against any regex (from our restricted grammar). Instead of hardcoding the steps, it uses a recursive helper function `process_node` that traverses the parse tree and logs each matching attempt.

```python
def process_node(node, string, pos):
    """
    Recursively processes the parse tree node against the given string starting at 'pos'.
    Returns a tuple (explanation, new_pos, success) where:
      - explanation is a list detailing each matching step.
      - new_pos is the updated string position.
      - success is True if the node matches; otherwise False.
    """
    explanation = []
    node_type = node["type"]

    if node_type == "literal":
        literal = node["value"]
        if string.startswith(literal, pos):
            explanation.append(f"Matched literal '{literal}' at position {pos}")
            return explanation, pos + len(literal), True
        else:
            return [f"Failed to match literal '{literal}' at position {pos}"], pos, False

    elif node_type == "sequence":
        for elem in node["elements"]:
            exp_elem, new_pos, success = process_node(elem, string, pos)
            explanation.extend(exp_elem)
            if not success:
                return explanation, new_pos, False
            pos = new_pos
        return explanation, pos, True

    elif node_type == "alternation":
        alt_explanations = []
        for option in node["options"]:
            exp_option, new_pos, success = process_node(option, string, pos)
            if success:
                explanation.append(f"Matched alternation option at position {pos}")
                explanation.extend(exp_option)
                return explanation, new_pos, True
            else:
                alt_explanations.append(exp_option)
        explanation.append(f"Failed to match any alternation option at position {pos}")
        explanation.extend(sum(alt_explanations, []))
        return explanation, pos, False

    elif node_type == "repeat":
        count = 0
        all_explanations = []
        current_pos = pos
        while count < node["max"]:
            exp_inner, new_pos, success = process_node(node["node"], string, current_pos)
            if success and new_pos > current_pos:
                all_explanations.extend(exp_inner)
                count += 1
                current_pos = new_pos
            else:
                break
        if count < node["min"]:
            all_explanations.append(f"Repeat failed: expected at least {node['min']} matches but got {count} at position {pos}")
            return all_explanations, current_pos, False
        all_explanations.append(f"Matched repeat node {count} times from position {pos} to {current_pos}")
        return all_explanations, current_pos, True

    else:
        return [f"Unknown node type: {node_type}"], pos, False
```

- This function processes a single node from the parse tree against the test string, starting at a specified position.
- Literal nodes: It checks if the substring at the current position matches the literal; if so, it logs the match.
- Sequence nodes: It processes each element sequentially, updating the position as it goes and logging each matching step.
- Alternation nodes: It tries each alternative and logs which option (if any) succeeded.
- Repeat nodes: It attempts to match the node repeatedly (up to the maximum allowed). If the number of successful repetitions falls short of the minimum requirement, the function reports a failure.
- The function returns a tuple containing the detailed explanation, the new position in the string, and whether the match was successful.

```python
def dynamic_sequence_processing(regex, string):
    """
    Dynamically processes the given regex against the test string,
    producing a step-by-step explanation of the matching process.
    """
    try:
        tree = parse_regex(regex)
    except Exception as e:
        return f"Regex parsing error: {e}"
    explanation, pos, success = process_node(tree, string, 0)
    if not success:
        explanation.append("Matching failed.")
    elif pos < len(string):
        explanation.append(f"Extra characters remain after position {pos}.")
    else:
        explanation.append("String fully matched the regex!")
    return "\n".join(explanation)
```

- This top-level function first parses the regex to build a parse tree.
- It then calls process_node on the entire tree and the test string.
- The function compiles all step-by-step explanations into a single output string.
- Finally, it adds a message indicating whether the entire string was successfully matched or if extra characters remained.

## Testing
The main testing section demonstrates both the generation of valid strings and the dynamic step-by-step processing of any given regex. For each regex in our list, the code displays a sample of the generated valid strings and the total number of combinations. The dynamic sequence-processing function then provides detailed feedback for a user-supplied test string.
```python
if __name__ == "__main__":
    # List of regexes for Variant 4.
    regex_list = [
        "(S|T)(U|V)W*Y+24",
        "L(M|N)O^3P*Q(2|3)",
        "R*S(T|U|V)W(X|Y|Z)^2",
        "O(P|Q|R)+2(3|4)"  # example from another variant
    ]

    for i, regex in enumerate(regex_list, start=1):
        print(f"===== Expression {i}: {regex} =====")
        try:
            valid_strings = generate_valid_from_regex(regex)
            print("First 10 strings:")
            for s in valid_strings[:10]:
                print(s)
            print("Total count:", len(valid_strings))
        except Exception as e:
            print(f"Error generating strings for {regex}: {e}")
        print("\n")

    print("===== Bonus: Dynamic Sequence Processing =====")
    regex = input("Enter a regex: ")
    test_str = input("Enter test string for dynamic processing: ")
    result = dynamic_sequence_processing(regex, test_str)
    print(result)

```

## Output Examples
### 1. Generation of Valid Strings::
```
===== Expression 1 matches =====
SUY24
SUYY24
SUYYY24
SUYYYY24
SUYYYYY24
SUWY24
SUWYY24
SUWYYY24
SUWYYYY24
SUWYYYYY24
Total count 120
```
### 2. Dynamic Sequence Processing:
```
===== Bonus point test string =====
Enter regex: (S|T)(U|V)W*Y+24
Enter test string for regex: SUWWYY241
Matched literal 'S' at position 0
Matched literal 'U' at position 1
Matched literal 'W' at position 2
Matched literal 'W' at position 3
Matched literal 'Y' at position 4
Matched literal 'Y' at position 5
Matched literal '24' at position 6
String fully matched the regex!
```

## Conclusions / Results

This lab demonstrates the generation of valid strings based on complex regular expressions. The implementation covers three different expressions by generating combinations that conform to the given patterns, while enforcing a repetition limit of 5 for unbounded sections and ensuring minimum occurrences where required (e.g., at least one `Y` in Expression 1). Additionally, a bonus function illustrates the step-by-step matching process for one of the expressions, thereby deepening the understanding of how regular expressions are applied in practice.

The approach highlights the importance of precise regex design, controlled repetition to avoid combinatorial explosion, and the value of a systematic process for matching and validation. The complete solution and its behavior are detailed in the provided code examples.

## Bibliography

[1] [Regular Expressions - Python Docs](https://docs.python.org/3/library/re.html)

[2] [Formal Language Theory](https://en.wikipedia.org/wiki/Formal_language)

[3] [Regular Expressions Tutorial](https://www.regular-expressions.info/)
