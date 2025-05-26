"""
interpreter.py - Stage 5 interpreter with control flow

Executes programs with support for control flow constructs:
- All existing Stage 4 features
- if/else conditional statements
- while loops with proper termination
- Code blocks and nested control structures
- input() function for user interaction
"""

import math
from tokens import Token
from ast_nodes import (
    NumberNode, BooleanNode, StringNode, VariableNode,
    BinaryOperationNode, UnaryOperationNode,
    AssignmentNode, PrintNode, ProgramNode, DeleteNode, NoneNode,
    ConversionNode,
    # NEW: Control flow nodes
    IfNode, WhileNode, BlockNode, InputNode
)
from environment import Environment


class InterpreterError(Exception):
    """Interpreter error with context information"""
    def __init__(self, message, node=None):
        self.message = message
        self.node = node
        super().__init__(message)


class ControlFlowException(Exception):
    """Base class for control flow exceptions"""
    pass


class BreakException(ControlFlowException):
    """Exception for breaking out of loops (future extension)"""
    pass


class ContinueException(ControlFlowException):
    """Exception for continuing loops (future extension)"""
    pass


class MiniPyValue:
    """
    Enhanced value wrapper for type tracking and operations.
    
    Provides explicit type information and operations for all
    MiniPyLang values including type conversion support.
    """
    
    # Value type constants
    NUMBER = 'NUMBER'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    NONE = 'NONE'
    
    def __init__(self, value, value_type=None):
        """Create typed value"""
        self.value = value
        
        # Infer type if not provided
        if value_type is None:
            if isinstance(value, bool):
                # Check bool first since bool is subclass of int in Python
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
        return self.type == self.NUMBER
    
    def is_boolean(self):
        return self.type == self.BOOLEAN
    
    def is_string(self):
        return self.type == self.STRING
    
    def is_none(self):
        return self.type == self.NONE
    
    def to_python_value(self):
        """Extract underlying Python value"""
        return self.value
    
    def is_truthy(self):
        """Determine truthiness for conditionals"""
        if self.is_boolean():
            return self.value
        elif self.is_number():
            return self.value != 0
        elif self.is_string():
            return len(self.value) > 0
        elif self.is_none():
            return False
        else:
            return True
    
    def __str__(self):
        """String representation for display"""
        if self.is_none():
            return "none"
        elif self.is_boolean():
            return "true" if self.value else "false"
        elif self.is_number():
            if isinstance(self.value, int):
                return str(self.value)
            elif isinstance(self.value, float):
                # Show decimal point for floats
                if self.value.is_integer():
                    return f"{self.value:.1f}"
                else:
                    return str(self.value)
        else:
            return str(self.value)


class Interpreter:
    """
    Enhanced Stage 5 interpreter with control flow for MiniPyLang.
    
    Executes programs with proper variable management, type checking,
    error handling, type conversion, and control flow constructs.
    """
    
    # Floating point comparison tolerance
    EPSILON = 1e-10
    
    # Loop safety limit to prevent infinite loops
    MAX_LOOP_ITERATIONS = 10000
    
    def __init__(self):
        """Initialize interpreter with empty environment"""
        self.global_env = Environment()
        
        # Track loop nesting for safety
        self.loop_iteration_count = 0
        self.in_loop = False
    
    def visit_ProgramNode(self, node):
        """Execute program as sequence of statements"""
        return self._execute_statement_list(node.statements)
    
    def _execute_statement_list(self, statements):
        """Execute list of statements"""
        last_result = None
        
        for statement in statements:
            try:
                result = self.visit(statement)
                
                # Track last expression result for interactive mode
                if not isinstance(statement, (AssignmentNode, PrintNode, DeleteNode, 
                                            IfNode, WhileNode)):
                    last_result = result
                    
            except (BreakException, ContinueException):
                # Control flow exceptions should bubble up to loop handlers
                raise
            except InterpreterError as e:
                raise e
            except Exception as e:
                raise InterpreterError(f"Runtime error: {str(e)}", statement)
        
        return last_result
    
    # NEW: Control flow visitor methods
    def visit_IfNode(self, node):
        """
        Execute conditional statement with proper boolean evaluation.
        
        Evaluates condition and executes appropriate branch.
        """
        try:
            # Evaluate condition
            condition_value = self.visit(node.condition)
            condition_minipy = self._ensure_minipy_value(condition_value)
            
            # Determine truthiness
            is_true = condition_minipy.is_truthy()
            
            if is_true and node.then_block:
                # Execute then branch
                return self.visit(node.then_block)
            elif not is_true and node.else_block:
                # Execute else branch
                return self.visit(node.else_block)
            
            return None
            
        except (BreakException, ContinueException):
            raise  # Pass through control flow exceptions
        except Exception as e:
            raise InterpreterError(f"Error in if statement: {str(e)}", node)
    
    def visit_WhileNode(self, node):
        """
        Execute while loop with safety limits and proper termination.
        
        Repeatedly evaluates condition and executes body until condition is false.
        """
        try:
            # Safety: Track that we're in a loop
            was_in_loop = self.in_loop
            self.in_loop = True
            iteration_count = 0
            
            while True:
                # Safety check for infinite loops
                iteration_count += 1
                if iteration_count > self.MAX_LOOP_ITERATIONS:
                    raise InterpreterError(
                        f"Loop exceeded maximum iterations ({self.MAX_LOOP_ITERATIONS}). "
                        "Possible infinite loop detected.", 
                        node
                    )
                
                # Evaluate condition
                condition_value = self.visit(node.condition)
                condition_minipy = self._ensure_minipy_value(condition_value)
                
                # Check if loop should continue
                if not condition_minipy.is_truthy():
                    break
                
                # Execute loop body
                try:
                    self.visit(node.body)
                except BreakException:
                    # Break out of loop (future extension)
                    break
                except ContinueException:
                    # Continue to next iteration (future extension)
                    continue
            
            # Restore loop state
            self.in_loop = was_in_loop
            return None
            
        except (BreakException, ContinueException):
            # Restore loop state before re-raising
            self.in_loop = was_in_loop
            raise
        except Exception as e:
            # Restore loop state before raising error
            self.in_loop = was_in_loop
            raise InterpreterError(f"Error in while loop: {str(e)}", node)
    
    def visit_BlockNode(self, node):
        """Execute block of statements"""
        try:
            return self._execute_statement_list(node.statements)
        except Exception as e:
            raise InterpreterError(f"Error in code block: {str(e)}", node)
    
    def visit_InputNode(self, node):
        """
        Handle input function calls with optional prompts.
        
        Supports input() and input("prompt") forms.
        """
        try:
            # Handle optional prompt
            if node.prompt_expression:
                prompt_value = self.visit(node.prompt_expression)
                prompt_minipy = self._ensure_minipy_value(prompt_value)
                
                # Convert prompt to string
                if prompt_minipy.is_string():
                    prompt_text = prompt_minipy.value
                else:
                    prompt_text = str(prompt_minipy)
            else:
                prompt_text = ""
            
            # Get user input
            try:
                user_input = input(prompt_text)
                return user_input  # Return as string
            except EOFError:
                # Handle end-of-file (Ctrl+D/Ctrl+Z)
                return ""
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                raise InterpreterError("Input interrupted by user", node)
                
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error in input() function: {str(e)}", node)
    
    # Enhanced type conversion with better error handling
    def visit_ConversionNode(self, node):
        """
        Handle type conversion function calls with comprehensive error handling.
        """
        try:
            # Evaluate the expression to convert
            value = self.visit(node.expression)
            conversion_type = node.conversion_type
            
            if conversion_type == 'str':
                # Convert any value to string representation
                if isinstance(value, bool):
                    return 'true' if value else 'false'
                elif value is None:
                    return 'none'
                elif isinstance(value, (int, float)):
                    if isinstance(value, float) and value.is_integer():
                        return f"{value:.1f}"  # Show 5.0 not 5
                    else:
                        return str(value)
                elif isinstance(value, str):
                    return value  # Already a string
                else:
                    return str(value)
            
            elif conversion_type == 'int':
                # Convert to integer with validation
                if isinstance(value, int):
                    return value  # Already an integer
                elif isinstance(value, float):
                    return int(value)  # Truncate decimal part: 3.7 -> 3
                elif isinstance(value, bool):
                    return 1 if value else 0
                elif isinstance(value, str):
                    # Try to parse string as integer
                    try:
                        stripped = value.strip()
                        if stripped == '':
                            return 0  # Empty string -> 0
                        elif stripped.lower() == 'true':
                            return 1
                        elif stripped.lower() == 'false':
                            return 0
                        elif stripped.lower() == 'none':
                            return 0
                        else:
                            # Handle both "42" and "42.0" -> 42
                            return int(float(stripped))
                    except ValueError:
                        raise InterpreterError(f"Cannot convert string '{value}' to integer", node)
                elif value is None:
                    return 0
                else:
                    raise InterpreterError(f"Cannot convert {type(value).__name__} to integer", node)
            
            elif conversion_type == 'float':
                # Convert to floating point number
                if isinstance(value, (int, float)):
                    return float(value)
                elif isinstance(value, bool):
                    return 1.0 if value else 0.0
                elif isinstance(value, str):
                    try:
                        stripped = value.strip()
                        if stripped == '':
                            return 0.0
                        elif stripped.lower() == 'true':
                            return 1.0
                        elif stripped.lower() == 'false':
                            return 0.0
                        elif stripped.lower() == 'none':
                            return 0.0
                        else:
                            return float(stripped)
                    except ValueError:
                        raise InterpreterError(f"Cannot convert string '{value}' to float", node)
                elif value is None:
                    return 0.0
                else:
                    raise InterpreterError(f"Cannot convert {type(value).__name__} to float", node)
            
            elif conversion_type == 'bool':
                # Convert to boolean using truthiness rules
                if isinstance(value, bool):
                    return value
                elif isinstance(value, (int, float)):
                    return value != 0  # 0 is false, everything else is true
                elif isinstance(value, str):
                    # String truthiness: empty string is false, non-empty is true
                    return len(value) > 0
                elif value is None:
                    return False
                else:
                    return True  # Most objects are truthy
            
            else:
                raise InterpreterError(f"Unknown conversion type: {conversion_type}", node)
                
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error in {node.conversion_type}() conversion: {str(e)}", node)
    
    # Existing Stage 4 visitor methods (unchanged)
    def visit_AssignmentNode(self, node):
        """Execute variable assignment: var = expr"""
        try:
            # Evaluate expression
            raw_value = self.visit(node.expression)
            
            # Wrap in MiniPyValue for type tracking
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
        """Execute print statement: print expr"""
        try:
            value = self.visit(node.expression)
            minipy_value = self._ensure_minipy_value(value)
            
            # Format output appropriately
            if minipy_value.is_none():
                print("none")
            elif minipy_value.is_string():
                print(minipy_value.value)  # Strings without quotes
            else:
                print(str(minipy_value))
            
            return None
            
        except Exception as e:
            raise InterpreterError(f"Error in print statement: {str(e)}", node)
    
    def visit_VariableNode(self, node):
        """Look up variable value"""
        try:
            minipy_value = self.global_env.get(node.name)
            return minipy_value.to_python_value()
            
        except Exception as e:
            raise InterpreterError(
                f"Error accessing variable '{node.name}': {str(e)}", 
                node
            )
    
    def visit_DeleteNode(self, node):
        """Delete variable: del var"""
        try:
            if not self.global_env.is_defined(node.variable_name):
                raise InterpreterError(
                    f"Cannot delete undefined variable '{node.variable_name}'", 
                    node
                )
            
            self.global_env.delete(node.variable_name)
            return None
            
        except Exception as e:
            raise InterpreterError(
                f"Error deleting variable '{node.variable_name}': {str(e)}", 
                node
            )
    
    # Literal value visitors
    def visit_NumberNode(self, node):
        return node.value
    
    def visit_BooleanNode(self, node):
        return node.value
    
    def visit_StringNode(self, node):
        return node.value
    
    def visit_NoneNode(self, node):
        return None
    
    def visit_BinaryOperationNode(self, node):
        """Execute binary operations with strict type checking"""
        try:
            left_value = self.visit(node.left)
            right_value = self.visit(node.right)
            
            # Arithmetic operations
            if node.operator.type == Token.PLUS:
                return self._handle_addition(left_value, right_value, node)
            
            elif node.operator.type == Token.MINUS:
                self._ensure_numbers(left_value, right_value, '-', node)
                return self._perform_arithmetic(left_value, right_value, lambda a, b: a - b)
            
            elif node.operator.type == Token.MULTIPLY:
                self._ensure_numbers(left_value, right_value, '*', node)
                return self._perform_arithmetic(left_value, right_value, lambda a, b: a * b)
            
            elif node.operator.type == Token.DIVIDE:
                self._ensure_numbers(left_value, right_value, '/', node)
                if abs(right_value) < self.EPSILON:
                    raise InterpreterError("Division by zero", node)
                return float(left_value) / float(right_value)
            
            # Comparison operations
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
            
            # Equality operations
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
        """Execute unary operations"""
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
    
    # Helper methods (unchanged from Stage 4)
    def _perform_arithmetic(self, left, right, operation):
        """Perform arithmetic while preserving types"""
        if isinstance(left, int) and isinstance(right, int):
            return operation(left, right)
        else:
            return operation(float(left), float(right))
    
    def _handle_addition(self, left_value, right_value, node):
        """Handle addition with strict type checking"""
        # String concatenation
        if isinstance(left_value, str) and isinstance(right_value, str):
            return left_value + right_value
        
        # Numeric addition
        elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            return self._perform_arithmetic(left_value, right_value, lambda a, b: a + b)
        
        # Type mismatch error
        else:
            left_type = type(left_value).__name__
            right_type = type(right_value).__name__
            raise InterpreterError(
                f"Cannot add {left_type} and {right_type}. "
                f"Numbers and strings cannot be mixed in addition operations. "
                f"Use explicit string conversion if concatenation is intended.",
                node
            )
    
    def _handle_equality(self, left_value, right_value):
        """Handle equality with floating point awareness"""
        # Different types are never equal
        if type(left_value) != type(right_value):
            return False
        
        # Floating point comparison with epsilon
        if isinstance(left_value, float) and isinstance(right_value, float):
            return abs(left_value - right_value) < self.EPSILON
        
        # Mixed int/float comparison
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            return abs(float(left_value) - float(right_value)) < self.EPSILON
        
        # Standard equality for other types
        return left_value == right_value
    
    def _ensure_minipy_value(self, value):
        """Convert raw values to MiniPyValue instances"""
        if isinstance(value, MiniPyValue):
            return value
        else:
            return MiniPyValue(value)
    
    def _ensure_number(self, value, operator, node):
        """Ensure value is a number"""
        if not isinstance(value, (int, float)):
            raise InterpreterError(
                f"Operator '{operator}' requires a number, got {type(value).__name__}", 
                node
            )
    
    def _ensure_numbers(self, left, right, operator, node):
        """Ensure both values are numbers"""
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise InterpreterError(
                f"Operator '{operator}' requires numbers, got {type(left).__name__} and {type(right).__name__}", 
                node
            )
    
    def _ensure_boolean(self, value, operator, node):
        """Ensure value is a boolean"""
        if not isinstance(value, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires a boolean, got {type(value).__name__}", 
                node
            )
    
    def _ensure_booleans(self, left, right, operator, node):
        """Ensure both values are booleans"""
        if not isinstance(left, bool) or not isinstance(right, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires booleans, got {type(left).__name__} and {type(right).__name__}", 
                node
            )
    
    def visit(self, node):
        """Visitor dispatch method"""
        if node is None:
            return None
        
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, None)
        
        if visitor_method is None:
            raise InterpreterError(f"No visit method for {type(node).__name__}")
        
        return visitor_method(node)
    
    def interpret(self, tree):
        """Main interpretation entry point"""
        if tree is None:
            raise InterpreterError("Cannot interpret empty program")
        
        try:
            return self.visit(tree)
        except (BreakException, ContinueException) as e:
            raise InterpreterError(f"Control flow statement outside loop context")
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Unexpected runtime error: {str(e)}")
    
    def get_environment_state(self):
        """Get current variables for debugging"""
        return self.global_env.get_all_variables()
    
    def reset_environment(self):
        """Clear all variables"""
        self.global_env.clear()
        self.loop_iteration_count = 0
        self.in_loop = False