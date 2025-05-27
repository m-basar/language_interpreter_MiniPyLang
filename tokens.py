"""
tokens.py - Enhanced Stage 6 token system with List support

Adds list data structure tokens to Stage 5:
- Square brackets [ ] for list literals and indexing
- Built-in list functions: append, remove, len
"""

class Token:
    """
    Enhanced token class supporting list data structures.
    
    Stage 6 adds list functionality with proper collection support.
    """
    
    # Data type tokens
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NONE = 'NONE'
    
    # Arithmetic operators
    PLUS = 'PLUS'              # +
    MINUS = 'MINUS'            # -
    MULTIPLY = 'MULTIPLY'      # *
    DIVIDE = 'DIVIDE'          # /
    
    # Comparison operators
    EQUAL = 'EQUAL'            # ==
    NOT_EQUAL = 'NOT_EQUAL'    # !=
    LESS_THAN = 'LESS_THAN'    # <
    GREATER_THAN = 'GREATER_THAN'  # >
    LESS_EQUAL = 'LESS_EQUAL'  # <=
    GREATER_EQUAL = 'GREATER_EQUAL'  # >=
    
    # Logical operators
    AND = 'AND'                # and
    OR = 'OR'                  # or
    NOT = 'NOT'                # !
    
    # Grouping
    LPAREN = 'LPAREN'          # (
    RPAREN = 'RPAREN'          # )
    LBRACE = 'LBRACE'          # {
    RBRACE = 'RBRACE'          # }
    LBRACKET = 'LBRACKET'      # [ - NEW for lists
    RBRACKET = 'RBRACKET'      # ] - NEW for lists
    
    # Variables and statements
    IDENTIFIER = 'IDENTIFIER'   # Variable names
    ASSIGN = 'ASSIGN'          # =
    PRINT = 'PRINT'            # print keyword
    DEL = 'DEL'                # del keyword
    
    # Control flow keywords
    IF = 'IF'                  # if keyword
    ELSE = 'ELSE'              # else keyword
    WHILE = 'WHILE'            # while keyword
    
    # Programme structure
    NEWLINE = 'NEWLINE'        # Line endings
    EOF = 'EOF'                # End of file
    COMMA = 'COMMA'            # , - NEW for list elements
    
    # Type conversion functions
    STR_FUNC = 'STR_FUNC'      # str() function
    INT_FUNC = 'INT_FUNC'      # int() function
    FLOAT_FUNC = 'FLOAT_FUNC'  # float() function
    BOOL_FUNC = 'BOOL_FUNC'    # bool() function
    
    # Input function
    INPUT_FUNC = 'INPUT_FUNC'  # input() function
    
    # NEW: List built-in functions
    APPEND_FUNC = 'APPEND_FUNC'  # append() function
    REMOVE_FUNC = 'REMOVE_FUNC'  # remove() function
    LEN_FUNC = 'LEN_FUNC'        # len() function
    
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __str__(self):
        """String representation for debugging"""
        if self.type == self.STRING:
            return f'Token({self.type}, \"{self.value}\")'
        elif self.type == self.IDENTIFIER:
            return f'Token({self.type}, {self.value})'
        else:
            return f'Token({self.type}, {self.value})'
    
    def __repr__(self):
        return self.__str__()
    
    # Collection support methods
    def __eq__(self, other):
        """
        Equality comparison for use in sets and as dict keys.
        
        Two tokens are equal if they have the same type and value.
        This allows tokens to be used in sets and as dictionary keys.
        """
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value
    
    def __hash__(self):
        """
        Hash implementation for use in sets and as dict keys.
        
        Based on type and value, allowing tokens to be used in
        hash-based collections efficiently.
        
        Example usage:
        - token_set = {token1, token2, token3}
        - token_dict = {token: "some_info"}
        """
        return hash((self.type, self.value))