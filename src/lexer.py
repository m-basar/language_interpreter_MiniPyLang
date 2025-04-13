class Token:
    """
    Represents a token in the language.
    
    Attributes:
        type (str): The type of the token
        value: The value of the token
        line (int): Line number where the token appears
        column (int): Column number where the token appears
    """
    def __init__(self, type, value, line=0, column=0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, column={self.column})"
    
    def __repr__(self):
        return self.__str__()

class Lexer:
    """
    Converts source code into tokens.
    """
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.current_char = self.source_code[0] if self.source_code else None
    
    def error(self):
        """Raises an error for invalid characters."""
        raise Exception(f"Invalid character '{self.current_char}' at line {self.line}, column {self.column}")
    
    def advance(self):
        """Advances to the next character in the source code."""
        self.position += 1
        self.column += 1
        
        if self.position >= len(self.source_code):
            self.current_char = None
        else:
            self.current_char = self.source_code[self.position]
            if self.current_char == '\n':
                self.line += 1
                self.column = 0
    
    def skip_whitespace(self):
        """Skips whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def number(self):
        """Processes a numeric token."""
        result = ''
        has_dot = False
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_dot:
                    break
                has_dot = True
            result += self.current_char
            self.advance()
        
        if has_dot:
            return float(result)
        else:
            return int(result)
    
    def tokenize(self):
        """Tokenizes the source code."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isdigit() or self.current_char == '.':
                self.tokens.append(Token('NUMBER', self.number(), self.line, self.column))
                continue
            
            if self.current_char == '+':
                self.tokens.append(Token('PLUS', '+', self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '-':
                self.tokens.append(Token('MINUS', '-', self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '*':
                self.tokens.append(Token('MULTIPLY', '*', self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '/':
                self.tokens.append(Token('DIVIDE', '/', self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == '(':
                self.tokens.append(Token('LPAREN', '(', self.line, self.column))
                self.advance()
                continue
            
            if self.current_char == ')':
                self.tokens.append(Token('RPAREN', ')', self.line, self.column))
                self.advance()
                continue
            
            self.error()
        
        self.tokens.append(Token('EOF', None, self.line, self.column))
        return self.tokens