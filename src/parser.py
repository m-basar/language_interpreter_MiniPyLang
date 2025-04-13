class AST:
    """Base class for all Abstract Syntax Tree nodes."""
    pass

class BinOp(AST):
    """
    Represents a binary operation in the AST.
    
    Attributes:
        left: Left operand
        token: Operation token
        right: Right operand
    """
    def __init__(self, left, token, right):
        self.left = left
        self.token = token
        self.right = right
        self.op = token.value
    
    def __str__(self):
        return f"BinOp({self.left}, {self.op}, {self.right})"

class UnaryOp(AST):
    """
    Represents a unary operation in the AST.
    
    Attributes:
        token: Operation token
        expr: Expression being operated on
    """
    def __init__(self, token, expr):
        self.token = token
        self.op = token.value
        self.expr = expr
    
    def __str__(self):
        return f"UnaryOp({self.op}, {self.expr})"

class Num(AST):
    """
    Represents a numeric value in the AST.
    
    Attributes:
        token: Number token
        value: Value of the number
    """
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f"Num({self.value})"

class Parser:
    """
    Parses tokens into an abstract syntax tree.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[0]
    
    def error(self):
        """Raises an error for invalid syntax."""
        raise Exception(f"Invalid syntax at token {self.current_token}")
    
    def advance(self):
        """Advances to the next token."""
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
    
    def eat(self, token_type):
        """
        Consumes the current token if it matches the expected type.
        
        Args:
            token_type: Expected token type
        """
        if self.current_token.type == token_type:
            self.advance()
        else:
            self.error()
    
    def factor(self):
        """
        Factor: NUMBER | (PLUS|MINUS) factor | LPAREN expr RPAREN
        """
        token = self.current_token
        
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Num(token)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        elif token.type in ('PLUS', 'MINUS'):
            self.eat(token.type)
            return UnaryOp(token, self.factor())
        
        self.error()
    
    def term(self):
        """
        Term: factor ((MULTIPLY|DIVIDE) factor)*
        """
        node = self.factor()
        
        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.factor())
        
        return node
    
    def expr(self):
        """
        Expression: term ((PLUS|MINUS) term)*
        """
        node = self.term()
        
        while self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(node, token, self.term())
        
        return node
    
    def parse(self):
        """
        Parses the tokens into an AST.
        
        Returns:
            The root node of the AST
        """
        return self.expr()