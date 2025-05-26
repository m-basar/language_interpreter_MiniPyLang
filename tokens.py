"""
tokens.py – Enhanced Stage 5 token system with minimal changes

Adds collection support (equality and hashing) to the existing Stage 4 + type conversion:
- str(), int(), float(), bool() conversion functions
- if, else, while keywords for control flow
- input() function for user input
- New: __eq__ and __hash__ methods for use in sets and dictionaries
"""

class Token:
    """
    Enhanced token class supporting control-flow constructs and collections.

    Stage 5 introduces control-flow elements that enable
    conditional execution and loops in MiniPyLang programmes.

    New: supports equality comparison and hashing for use in
    sets and as dictionary keys.
    """

    # Data-type tokens
    NUMBER     = 'NUMBER'
    STRING     = 'STRING'
    TRUE       = 'TRUE'
    FALSE      = 'FALSE'
    NONE       = 'NONE'

    # Arithmetic operators
    PLUS       = 'PLUS'        # +
    MINUS      = 'MINUS'       # –
    MULTIPLY   = 'MULTIPLY'    # ×
    DIVIDE     = 'DIVIDE'      # ÷

    # Comparison operators
    EQUAL          = 'EQUAL'         # ==
    NOT_EQUAL      = 'NOT_EQUAL'     # !=
    LESS_THAN      = 'LESS_THAN'     # <
    GREATER_THAN   = 'GREATER_THAN'  # >
    LESS_EQUAL     = 'LESS_EQUAL'    # <=
    GREATER_EQUAL  = 'GREATER_EQUAL' # >=

    # Logical operators
    AND        = 'AND'         # and
    OR         = 'OR'          # or
    NOT        = 'NOT'         # not

    # Grouping
    LPAREN     = 'LPAREN'      # (
    RPAREN     = 'RPAREN'      # )
    LBRACE     = 'LBRACE'      # { – new for code blocks
    RBRACE     = 'RBRACE'      # } – new for code blocks

    # Variables and statements
    IDENTIFIER = 'IDENTIFIER'  # variable names
    ASSIGN     = 'ASSIGN'      # =
    PRINT      = 'PRINT'       # print keyword
    DEL        = 'DEL'         # del keyword

    # Control-flow keywords
    IF         = 'IF'          # if keyword
    ELSE       = 'ELSE'        # else keyword
    WHILE      = 'WHILE'       # while keyword

    # Programme structure
    NEWLINE    = 'NEWLINE'     # line endings
    EOF        = 'EOF'         # end of file

    # Type-conversion functions
    STR_FUNC   = 'STR_FUNC'    # str() function
    INT_FUNC   = 'INT_FUNC'    # int() function
    FLOAT_FUNC = 'FLOAT_FUNC'  # float() function
    BOOL_FUNC  = 'BOOL_FUNC'   # bool() function

    # Input function
    INPUT_FUNC = 'INPUT_FUNC'  # input() function

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """Human-readable representation for debugging."""
        if self.type == self.STRING:
            return f'Token({self.type}, "{self.value}")'
        elif self.type == self.IDENTIFIER:
            return f'Token({self.type}, {self.value})'
        else:
            return f'Token({self.type}, {self.value})'

    def __repr__(self):
        return self.__str__()

    # New: collection support methods
    def __eq__(self, other):
        """
        Equality comparison for use in sets and as dictionary keys.

        Two tokens are equal if they have the same type and value.
        This permits tokens to be used in sets and as dictionary keys.
        """
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value

    def __hash__(self):
        """
        Hash implementation for use in sets and as dictionary keys.

        Based on type and value, allowing tokens to be used in
        hash-based collections efficiently.

        Example usage:
        - token_set = {token1, token2, token3}
        - token_dict = {token: "some_info"}
        """
        return hash((self.type, self.value))
