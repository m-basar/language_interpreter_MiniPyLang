"""
parser.py - Enhanced parser supporting multi-statement programs with variables

Stage 4 parsing introduces several new concepts:
1. Distinguishing between statements and expressions
2. Handling statement sequences separated by newlines
3. Managing variable assignments and references
4. Integrating control flow preparation for future stages
"""

from tokens import Token
from ast_nodes import (
    NumberNode, BooleanNode, StringNode, VariableNode,
    BinaryOperationNode, UnaryOperationNode,
    AssignmentNode, PrintNode, ProgramNode
)


class ParseError(Exception):
    """Enhanced parse error with detailed context information"""
    def __init__(self, message, token=None, line=None):
        self.message = message
        self.token = token
        self.line = line
        
        error_msg = message
        if token and hasattr(token, 'type'):
            error_msg += f" (found {token.type}: {token.value})"
        if line:
            error_msg += f" at line {line}"
        
        super().__init__(error_msg)


class Parser:
    """
    Enhanced parser supporting multi-statement programs with variables.
    
    The parser now handles the distinction between statements and expressions,
    which is fundamental to most programming languages. This architectural
    change prepares us for control flow statements in Stage 5.
    
    Grammar:
    program     : statement_list
    statement_list : statement (NEWLINE statement)*
    statement   : assignment | print_stmt | expression
    assignment  : IDENTIFIER ASSIGN expression
    print_stmt  : PRINT expression
    expression  : logical_or
    logical_or  : logical_and (OR logical_and)*
    logical_and : equality (AND equality)*
    equality    : comparison ((EQUAL | NOT_EQUAL) comparison)*
    comparison  : term ((LESS_THAN | GREATER_THAN | LESS_EQUAL | GREATER_EQUAL) term)*
    term        : factor ((PLUS | MINUS) factor)*
    factor      : unary ((MULTIPLY | DIVIDE) unary)*
    unary       : (PLUS | MINUS | NOT) unary | primary
    primary     : NUMBER | BOOLEAN | STRING | IDENTIFIER | LPAREN expression RPAREN
    """
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        
        # Skip any leading newlines
        while self.current_token.type == Token.NEWLINE:
            self.current_token = self.lexer.get_next_token()
    
    def error(self, message="Invalid syntax"):
        """Enhanced error reporting with token context"""
        line_info = getattr(self.lexer, 'line', None)
        raise ParseError(message, self.current_token, line_info)
    
    def eat(self, token_type):
        """
        Consume a token of the expected type with enhanced error reporting.
        
        This method now provides more specific error messages to help
        users understand what went wrong in their programs.
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            expected_name = token_type.replace('_', ' ').lower()
            self.error(f"Expected {expected_name}")
    
    def skip_newlines(self):
        """
        Skip newline tokens for flexible statement formatting.
        
        This method allows users to include blank lines in their programs
        for readability without affecting execution.
        """
        while self.current_token.type == Token.NEWLINE:
            self.current_token = self.lexer.get_next_token()
    
    def program(self):
        """
        Parse a complete program consisting of multiple statements.
        
        This is the new top-level parsing rule that handles sequences
        of statements, transforming our language from a calculator
        into a programming environment.
        """
        statements = []
        
        # Skip any leading newlines
        self.skip_newlines()
        
        # Parse statements until end of input
        while self.current_token.type != Token.EOF:
            stmt = self.statement()
            statements.append(stmt)
            
            # Handle statement separators (newlines or EOF)
            if self.current_token.type == Token.NEWLINE:
                self.eat(Token.NEWLINE)
                self.skip_newlines()  # Allow multiple blank lines
            elif self.current_token.type == Token.EOF:
                break
            else:
                self.error("Expected newline or end of input after statement")
        
        return ProgramNode(statements)
    
    def statement(self):
        """
        Parse a single statement: assignment, print, or expression.
        
        This method demonstrates the fundamental distinction between
        statements (which perform actions) and expressions (which produce values).
        """
        # Check for assignment: IDENTIFIER ASSIGN expression
        if (self.current_token.type == Token.IDENTIFIER and 
            hasattr(self.lexer, 'peek') and 
            self.lexer.peek() == '='):
            return self.assignment()
        
        # Check for print statement: PRINT expression
        elif self.current_token.type == Token.PRINT:
            return self.print_statement()
        
        # Otherwise, it's an expression statement
        else:
            return self.expression()
    
    def assignment(self):
        """
        Parse variable assignment: IDENTIFIER ASSIGN expression
        
        Assignment statements modify program state by storing values
        in the environment. This is where programs gain memory.
        """
        # Get the variable name
        if self.current_token.type != Token.IDENTIFIER:
            self.error("Expected variable name in assignment")
        
        variable_name = self.current_token.value
        self.eat(Token.IDENTIFIER)
        
        # Expect assignment operator
        self.eat(Token.ASSIGN)
        
        # Parse the expression to assign
        expression = self.expression()
        
        return AssignmentNode(variable_name, expression)
    
    def print_statement(self):
        """
        Parse print statement: PRINT expression
        
        Print statements provide program output, enabling communication
        between the program and its users.
        """
        self.eat(Token.PRINT)
        expression = self.expression()
        return PrintNode(expression)
    
    def primary(self):
        """
        Parse primary expressions: literals, variables, and parenthesized expressions.
        
        The addition of IDENTIFIER for variable lookup is the key change
        that enables programs to access stored values.
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
        
        elif token.type == Token.STRING:
            self.eat(Token.STRING)
            return StringNode(token)
        
        elif token.type == Token.IDENTIFIER:
            # Variable reference - new for Stage 4
            self.eat(Token.IDENTIFIER)
            return VariableNode(token)
        
        elif token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.expression()
            self.eat(Token.RPAREN)
            return node
        
        else:
            self.error("Expected number, boolean, string, variable, or parenthesized expression")
    
    # The rest of the expression parsing methods remain largely unchanged
    # but now work within the new statement-based architecture
    
    def unary(self):
        """Parse unary expressions: +, -, ! followed by unary expressions"""
        if self.current_token.type in (Token.PLUS, Token.MINUS, Token.NOT):
            token = self.current_token
            self.eat(token.type)
            return UnaryOperationNode(token, self.unary())
        else:
            return self.primary()
    
    def factor(self):
        """Parse multiplication and division"""
        node = self.unary()
        
        while self.current_token.type in (Token.MULTIPLY, Token.DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.unary())
        
        return node
    
    def term(self):
        """Parse addition and subtraction"""
        node = self.factor()
        
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.factor())
        
        return node
    
    def comparison(self):
        """Parse comparison operations"""
        node = self.term()
        
        while self.current_token.type in (Token.LESS_THAN, Token.GREATER_THAN, 
                                         Token.LESS_EQUAL, Token.GREATER_EQUAL):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.term())
        
        return node
    
    def equality(self):
        """Parse equality and inequality operations"""
        node = self.comparison()
        
        while self.current_token.type in (Token.EQUAL, Token.NOT_EQUAL):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.comparison())
        
        return node
    
    def logical_and(self):
        """Parse logical AND operations"""
        node = self.equality()
        
        while self.current_token.type == Token.AND:
            token = self.current_token
            self.eat(Token.AND)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.equality())
        
        return node
    
    def logical_or(self):
        """Parse logical OR operations"""
        node = self.logical_and()
        
        while self.current_token.type == Token.OR:
            token = self.current_token
            self.eat(Token.OR)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.logical_and())
        
        return node
    
    def expression(self):
        """Parse complete expressions"""
        return self.logical_or()
    
    def parse(self):
        """Main parsing entry point"""
        return self.program()