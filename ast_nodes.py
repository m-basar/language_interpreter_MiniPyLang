"""
ast_nodes.py – AST node definitions with enhanced string representations

These updated nodes provide clearer output when visualising parse trees.
"""

class ASTNode:
    """Base class for all AST nodes."""
    pass

class NumberNode(ASTNode):
    """Represents a numeric literal."""

    def __init__(self, token):
        self.token = token
        self.value = token.value

    def __str__(self):
        # Display the value for clarity during tree visualisation
        return f'Number({self.value})'

class BinaryOperationNode(ASTNode):
    """Represents a binary operation such as +, -, *, or /."""

    def __init__(self, left, operator_token, right):
        self.left = left
        self.token = self.operator = operator_token
        self.right = right

    def __str__(self):
        # Show the operator symbol for easy identification in trees
        return f'BinaryOp({self.operator.value})'

class UnaryOperationNode(ASTNode):
    """Represents a unary operation, e.g., -5 or +3."""

    def __init__(self, operator_token, operand):
        self.token = self.operator = operator_token
        self.operand = operand

    def __str__(self):
        # Show the unary operator for clarity in visualisations
        return f'UnaryOp({self.operator.value})'
