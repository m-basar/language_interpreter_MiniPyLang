"""
interpreter.py - Addressing value storage and floating point

This enhanced version provides more sophisticated handling of value types
and addresses the floating point equality.
"""

import math
from tokens import Token
from ast_nodes import (
    NumberNode, BooleanNode, StringNode, VariableNode,
    BinaryOperationNode, UnaryOperationNode,
    AssignmentNode, PrintNode, ProgramNode
)
from environment import Environment


class InterpreterError(Exception):
    """Enhanced interpreter error with detailed context information"""
    def __init__(self, message, node=None):
        self.message = message
        self.node = node
        super().__init__(message)


class MiniPyValue:
    """
    Enhanced value representation addressing Stage 2 in-memory storage.
    
    This class provides explicit type handling and helps manage the interaction
    between different data types in a more systematic way. It also provides
    a foundation for adding None/nil values.
    """
    
    # Value type constants
    NUMBER = 'NUMBER'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    NONE = 'NONE'  # Adding None/nil support
    
    def __init__(self, value, value_type=None):
        """
        Create a MiniPy value with explicit type tracking.
        
        This addresses the in-memory representation
        by providing clear type information alongside the actual value.
        """
        self.value = value
        
        # Infer type if not explicitly provided
        if value_type is None:
            if isinstance(value, bool):
                # Check bool first since bool is a subclass of int in Python
                self.type = self.BOOLEAN
            elif isinstance(value, (int, float)):
                self.type = self.NUMBER
            elif isinstance(value, str):
                self.type = self.STRING
            elif value is None:
                self.type = self.NONE
            else:
                raise InterpreterError(f"Unknown value type: {type(value)}")
        else:
            self.type = value_type
    
    def is_number(self):
        """Check if this value represents a number"""
        return self.type == self.NUMBER
    
    def is_boolean(self):
        """Check if this value represents a boolean"""
        return self.type == self.BOOLEAN
    
    def is_string(self):
        """Check if this value represents a string"""
        return self.type == self.STRING
    
    def is_none(self):
        """Check if this value represents None/nil"""
        return self.type == self.NONE
    
    def to_python_value(self):
        """Extract the underlying Python value"""
        return self.value
    
    def __str__(self):
        """String representation for debugging and display"""
        if self.is_none():
            return "none"
        elif self.is_boolean():
            return "true" if self.value else "false"
        elif self.is_number() and isinstance(self.value, float):
            # Handle floating point display nicely
            if self.value.is_integer():
                return str(int(self.value))
            else:
                return str(self.value)
        else:
            return str(self.value)


class Interpreter:
    """
    Enhanced interpreter for MiniPy language.
    
    This version provides more sophisticated value handling, floating point
    equality management, and support for None/nil values.
    """
    
    # Floating point comparison tolerance
    EPSILON = 1e-10
    
    def __init__(self):
        """Initialise interpreter with enhanced environment support"""
        self.global_env = Environment()
    
    def visit_ProgramNode(self, node):
        """Execute program with enhanced value handling"""
        last_result = None
        
        for statement in node.statements:
            try:
                result = self.visit(statement)
                
                # Keep track of the last expression result
                if not isinstance(statement, (AssignmentNode, PrintNode)):
                    last_result = result
                    
            except InterpreterError as e:
                raise e
            except Exception as e:
                raise InterpreterError(f"Runtime error: {str(e)}", statement)
        
        return last_result
    
    def visit_AssignmentNode(self, node):
        """
        Enhanced assignment handling with explicit value type management.
        
        This addresses data persistence by providing
        more sophisticated variable lifecycle management.
        """
        try:
            # Evaluate the expression and wrap in MiniPyValue
            raw_value = self.visit(node.expression)
            
            # Handle special case for None/nil assignment
            if isinstance(raw_value, str) and raw_value.lower() == 'none':
                # Following Lua's approach: assigning 'none' deletes the variable
                if self.global_env.is_defined(node.variable_name):
                    self.global_env.delete(node.variable_name)
                return None
            
            # Wrap in MiniPyValue for better type management
            value = self._ensure_minipy_value(raw_value)
            
            # Store in environment
            self.global_env.define(node.variable_name, value)
            
            return None
            
        except Exception as e:
            raise InterpreterError(
                f"Error in assignment to '{node.variable_name}': {str(e)}", 
                node
            )
    
    def visit_PrintNode(self, node):
        """Enhanced print with better formatting for all value types"""
        try:
            value = self.visit(node.expression)
            minipy_value = self._ensure_minipy_value(value)
            
            # Format output appropriately for each type
            if minipy_value.is_none():
                print("none")
            elif minipy_value.is_string():
                print(minipy_value.value)  # Strings display without quotes
            else:
                print(str(minipy_value))
            
            return None
            
        except Exception as e:
            raise InterpreterError(f"Error in print statement: {str(e)}", node)
    
    def visit_VariableNode(self, node):
        """Enhanced variable lookup with proper value type handling"""
        try:
            minipy_value = self.global_env.get(node.name)
            return minipy_value.to_python_value()
            
        except Exception as e:
            raise InterpreterError(
                f"Error accessing variable '{node.name}': {str(e)}", 
                node
            )
    
    def visit_NumberNode(self, node):
        """Return raw number value for internal processing"""
        return node.value
    
    def visit_BooleanNode(self, node):
        """Return raw boolean value for internal processing"""
        return node.value
    
    def visit_StringNode(self, node):
        """Return raw string value for internal processing"""
        return node.value
    
    def visit_BinaryOperationNode(self, node):
        """
        Enhanced binary operations.
        
        This implementation provides epsilon-based floating point equality
        and more robust type checking across all operations.
        """
        try:
            left_value = self.visit(node.left)
            right_value = self.visit(node.right)
            
            # Handle arithmetic operations
            if node.operator.type == Token.PLUS:
                return self._handle_addition(left_value, right_value, node)
            
            elif node.operator.type == Token.MINUS:
                self._ensure_numbers(left_value, right_value, '-', node)
                return left_value - right_value
            
            elif node.operator.type == Token.MULTIPLY:
                self._ensure_numbers(left_value, right_value, '*', node)
                return left_value * right_value
            
            elif node.operator.type == Token.DIVIDE:
                self._ensure_numbers(left_value, right_value, '/', node)
                if abs(right_value) < self.EPSILON:  # Better zero checking
                    raise InterpreterError("Division by zero", node)
                return left_value / right_value
            
            # Enhanced comparison operations with floating point awareness
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
            
            # Enhanced equality operations addressing floating point concerns
            elif node.operator.type == Token.EQUAL:
                return self._handle_equality(left_value, right_value)
            
            elif node.operator.type == Token.NOT_EQUAL:
                return not self._handle_equality(left_value, right_value)
            
            # Logical operations
            elif node.operator.type == Token.AND:
                self._ensure_booleans(left_value, right_value, 'and', node)
                return left_value and right_value
            
            elif node.operator.type == Token.OR:
                self._ensure_booleans(left_value, right_value, 'or', node)
                return left_value or right_value
            
            else:
                raise InterpreterError(f"Unknown binary operator: {node.operator.type}", node)
                
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error in binary operation: {str(e)}", node)
    
    def visit_UnaryOperationNode(self, node):
        """Enhanced unary operations with better error handling"""
        try:
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
                
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error in unary operation: {str(e)}", node)
    
    def _handle_addition(self, left_value, right_value, node):
        """Enhanced addition with comprehensive type handling"""
        # String concatenation with automatic conversion
        if isinstance(left_value, str) or isinstance(right_value, str):
            left_str = self._convert_to_string(left_value)
            right_str = self._convert_to_string(right_value)
            return left_str + right_str
        elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            return left_value + right_value
        else:
            raise InterpreterError(
                f"Cannot add {type(left_value).__name__} and {type(right_value).__name__}", 
                node
            )
    
    def _handle_equality(self, left_value, right_value):
        """
        Enhanced equality handling.
        
        This implementation uses epsilon-based comparison for floating point
        numbers to avoid the common pitfalls of floating point equality.
        """
        # Different types are never equal
        if type(left_value) != type(right_value):
            return False
        
        # Special handling for floating point numbers
        if isinstance(left_value, float) and isinstance(right_value, float):
            return abs(left_value - right_value) < self.EPSILON
        
        # Handle mixed int/float comparisons
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            return abs(float(left_value) - float(right_value)) < self.EPSILON
        
        # Standard equality for other types
        return left_value == right_value
    
    def _ensure_minipy_value(self, value):
        """Convert raw Python values to MiniPyValue instances"""
        if isinstance(value, MiniPyValue):
            return value
        else:
            return MiniPyValue(value)
    
    def _convert_to_string(self, value):
        """Enhanced string conversion handling all value types"""
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            else:
                return str(value)
        elif value is None:
            return 'none'
        else:
            return str(value)
    
    def _ensure_number(self, value, operator, node):
        """Enhanced number type checking"""
        if not isinstance(value, (int, float)):
            raise InterpreterError(
                f"Operator '{operator}' requires a number, got {type(value).__name__}", 
                node
            )
    
    def _ensure_numbers(self, left, right, operator, node):
        """Enhanced number type checking for binary operations"""
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise InterpreterError(
                f"Operator '{operator}' requires numbers, got {type(left).__name__} and {type(right).__name__}", 
                node
            )
    
    def _ensure_boolean(self, value, operator, node):
        """Enhanced boolean type checking"""
        if not isinstance(value, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires a boolean, got {type(value).__name__}", 
                node
            )
    
    def _ensure_booleans(self, left, right, operator, node):
        """Enhanced boolean type checking for binary operations"""
        if not isinstance(left, bool) or not isinstance(right, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires booleans, got {type(left).__name__} and {type(right).__name__}", 
                node
            )
    
    def visit(self, node):
        """Enhanced visitor dispatch with comprehensive error handling"""
        if node is None:
            return None
        
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, None)
        
        if visitor_method is None:
            raise InterpreterError(f"No visit method for {type(node).__name__}")
        
        return visitor_method(node)
    
    def interpret(self, tree):
        """Main interpretation method with enhanced error handling"""
        if tree is None:
            raise InterpreterError("Cannot interpret empty program")
        
        try:
            return self.visit(tree)
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Unexpected runtime error: {str(e)}")
    
    def get_environment_state(self):
        """Return current variable state for debugging"""
        return self.global_env.get_all_variables()
    
    def reset_environment(self):
        """Clear all variables for testing"""
        self.global_env.clear()