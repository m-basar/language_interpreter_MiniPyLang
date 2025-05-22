"""
parser.py - Enhanced recursive descent parser with Boolean support

We're extending our grammar to handle Boolean expressions and comparisons.
The key challenge is establishing proper operator precedence.

Enhanced Grammar:
logical_or    : logical_and (OR logical_and)*
logical_and   : equality (AND equality)*
equality      : comparison ((EQUAL | NOT_EQUAL) comparison)*
comparison    : expression ((LESS_THAN | GREATER_THAN | LESS_EQUAL | GREATER_EQUAL) expression)*
expression    : term ((PLUS | MINUS) term)*
term          : factor ((MULTIPLY | DIVIDE) factor)*
factor        : NUMBER | BOOLEAN | LPAREN logical_or RPAREN | (PLUS | MINUS | NOT) factor
"""

from tokens import Token
from ast_nodes import NumberNode, BooleanNode, BinaryOperationNode, UnaryOperationNode

class ParseError(Exception):
    """Custom exception for parsing errors"""
    pass

class Parser:
    """
    Enhanced parser that handles both arithmetic and Boolean expressions.
    
    The grammar is structured to ensure proper operator precedence:
    1. Logical OR (lowest precedence)
    2. Logical AND
    3. Equality/Inequality (==, !=)
    4. Comparison (<, >, <=, >=)
    5. Addition/Subtraction
    6. Multiplication/Division
    7. Unary operators (-, +, !) (highest precedence)
    """
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self, message="Invalid syntax"):
        raise ParseError(f"{message}. Current token: {self.current_token}")
    
    def eat(self, token_type):
        """Consume a token of the expected type"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}")
    
    def factor(self):
        """
        Parse factors: NUMBER | BOOLEAN | LPAREN logical_or RPAREN | (PLUS | MINUS | NOT) factor
        
        Factors are the atomic elements of our expressions.
        """
        token = self.current_token
        
        if token.type == Token.NUMBER:
            self.eat(Token.NUMBER)
            return NumberNode(token)
        
        elif token.type == Token.TRUE:
            self.eat(Token.TRUE)
            return BooleanNode(token)
        
        elif token.type == Token.FALSE:
            self.eat(Token.FALSE)
            return BooleanNode(token)
        
        elif token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.logical_or()  # Parse the full expression inside parentheses
            self.eat(Token.RPAREN)
            return node
        
        elif token.type in (Token.PLUS, Token.MINUS, Token.NOT):
            # Handle unary operators
            self.eat(token.type)
            return UnaryOperationNode(token, self.factor())
        
        else:
            self.error("Expected number, boolean, parentheses, or unary operator")
    
    def term(self):
        """Parse terms: factor ((MULTIPLY | DIVIDE) factor)*"""
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
        """Parse expressions: term ((PLUS | MINUS) term)*"""
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
        """
        Parse comparisons: expression ((LESS_THAN | GREATER_THAN | LESS_EQUAL | GREATER_EQUAL) expression)*
        
        Comparison operators have lower precedence than arithmetic operators.
        """
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
        """
        Parse equality: comparison ((EQUAL | NOT_EQUAL) comparison)*
        
        Equality operators have lower precedence than comparison operators.
        """
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
        """
        Parse logical AND: equality (AND equality)*
        
        Logical AND has lower precedence than equality operators.
        """
        node = self.equality()
        
        while self.current_token.type == Token.AND:
            token = self.current_token
            self.eat(Token.AND)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.equality())
        
        return node
    
    def logical_or(self):
        """
        Parse logical OR: logical_and (OR logical_and)*
        
        Logical OR has the lowest precedence of all operators.
        """
        node = self.logical_and()
        
        while self.current_token.type == Token.OR:
            token = self.current_token
            self.eat(Token.OR)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.logical_and())
        
        return node
    
    def parse(self):
        """Parse the input and return the root of the AST"""
        ast = self.logical_or()  # Start with the lowest precedence rule
        
        if self.current_token.type != Token.EOF:
            self.error("Unexpected token after expression")
        
        return ast
