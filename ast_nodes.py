"""
ast_nodes.py – Abstract Syntax Tree node definitions

AST nodes represent the structure of parsed expressions.
Each node type corresponds to a different kind of construct in the language.
"""

class ASTNode:
    """
    Base class for all AST nodes.
    This establishes the common interface shared by all nodes.
    """
    pass

class NumberNode(ASTNode):
    """
    Represents a numeric literal in an expression.
    This is a leaf node – it has no children.

    Example: In the expression "5 + 3", there would be two NumberNode instances,
    one for 5 and one for 3.
    """

    def __init__(self, token):
        """
        Args:
            token: The token containing the numeric value.
        """
        self.token = token
        self.value = token.value

    def __str__(self):
        return f'NumberNode({self.value})'

class BinaryOperationNode(ASTNode):
    """
    Represents a binary operation (an operation with two operands).
    This is an internal node with precisely two children: left and right.

    Example: In "5 + 3", this would represent the '+' operation with 5 and 3 as its children.
    """

    def __init__(self, left, operator_token, right):
        """
        Args:
            left: The left operand (another AST node).
            operator_token: The token representing the operation (+, -, *, /).
            right: The right operand (another AST node).
        """
        self.left = left
        self.token = self.operator = operator_token
        self.right = right

    def __str__(self):
        return f'BinaryOp({self.left}, {self.operator.value}, {self.right})'

class UnaryOperationNode(ASTNode):
    """
    Represents a unary operation (an operation with one operand).
    This is used for cases such as negative numbers: -5

    Example: In "-5", this would represent the '-' operation with 5 as its child.
    """

    def __init__(self, operator_token, operand):
        """
        Args:
            operator_token: The token representing the operation (+ or -).
            operand: The operand (another AST node).
        """
        self.token = self.operator = operator_token
        self.operand = operand

    def __str__(self):
        return f'UnaryOp({self.operator.value}, {self.operand})'
