"""
tokens.py – Token definitions for arithmetic and Boolean expressions

This module extends the token vocabulary to include Boolean concepts,
enabling the language to process both arithmetic and Boolean expressions.
"""

class Token:
    """
    Token class with support for arithmetic and Boolean operations.
    New categories of symbols are included for Boolean logic.
    """

    # Arithmetic token types
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'

    # Boolean literal tokens
    TRUE = 'TRUE'                # The literal value true
    FALSE = 'FALSE'              # The literal value false

    # Comparison operator tokens
    EQUAL = 'EQUAL'              # == (equality)
    NOT_EQUAL = 'NOT_EQUAL'      # != (inequality)
    LESS_THAN = 'LESS_THAN'      # <
    GREATER_THAN = 'GREATER_THAN'  # >
    LESS_EQUAL = 'LESS_EQUAL'    # <=
    GREATER_EQUAL = 'GREATER_EQUAL'  # >=

    # Logical operator tokens
    AND = 'AND'                  # and (logical AND)
    OR = 'OR'                    # or (logical OR)
    NOT = 'NOT'                  # ! (logical negation)

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {self.value})'

    def __repr__(self):
        return self.__str__()

def create_token(token_type, value):
    """Factory function for creating tokens."""
    return Token(token_type, value)
