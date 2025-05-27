"""
tokens.py - Enhanced Stage 6 token system with List and Dictionary support

Adds list and dictionary data structure tokens to Stage 5:
- Square brackets [ ] for list literals and indexing
- Curly braces { } for dictionary literals (reused from control flow)
- Colon : for dictionary key-value pairs
- Built-in list functions: append, remove, len
- Built-in dictionary functions: keys, values, has_key, del_key
"""

class Token:
    """
    Enhanced token class supporting list and dictionary data structures.
    
    Stage 6 adds list and dictionary functionality with proper collection support.
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
    LBRACE = 'LBRACE'          # { - Used for both control flow and dictionaries
    RBRACE = 'RBRACE'          # } - Used for both control flow and dictionaries
    LBRACKET = 'LBRACKET'      # [ - For lists and indexing
    RBRACKET = 'RBRACKET'      # ] - For lists and indexing
    
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
    COMMA = 'COMMA'            # , - For list elements and dictionary pairs
    COLON = 'COLON'            # : - NEW for dictionary key-value pairs
    
    # Type conversion functions
    STR_FUNC = 'STR_FUNC'      # str() function
    INT_FUNC = 'INT_FUNC'      # int() function
    FLOAT_FUNC = 'FLOAT_FUNC'  # float() function
    BOOL_FUNC = 'BOOL_FUNC'    # bool() function
    
    # Input function
    INPUT_FUNC = 'INPUT_FUNC'  # input() function
    
    # List built-in functions
    APPEND_FUNC = 'APPEND_FUNC'  # append() function
    REMOVE_FUNC = 'REMOVE_FUNC'  # remove() function
    LEN_FUNC = 'LEN_FUNC'        # len() function
    
    # NEW: Dictionary built-in functions
    KEYS_FUNC = 'KEYS_FUNC'      # keys() function
    VALUES_FUNC = 'VALUES_FUNC'  # values() function
    HAS_KEY_FUNC = 'HAS_KEY_FUNC'  # has_key() function
    DEL_KEY_FUNC = 'DEL_KEY_FUNC'  # del_key() function
    
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