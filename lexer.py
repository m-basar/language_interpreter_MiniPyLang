"""
lexer.py – Lexical analyser for arithmetic expressions

The lexer's role is to take raw text and break it down into tokens.
It is similar to reading a sentence and identifying each word and punctuation mark.
"""

from tokens import Token

class LexerError(Exception):
    """Custom exception for lexical analysis errors."""
    pass

class Lexer:
    """
    The lexer scans through input text and produces a stream of tokens.
    It functions as a sophisticated, character-by-character reader.
    """

    def __init__(self, text):
        """
        Initialise the lexer with input text.

        Args:
            text: The arithmetic expression to be tokenised.
        """
        self.text = text
        self.pos = 0  # Current position in the text
        self.current_char = self.text[self.pos] if text else None

    def error(self, message="Invalid character"):
        """Raise an error with helpful position information."""
        raise LexerError(f"{message} at position {self.pos}: '{self.current_char}'")

    def advance(self):
        """
        Move to the next character in the input.
        This is equivalent to moving a reading cursor forwards.
        """
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None  # End of input reached
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """
        Skip spaces, tabs, and other whitespace characters.
        In most programming languages, whitespace is for readability only.
        """
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def read_number(self):
        """
        Read a complete number from the input.
        This supports both integers (such as 42) and decimals (such as 3.14).
        """
        result = ''

        # Read the integer part
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        # Check for decimal point
        if self.current_char == '.':
            result += self.current_char
            self.advance()

            # Read the fractional part
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

        return float(result)

    def get_next_token(self):
        """
        Analyse the current position and return the next token.
        This is the primary method to be called by other components of the programme.
        """
        while self.current_char is not None:

            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Numbers (including decimals)
            if self.current_char.isdigit():
                return Token(Token.NUMBER, self.read_number())

            # Single-character tokens
            if self.current_char == '+':
                self.advance()
                return Token(Token.PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(Token.MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(Token.MULTIPLY, '*')

            if self.current_char == '/':
                self.advance()
                return Token(Token.DIVIDE, '/')

            if self.current_char == '(':
                self.advance()
                return Token(Token.LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(Token.RPAREN, ')')

            # If an invalid character is encountered
            self.error()

        # End of input reached
        return Token(Token.EOF, None)
