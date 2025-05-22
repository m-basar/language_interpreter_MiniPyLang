"""
parser.py - Enhanced parser with string literal support

Adding string support to the parser demonstrates how new data types
can be integrated into existing grammatical structures without
disrupting the overall parsing strategy.
"""

from tokens import Token
from ast_nodes import NumberNode, BooleanNode, StringNode, BinaryOperationNode, UnaryOperationNode

class ParseError(Exception):
    """Enhanced parse error with better context information"""
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        error_msg = message
        if token:
            error_msg += f" (found {token})"
        super().__init__(error_msg)

class Parser:
    """
    Enhanced parser supporting arithmetic, Boolean, and string expressions.
    
    The grammar remains largely unchanged, demonstrating how well-designed
    language grammars can accommodate new features gracefully.
    
    Grammar (unchanged structure, expanded terminals):
    logical_or    : logical_and (OR logical_and)*
    logical_and   : equality (AND equality)*
    equality      : comparison ((EQUAL | NOT_EQUAL) comparison)*
    comparison    : expression ((LESS_THAN | GREATER_THAN | LESS_EQUAL | GREATER_EQUAL) expression)*
    expression    : term ((PLUS | MINUS) term)*
    term          : factor ((MULTIPLY | DIVIDE) factor)*
    factor        : NUMBER | BOOLEAN | STRING | LPAREN logical_or RPAREN | (PLUS | MINUS | NOT) factor
    """
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self, message="Invalid syntax"):
        """Raise a parsing error with context information"""
        raise ParseError(message, self.current_token)
    
    def eat(self, token_type):
        """
        Consume a token of the expected type.
        
        This method provides clear error messages when the parser
        encounters unexpected tokens, which helps with debugging.
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}")
    
    def factor(self):
        """
        Parse factors: NUMBER | BOOLEAN | STRING | LPAREN logical_or RPAREN | (PLUS | MINUS | NOT) factor
        
        The addition of STRING to this rule demonstrates how new data types
        integrate into existing grammatical structures.
        """
        token = self.current_token
        
        # Numeric literals
        if token.type == Token.NUMBER:
            self.eat(Token.NUMBER)
            return NumberNode(token)
        
        # Boolean literals
        elif token.type == Token.TRUE:
            self.eat(Token.TRUE)
            return BooleanNode(token)
        
        elif token.type == Token.FALSE:
            self.eat(Token.FALSE)
            return BooleanNode(token)
        
        # String literals - new for Stage 3
        elif token.type == Token.STRING:
            self.eat(Token.STRING)
            return StringNode(token)
        
        # Parenthesised expressions
        elif token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.logical_or()  # Parse the full expression inside parentheses
            self.eat(Token.RPAREN)
            return node
        
        # Unary operators
        elif token.type in (Token.PLUS, Token.MINUS, Token.NOT):
            self.eat(token.type)
            return UnaryOperationNode(token, self.factor())
        
        else:
            self.error("Expected number, boolean, string, parenthesis, or unary operator")
    
    def term(self):
        """Parse multiplication and division - unchanged from previous stages"""
        node = self.factor()
        
        while self.current_token.type in (Token.MULTIPLY, Token.DIVIDE):
            token = self.current_token
            
            if token.type == Token.MULTIPLY:
                self.eat(Token.MULTIPLY)
            elif token.type == Token.DIVIDE:
                self.eat(Token.DIVIDE)
            
            node = BinaryOperationNode(left=node, operator_token=token, right=self.factor())
        
        return node
    
    def expression(self):
        """Parse addition and subtraction - unchanged but now handles string concatenation"""
        node = self.term()
        
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            token = self.current_token
            
            if token.type == Token.PLUS:
                self.eat(Token.PLUS)
            elif token.type == Token.MINUS:
                self.eat(Token.MINUS)
            
            node = BinaryOperationNode(left=node, operator_token=token, right=self.term())
        
        return node
    
    def comparison(self):
        """Parse comparison operations - unchanged from Stage 2"""
        node = self.expression()
        
        while self.current_token.type in (Token.LESS_THAN, Token.GREATER_THAN, 
                                         Token.LESS_EQUAL, Token.GREATER_EQUAL):
            token = self.current_token
            
            if token.type == Token.LESS_THAN:
                self.eat(Token.LESS_THAN)
            elif token.type == Token.GREATER_THAN:
                self.eat(Token.GREATER_THAN)
            elif token.type == Token.LESS_EQUAL:
                self.eat(Token.LESS_EQUAL)
            elif token.type == Token.GREATER_EQUAL:
                self.eat(Token.GREATER_EQUAL)
            
            node = BinaryOperationNode(left=node, operator_token=token, right=self.expression())
        
        return node
    
    def equality(self):
        """Parse equality operations - unchanged from Stage 2"""
        node = self.comparison()
        
        while self.current_token.type in (Token.EQUAL, Token.NOT_EQUAL):
            token = self.current_token
            
            if token.type == Token.EQUAL:
                self.eat(Token.EQUAL)
            elif token.type == Token.NOT_EQUAL:
                self.eat(Token.NOT_EQUAL)
            
            node = BinaryOperationNode(left=node, operator_token=token, right=self.comparison())
        
        return node
    
    def logical_and(self):
        """Parse logical AND operations - unchanged from Stage 2"""
        node = self.equality()
        
        while self.current_token.type == Token.AND:
            token = self.current_token
            self.eat(Token.AND)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.equality())
        
        return node
    
    def logical_or(self):
        """Parse logical OR operations - top level of expression grammar"""
        node = self.logical_and()
        
        while self.current_token.type == Token.OR:
            token = self.current_token
            self.eat(Token.OR)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.logical_and())
        
        return node
    
    def parse(self):
        """Parse the complete input and return the AST root"""
        ast = self.logical_or()
        
        if self.current_token.type != Token.EOF:
            self.error("Unexpected token after expression")
        
        return ast
