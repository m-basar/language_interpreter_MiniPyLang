"""
parser.py - Enhanced Stage 6 parser with list and dictionary support

Converts tokens into AST supporting list and dictionary constructs:
- List literals: [1, 2, 3]
- Dictionary literals: {"key": "value", "age": 25}
- Index/key access: list[index], dict["key"]
- Index/key assignment: list[index] = value, dict["key"] = value
- List functions: append(list, value), remove(list, index), len(list)
- Dictionary functions: keys(dict), values(dict), has_key(dict, key), del_key(dict, key)
"""

from tokens import Token
from ast_nodes import (
    NumberNode, BooleanNode, StringNode, VariableNode,
    BinaryOperationNode, UnaryOperationNode,
    AssignmentNode, PrintNode, ProgrammeNode, DeleteNode, NoneNode,
    ConversionNode, InputNode,
    IfNode, WhileNode, BlockNode,
    # List and Dictionary nodes
    ListNode, DictNode, IndexAccessNode, IndexAssignmentNode, 
    ListFunctionNode, DictFunctionNode
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
    Enhanced Stage 6 parser with list and dictionary support for MiniPyLang.
    
    Grammar (enhanced with lists and dictionaries):
    programme     : statement_list
    statement_list : statement (NEWLINE statement)*
    statement     : assignment | index_assignment | print_stmt | delete_stmt | if_stmt | while_stmt | expression
    assignment    : IDENTIFIER ASSIGN expression
    index_assignment : postfix_expr LBRACKET expression RBRACKET ASSIGN expression
    print_stmt    : PRINT expression
    delete_stmt   : DEL IDENTIFIER
    if_stmt       : IF LPAREN expression RPAREN block (ELSE block)?
    while_stmt    : WHILE LPAREN expression RPAREN block
    block         : LBRACE statement_list RBRACE | statement
    expression    : logical_or
    logical_or    : logical_and (OR logical_and)*
    logical_and   : equality (AND equality)*
    equality      : comparison ((EQUAL | NOT_EQUAL) comparison)*
    comparison    : term ((LESS_THAN | GREATER_THAN | LESS_EQUAL | GREATER_EQUAL) term)*
    term          : factor ((PLUS | MINUS) factor)*
    factor        : unary ((MULTIPLY | DIVIDE) unary)*
    unary         : (PLUS | MINUS | NOT) unary | postfix
    postfix       : primary (LBRACKET expression RBRACKET)*
    primary       : NUMBER | BOOLEAN | STRING | IDENTIFIER | NONE | list_literal | dict_literal |
                    conversion_call | list_function_call | dict_function_call | input_call | LPAREN expression RPAREN
    list_literal  : LBRACKET (expression (COMMA expression)*)? RBRACKET
    dict_literal  : LBRACE (dict_pair (COMMA dict_pair)*)? RBRACE
    dict_pair     : expression COLON expression
    conversion_call : (STR_FUNC | INT_FUNC | FLOAT_FUNC | BOOL_FUNC) LPAREN expression RPAREN
    list_function_call : (APPEND_FUNC | REMOVE_FUNC | LEN_FUNC) LPAREN expression (COMMA expression)* RPAREN
    dict_function_call : (KEYS_FUNC | VALUES_FUNC | HAS_KEY_FUNC | DEL_KEY_FUNC) LPAREN expression (COMMA expression)* RPAREN
    input_call    : INPUT_FUNC LPAREN (expression)? RPAREN
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
        """Look ahead at next token without consuming current token"""
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
    
    def programme(self):
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
                # For interactive mode - allow statements without newlines
                break
        
        return ProgrammeNode(statements)
    
    def statement(self):
        """Parse individual statements including list and dictionary operations"""
        # Delete statement: del variable
        if self.current_token.type == Token.DEL:
            return self.delete_statement()
        
        # Print statement: print expression
        elif self.current_token.type == Token.PRINT:
            return self.print_statement()
        
        # If statement
        elif self.current_token.type == Token.IF:
            return self.if_statement()
        
        # While statement
        elif self.current_token.type == Token.WHILE:
            return self.while_statement()
        
        # Assignment, index assignment, or expression
        elif self.current_token.type == Token.IDENTIFIER:
            # Look ahead to determine statement type
            next_token = self.peek_next_token()
            if next_token.type == Token.ASSIGN:
                return self.assignment()
            else:
                # Could be index assignment: variable[index] = value or dict["key"] = value
                # Parse as expression first, then check for assignment
                expr = self.expression()
                
                # Check if this is an index assignment
                if (isinstance(expr, IndexAccessNode) and 
                    self.current_token.type == Token.ASSIGN):
                    self.eat(Token.ASSIGN)
                    value_expr = self.expression()
                    return IndexAssignmentNode(
                        expr.container_expression,
                        expr.key_expression,
                        value_expr
                    )
                else:
                    return expr
        
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
    
    # Control flow statement parsing (unchanged from Stage 5)
    def if_statement(self):
        """Parse if statement: if (condition) { statements } else { statements }"""
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
        """Parse code block: { statement1; statement2; ... } or single statement"""
        if self.current_token.type == Token.LBRACE:
            # Need to distinguish between dictionary literal and code block
            # Look ahead to see if this looks like a dictionary or code block
            if self._looks_like_dictionary():
                # This is actually a dictionary literal, not a code block
                # Let it be handled by primary() -> dict_literal()
                self.error("Expected statement, not dictionary literal")
            
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
    
    def _looks_like_dictionary(self):
        """
        Heuristic to distinguish between dictionary literals and code blocks.
        Returns True if the content after { looks like a dictionary.
        """
        # Save current state
        saved_pos = self.lexer.pos
        saved_char = self.lexer.current_char
        saved_line = self.lexer.line
        saved_column = self.lexer.column
        saved_token = self.current_token
        
        try:
            # Look ahead after the opening brace
            if self.current_token.type == Token.LBRACE:
                self.current_token = self.lexer.get_next_token()
                
                # Empty braces could be either {} dict or {} block
                if self.current_token.type == Token.RBRACE:
                    return True  # Assume empty dictionary
                
                # Skip any newlines
                while self.current_token.type == Token.NEWLINE:
                    self.current_token = self.lexer.get_next_token()
                
                # Look for pattern: expression : expression
                # If we see keywords like 'if', 'while', 'print', it's likely a block
                if self.current_token.type in (Token.IF, Token.WHILE, Token.PRINT, Token.DEL):
                    return False
                
                # Try to parse what looks like a key
                try:
                    # Simple heuristic: if we see : after some tokens, it's likely a dictionary
                    token_count = 0
                    while (self.current_token.type not in (Token.EOF, Token.RBRACE, Token.NEWLINE) and 
                           token_count < 10):  # Limit lookahead
                        if self.current_token.type == Token.COLON:
                            return True
                        if self.current_token.type in (Token.IF, Token.WHILE, Token.PRINT, Token.DEL):
                            return False
                        self.current_token = self.lexer.get_next_token()
                        token_count += 1
                except:
                    pass
            
            return False
            
        finally:
            # Restore state
            self.lexer.pos = saved_pos
            self.lexer.current_char = saved_char
            self.lexer.line = saved_line
            self.lexer.column = saved_column
            self.current_token = saved_token
    
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
            return self.postfix()
    
    def postfix(self):
        """
        Parse postfix operations including index access: expr[index][index2]...
        
        This handles chained index operations like list[0][1] for nested structures.
        """
        node = self.primary()
        
        # Handle chained index access
        while self.current_token.type == Token.LBRACKET:
            self.eat(Token.LBRACKET)
            index_expr = self.expression()
            self.eat(Token.RBRACKET)
            node = IndexAccessNode(node, index_expr)
        
        return node
    
    def primary(self):
        """
        Parse primary expressions including list literals, dictionary literals, and functions.
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
        
        # List literal
        elif token.type == Token.LBRACKET:
            return self.list_literal()
        
        # Dictionary literal (reuses LBRACE/RBRACE from control flow)
        elif token.type == Token.LBRACE:
            return self.dict_literal()
        
        # Type conversion functions
        elif token.type in (Token.STR_FUNC, Token.INT_FUNC, Token.FLOAT_FUNC, Token.BOOL_FUNC):
            return self.conversion_call()
        
        # Input function
        elif token.type == Token.INPUT_FUNC:
            return self.input_call()
        
        # List functions
        elif token.type in (Token.APPEND_FUNC, Token.REMOVE_FUNC, Token.LEN_FUNC):
            return self.list_function_call()
        
        # NEW: Dictionary functions
        elif token.type in (Token.KEYS_FUNC, Token.VALUES_FUNC, Token.HAS_KEY_FUNC, Token.DEL_KEY_FUNC):
            return self.dict_function_call()
        
        elif token.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.expression()
            self.eat(Token.RPAREN)
            return node
        
        else:
            self.error("Expected number, boolean, string, variable, list, dictionary, function call, or parenthesised expression")
    
    def list_literal(self):
        """
        Parse list literal: [element1, element2, element3]
        
        Supports empty lists [] and lists with mixed types.
        """
        self.eat(Token.LBRACKET)
        
        elements = []
        
        # Handle empty list
        if self.current_token.type == Token.RBRACKET:
            self.eat(Token.RBRACKET)
            return ListNode(elements)
        
        # Parse first element
        elements.append(self.expression())
        
        # Parse remaining elements
        while self.current_token.type == Token.COMMA:
            self.eat(Token.COMMA)
            # Allow trailing comma: [1, 2, 3,]
            if self.current_token.type == Token.RBRACKET:
                break
            elements.append(self.expression())
        
        self.eat(Token.RBRACKET)
        return ListNode(elements)
    
    def dict_literal(self):
        """
        NEW: Parse dictionary literal: {"key1": value1, "key2": value2}
        
        Supports empty dictionaries {} and dictionaries with mixed key/value types.
        """
        self.eat(Token.LBRACE)
        
        pairs = []
        
        # Handle empty dictionary
        if self.current_token.type == Token.RBRACE:
            self.eat(Token.RBRACE)
            return DictNode(pairs)
        
        # Parse first key-value pair
        key_expr = self.expression()
        self.eat(Token.COLON)
        value_expr = self.expression()
        pairs.append((key_expr, value_expr))
        
        # Parse remaining pairs
        while self.current_token.type == Token.COMMA:
            self.eat(Token.COMMA)
            # Allow trailing comma: {"a": 1, "b": 2,}
            if self.current_token.type == Token.RBRACE:
                break
            
            key_expr = self.expression()
            self.eat(Token.COLON)
            value_expr = self.expression()
            pairs.append((key_expr, value_expr))
        
        self.eat(Token.RBRACE)
        return DictNode(pairs)
    
    def conversion_call(self):
        """Parse type conversion function calls: str(expr), int(expr), etc."""
        # Get the conversion type
        conversion_type = self.current_token.value  # 'str', 'int', 'float', 'bool'
        self.eat(self.current_token.type)  # Eat the conversion function token
        
        # Parse function call syntax: function(argument)
        self.eat(Token.LPAREN)
        expression = self.expression()
        self.eat(Token.RPAREN)
        
        return ConversionNode(conversion_type, expression)
    
    def input_call(self):
        """Parse input function calls: input() or input("prompt")"""
        self.eat(Token.INPUT_FUNC)
        self.eat(Token.LPAREN)
        
        # Optional prompt argument
        prompt_expression = None
        if self.current_token.type != Token.RPAREN:
            prompt_expression = self.expression()
        
        self.eat(Token.RPAREN)
        
        return InputNode(prompt_expression)
    
    def list_function_call(self):
        """
        Parse list function calls: append(list, value), remove(list, index), len(list)
        
        Different functions have different argument requirements:
        - append(list, value): 2 arguments
        - remove(list, index): 2 arguments  
        - len(list): 1 argument
        """
        function_name = self.current_token.value
        self.eat(self.current_token.type)  # Eat the function token
        
        self.eat(Token.LPAREN)
        
        arguments = []
        
        # Handle empty argument list (shouldn't happen for list functions, but be safe)
        if self.current_token.type == Token.RPAREN:
            self.eat(Token.RPAREN)
            return ListFunctionNode(function_name, arguments)
        
        # Parse first argument
        arguments.append(self.expression())
        
        # Parse remaining arguments
        while self.current_token.type == Token.COMMA:
            self.eat(Token.COMMA)
            arguments.append(self.expression())
        
        self.eat(Token.RPAREN)
        
        # Validate argument count for each function
        if function_name == 'len' and len(arguments) != 1:
            self.error(f"len() takes exactly 1 argument ({len(arguments)} given)")
        elif function_name in ['append', 'remove'] and len(arguments) != 2:
            self.error(f"{function_name}() takes exactly 2 arguments ({len(arguments)} given)")
        
        return ListFunctionNode(function_name, arguments)
    
    def dict_function_call(self):
        """
        NEW: Parse dictionary function calls: keys(dict), values(dict), has_key(dict, key), del_key(dict, key)
        
        Different functions have different argument requirements:
        - keys(dict): 1 argument
        - values(dict): 1 argument
        - has_key(dict, key): 2 arguments
        - del_key(dict, key): 2 arguments
        """
        function_name = self.current_token.value
        self.eat(self.current_token.type)  # Eat the function token
        
        self.eat(Token.LPAREN)
        
        arguments = []
        
        # Handle empty argument list (shouldn't happen for dict functions, but be safe)
        if self.current_token.type == Token.RPAREN:
            self.eat(Token.RPAREN)
            return DictFunctionNode(function_name, arguments)
        
        # Parse first argument
        arguments.append(self.expression())
        
        # Parse remaining arguments
        while self.current_token.type == Token.COMMA:
            self.eat(Token.COMMA)
            arguments.append(self.expression())
        
        self.eat(Token.RPAREN)
        
        # Validate argument count for each function
        if function_name in ['keys', 'values'] and len(arguments) != 1:
            self.error(f"{function_name}() takes exactly 1 argument ({len(arguments)} given)")
        elif function_name in ['has_key', 'del_key'] and len(arguments) != 2:
            self.error(f"{function_name}() takes exactly 2 arguments ({len(arguments)} given)")
        
        return DictFunctionNode(function_name, arguments)
    
    def parse(self):
        """Main parsing entry point"""
        return self.programme()