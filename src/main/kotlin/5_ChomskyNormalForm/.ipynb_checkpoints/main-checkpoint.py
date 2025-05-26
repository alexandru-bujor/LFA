EPSILON = 'ε'


class Grammar:
    def __init__(self, non_terminals, terminals, rules, start='S'):
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.rules = rules
        self.start = start

    def print_rules(self):
        """Print the grammar rules in a readable format."""
        for nt in self.rules:
            print(f"{nt} → {' | '.join(self.rules[nt])}")

    def eliminate_epsilon_productions(self):
        """Step 1: Eliminate ε-productions."""
        # Find all nullable non-terminals
        nullable = set()
        for nt in self.non_terminals:
            if EPSILON in self.rules[nt]:
                nullable.add(nt)

        # Find indirect nullable non-terminals
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for prod in self.rules[nt]:
                    if all(sym in nullable for sym in prod):
                        if nt not in nullable:
                            nullable.add(nt)
                            changed = True

        # Generate new productions without ε
        new_rules = {}
        for nt in self.rules:
            new_prods = []
            for prod in self.rules[nt]:
                if prod != EPSILON:
                    # Generate all possible combinations without nullable symbols
                    expansions = ['']
                    for sym in prod:
                        new_expansions = []
                        for e in expansions:
                            new_expansions.append(e + sym)
                            if sym in nullable:
                                new_expansions.append(e)
                        expansions = new_expansions
                    new_prods.extend([e for e in expansions if e])
            new_rules[nt] = list(set(new_prods))  # Remove duplicates

        self.rules = new_rules
        # Remove ε from terminals if present
        if EPSILON in self.terminals:
            self.terminals.remove(EPSILON)

    def eliminate_renaming(self):
        """Step 2: Eliminate unit productions."""
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                # Find unit productions
                unit_prods = [p for p in self.rules[nt]
                              if len(p) == 1 and p in self.non_terminals]
                for up in unit_prods:
                    # Add productions of the unit non-terminal
                    self.rules[nt].remove(up)
                    for prod in self.rules[up]:
                        if prod not in self.rules[nt]:
                            self.rules[nt].append(prod)
                            changed = True

    def eliminate_inaccessible_symbols(self):
        """Step 3: Eliminate inaccessible symbols."""
        accessible = {self.start}
        changed = True
        while changed:
            changed = False
            for nt in list(accessible):
                for prod in self.rules[nt]:
                    for sym in prod:
                        if sym in self.non_terminals and sym not in accessible:
                            accessible.add(sym)
                            changed = True

        # Remove inaccessible symbols
        self.non_terminals = [nt for nt in self.non_terminals if nt in accessible]
        self.rules = {nt: self.rules[nt] for nt in self.non_terminals}

    def eliminate_non_productive_symbols(self):
        """Step 4: Eliminate non-productive symbols."""
        productive = set()
        # Terminals are productive by definition
        # Find non-terminals that produce terminal strings
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for prod in self.rules[nt]:
                    if all(sym in productive or sym in self.terminals for sym in prod):
                        if nt not in productive:
                            productive.add(nt)
                            changed = True

        # Remove non-productive symbols
        self.non_terminals = [nt for nt in self.non_terminals if nt in productive]
        self.rules = {nt: [prod for prod in self.rules[nt]
                           if all(sym in productive or sym in self.terminals for sym in prod)]
                      for nt in self.non_terminals}

    def _create_new_non_terminal(self, existing):
        """Helper to create new non-terminal symbols."""
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if c not in existing:
                return c
        # If all single letters are used, start combining
        for c1 in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            for c2 in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                new_nt = c1 + c2
                if new_nt not in existing:
                    return new_nt
        raise ValueError("Cannot create new non-terminal symbol")

    def to_cnf(self):
        """Convert grammar to Chomsky Normal Form."""
        # Step 1-4 already implemented
        self.eliminate_epsilon_productions()
        self.eliminate_renaming()
        self.eliminate_inaccessible_symbols()
        self.eliminate_non_productive_symbols()

        # Step 5: Convert remaining productions to CNF
        new_rules = {}
        terminal_productions = {}

        # Create new productions for terminals
        for t in self.terminals:
            new_nt = self._create_new_non_terminal(self.non_terminals)
            terminal_productions[t] = new_nt
            self.non_terminals.append(new_nt)
            new_rules[new_nt] = [t]

        # Process all rules
        for nt in list(self.rules):
            new_prods = []
            for prod in self.rules[nt]:
                # Case 1: Production is single terminal
                if len(prod) == 1 and prod in self.terminals:
                    new_prods.append(prod)
                # Case 2: Production is two symbols (terminal or non-terminal)
                elif len(prod) == 2:
                    # Replace terminals with their new non-terminals
                    new_prod = []
                    for sym in prod:
                        if sym in self.terminals:
                            new_prod.append(terminal_productions[sym])
                        else:
                            new_prod.append(sym)
                    new_prods.append(''.join(new_prod))
                # Case 3: Production length > 2 - break it down
                elif len(prod) > 2:
                    current = prod
                    # Replace terminals first
                    temp = []
                    for sym in current:
                        if sym in self.terminals:
                            temp.append(terminal_productions[sym])
                        else:
                            temp.append(sym)
                    current = ''.join(temp)

                    # Break down long productions
                    while len(current) > 2:
                        first_two = current[:2]
                        remaining = current[2:]

                        # Check if we already have a rule for these two symbols
                        found = False
                        for existing_nt in new_rules:
                            if first_two in new_rules[existing_nt]:
                                new_nt = existing_nt
                                found = True
                                break

                        if not found:
                            new_nt = self._create_new_non_terminal(self.non_terminals)
                            self.non_terminals.append(new_nt)
                            new_rules[new_nt] = [first_two]

                        current = new_nt + remaining
                    new_prods.append(current)
            self.rules[nt] = new_prods

        # Add the new rules we created
        self.rules.update(new_rules)

    def is_cnf(self):
        """Check if grammar is in CNF."""
        for nt in self.rules:
            for prod in self.rules[nt]:
                # Valid CNF productions are:
                # 1. Single terminal
                # 2. Two non-terminals
                if len(prod) == 1 and prod not in self.terminals:
                    return False
                if len(prod) == 2 and any(sym in self.terminals for sym in prod):
                    return False
                if len(prod) > 2:
                    return False
        return True


def main():
    # Variant 4 grammar
    Vn = ['S', 'A', 'B', 'C', 'D']
    Vt = ['a', 'b']
    P = {
        'S': ['aB', 'bA', 'A'],
        'A': ['B', 'AS', 'bBAB', 'b'],
        'B': ['b', 'bS', 'aD', EPSILON],
        'D': ['AA'],
        'C': ['Ba']
    }

    grammar = Grammar(Vn, Vt, P)

    print("Original Grammar:")
    grammar.print_rules()

    print("\nStep 1: Eliminate ε-productions")
    grammar.eliminate_epsilon_productions()
    grammar.print_rules()

    print("\nStep 2: Eliminate renaming")
    grammar.eliminate_renaming()
    grammar.print_rules()

    print("\nStep 3: Eliminate inaccessible symbols")
    grammar.eliminate_inaccessible_symbols()
    grammar.print_rules()

    print("\nStep 4: Eliminate non-productive symbols")
    grammar.eliminate_non_productive_symbols()
    grammar.print_rules()

    print("\nStep 5: Convert to CNF")
    grammar.to_cnf()
    grammar.print_rules()

    print("\nGrammar is now in CNF:", grammar.is_cnf())


if __name__ == "__main__":
    main()