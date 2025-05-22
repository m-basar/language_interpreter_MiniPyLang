"""
lexer.py - Lexical analyser with Boolean support

The lexer now needs to recognise Boolean literals and logical operators.
We're teaching it to read a richer vocabulary.
"""

from tokens import Token

class LexerError(Exception):
    """Custom exception for lexical analysis errors"""
    pass

class Lexer:
    """
    Enhanced lexer that can tokenise both arithmetic and Boolean expressions.
    
    The key challenge here is handling multi-character operators like <= and >=,
    as well as recognising keyword literals like 'true' and 'false'.
    """
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None
    
    def error(self, message="Invalid character"):
        raise LexerError(f"{message} at position {self.pos}: '{self.current_char}'")
    
    def advance(self):
        """Move to the next character in the input"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def peek(self):
        """
        Look at the next character without consuming it.
        This is crucial for recognising multi-character operators like <= and >=.
        """
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]
    
    def skip_whitespace(self):
        """Skip over whitespace characters"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def read_number(self):
        """Read a complete number (unchanged from Stage 1)"""
        result = ''
        
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
        
        return float(result)
    
    def read_identifier(self):
        """
        Read an identifier (like 'true', 'false', 'and', 'or').
        Identifiers are sequences of letters that represent keywords in our language.
        """
        result = ''
        
        # Read letters (and potentially underscores for future extensions)
        while (self.current_char is not None and 
               (self.current_char.isalpha() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        return result
    
    def get_next_token(self):
        """Enhanced tokeniser that handles Boolean expressions"""
        while self.current_char is not None:
            
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Numbers (unchanged from Stage 1)
            if self.current_char.isdigit():
                return Token(Token.NUMBER, self.read_number())
            
            # Identifiers and keywords (true, false, and, or)
            if self.current_char.isalpha():
                identifier = self.read_identifier()
                
                # Check if it's a Boolean literal or logical operator
                if identifier.lower() == 'true':
                    return Token(Token.TRUE, True)
                elif identifier.lower() == 'false':
                    return Token(Token.FALSE, False)
                elif identifier.lower() == 'and':
                    return Token(Token.AND, 'and')
                elif identifier.lower() == 'or':
                    return Token(Token.OR, 'or')
                else:
                    # For now, we don't support arbitrary identifiers
                    self.error(f"Unknown identifier: {identifier}")
            
            # Arithmetic operators (unchanged from Stage 1)
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
            
            # Parentheses (unchanged from Stage 1)
            if self.current_char == '(':
                self.advance()
                return Token(Token.LPAREN, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(Token.RPAREN, ')')
            
            # Comparison and logical operators (new for Stage 2)
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()  # consume first =
                    self.advance()  # consume second =
                    return Token(Token.EQUAL, '==')
                else:
                    self.error("Single '=' not supported (use '==' for equality)")
            
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()  # consume !
                    self.advance()  # consume =
                    return Token(Token.NOT_EQUAL, '!=')
                else:
                    self.advance()  # consume !
                    return Token(Token.NOT, '!')
            
            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()  # consume <
                    self.advance()  # consume =
                    return Token(Token.LESS_EQUAL, '<=')
                else:
                    self.advance()  # consume <
                    return Token(Token.LESS_THAN, '<')
            
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()  # consume >
                    self.advance()  # consume =
                    return Token(Token.GREATER_EQUAL, '>=')
                else:
                    self.advance()  # consume >
                    return Token(Token.GREATER_THAN, '>')
            
            # If we get here, we found an invalid character
            self.error()
        
        return Token(Token.EOF, None)
