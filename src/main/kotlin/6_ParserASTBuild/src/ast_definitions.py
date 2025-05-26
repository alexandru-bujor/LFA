from typing import List
from lexer import TokenType

class ASTNode:
    def __init__(self, token_type: TokenType, value: str = None):
        self.token_type = token_type
        self.value = value
        self.children: List['ASTNode'] = []

    def add_child(self, node: 'ASTNode'):
        self.children.append(node)

    def __repr__(self, level=0):
        indent = '  ' * level
        val = f": {self.value}" if self.value is not None else ""
        s = f"{indent}{self.token_type.name}{val}"
        for child in self.children:
            s += "\n" + child.__repr__(level+1)
        return s