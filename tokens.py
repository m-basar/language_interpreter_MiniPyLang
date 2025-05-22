"""
tokens.py – Token definitions for our arithmetic language

This file defines all the types of symbols recognised by our language.
Consider tokens as the 'words' within the vocabulary of our programming language.
"""

class Token:
    """
    A token represents a significant symbol in our language.
    Each token has a type (indicating the category of symbol) and a value (the actual content).
    """

    # Token types – analogous to categories of words in natural language
    NUMBER = 'NUMBER'        # Numeric literals, e.g., 5, 3.14, -7
    PLUS = 'PLUS'            # Addition operator +
    MINUS = 'MINUS'          # Subtraction operator - (also for unary negation)
    MULTIPLY = 'MULTIPLY'    # Multiplication operator *
    DIVIDE = 'DIVIDE'        # Division operator /
    LPAREN = 'LPAREN'        # Left parenthesis (
    RPAREN = 'RPAREN'        # Right parenthesis )
    EOF = 'EOF'              # End of input marker

    def __init__(self, type, value):
        """
        Initialise a new token.

        Args:
            type: The category of this token (one of the constants above)
            value: The actual content (e.g., the number 5 or the symbol '+')
        """
        self.type = type
        self.value = value

    def __str__(self):
        """Return a string representation for straightforward debugging."""
        return f'Token({self.type}, {self.value})'

    def __repr__(self):
        """Return the string representation for lists and debugging."""
        return self.__str__()

# Helper function to facilitate token creation
def create_token(token_type, value):
    """
    Factory function for convenient token creation.
    This will be particularly useful as the language becomes more sophisticated.
    """
    return Token(token_type, value)
