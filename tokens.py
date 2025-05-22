"""
tokens.py - Enhanced token system supporting variables and statements

Stage 4 introduces the distinction between expressions (which produce values)
and statements (which perform actions). This fundamental concept shapes
how we think about programme execution and state management.
"""

class Token:
    """
    Enhanced token class supporting variables, assignment, and statements.
    
    The addition of variables requires new token types that represent
    programme structure rather than just data and operations.
    """
    
    # Existing data type tokens from previous stages
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    
    # Existing operator tokens
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    EQUAL = 'EQUAL'            # == for comparison
    NOT_EQUAL = 'NOT_EQUAL'    # !=
    LESS_THAN = 'LESS_THAN'    # <
    GREATER_THAN = 'GREATER_THAN'  # >
    LESS_EQUAL = 'LESS_EQUAL'  # <=
    GREATER_EQUAL = 'GREATER_EQUAL'  # >=
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    # Grouping tokens
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    
    # New tokens for Stage 4: Variables and Statements
    IDENTIFIER = 'IDENTIFIER'  # Variable names like 'quickMaths', 'userName'
    ASSIGN = 'ASSIGN'          # = for assignment (different from == comparison)
    PRINT = 'PRINT'            # 'print' keyword for output
    NEWLINE = 'NEWLINE'        # Line separators for statement boundaries
    EOF = 'EOF'
    
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __str__(self):
        """Enhanced string representation with better formatting for debugging"""
        if self.type == self.STRING:
            return f'Token({self.type}, \"{self.value}\")'
        elif self.type == self.IDENTIFIER:
            return f'Token({self.type}, {self.value})'
        else:
            return f'Token({self.type}, {self.value})'
    
    def __repr__(self):
        return self.__str__()

def create_token(token_type, value):
    """
    Factory function for creating tokens with validation.
    
    As our language grows more complex, factory functions help ensure
    tokens are created consistently and can include validation logic.
    """
    return Token(token_type, value)
