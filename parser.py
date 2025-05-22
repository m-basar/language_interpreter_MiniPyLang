"""
parser.py – Recursive descent parser for arithmetic expressions

The parser takes tokens from the lexer and constructs an Abstract Syntax Tree (AST).
It implements operator precedence and handles parentheses correctly.
"""

from tokens import Token
from ast_nodes import NumberNode, BinaryOperationNode, UnaryOperationNode

class ParseError(Exception):
    """Custom exception for parsing errors."""
    pass

class Parser:
    """
    Recursive descent parser that constructs an AST from tokens.

    This parser implements the following grammar:
      expression : term ((PLUS | MINUS) term)*
      term       : factor ((MULTIPLY | DIVIDE) factor)*
      factor     : NUMBER | LPAREN expression RPAREN | (PLUS | MINUS) factor

    This grammar ensures correct operator precedence:
      - Multiplication and division have higher precedence than addition and subtraction
      - Parentheses may override the default precedence
      - Unary operators (such as -5) are handled at the factor level
    """

    def __init__(self, lexer):
        """
        Initialise the parser with a lexer.

        Args:
            lexer: The lexer providing the sequence of tokens.
        """
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message="Invalid syntax"):
        """Raise a parsing error with informative details."""
        raise ParseError(f"{message}. Current token: {self.current_token}")

    def eat(self, token_type):
        """
        Consume a token of the expected type.
        This method checks that the next 'word' in our language is as anticipated.

        Args:
            token_type: The expected token type.
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}")

    def factor(self):
        """
        Parse a factor: NUMBER | LPAREN expression RPAREN | (PLUS | MINUS) factor

        Factors are the atomic units of our expressions – elements that cannot be
        further decomposed by binary operators.
        """
        token = self.current_token

        if token.type == Token.NUMBER:
            self.eat(Token.NUMBER)
            return NumberNode(token)

        elif token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.expression()  # Parse the expression within parentheses
            self.eat(Token.RPAREN)
            return node

        elif token.type in (Token.PLUS, Token.MINUS):
            # Handle unary operations such as -5 or +3
            self.eat(token.type)
            return UnaryOperationNode(token, self.factor())

        else:
            self.error("Expected a number, parenthesis, or unary operator")

    def term(self):
        """
        Parse a term: factor ((MULTIPLY | DIVIDE) factor)*

        Terms address multiplication and division, which take precedence over
        addition and subtraction.
        """
        node = self.factor()

        while self.current_token.type in (Token.MULTIPLY, Token.DIVIDE):
            token = self.current_token

            if token.type == Token.MULTIPLY:
                self.eat(Token.MULTIPLY)
            elif token.type == Token.DIVIDE:
                self.eat(Token.DIVIDE)

            # Form a binary operation node with the operator and operands
            node = BinaryOperationNode(left=node, operator_token=token, right=self.factor())

        return node

    def expression(self):
        """
        Parse an expression: term ((PLUS | MINUS) term)*

        This is the top level of our grammar. Expressions handle addition and
        subtraction, which are of lowest precedence.
        """
        node = self.term()

        while self.current_token.type in (Token.PLUS, Token.MINUS):
            token = self.current_token

            if token.type == Token.PLUS:
                self.eat(Token.PLUS)
            elif token.type == Token.MINUS:
                self.eat(Token.MINUS)

            # Form a binary operation node
            node = BinaryOperationNode(left=node, operator_token=token, right=self.term())

        return node

    def parse(self):
        """
        Parse the input and return the root of the AST.
        This is the principal method for use by external code.
        """
        ast = self.expression()

        # Ensure the entire input has been consumed
        if self.current_token.type != Token.EOF:
            self.error("Unexpected token following expression")

        return ast
