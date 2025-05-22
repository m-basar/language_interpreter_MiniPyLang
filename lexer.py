"""
lexer.py - Enhanced lexical analyser with comprehensive string support

String tokenisation introduces several challenges:
1. Recognising delimiter boundaries
2. Handling escape sequences for special characters
3. Proper error reporting for malformed strings
4. Maintaining position tracking through multi-character tokens
"""

from tokens import Token

class LexerError(Exception):
    """Enhanced exception class with position information for better debugging"""
    def __init__(self, message, position=None):
        self.message = message
        self.position = position
        super().__init__(f"{message}" + (f" at position {position}" if position else ""))

class Lexer:
    """
    Enhanced lexer that can process string literals alongside numbers and operators.
    
    The key challenge here is handling strings, which can contain almost any
    character and require special processing for escape sequences.
    """
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None
    
    def error(self, message="Invalid character"):
        """Raise a lexer error with helpful position information"""
        raise LexerError(message, self.pos)
    
    def advance(self):
        """Move to the next character, handling end-of-input gracefully"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def peek(self):
        """
        Look ahead one character without consuming it.
        Essential for multi-character operators like <= and >=.
        """
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]
    
    def skip_whitespace(self):
        """Skip whitespace characters efficiently"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def read_number(self):
        """
        Read numeric literals (unchanged from previous stages)
        
        This method demonstrates consistency in our lexer design –
        each data type has its own specialised reading method.
        """
        result = ''
        
        # Read integer part
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        # Handle decimal point and fractional part
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
        
        return float(result)
    
    def read_string(self):
        """
        Read a complete string literal with escape sequence support.
        
        This method demonstrates how to handle delimited tokens and
        escape sequences, which are fundamental concepts in language processing.
        """
        result = ''
        start_pos = self.pos  # Remember where the string started for error reporting
        
        # Skip the opening quote
        self.advance()
        
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                # Handle escape sequences for non-printable characters
                self.advance()
                
                if self.current_char is None:
                    raise LexerError(f"Unterminated string literal starting at position {start_pos}")
                
                # Map escape sequences to their actual characters
                escape_sequences = {
                    'n': '\n',    # newline
                    't': '\t',    # tab
                    'r': '\r',    # carriage return
                    '\\': '\\',   # backslash
                    '"': '"',     # quote
                    '0': '\0'     # null character
                }
                
                if self.current_char in escape_sequences:
                    result += escape_sequences[self.current_char]
                else:
                    # For unknown escape sequences, include both the backslash and character
                    result += '\\' + self.current_char
                
                self.advance()
            else:
                # Regular character - add it directly
                result += self.current_char
                self.advance()
        
        # Check for proper string termination
        if self.current_char != '"':
            raise LexerError(f"Unterminated string literal starting at position {start_pos}")
        
        # Skip the closing quote
        self.advance()
        
        return result
    
    def read_identifier(self):
        """
        Read identifiers and keywords (enhanced from Stage 2)
        
        This method handles variable names and language keywords.
        The ability to distinguish between identifiers and keywords
        becomes crucial as the language grows.
        """
        result = ''
        
        # Read the complete identifier
        while (self.current_char is not None and 
               (self.current_char.isalpha() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        return result
    
    def get_next_token(self):
        """
        Enhanced tokeniser that handles all MiniPyLang data types.
        
        This method demonstrates how lexical analysis becomes more complex
        as we add features, but maintains a clear structure.
        """
        while self.current_char is not None:
            
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # String literals - new for Stage 3
            if self.current_char == '"':
                return Token(Token.STRING, self.read_string())
            
            # Numeric literals
            if self.current_char.isdigit():
                return Token(Token.NUMBER, self.read_number())
            
            # Identifiers and keywords (true, false, and, or)
            if self.current_char.isalpha():
                identifier = self.read_identifier()
                
                # Map keywords to their token types
                keyword_map = {
                    'true': (Token.TRUE, True),
                    'false': (Token.FALSE, False),
                    'and': (Token.AND, 'and'),
                    'or': (Token.OR, 'or')
                }
                
                identifier_lower = identifier.lower()
                if identifier_lower in keyword_map:
                    token_type, token_value = keyword_map[identifier_lower]
                    return Token(token_type, token_value)
                else:
                    # For now, we don't support arbitrary identifiers
                    # This will change in Stage 4 when we add variables
                    self.error(f"Unknown identifier: {identifier}")
            
            # Single-character arithmetic operators
            single_char_tokens = {
                '+': Token.PLUS,
                '-': Token.MINUS,
                '*': Token.MULTIPLY,
                '/': Token.DIVIDE,
                '(': Token.LPAREN,
                ')': Token.RPAREN
            }
            
            if self.current_char in single_char_tokens:
                token_type = single_char_tokens[self.current_char]
                char = self.current_char
                self.advance()
                return Token(token_type, char)
            
            # Multi-character comparison and logical operators
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
                    self.advance()  # consume 
                    self.advance()  # consume =
                    return Token(Token.LESS_EQUAL, '<=')
                else:
                    self.advance()  # consume 
                    return Token(Token.LESS_THAN, '<')
            
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()  # consume >
                    self.advance()  # consume =
                    return Token(Token.GREATER_EQUAL, '>=')
                else:
                    self.advance()  # consume >
                    return Token(Token.GREATER_THAN, '>')
            
            # If we reach here, we encountered an invalid character
            self.error(f"Invalid character: '{self.current_char}'")
        
        return Token(Token.EOF, None)
