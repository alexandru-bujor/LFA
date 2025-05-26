# Parser & Building an Abstract Syntax Tree

### Course: Formal Languages & Finite Automata

### Author: Bujor Alexandru

## Theory

Parsing is a fundamental process in computer science and language processing where a sequence of characters (such as the text of a program) is analyzed to determine its grammatical structure with respect to a given formal grammar [1]. Parsing is crucial for a variety of applications including compilers, interpreters, and data processing tools.

Parsing involves two primary stages: lexical analysis and syntactic analysis. **Lexical analysis** (performed by a **lexer**) breaks down the input into a series of tokens, which are sequences of characters with a collective meaning. **Syntactic analysis** (performed by a **parser**) then organizes these tokens into a hierarchical structure that reflects the grammar of the language.

Implementing a parser can be done manually, where a developer writes code to handle each expected pattern in the input. However, it's more common to use a parser generator like **PLY (Python Lex-Yacc)** [2], which allows for defining grammar rules declaratively. PLY takes these rules and generates Python code that can parse texts according to the defined grammar. This greatly simplifies the development of parsers, ensuring accuracy and efficiency.

An Abstract Syntax Tree (AST) is a tree representation of the abstract syntactic structure of source code written in a programming language [3]. Each node in the tree denotes a construction occurring in the source code. The abstract nature of the syntax tree is due to its omission of certain syntactic details which are not relevant for the analysis or transformation of the source code.

## Objectives

1. Get familiar with parsing, what it is and how it can be programmed.
2. Get familiar with the concept of AST.
3. In addition to what has been done in the 3rd lab work do the following:
   1. In case you didn't have a type that denotes the possible types of tokens you need to:
      1. Have a type **_TokenType_** (like an enum) that can be used in the lexical analysis to categorize the tokens.
      2. Please use regular expressions to identify the type of the token.
   2. Implement the necessary data structures for an AST that could be used for the text you have processed in the 3rd lab work.
   3. Implement a simple parser program that could extract the syntactic information from the input text.

## Implementation

I build four main Python modules, plus a Jupyter notebook for testing and visualization:

- **lexer.py**: regex-based lexical analyzer emitting `(type, value)` tokens.  
- **ast_definitions.py**: `ASTNode` class representing tree nodes.  
- **parser.py**: stack‐based parser that nests context keywords and builds the AST.  
- **utils.py**: utility to render the AST as a Graphviz diagram.  
- **main.ipynb**: Jupyter notebook demonstrating tokenization, AST printing, and Graphviz visualization.

### Lexer

- Defines a `TokenType` enum for all token categories: IP, MAC, strings, numbers, DSL keywords, and a fallback `ID`.

```python
class TokenType(Enum):
    IPV4_ADDRESS = auto()
    MAC_ADDRESS  = auto()
    STRING       = auto()
    NUMBER       = auto()
    # ... all DSL keywords e.g. KEYWORD_DEVICE, KEYWORD_INTERFACE, etc.
    ID           = auto()
```

- Maintains an ordered list of `(TokenType, compiled_regex)` pairs.  
- The `tokenize(text: str) -> List[Token]` function scans the input left-to-right, matching the first regex at each position.  

```python
for ttype, regex in _token_specs:
   m = regex.match(text, pos)
   if not m:
       continue
   tokens.append(Token(ttype, m.group(0)))
   pos = m.end()
   break
```

- Whitespace is skipped; unrecognized characters raise `SyntaxError`.

```python
else:
    raise SyntaxError(f"Illegal character '{text[pos]}' at pos {pos}")
```

### AST Definitions

In my network‐DSL, the AST represents each parsed command and its arguments as a tree of `ASTNode` objects. Key points:

- Each node has a `token_type` (from `TokenType`) and an optional `value` (for literals or identifiers).
- Children of a node represent nested commands or parameters.
- A custom `__repr__` prints the tree indented for easy debugging.
In the context of this image processing DSL, the AST represents the parsed commands as tree-like structures. Below are the class definitions that form the backbone of our AST for the DSL.

```python
class ASTNode:
    def __init__(self, token_type: TokenType, value: Optional[str] = None):
        self.token_type = token_type
        self.value = value
        self.children: List['ASTNode'] = []

    def add_child(self, node: 'ASTNode'):
        self.children.append(node)

    def __repr__(self, level=0) -> str:
        indent = '  ' * level
        text = f"{indent}{self.token_type.name}"
        if self.value is not None:
            text += f"({self.value})"
        for child in self.children:
            text += "" + child.__repr__(level+1)
        return text
```

### Parser

Implements a simple stack‐based parser for our DSL, where certain keywords introduce nested contexts:

1. Define `_context_order`, e.g., `[KEYWORD_NETWORK, KEYWORD_DEVICE, KEYWORD_INTERFACE, …]`.  
2. Maintain a stack of AST nodes, starting with a root `PROGRAM` node.  
3. On a context keyword token: pop to the parent level, create a new node with the next token as its name, push it.  
4. On other keywords: attach a leaf node with its argument.  
5. On stray literals or IDs: attach them as unnamed leaves.


```python
from lexer import tokenize, TokenType, Token
from ast_definitions import ASTNode

def parse(tokens: List[Token]) -> ASTNode:
    root = ASTNode(TokenType.ID, 'PROGRAM')
    stack = [root]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.type in _context_levels:
            level = _context_levels[tok.type]
            while len(stack)-1 > level:
                stack.pop()
            name = tokens[i+1].value
            node = ASTNode(tok.type, name)
            stack[-1].add_child(node)
            stack.append(node)
            i += 2
        elif tok.type.name.startswith('KEYWORD_'):
            arg = tokens[i+1].value if i+1 < len(tokens) else None
            node = ASTNode(tok.type, arg)
            stack[-1].add_child(node)
            i += 2 if arg else 1
        else:
            stack[-1].add_child(ASTNode(tok.type, tok.value))
            i += 1
    return root
```

### Visualization

Visualization is a powerful tool for understanding and debugging ASTs. As such, I created the `render_ast_diagram` function in `utils.py`. This function recursively traverses the AST and creates nodes and edges in a Graphviz `Digraph` object to represent the tree structure.

When `render_ast_diagram` is invoked, it first checks if the provided `node` is an instance of `ASTNode`. If so, a label is generated that combines the type of the node and its name. This is what will be displayed on the graph:

```python
label = f"{node.token_type.name}\n{node.value or ''}"
```

This label is then used to create a Graphviz `node`. If the `node` has an attribute `value`, which typically represents the value of a flag, this information is appended to the label.

Using `node_id` ensures each node is given a unique identifier in the graph, allowing Graphviz to distinguish between different instances of nodes that may share the same name:

```python
graph.node(node_id, label=label)
```

If the current `node` is not the root node (`parent` is not `None`), an edge is drawn from the parent to the current node, thereby constructing the hierarchical relationships between nodes.

The function then recursively processes each child of the current `node`:

```python
for child in node.children:
    render_ast(child, graph, node_id)
```

For nodes that represent leaf elements, such as strings or numbers, these are directly added to the graph without children.

In the event of an error token (`p` is `None`), the function emits a generic syntax error message.

## Conclusions / Results

Through the implementation of a parser and the definition of a structured AST, I have gained insight into how grammatical rules of a language can be transformed into a programmatically manipulable format. The construction of the AST and its subsequent visualization using Graphviz allowed to see the hierarchical nature of language constructs, facilitating a deeper comprehension of the parsing process and error handling within the chosen DSL.

The source code is available in the `/src` folder of this directory, with the detailed results documented in the Jupyter Notebook titled `main.ipynb`. This interactive notebook includes code snippets and execution outputs that demonstrate the implementation of the AST and parser.

## Bibliography

[1] [PLY (Python Lex-Yacc)](https://www.dabeaz.com/ply/)

[2] [Parsing Wiki](https://en.wikipedia.org/wiki/Parsing)

[3] [Abstract Syntax Tree Wiki](https://en.wikipedia.org/wiki/Abstract_syntax_tree)