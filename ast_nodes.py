"""
ast_nodes.py - AST nodes with Boolean support

We're adding new node types to represent Boolean values and logical operations.
"""

class ASTNode:
    """Base class for all AST nodes."""
    pass

class NumberNode(ASTNode):
    """Represents a numeric literal (unchanged from Stage 1)."""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f'Number({self.value})'

class BooleanNode(ASTNode):
    """
    Represents a Boolean literal (true or false).
    This is similar to NumberNode but for Boolean values.
    """
    
    def __init__(self, token):
        self.token = token
        self.value = token.value  # This will be True or False
    
    def __str__(self):
        return f'Boolean({self.value})'

class BinaryOperationNode(ASTNode):
    """
    Represents any binary operation (arithmetic, comparison, or logical).
    We're reusing this node type for all binary operations, which keeps our AST simple.
    """
    
    def __init__(self, left, operator_token, right):
        self.left = left
        self.token = self.operator = operator_token
        self.right = right
    
    def __str__(self):
        return f'BinaryOp({self.operator.value})'

class UnaryOperationNode(ASTNode):
    """
    Represents unary operations (-, +, or ! for Boolean negation).
    We're extending this to handle logical NOT in addition to arithmetic negation.
    """
    
    def __init__(self, operator_token, operand):
        self.token = self.operator = operator_token
        self.operand = operand
    
    def __str__(self):
        return f'UnaryOp({self.operator.value})'
