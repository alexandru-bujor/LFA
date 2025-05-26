import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Union


# Token types
class TokenType(Enum):
    # Data types
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    EQUALS = auto()
    EQEQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMICOLON = auto()

    # Keywords
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    VAR = auto()
    PRINT = auto()

    # Other
    EOF = auto()


# Token class
@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


# AST Node types
class ASTNodeType(Enum):
    PROGRAM = auto()
    VARIABLE_DECLARATION = auto()
    ASSIGNMENT = auto()
    BINARY_OPERATION = auto()
    LITERAL = auto()
    IDENTIFIER = auto()
    IF_STATEMENT = auto()
    WHILE_LOOP = auto()
    FUNCTION_DEFINITION = auto()
    FUNCTION_CALL = auto()
    RETURN_STATEMENT = auto()
    PRINT_STATEMENT = auto()
    BLOCK = auto()


# AST Node classes
class ASTNode:
    pass


@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]


@dataclass
class VariableDeclarationNode(ASTNode):
    identifier: str
    value: ASTNode


@dataclass
class AssignmentNode(ASTNode):
    identifier: str
    value: ASTNode


@dataclass
class BinaryOperationNode(ASTNode):
    left: ASTNode
    operator: TokenType
    right: ASTNode


@dataclass
class LiteralNode(ASTNode):
    value: Union[int, float, str, bool]


@dataclass
class IdentifierNode(ASTNode):
    name: str


@dataclass
class IfStatementNode(ASTNode):
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode]


@dataclass
class WhileLoopNode(ASTNode):
    condition: ASTNode
    body: ASTNode


@dataclass
class FunctionDefinitionNode(ASTNode):
    name: str
    parameters: List[str]
    body: ASTNode


@dataclass
class FunctionCallNode(ASTNode):
    name: str
    arguments: List[ASTNode]


@dataclass
class ReturnStatementNode(ASTNode):
    value: ASTNode


@dataclass
class PrintStatementNode(ASTNode):
    value: ASTNode


@dataclass
class BlockNode(ASTNode):
    statements: List[ASTNode]


# Lexer
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char != '\n' and self.current_char is not None:
            self.advance()
        self.advance()

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            # Try to match token patterns
            token = self.try_match_token()
            if token:
                return token

            raise Exception(f"Unexpected character '{self.current_char}' at line {self.line}, column {self.column}")

        return Token(TokenType.EOF, '', self.line, self.column)

    def try_match_token(self):
        # Match patterns for each token type
        patterns = [
            (TokenType.INT, r'\d+'),
            (TokenType.FLOAT, r'\d+\.\d+'),
            (TokenType.STRING, r'"[^"]*"'),
            (TokenType.BOOL, r'true|false'),
            (TokenType.PLUS, r'\+'),
            (TokenType.MINUS, r'-'),
            (TokenType.MULTIPLY, r'\*'),
            (TokenType.DIVIDE, r'/'),
            (TokenType.EQUALS, r'='),
            (TokenType.EQEQ, r'=='),
            (TokenType.NEQ, r'!='),
            (TokenType.LT, r'<'),
            (TokenType.GT, r'>'),
            (TokenType.LTE, r'<='),
            (TokenType.GTE, r'>='),
            (TokenType.LPAREN, r'\('),
            (TokenType.RPAREN, r'\)'),
            (TokenType.LBRACE, r'\{'),
            (TokenType.RBRACE, r'\}'),
            (TokenType.COMMA, r','),
            (TokenType.SEMICOLON, r';'),
            (TokenType.IF, r'if'),
            (TokenType.ELSE, r'else'),
            (TokenType.WHILE, r'while'),
            (TokenType.FOR, r'for'),
            (TokenType.FUNCTION, r'function'),
            (TokenType.RETURN, r'return'),
            (TokenType.VAR, r'var'),
            (TokenType.PRINT, r'print'),
            (TokenType.IDENTIFIER, r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ]

        for token_type, pattern in patterns:
            regex = re.compile(pattern)
            match = regex.match(self.text, self.pos)
            if match:
                value = match.group()
                token = Token(token_type, value, self.line, self.column)
                for _ in range(len(value)):
                    self.advance()
                return token

        return None


# Parser
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Expected {token_type}, got {self.current_token.type} at line {self.current_token.line}")

    def parse(self):
        statements = []
        while self.current_token.type != TokenType.EOF:
            statements.append(self.parse_statement())
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
        return ProgramNode(statements)

    def parse_statement(self):
        if self.current_token.type == TokenType.VAR:
            return self.parse_variable_declaration()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_loop()
        elif self.current_token.type == TokenType.FUNCTION:
            return self.parse_function_definition()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif self.current_token.type == TokenType.PRINT:
            return self.parse_print_statement()
        elif self.current_token.type == TokenType.IDENTIFIER:
            # Could be assignment or function call
            next_token = self.lexer.get_next_token()
            self.lexer.pos -= len(next_token.value)  # Put it back
            if next_token.type == TokenType.EQUALS:
                return self.parse_assignment()
            elif next_token.type == TokenType.LPAREN:
                return self.parse_function_call()
            else:
                return self.parse_expression()
        else:
            return self.parse_expression()

    def parse_variable_declaration(self):
        self.eat(TokenType.VAR)
        identifier = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.EQUALS)
        value = self.parse_expression()
        return VariableDeclarationNode(identifier, value)

    def parse_assignment(self):
        identifier = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.EQUALS)
        value = self.parse_expression()
        return AssignmentNode(identifier, value)

    def parse_if_statement(self):
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenType.RPAREN)
        then_branch = self.parse_block()

        else_branch = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_branch = self.parse_block()

        return IfStatementNode(condition, then_branch, else_branch)

    def parse_while_loop(self):
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.parse_expression()
        self.eat(TokenType.RPAREN)
        body = self.parse_block()
        return WhileLoopNode(condition, body)

    def parse_function_definition(self):
        self.eat(TokenType.FUNCTION)
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)

        parameters = []
        if self.current_token.type != TokenType.RPAREN:
            parameters.append(self.current_token.value)
            self.eat(TokenType.IDENTIFIER)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                parameters.append(self.current_token.value)
                self.eat(TokenType.IDENTIFIER)

        self.eat(TokenType.RPAREN)
        body = self.parse_block()
        return FunctionDefinitionNode(name, parameters, body)

    def parse_return_statement(self):
        self.eat(TokenType.RETURN)
        value = self.parse_expression()
        return ReturnStatementNode(value)

    def parse_print_statement(self):
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        value = self.parse_expression()
        self.eat(TokenType.RPAREN)
        return PrintStatementNode(value)

    def parse_function_call(self):
        name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)

        arguments = []
        if self.current_token.type != TokenType.RPAREN:
            arguments.append(self.parse_expression())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                arguments.append(self.parse_expression())

        self.eat(TokenType.RPAREN)
        return FunctionCallNode(name, arguments)

    def parse_block(self):
        self.eat(TokenType.LBRACE)
        statements = []

        while self.current_token.type != TokenType.RBRACE:
            statements.append(self.parse_statement())
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)

        self.eat(TokenType.RBRACE)
        return BlockNode(statements)

    def parse_expression(self):
        return self.parse_binary_expression(self.parse_term, [
            (TokenType.EQEQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE),
            (TokenType.PLUS, TokenType.MINUS),
            (TokenType.MULTIPLY, TokenType.DIVIDE)
        ])

    def parse_term(self):
        token = self.current_token

        if token.type == TokenType.INT:
            self.eat(TokenType.INT)
            return LiteralNode(int(token.value))
        elif token.type == TokenType.FLOAT:
            self.eat(TokenType.FLOAT)
            return LiteralNode(float(token.value))
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return LiteralNode(token.value[1:-1])  # Remove quotes
        elif token.type == TokenType.BOOL:
            self.eat(TokenType.BOOL)
            return LiteralNode(token.value == 'true')
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.parse_expression()
            self.eat(TokenType.RPAREN)
            return node
        elif token.type == TokenType.IDENTIFIER:
            # Check if it's a function call
            next_token = self.lexer.get_next_token()
            self.lexer.pos -= len(next_token.value)  # Put it back
            if next_token.type == TokenType.LPAREN:
                return self.parse_function_call()
            else:
                self.eat(TokenType.IDENTIFIER)
                return IdentifierNode(token.value)
        else:
            raise Exception(f"Unexpected token {token.type} at line {token.line}")

    def parse_binary_expression(self, parse_operand, operator_groups):
        node = parse_operand(self)

        for operators in operator_groups:
            while self.current_token.type in operators:
                operator = self.current_token.type
                self.eat(operator)
                right = parse_operand(self)
                node = BinaryOperationNode(node, operator, right)

        return node


# AST Printer for visualization
class ASTPrinter:
    def print(self, node, indent=0):
        if isinstance(node, ProgramNode):
            print("  " * indent + "Program")
            for stmt in node.statements:
                self.print(stmt, indent + 1)
        elif isinstance(node, VariableDeclarationNode):
            print("  " * indent + f"VarDecl: {node.identifier}")
            self.print(node.value, indent + 1)
        elif isinstance(node, AssignmentNode):
            print("  " * indent + f"Assign: {node.identifier}")
            self.print(node.value, indent + 1)
        elif isinstance(node, BinaryOperationNode):
            print("  " * indent + f"BinaryOp: {node.operator}")
            self.print(node.left, indent + 1)
            self.print(node.right, indent + 1)
        elif isinstance(node, LiteralNode):
            print("  " * indent + f"Literal: {node.value}")
        elif isinstance(node, IdentifierNode):
            print("  " * indent + f"Identifier: {node.name}")
        elif isinstance(node, IfStatementNode):
            print("  " * indent + "If")
            print("  " * (indent + 1) + "Condition:")
            self.print(node.condition, indent + 2)
            print("  " * (indent + 1) + "Then:")
            self.print(node.then_branch, indent + 2)
            if node.else_branch:
                print("  " * (indent + 1) + "Else:")
                self.print(node.else_branch, indent + 2)
        elif isinstance(node, WhileLoopNode):
            print("  " * indent + "While")
            print("  " * (indent + 1) + "Condition:")
            self.print(node.condition, indent + 2)
            print("  " * (indent + 1) + "Body:")
            self.print(node.body, indent + 2)
        elif isinstance(node, FunctionDefinitionNode):
            print("  " * indent + f"Function: {node.name}")
            print("  " * (indent + 1) + "Parameters: " + ", ".join(node.parameters))
            print("  " * (indent + 1) + "Body:")
            self.print(node.body, indent + 2)
        elif isinstance(node, FunctionCallNode):
            print("  " * indent + f"Call: {node.name}")
            for arg in node.arguments:
                self.print(arg, indent + 1)
        elif isinstance(node, ReturnStatementNode):
            print("  " * indent + "Return")
            self.print(node.value, indent + 1)
        elif isinstance(node, PrintStatementNode):
            print("  " * indent + "Print")
            self.print(node.value, indent + 1)
        elif isinstance(node, BlockNode):
            print("  " * indent + "Block")
            for stmt in node.statements:
                self.print(stmt, indent + 1)


# Example usage
if __name__ == "__main__":
    code = """
    var x = 10;
    var y = 20;
    var sum = x + y;

    function add(a, b) {
        return a + b;
    }

    if (sum > 15) {
        print("Sum is greater than 15");
    } else {
        print("Sum is 15 or less");
    }

    var result = add(x, y);
    print(result);
    """

    # Lexical analysis
    lexer = Lexer(code)

    # Syntax analysis and AST construction
    parser = Parser(lexer)
    ast = parser.parse()

    # Print the AST
    printer = ASTPrinter()
    printer.print(ast)