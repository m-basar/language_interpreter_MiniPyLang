"""
interpreter.py - Enhanced interpreter with comprehensive string support

String support in the interpreter requires careful consideration of type
interactions and coercion rules. These decisions define much of your
language's personality and usability.
"""

from tokens import Token
from ast_nodes import NumberNode, BooleanNode, StringNode, BinaryOperationNode, UnaryOperationNode

class InterpreterError(Exception):
    """Enhanced interpreter error with context information"""
    def __init__(self, message, node=None):
        self.message = message
        self.node = node
        super().__init__(message)

class Interpreter:
    """
    Enhanced interpreter supporting arithmetic, Boolean, and string operations.
    
    The interpreter implements the semantic rules that define how different
    data types interact in MiniPyLang. These rules represent important
    language design decisions.
    """
    
    def visit_NumberNode(self, node):
        """Visit a number node - unchanged from previous stages"""
        return node.value
    
    def visit_BooleanNode(self, node):
        """Visit a Boolean node - unchanged from Stage 2"""
        return node.value
    
    def visit_StringNode(self, node):
        """
        Visit a string node - new for Stage 3
        
        String evaluation is straightforward since string nodes
        represent literal values, just like numbers and Booleans.
        """
        return node.value
    
    def visit_BinaryOperationNode(self, node):
        """
        Enhanced binary operation handling with string support.
        
        This method implements the semantic rules for how different
        data types interact in MiniPyLang. These rules represent
        fundamental language design decisions.
        """
        left_value = self.visit(node.left)
        right_value = self.visit(node.right)
        
        # Addition: Arithmetic for numbers, concatenation for strings
        if node.operator.type == Token.PLUS:
            return self._handle_addition(left_value, right_value, node)
        
        # Subtraction: Only valid for numbers
        elif node.operator.type == Token.MINUS:
            self._ensure_numbers(left_value, right_value, '-', node)
            return left_value - right_value
        
        # Multiplication: Only valid for numbers
        elif node.operator.type == Token.MULTIPLY:
            self._ensure_numbers(left_value, right_value, '*', node)
            return left_value * right_value
        
        # Division: Only valid for numbers
        elif node.operator.type == Token.DIVIDE:
            self._ensure_numbers(left_value, right_value, '/', node)
            if right_value == 0:
                raise InterpreterError("Division by zero", node)
            return left_value / right_value
        
        # Comparison operations: Valid for numbers, but not strings
        elif node.operator.type == Token.LESS_THAN:
            self._ensure_numbers(left_value, right_value, '<', node)
            return left_value < right_value
        
        elif node.operator.type == Token.GREATER_THAN:
            self._ensure_numbers(left_value, right_value, '>', node)
            return left_value > right_value
        
        elif node.operator.type == Token.LESS_EQUAL:
            self._ensure_numbers(left_value, right_value, '<=', node)
            return left_value <= right_value
        
        elif node.operator.type == Token.GREATER_EQUAL:
            self._ensure_numbers(left_value, right_value, '>=', node)
            return left_value >= right_value
        
        # Equality operations: Valid for any types
        elif node.operator.type == Token.EQUAL:
            return self._handle_equality(left_value, right_value)
        
        elif node.operator.type == Token.NOT_EQUAL:
            return not self._handle_equality(left_value, right_value)
        
        # Logical operations: Only valid for Booleans
        elif node.operator.type == Token.AND:
            self._ensure_booleans(left_value, right_value, 'and', node)
            return left_value and right_value
        
        elif node.operator.type == Token.OR:
            self._ensure_booleans(left_value, right_value, 'or', node)
            return left_value or right_value
        
        else:
            raise InterpreterError(f"Unknown binary operator: {node.operator.type}", node)
    
    def visit_UnaryOperationNode(self, node):
        """Enhanced unary operation handling - unchanged from Stage 2"""
        operand_value = self.visit(node.operand)
        
        if node.operator.type == Token.PLUS:
            self._ensure_number(operand_value, '+', node)
            return +operand_value
        
        elif node.operator.type == Token.MINUS:
            self._ensure_number(operand_value, '-', node)
            return -operand_value
        
        elif node.operator.type == Token.NOT:
            self._ensure_boolean(operand_value, '!', node)
            return not operand_value
        
        else:
            raise InterpreterError(f"Unknown unary operator: {node.operator.type}", node)
    
    def _handle_addition(self, left_value, right_value, node):
        """
        Handle addition operation with intelligent type handling.
        
        This method implements a key language design decision:
        - If both operands are numbers, perform arithmetic addition
        - If either operand is a string, convert both to strings and concatenate
        - This makes string operations intuitive while preserving numeric arithmetic
        """
        # If either operand is a string, treat this as string concatenation
        if isinstance(left_value, str) or isinstance(right_value, str):
            # Convert both operands to strings for concatenation
            left_str = self._convert_to_string(left_value)
            right_str = self._convert_to_string(right_value)
            return left_str + right_str
        
        # If both operands are numbers, perform arithmetic addition
        elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            return left_value + right_value
        
        else:
            # This shouldn't happen with current language features, but provides clarity
            raise InterpreterError(
                f"Cannot add {type(left_value).__name__} and {type(right_value).__name__}", 
                node
            )
    
    def _handle_equality(self, left_value, right_value):
        """
        Handle equality comparison with sensible type rules.
        
        This method implements another important design decision:
        - Values of the same type are compared directly
        - Values of different types are considered unequal
        - This prevents surprising behaviour while being predictable
        """
        # Values of different types are never equal
        if type(left_value) != type(right_value):
            return False
        
        # Values of the same type are compared directly
        return left_value == right_value
    
    def _convert_to_string(self, value):
        """
        Convert any value to its string representation.
        
        This method defines how different data types appear when
        converted to strings, which affects concatenation behaviour.
        """
        if isinstance(value, bool):
            # Convert Boolean values to lowercase strings for consistency
            return 'true' if value else 'false'
        elif isinstance(value, float):
            # Format numbers nicely, removing unnecessary decimal places
            if value.is_integer():
                return str(int(value))
            else:
                return str(value)
        else:
            # For strings and other types, use default string conversion
            return str(value)
    
    def _ensure_number(self, value, operator, node):
        """Ensure a value is numeric for arithmetic operations"""
        if not isinstance(value, (int, float)):
            raise InterpreterError(
                f"Operator '{operator}' requires a number, got {type(value).__name__}", 
                node
            )
    
    def _ensure_numbers(self, left, right, operator, node):
        """Ensure both values are numeric for arithmetic/comparison operations"""
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise InterpreterError(
                f"Operator '{operator}' requires numbers, got {type(left).__name__} and {type(right).__name__}", 
                node
            )
    
    def _ensure_boolean(self, value, operator, node):
        """Ensure a value is Boolean for logical operations"""
        if not isinstance(value, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires a Boolean, got {type(value).__name__}", 
                node
            )
    
    def _ensure_booleans(self, left, right, operator, node):
        """Ensure both values are Boolean for logical operations"""
        if not isinstance(left, bool) or not isinstance(right, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires Booleans, got {type(left).__name__} and {type(right).__name__}", 
                node
            )
    
    def visit(self, node):
        """Dispatch visitor method - unchanged from previous stages"""
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, None)
        
        if visitor_method is None:
            raise InterpreterError(f"No visit method for {type(node).__name__}")
        
        return visitor_method(node)
    
    def interpret(self, tree):
        """Main interpretation method - unchanged from previous stages"""
        if tree is None:
            raise InterpreterError("Cannot interpret empty tree")
        
        return self.visit(tree)
