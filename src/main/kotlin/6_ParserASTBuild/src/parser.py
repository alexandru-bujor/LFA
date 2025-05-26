from typing import List
from lexer import Token, TokenType, tokenize
from ast_definitions import ASTNode

# Keywords that introduce nested contexts, in increasing depth
_context_order = [
    TokenType.KEYWORD_NETWORK,
    TokenType.KEYWORD_DEVICE,
    TokenType.KEYWORD_MODULE,
    TokenType.KEYWORD_SLOT,
    TokenType.KEYWORD_INTERFACE,
]
_context_levels = {tt: idx for idx, tt in enumerate(_context_order)}


def parse(tokens: List[Token]) -> ASTNode:
    """
    Builds a simple AST by nesting context keywords and attaching
    leaf commands and literals under the current context node.
    """
    # root of AST
    root = ASTNode(TokenType.ID, 'PROGRAM')
    stack: List[ASTNode] = [root]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        # context keyword -> nest
        if tok.type in _context_levels:
            level = _context_levels[tok.type]
            # pop back to parent of this context
            while len(stack)-1 > level:
                stack.pop()
            # next token is the context name
            if i+1 < len(tokens):
                name = tokens[i+1].value
                node = ASTNode(tok.type, name)
                stack[-1].add_child(node)
                stack.append(node)
                i += 2
            else:
                raise SyntaxError(f"Expected name after {tok.value}")
        # other keywords (leaf commands)
        elif tok.type.name.startswith('KEYWORD_'):
            if i+1 < len(tokens):
                arg = tokens[i+1].value
                node = ASTNode(tok.type, arg)
                stack[-1].add_child(node)
                i += 2
            else:
                # no argument, just a flag
                node = ASTNode(tok.type)
                stack[-1].add_child(node)
                i += 1
        else:
            # literal or ID
            node = ASTNode(tok.type, tok.value)
            stack[-1].add_child(node)
            i += 1
    return root


if __name__ == '__main__':
    sample = 'device router1 interface eth0 ip 192.168.0.1 mac 00ab.cd34.ef56 vlan 10 desc "Main uplink"'
    tokens = tokenize(sample)
    ast = parse(tokens)
    print(ast)