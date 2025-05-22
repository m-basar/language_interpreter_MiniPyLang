"""
ast_nodes.py - Enhanced AST nodes with string literal support

String nodes introduce the concept of variable-length data in our AST.
Unlike numbers and Booleans, strings can be arbitrarily long, which
has implications for memory usage and processing time.
"""

class ASTNode:
    """Base class for all AST nodes – unchanged"""
    pass

class NumberNode(ASTNode):
    """Numeric literal node – unchanged from previous stages"""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f'Number({self.value})'

class BooleanNode(ASTNode):
    """Boolean literal node – unchanged from Stage 2"""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f'Boolean({self.value})'

class StringNode(ASTNode):
    """
    String literal node – new for Stage 3

    String nodes represent textual literals in our language.
    They are similar to number and Boolean nodes but represent
    potentially large, variable-length data.
    """
    
    def __init__(self, token):
        self.token = token
        self.value = token.value  # The actual string content
    
    def __str__(self):
        # Truncate very long strings for readable debugging output
        if len(self.value) > 20:
            return f'String("{self.value[:17]}...")'
        else:
            return f'String("{self.value}")'

class BinaryOperationNode(ASTNode):
    """
    Binary operation node – enhanced to handle string operations

    This node type now represents arithmetic, comparison, logical,
    and string operations, demonstrating how AST nodes may be
    reused across different language features.
    """
    
    def __init__(self, left, operator_token, right):
        self.left = left
        self.token = self.operator = operator_token
        self.right = right
    
    def __str__(self):
        return f'BinaryOp({self.operator.value})'

class UnaryOperationNode(ASTNode):
    """Unary operation node – unchanged from previous stages"""
    
    def __init__(self, operator_token, operand):
        self.token = self.operator = operator_token
        self.operand = operand
    
    def __str__(self):
        return f'UnaryOp({self.operator.value})'
