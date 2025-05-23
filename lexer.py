"""
lexer.py - Enhanced lexer with comprehensive comment support

Adding comment support demonstrates how language features can be
completely transparent to most of the language implementation.
Comments only affect the lexer—the parser and interpreter never
even know they existed.
"""

from tokens import Token


class LexerError(Exception):
    """Enhanced lexer error with line and column information for debugging"""
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
    Enhanced lexer supporting comments, variables, and multi-statement programs.
    
    The addition of comment support demonstrates how some language features
    affect only one component of the language processor. Comments are
    recognised and discarded by the lexer, making them invisible to
    the parser and interpreter.
    """
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if text else None
        
        # Track position for better error reporting
        self.line = 1
        self.column = 1
    
    def error(self, message="Invalid character"):
        """Enhanced error reporting with position information"""
        raise LexerError(message, self.line, self.column)
    
    def advance(self):
        """
        Advance position with line and column tracking.
        
        Position tracking becomes even more important when handling
        comments, as we need to properly track line boundaries.
        """
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
        """Look ahead one character without advancing position"""
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        else:
            return self.text[peek_pos]
    
    def skip_whitespace(self):
        """
        Skip whitespace but preserve newlines as statement separators.
        
        Comments are handled separately from whitespace because they
        have different semantics—comments extend to the end of a line,
        while whitespace is typically just individual characters.
        """
        while (self.current_char is not None and 
               self.current_char in ' \t\r'):  # Note: \n is NOT included
            self.advance()
    
    def skip_comment(self):
        """
        Skip a comment from # to the end of the line.
        
        This method demonstrates the conceptual simplicity of comments:
        once we see the comment marker, we simply ignore everything
        until we reach a newline or the end of the input.
        """
        # We're currently at the # character, so advance past it
        self.advance()
        
        # Skip everything until we reach a newline or end of input
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        
        # Note: We don't advance past the newline because newlines
        # are meaningful tokens in our language (statement separators)
    
    def read_number(self):
        """Read numeric literals - unchanged from previous stages"""
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
    
    def read_string(self):
        """Read string literals - unchanged from Stage 3"""
        result = ''
        start_line = self.line
        
        self.advance()  # Skip opening quote
        
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                
                if self.current_char is None:
                    raise LexerError(f"Unterminated string literal starting at line {start_line}")
                
                escape_sequences = {
                    'n': '\n', 't': '\t', 'r': '\r',
                    '\\': '\\', '"': '"', '0': '\0'
                }
                
                if self.current_char in escape_sequences:
                    result += escape_sequences[self.current_char]
                else:
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
        """
        Read identifiers (variable names) and keywords.
        
        Identifiers remain unchanged with comment support because
        comments can't appear in the middle of identifiers.
        """
        result = ''
        
        # Ensure identifier starts with valid character
        if not (self.current_char.isalpha() or self.current_char == '_'):
            self.error("Identifier must start with letter or underscore")
        
        # Read the complete identifier
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        return result
    
    def get_next_token(self):
        """
        Enhanced tokeniser supporting comments alongside all other features.
        
        The key insight here is that comment handling is integrated into
        the main tokenisation loop. When we encounter a comment marker,
        we skip the comment and continue tokenising normally.
        """
        while self.current_char is not None:
            
            # Handle comments - this is the new addition for comment support
            if self.current_char == '#':
                self.skip_comment()
                continue  # After skipping the comment, continue tokenising
            
            # Handle newlines as statement separators
            if self.current_char == '\n':
                self.advance()
                return Token(Token.NEWLINE, '\\n')
            
            # Skip whitespace (but not newlines)
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
                
                # Map keywords to their token types
                keyword_map = {
                    'true': (Token.TRUE, True),
                    'false': (Token.FALSE, False),
                    'and': (Token.AND, 'and'),
                    'or': (Token.OR, 'or'),
                    'print': (Token.PRINT, 'print'),
                    'none': (Token.NONE, None)
                }
                
                identifier_lower = identifier.lower()
                if identifier_lower in keyword_map:
                    token_type, token_value = keyword_map[identifier_lower]
                    return Token(token_type, token_value)
                else:
                    # This is a variable name
                    return Token(Token.IDENTIFIER, identifier)
            
            # Assignment vs. equality comparison
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()  # consume first =
                    self.advance()  # consume second =
                    return Token(Token.EQUAL, '==')
                else:
                    self.advance()  # consume single =
                    return Token(Token.ASSIGN, '=')
            
            # Other comparison and logical operators (unchanged)
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
            
            # Single-character operators (unchanged)
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
            
            # Unknown character
            self.error(f"Invalid character: '{self.current_char}'")
        
        return Token(Token.EOF, None)