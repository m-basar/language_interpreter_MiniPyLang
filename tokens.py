"""
tokens.py - Enhanced token definitions including string literals

We're adding support for string literals, which introduces new concepts
about how tokens can be recognised and processed.
"""

class Token:
    """
    Enhanced token class that now supports string literals.
    
    String tokens are different from our previous tokens because they
    can contain arbitrary content between delimiters (quote marks).
    This introduces complexity in lexical analysis.
    """
    
    # Existing token types from Stages 1 and 2
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    EOF = 'EOF'
    
    # Boolean token types
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    EQUAL = 'EQUAL'
    NOT_EQUAL = 'NOT_EQUAL'
    LESS_THAN = 'LESS_THAN'
    GREATER_THAN = 'GREATER_THAN'
    LESS_EQUAL = 'LESS_EQUAL'
    GREATER_EQUAL = 'GREATER_EQUAL'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    # New string token type
    STRING = 'STRING'              # For string literals like "hello world"
    
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __str__(self):
        # Special handling for string display to show quotes
        if self.type == self.STRING:
            return f'Token({self.type}, \"{self.value}\")'
        return f'Token({self.type}, {self.value})'
    
    def __repr__(self):
        return self.__str__()

def create_token(token_type, value):
    """Factory function for creating tokens with validation"""
    return Token(token_type, value)
