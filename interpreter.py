"""
interpreter.py – Tree-walking interpreter for arithmetic expressions

The interpreter traverses the AST and computes the final result.
It utilises the visitor pattern to handle different types of nodes.
"""

from tokens import Token
from ast_nodes import NumberNode, BinaryOperationNode, UnaryOperationNode

class InterpreterError(Exception):
    """Custom exception for interpreter errors."""
    pass

class Interpreter:
    """
    Tree-walking interpreter that evaluates AST nodes.

    The interpreter employs the visitor pattern: for each type of AST node,
    there is a corresponding visit method that knows how to evaluate that node.
    """

    def visit_NumberNode(self, node):
        """
        Visit a number node and return its value.
        This is the base case for recursive evaluation.
        """
        return node.value

    def visit_BinaryOperationNode(self, node):
        """
        Visit a binary operation node and return the result of the operation.
        This method recursively evaluates the left and right operands first.
        """
        # Evaluate left and right operands
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)

        # Apply the appropriate operation
        if node.operator.type == Token.PLUS:
            return left_value + right_value
        elif node.operator.type == Token.MINUS:
            return left_value - right_value
        elif node.operator.type == Token.MULTIPLY:
            return left_value * right_value
        elif node.operator.type == Token.DIVIDE:
            if right_value == 0:
                raise InterpreterError("Division by zero")
            return left_value / right_value
        else:
            raise InterpreterError(f"Unknown binary operator: {node.operator.type}")

    def visit_UnaryOperationNode(self, node):
        """
        Visit a unary operation node and return the result.
        This handles cases such as -5 or +3.
        """
        # Evaluate the operand
        operand_value = self.visit(node.operand)

        # Apply the unary operation
        if node.operator.type == Token.PLUS:
            return +operand_value  # Essentially a no-op
        elif node.operator.type == Token.MINUS:
            return -operand_value
        else:
            raise InterpreterError(f"Unknown unary operator: {node.operator.type}")

    def visit(self, node):
        """
        Dispatch method that calls the appropriate visit method based on node type.
        This is the core of the visitor pattern.
        """
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, None)
        if visitor_method is None:
            raise InterpreterError(f"No visit method for {type(node).__name__}")
        return visitor_method(node)

    def interpret(self, tree):
        """
        Interpret an AST and return the computed result.
        This is the principal method to be called externally.
        """
        if tree is None:
            raise InterpreterError("Cannot interpret an empty tree")
        return self.visit(tree)
