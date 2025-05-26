"""
lexer.py – Stage 5 lexical analyser with control flow

Handles tokenisation of Stage 5 control flow constructs:
- if, else, while keywords
- Braces { } for code blocks
- input() function for user interaction
"""

from tokens import Token


class LexerError(Exception):
    """Lexer error with position information"""
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        location_info = ""
        if line is not None:
            location_info = f" at line {line}"
            if column is not None:
                location_info += f", column {column}"
        super().__init__(f"{message}{location_info}")


class Lexer:
    """
    Enhanced lexer for Stage 5 MiniPyLang with control flow.
    
    Converts source code text into tokens including control flow constructs.
    """
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None
        self.line = 1
        self.column = 1
    
    def error(self, message="Invalid character"):
        """Raise lexer error with position information"""
        raise LexerError(message, self.line, self.column)
    
    def advance(self):
        """Move to next character and track position"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def peek(self):
        """Look at next character without advancing"""
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]
    
    def skip_whitespace(self):
        """Skip spaces, tabs, carriage returns (but not newlines)"""
        while (self.current_char is not None and 
               self.current_char in ' \t\r'):
            self.advance()
    
    def skip_comment(self):
        """Skip comment from # to end of line"""
        self.advance()  # Skip the #
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
    
    def read_number(self):
        """Read integer or floating-point number"""
        result = ''
        has_decimal = False
        
        # Read integer part
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        
        # Check for decimal point
        if self.current_char == '.':
            has_decimal = True
            result += self.current_char
            self.advance()
            
            # Read fractional part
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
        
        # Return appropriate numeric type
        if has_decimal:
            return float(result)
        else:
            return int(result)
    
    def read_string(self):
        """Read string literal with escape sequence support"""
        result = ''
        start_line = self.line
        
        self.advance()  # Skip opening quote
        
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                # Handle escape sequences
                self.advance()
                
                if self.current_char is None:
                    raise LexerError(f"Unterminated string literal starting at line {start_line}")
                
                # Common escape sequences
                escape_sequences = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '\\': '\\',
                    '"': '"',
                    '0': '\0'
                }
                
                if self.current_char in escape_sequences:
                    result += escape_sequences[self.current_char]
                else:
                    # Unknown escape sequence – include literally
                    result += '\\' + self.current_char
                
                self.advance()
            else:
                result += self.current_char
                self.advance()
        
        if self.current_char != '"':
            raise LexerError(f"Unterminated string literal starting at line {start_line}")
        
        self.advance()  # Skip closing quote
        return result
    
    def read_identifier(self):
        """Read identifier or keyword"""
        result = ''
        
        # Must start with letter or underscore
        if not (self.current_char.isalpha() or self.current_char == '_'):
            self.error("Identifier must start with letter or underscore")
        
        # Read alphanumeric characters and underscores
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        return result
    
    def get_next_token(self):
        """Get the next token from the input"""
        while self.current_char is not None:
            
            # Skip comments
            if self.current_char == '#':
                self.skip_comment()
                continue
            
            # Handle newlines as statement separators
            if self.current_char == '\n':
                self.advance()
                return Token(Token.NEWLINE, '\\n')
            
            # Skip whitespace
            if self.current_char in ' \t\r':
                self.skip_whitespace()
                continue
            
            # String literals
            if self.current_char == '"':
                return Token(Token.STRING, self.read_string())
            
            # Numeric literals
            if self.current_char.isdigit():
                return Token(Token.NUMBER, self.read_number())
            
            # Identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                identifier = self.read_identifier()
                
                # Enhanced keyword map with control flow and functions
                keyword_map = {
                    # Existing keywords
                    'true': (Token.TRUE, True),
                    'false': (Token.FALSE, False),
                    'and': (Token.AND, 'and'),
                    'or': (Token.OR, 'or'),
                    'print': (Token.PRINT, 'print'),
                    'del': (Token.DEL, 'del'),
                    'none': (Token.NONE, None),
                    
                    # Type conversion functions
                    'str': (Token.STR_FUNC, 'str'),
                    'int': (Token.INT_FUNC, 'int'),
                    'float': (Token.FLOAT_FUNC, 'float'),
                    'bool': (Token.BOOL_FUNC, 'bool'),
                    
                    # NEW: Control flow keywords
                    'if': (Token.IF, 'if'),
                    'else': (Token.ELSE, 'else'),
                    'while': (Token.WHILE, 'while'),
                    
                    # NEW: Input function
                    'input': (Token.INPUT_FUNC, 'input')
                }
                
                identifier_lower = identifier.lower()
                if identifier_lower in keyword_map:
                    token_type, token_value = keyword_map[identifier_lower]
                    return Token(token_type, token_value)
                else:
                    return Token(Token.IDENTIFIER, identifier)
            
            # Two-character operators
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(Token.EQUAL, '==')
                else:
                    self.advance()
                    return Token(Token.ASSIGN, '=')
            
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(Token.NOT_EQUAL, '!=')
                else:
                    self.advance()
                    return Token(Token.NOT, '!')
            
            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(Token.LESS_EQUAL, '<=')
                else:
                    self.advance()
                    return Token(Token.LESS_THAN, '<')
            
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(Token.GREATER_EQUAL, '>=')
                else:
                    self.advance()
                    return Token(Token.GREATER_THAN, '>')
            
            # Single-character operators
            single_char_tokens = {
                '+': Token.PLUS,
                '-': Token.MINUS,
                '*': Token.MULTIPLY,
                '/': Token.DIVIDE,
                '(': Token.LPAREN,
                ')': Token.RPAREN,
                # NEW: Braces for code blocks
                '{': Token.LBRACE,
                '}': Token.RBRACE
            }
            
            if self.current_char in single_char_tokens:
                token_type = single_char_tokens[self.current_char]
                char = self.current_char
                self.advance()
                return Token(token_type, char)
            
            # Unknown character
            self.error(f"Invalid character: '{self.current_char}'")
        
        return Token(Token.EOF, None)
