"""
parser.py - Enhanced Stage 5 parser with control flow

Converts tokens into an AST supporting control flow constructs:
- if statements with optional else clauses
- while loops
- Code blocks with braces
- input() function calls
"""

from tokens import Token
from ast_nodes import (
    NumberNode, BooleanNode, StringNode, VariableNode,
    BinaryOperationNode, UnaryOperationNode,
    AssignmentNode, PrintNode, ProgramNode, DeleteNode, NoneNode,
    ConversionNode,
    # NEW: Control flow nodes
    IfNode, WhileNode, BlockNode, InputNode
)


class ParseError(Exception):
    """Parser error with context information"""
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
    Enhanced Stage 5 parser with control flow for MiniPyLang.
    
    Grammar (enhanced with control flow):
    programme     : statement_list
    statement_list : statement (NEWLINE statement)*
    statement   : assignment | print_stmt | delete_stmt | if_stmt | while_stmt | expression
    assignment  : IDENTIFIER ASSIGN expression
    print_stmt  : PRINT expression
    delete_stmt : DEL IDENTIFIER
    if_stmt     : IF LPAREN expression RPAREN block (ELSE block)?
    while_stmt  : WHILE LPAREN expression RPAREN block
    block       : LBRACE statement_list RBRACE | statement
    expression  : logical_or
    logical_or  : logical_and (OR logical_and)*
    logical_and : equality (AND equality)*
    equality    : comparison ((EQUAL | NOT_EQUAL) comparison)*
    comparison  : term ((LESS_THAN | GREATER_THAN | LESS_EQUAL | GREATER_EQUAL) term)*
    term        : factor ((PLUS | MINUS) factor)*
    factor      : unary ((MULTIPLY | DIVIDE) unary)*
    unary       : (PLUS | MINUS | NOT) unary | primary
    primary     : NUMBER | BOOLEAN | STRING | IDENTIFIER | NONE | conversion_call | input_call | LPAREN expression RPAREN
    conversion_call : (STR_FUNC | INT_FUNC | FLOAT_FUNC | BOOL_FUNC) LPAREN expression RPAREN
    input_call  : INPUT_FUNC LPAREN (expression)? RPAREN
    """
    
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        
        # Skip any leading newlines
        while self.current_token.type == Token.NEWLINE:
            self.current_token = self.lexer.get_next_token()
    
    def error(self, message="Invalid syntax"):
        """Raise parser error with context"""
        line_info = getattr(self.lexer, 'line', None)
        raise ParseError(message, self.current_token, line_info)
    
    def eat(self, token_type):
        """Consume expected token type"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            expected_name = token_type.replace('_', ' ').lower()
            self.error(f"Expected {expected_name}")
    
    def peek_next_token(self):
        """Look ahead at the next token without consuming the current token"""
        # Save lexer state
        saved_pos = self.lexer.pos
        saved_char = self.lexer.current_char
        saved_line = self.lexer.line
        saved_column = self.lexer.column
        
        # Get next token
        next_token = self.lexer.get_next_token()
        
        # Restore lexer state
        self.lexer.pos = saved_pos
        self.lexer.current_char = saved_char
        self.lexer.line = saved_line
        self.lexer.column = saved_column
        
        return next_token
    
    def skip_newlines(self):
        """Skip newline tokens for flexible formatting"""
        while self.current_token.type == Token.NEWLINE:
            self.current_token = self.lexer.get_next_token()
    
    def program(self):
        """Parse complete programme: sequence of statements"""
        statements = []
        
        # Skip leading newlines
        self.skip_newlines()
        
        # Parse statements until end of input
        while self.current_token.type != Token.EOF:
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
            
            # Handle statement separators
            if self.current_token.type == Token.NEWLINE:
                self.eat(Token.NEWLINE)
                self.skip_newlines()
            elif self.current_token.type == Token.EOF:
                break
            else:
                # For interactive mode – allow statements without newlines
                break
        
        return ProgramNode(statements)
    
    def statement(self):
        """Parse individual statements including control flow"""
        # Delete statement: del variable
        if self.current_token.type == Token.DEL:
            return self.delete_statement()
        
        # Print statement: print expression
        elif self.current_token.type == Token.PRINT:
            return self.print_statement()
        
        # NEW: If statement
        elif self.current_token.type == Token.IF:
            return self.if_statement()
        
        # NEW: While statement
        elif self.current_token.type == Token.WHILE:
            return self.while_statement()
        
        # Assignment or variable reference
        elif self.current_token.type == Token.IDENTIFIER:
            # Look ahead to determine if this is assignment
            next_token = self.peek_next_token()
            if next_token.type == Token.ASSIGN:
                return self.assignment()
            else:
                # Variable reference in expression
                return self.expression()
        
        # Expression statement
        else:
            return self.expression()
    
    def delete_statement(self):
        """Parse delete statement: del variable_name"""
        self.eat(Token.DEL)
        
        if self.current_token.type != Token.IDENTIFIER:
            self.error("Expected variable name after 'del'")
        
        variable_name = self.current_token.value
        self.eat(Token.IDENTIFIER)
        
        return DeleteNode(variable_name)
    
    def assignment(self):
        """Parse assignment: variable = expression"""
        if self.current_token.type != Token.IDENTIFIER:
            self.error("Expected variable name in assignment")
        
        variable_name = self.current_token.value
        self.eat(Token.IDENTIFIER)
        self.eat(Token.ASSIGN)
        expression = self.expression()
        
        return AssignmentNode(variable_name, expression)
    
    def print_statement(self):
        """Parse print statement: print expression"""
        self.eat(Token.PRINT)
        expression = self.expression()
        return PrintNode(expression)
    
    # NEW: Control flow statement parsing
    def if_statement(self):
        """
        Parse if statement: if (condition) { statements } else { statements }
        
        The else clause is optional.
        """
        self.eat(Token.IF)
        self.eat(Token.LPAREN)
        condition = self.expression()
        self.eat(Token.RPAREN)
        
        then_block = self.block()
        
        # Optional else clause
        else_block = None
        if self.current_token.type == Token.ELSE:
            self.eat(Token.ELSE)
            else_block = self.block()
        
        return IfNode(condition, then_block, else_block)
    
    def while_statement(self):
        """Parse while loop: while (condition) { statements }"""
        self.eat(Token.WHILE)
        self.eat(Token.LPAREN)
        condition = self.expression()
        self.eat(Token.RPAREN)
        
        body = self.block()
        
        return WhileNode(condition, body)
    
    def block(self):
        """
        Parse code block: { statement1; statement2; ... } or single statement
        
        Supports both braced blocks and single statements for flexibility.
        """
        if self.current_token.type == Token.LBRACE:
            # Braced block
            self.eat(Token.LBRACE)
            self.skip_newlines()
            
            statements = []
            while self.current_token.type not in (Token.RBRACE, Token.EOF):
                stmt = self.statement()
                if stmt is not None:
                    statements.append(stmt)
                
                # Handle statement separators within blocks
                if self.current_token.type == Token.NEWLINE:
                    self.eat(Token.NEWLINE)
                    self.skip_newlines()
                elif self.current_token.type == Token.RBRACE:
                    break
                else:
                    # Allow single statements without separators in interactive mode
                    break
            
            self.eat(Token.RBRACE)
            return BlockNode(statements)
        else:
            # Single statement (no braces)
            stmt = self.statement()
            return BlockNode([stmt] if stmt is not None else [])
    
    def expression(self):
        """Parse complete expressions"""
        return self.logical_or()
    
    def logical_or(self):
        """Parse logical OR: expr1 or expr2"""
        node = self.logical_and()
        
        while self.current_token.type == Token.OR:
            token = self.current_token
            self.eat(Token.OR)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.logical_and())
        
        return node
    
    def logical_and(self):
        """Parse logical AND: expr1 and expr2"""
        node = self.equality()
        
        while self.current_token.type == Token.AND:
            token = self.current_token
            self.eat(Token.AND)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.equality())
        
        return node
    
    def equality(self):
        """Parse equality operations: expr1 == expr2, expr1 != expr2"""
        node = self.comparison()
        
        while self.current_token.type in (Token.EQUAL, Token.NOT_EQUAL):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.comparison())
        
        return node
    
    def comparison(self):
        """Parse comparison operations: <, >, <=, >="""
        node = self.term()
        
        while self.current_token.type in (Token.LESS_THAN, Token.GREATER_THAN, 
                                         Token.LESS_EQUAL, Token.GREATER_EQUAL):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.term())
        
        return node
    
    def term(self):
        """Parse addition and subtraction: expr1 + expr2, expr1 - expr2"""
        node = self.factor()
        
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.factor())
        
        return node
    
    def factor(self):
        """Parse multiplication and division: expr1 * expr2, expr1 / expr2"""
        node = self.unary()
        
        while self.current_token.type in (Token.MULTIPLY, Token.DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOperationNode(left=node, operator_token=token, right=self.unary())
        
        return node
    
    def unary(self):
        """Parse unary operations: +expr, -expr, !expr"""
        if self.current_token.type in (Token.PLUS, Token.MINUS, Token.NOT):
            token = self.current_token
            self.eat(token.type)
            return UnaryOperationNode(token, self.unary())
        else:
            return self.primary()
    
    def primary(self):
        """
        Parse primary expressions including type conversion and input functions.
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
            # Variable reference
            self.eat(Token.IDENTIFIER)
            return VariableNode(token)
        
        elif token.type == Token.NONE:
            self.eat(Token.NONE)
            return NoneNode(token)
        
        # Type conversion functions
        elif token.type in (Token.STR_FUNC, Token.INT_FUNC, Token.FLOAT_FUNC, Token.BOOL_FUNC):
            return self.conversion_call()
        
        # NEW: Input function
        elif token.type == Token.INPUT_FUNC:
            return self.input_call()
        
        elif token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.expression()
            self.eat(Token.RPAREN)
            return node
        
        else:
            self.error("Expected number, boolean, string, variable, function call, or parenthesised expression")
    
    def conversion_call(self):
        """
        Parse type conversion function calls: str(expr), int(expr), etc.
        """
        # Get the conversion type
        conversion_type = self.current_token.value  # 'str', 'int', 'float', 'bool'
        self.eat(self.current_token.type)  # Eat the conversion function token
        
        # Parse function call syntax: function(argument)
        self.eat(Token.LPAREN)
        expression = self.expression()
        self.eat(Token.RPAREN)
        
        return ConversionNode(conversion_type, expression)
    
    def input_call(self):
        """
        Parse input function calls: input() or input("prompt")
        """
        self.eat(Token.INPUT_FUNC)
        self.eat(Token.LPAREN)
        
        # Optional prompt argument
        prompt_expression = None
        if self.current_token.type != Token.RPAREN:
            prompt_expression = self.expression()
        
        self.eat(Token.RPAREN)
        
        return InputNode(prompt_expression)
    
    def parse(self):
        """Main parsing entry point"""
        return self.program()
