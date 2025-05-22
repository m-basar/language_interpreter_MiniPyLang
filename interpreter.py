"""
interpreter.py - Enhanced interpreter with Boolean support

The interpreter now handles Boolean values and logical operations.
We need to make decisions about type interactions and conversions.
"""

from tokens import Token
from ast_nodes import NumberNode, BooleanNode, BinaryOperationNode, UnaryOperationNode

class InterpreterError(Exception):
    """Custom exception for interpreter errors"""
    pass

class Interpreter:
    """
    Enhanced interpreter that evaluates both arithmetic and Boolean expressions.
    
    We need to handle type checking and decide how different types interact.
    """
    
    def visit_NumberNode(self, node):
        """Visit a number node and return its value"""
        return node.value
    
    def visit_BooleanNode(self, node):
        """Visit a Boolean node and return its value"""
        return node.value
    
    def visit_BinaryOperationNode(self, node):
        """
        Visit a binary operation node and return the result.
        
        This is where we handle the semantics of different operator types.
        """
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        
        # Arithmetic operations (work only with numbers)
        if node.operator.type == Token.PLUS:
            self._ensure_numbers(left_value, right_value, '+')
            return left_value + right_value
        
        elif node.operator.type == Token.MINUS:
            self._ensure_numbers(left_value, right_value, '-')
            return left_value - right_value
        
        elif node.operator.type == Token.MULTIPLY:
            self._ensure_numbers(left_value, right_value, '*')
            return left_value * right_value
        
        elif node.operator.type == Token.DIVIDE:
            self._ensure_numbers(left_value, right_value, '/')
            if right_value == 0:
                raise InterpreterError("Division by zero")
            return left_value / right_value
        
        # Comparison operations (work with numbers, produce Booleans)
        elif node.operator.type == Token.LESS_THAN:
            self._ensure_numbers(left_value, right_value, '<')
            return left_value < right_value
        
        elif node.operator.type == Token.GREATER_THAN:
            self._ensure_numbers(left_value, right_value, '>')
            return left_value > right_value
        
        elif node.operator.type == Token.LESS_EQUAL:
            self._ensure_numbers(left_value, right_value, '<=')
            return left_value <= right_value
        
        elif node.operator.type == Token.GREATER_EQUAL:
            self._ensure_numbers(left_value, right_value, '>=')
            return left_value >= right_value
        
        # Equality operations (work with any matching types)
        elif node.operator.type == Token.EQUAL:
            # We allow equality comparison between same types
            if type(left_value) != type(right_value):
                return False  # Different types are never equal
            return left_value == right_value
        
        elif node.operator.type == Token.NOT_EQUAL:
            if type(left_value) != type(right_value):
                return True  # Different types are always not equal
            return left_value != right_value
        
        # Logical operations (work only with Booleans)
        elif node.operator.type == Token.AND:
            self._ensure_booleans(left_value, right_value, 'and')
            return left_value and right_value
        
        elif node.operator.type == Token.OR:
            self._ensure_booleans(left_value, right_value, 'or')
            return left_value or right_value
        
        else:
            raise InterpreterError(f"Unknown binary operator: {node.operator.type}")
    
    def visit_UnaryOperationNode(self, node):
        """
        Visit a unary operation node and return the result.
        """
        operand_value = self.visit(node.operand)
        
        if node.operator.type == Token.PLUS:
            self._ensure_number(operand_value, '+')
            return +operand_value
        
        elif node.operator.type == Token.MINUS:
            self._ensure_number(operand_value, '-')
            return -operand_value
        
        elif node.operator.type == Token.NOT:
            self._ensure_boolean(operand_value, '!')
            return not operand_value
        
        else:
            raise InterpreterError(f"Unknown unary operator: {node.operator.type}")
    
    def _ensure_number(self, value, operator):
        """Ensure a value is a number for arithmetic operations"""
        if not isinstance(value, (int, float)):
            raise InterpreterError(f"Operator '{operator}' requires a number, got {type(value).__name__}")
    
    def _ensure_numbers(self, left, right, operator):
        """Ensure both values are numbers for arithmetic/comparison operations"""
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise InterpreterError(f"Operator '{operator}' requires numbers, got {type(left).__name__} and {type(right).__name__}")
    
    def _ensure_boolean(self, value, operator):
        """Ensure a value is a Boolean for logical operations"""
        if not isinstance(value, bool):
            raise InterpreterError(f"Operator '{operator}' requires a Boolean, got {type(value).__name__}")
    
    def _ensure_booleans(self, left, right, operator):
        """Ensure both values are Booleans for logical operations"""
        if not isinstance(left, bool) or not isinstance(right, bool):
            raise InterpreterError(f"Operator '{operator}' requires Booleans, got {type(left).__name__} and {type(right).__name__}")
    
    def visit(self, node):
        """Dispatch method that calls the appropriate visit method"""
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, None)
        
        if visitor_method is None:
            raise InterpreterError(f"No visit method for {type(node).__name__}")
        
        return visitor_method(node)
    
    def interpret(self, tree):
        """Interpret an AST and return the computed result"""
        if tree is None:
            raise InterpreterError("Cannot interpret an empty tree")
        
        return self.visit(tree)
