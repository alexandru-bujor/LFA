def parse_expression(s, pos=0, stop_chars=set(')')):
    """
    Parses an expression which may contain concatenation and alternation (using '|').
    Returns a parse tree and the new position.
    """
    alternatives = []
    sequence = []
    while pos < len(s) and s[pos] not in stop_chars:
        if s[pos] == '|':
            # End the current alternative and start a new one.
            alternatives.append(sequence_to_node(sequence))
            sequence = []
            pos += 1  # Skip the '|' character.
        else:
            node, pos = parse_atom(s, pos)
            sequence.append(node)
    # Append the final alternative.
    alternatives.append(sequence_to_node(sequence))
    if len(alternatives) == 1:
        return alternatives[0], pos
    else:
        return {"type": "alternation", "options": alternatives}, pos


def sequence_to_node(seq):
    """
    Combines a list of nodes into a sequence node.
    If only one node is present, returns it directly.
    """
    if not seq:
        return {"type": "literal", "value": ""}
    if len(seq) == 1:
        return seq[0]
    return {"type": "sequence", "elements": seq}


def parse_atom(s, pos):
    """
    Parses a single atom which is either a group (in parentheses) or a literal.
    After reading the atom, it checks for an attached quantifier (*, +, or ^number).
    Returns the constructed node and the new position.
    """
    if s[pos] == '(':
        # Parse a grouped subexpression.
        pos += 1  # Skip '('
        node, pos = parse_expression(s, pos, stop_chars={')'})
        if pos >= len(s) or s[pos] != ')':
            raise Exception("Missing closing parenthesis")
        pos += 1  # Skip ')'
    else:
        # Parse consecutive literal characters until a special char is encountered.
        start = pos
        while pos < len(s) and s[pos] not in set("()*+|^"):
            pos += 1
        literal = s[start:pos]
        node = {"type": "literal", "value": literal}

    # Check for quantifiers following the atom.
    if pos < len(s):
        if s[pos] == '*':
            # 0 to 5 repetitions.
            node = {"type": "repeat", "node": node, "min": 0, "max": 5}
            pos += 1
        elif s[pos] == '+':
            # 1 to 5 repetitions.
            node = {"type": "repeat", "node": node, "min": 1, "max": 5}
            pos += 1
        elif s[pos] == '^':
            # Exact repetition as specified by the number following '^'.
            pos += 1  # Skip '^'
            num_start = pos
            while pos < len(s) and s[pos].isdigit():
                pos += 1
            if num_start == pos:
                raise Exception("Expected number after '^'")
            number = int(s[num_start:pos])
            node = {"type": "repeat", "node": node, "min": number, "max": number}
    return node, pos


def parse_regex(s):
    """
    Top-level regex parser. Returns the parse tree.
    """
    tree, pos = parse_expression(s, 0, stop_chars=set())
    if pos != len(s):
        raise Exception("Unexpected characters at end of regex")
    return tree


def generate_from_tree(node):
    """
    Recursively generates all strings that match the parsed regex node.
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
    Given a regex string, parse it into a tree and generate all valid strings.
    """
    tree = parse_regex(regex)
    return generate_from_tree(tree)


# --- Dynamic Sequence Processing (Step-by-Step Matching) --- #

def process_node(node, string, pos):
    """
    Recursively processes the parse tree node against the given string starting at 'pos'.
    Returns a tuple (explanation, new_pos, success), where:
      - explanation is a list of strings detailing the processing steps,
      - new_pos is the updated position in the string,
      - success is a boolean indicating a successful match.
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
        for i, elem in enumerate(node["elements"]):
            exp_elem, new_pos, success = process_node(elem, string, pos)
            explanation.extend(exp_elem)
            if not success:
                return explanation, new_pos, False
            pos = new_pos
        return explanation, pos, True

    elif node_type == "alternation":
        # Attempt each alternative.
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
        # Try greedy matching up to 'max' times.
        while count < node["max"]:
            exp_inner, new_pos, success = process_node(node["node"], string, current_pos)
            if success and new_pos > current_pos:  # Ensure progress is made.
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

if __name__ == "__main__":
    # List of regexes for Variant 4.
    regex_list = [
        "(S|T)(U|V)W*Y+24",
        "L(M|N)O^3P*Q(2|3)",
        "R*S(T|U|V)W(X|Y|Z)^2",
        "O(P|Q|R)+2(3|4)" # example from variant 3
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
