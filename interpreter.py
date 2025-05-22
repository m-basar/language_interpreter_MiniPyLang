"""
interpreter.py - Complete Stage 4 interpreter with variable support

This enhanced interpreter transforms MiniPyLang from an expression evaluator
into a stateful programming environment. The key addition is the integration
of an environment for variable storage and the ability to execute sequences
of statements that modify program state over time.
"""

from tokens import Token
from ast_nodes import (
    NumberNode, BooleanNode, StringNode, VariableNode,
    BinaryOperationNode, UnaryOperationNode,
    AssignmentNode, PrintNode, ProgramNode
)
from environment import Environment


class InterpreterError(Exception):
    """Enhanced interpreter error with context information for debugging"""
    def __init__(self, message, node=None):
        self.message = message
        self.node = node
        super().__init__(message)


class Interpreter:
    """
    Complete Stage 4 interpreter supporting programs, variables, and statements.
    
    The interpreter now maintains program state through an environment and
    can execute sequences of statements that build up complex computations
    over time. This represents the fundamental shift from calculation to
    programming.
    """
    
    def __init__(self):
        """
        Initialise the interpreter with a global environment.
        
        The environment represents the program's memory, storing variable
        values that persist across statement executions. This is what
        gives our language the ability to remember information.
        """
        self.global_env = Environment()
    
    def visit_ProgramNode(self, node):
        """
        Execute a complete program consisting of multiple statements.
        
        This method represents the heart of program execution. It processes
        each statement in sequence, allowing the program state to evolve
        over time. Unlike expression evaluation, program execution is about
        the side effects (variable assignments, print output) rather than
        just producing a final value.
        """
        last_result = None
        
        for statement in node.statements:
            try:
                # Execute each statement and capture its result
                result = self.visit(statement)
                
                # Keep track of the last expression result for interactive mode
                if not isinstance(statement, (AssignmentNode, PrintNode)):
                    last_result = result
                    
            except InterpreterError as e:
                # Re-raise interpreter errors with additional context
                raise e
            except Exception as e:
                # Wrap unexpected errors with context information
                raise InterpreterError(f"Runtime error: {str(e)}", statement)
        
        # Return the last expression result for interactive mode
        return last_result
    
    def visit_AssignmentNode(self, node):
        """
        Execute variable assignment: variable = expression
        
        Assignment is fundamental to stateful programming. It evaluates
        an expression and stores the result in the program's memory,
        creating a persistent association between a name and a value.
        """
        try:
            # Evaluate the expression on the right side of the assignment
            value = self.visit(node.expression)
            
            # Store the value in the environment using the variable name
            self.global_env.define(node.variable_name, value)
            
            # Assignment statements don't return values (they perform actions)
            return None
            
        except Exception as e:
            raise InterpreterError(
                f"Error in assignment to '{node.variable_name}': {str(e)}", 
                node
            )
    
    def visit_PrintNode(self, node):
        """
        Execute print statement: print expression
        
        Print statements provide program output, enabling communication
        between the program and its users. They evaluate an expression
        and display the result in a user-friendly format.
        """
        try:
            # Evaluate the expression to print
            value = self.visit(node.expression)
            
            # Format the value for display
            formatted_value = self._format_for_output(value)
            
            # Output the result
            print(formatted_value)
            
            # Print statements don't return values (they perform actions)
            return None
            
        except Exception as e:
            raise InterpreterError(f"Error in print statement: {str(e)}", node)
    
    def visit_VariableNode(self, node):
        """
        Look up a variable's value from the environment.
        
        Variable lookup is the complement to assignment. While assignment
        stores values in memory, variable lookup retrieves them for use
        in expressions. This creates the connection between program memory
        and computation.
        """
        try:
            # Retrieve the variable's current value from the environment
            return self.global_env.get(node.name)
            
        except Exception as e:
            raise InterpreterError(
                f"Error accessing variable '{node.name}': {str(e)}", 
                node
            )
    
    # Expression evaluation methods (enhanced from previous stages)
    
    def visit_NumberNode(self, node):
        """Evaluate number literals - unchanged from previous stages"""
        return node.value
    
    def visit_BooleanNode(self, node):
        """Evaluate boolean literals - unchanged from previous stages"""
        return node.value
    
    def visit_StringNode(self, node):
        """Evaluate string literals - unchanged from Stage 3"""
        return node.value
    
    def visit_BinaryOperationNode(self, node):
        """
        Evaluate binary operations with comprehensive type handling.
        
        Binary operations now work with values that might come from variables,
        requiring robust type checking and error handling. The operations
        themselves are unchanged, but the values they work with are now
        more dynamic.
        """
        try:
            # Evaluate both operands (these might involve variable lookups)
            left_value = self.visit(node.left)
            right_value = self.visit(node.right)
            
            # Handle each operation type with appropriate type checking
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
                if right_value == 0:
                    raise InterpreterError("Division by zero", node)
                return left_value / right_value
            
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
            # Re-raise interpreter errors without modification
            raise
        except Exception as e:
            # Wrap other errors with context
            raise InterpreterError(f"Error in binary operation: {str(e)}", node)
    
    def visit_UnaryOperationNode(self, node):
        """Evaluate unary operations - enhanced with better error handling"""
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
    
    # Helper methods for type handling and formatting
    
    def _handle_addition(self, left_value, right_value, node):
        """
        Handle addition with intelligent type coercion for string concatenation.
        
        This method implements a key design decision: when either operand is
        a string, perform concatenation; otherwise, perform arithmetic addition.
        This makes string operations intuitive while preserving numeric arithmetic.
        """
        if isinstance(left_value, str) or isinstance(right_value, str):
            # String concatenation with automatic type conversion
            left_str = self._convert_to_string(left_value)
            right_str = self._convert_to_string(right_value)
            return left_str + right_str
        elif isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            # Numeric addition
            return left_value + right_value
        else:
            raise InterpreterError(
                f"Cannot add {type(left_value).__name__} and {type(right_value).__name__}", 
                node
            )
    
    def _handle_equality(self, left_value, right_value):
        """
        Handle equality comparison with sensible type rules.
        
        Values of different types are considered unequal, which prevents
        surprising behavior while maintaining predictable semantics.
        """
        if type(left_value) != type(right_value):
            return False
        return left_value == right_value
    
    def _convert_to_string(self, value):
        """
        Convert any value to its string representation for concatenation.
        
        This method defines how different data types appear when converted
        to strings, affecting concatenation behavior and print output.
        """
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, float):
            # Format numbers nicely, removing unnecessary decimal places
            if value.is_integer():
                return str(int(value))
            else:
                return str(value)
        else:
            return str(value)
    
    def _format_for_output(self, value):
        """
        Format values for user-friendly display in print statements.
        
        This method ensures that output looks natural and readable,
        which improves the user experience of your language.
        """
        if isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            else:
                return str(value)
        elif isinstance(value, str):
            return value  # Strings are displayed without quotes in output
        else:
            return str(value)
    
    # Type checking helper methods
    
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
        """Ensure a value is boolean for logical operations"""
        if not isinstance(value, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires a boolean, got {type(value).__name__}", 
                node
            )
    
    def _ensure_booleans(self, left, right, operator, node):
        """Ensure both values are boolean for logical operations"""
        if not isinstance(left, bool) or not isinstance(right, bool):
            raise InterpreterError(
                f"Operator '{operator}' requires booleans, got {type(left).__name__} and {type(right).__name__}", 
                node
            )
    
    # Visitor dispatch method
    
    def visit(self, node):
        """
        Enhanced visitor dispatch with comprehensive error handling.
        
        The visitor pattern allows the interpreter to handle different
        node types through corresponding visit methods, providing clean
        separation of concerns and easy extensibility.
        """
        if node is None:
            return None
        
        method_name = f'visit_{type(node).__name__}'
        visitor_method = getattr(self, method_name, None)
        
        if visitor_method is None:
            raise InterpreterError(f"No visit method for {type(node).__name__}")
        
        return visitor_method(node)
    
    def interpret(self, tree):
        """
        Main interpretation method for executing programs.
        
        This method serves as the entry point for program execution,
        handling the top-level program structure and providing
        comprehensive error reporting.
        """
        if tree is None:
            raise InterpreterError("Cannot interpret empty program")
        
        try:
            return self.visit(tree)
        except InterpreterError:
            # Re-raise interpreter errors without modification
            raise
        except Exception as e:
            # Wrap unexpected errors with context
            raise InterpreterError(f"Unexpected runtime error: {str(e)}")
    
    # Debugging and inspection methods
    
    def get_environment_state(self):
        """
        Return the current state of all variables for debugging.
        
        This method is useful for understanding program state and
        for implementing debugging features in development tools.
        """
        return self.global_env.get_all_variables()
    
    def reset_environment(self):
        """
        Clear all variables for testing or restarting program execution.
        
        This method is particularly useful in interactive mode when
        users want to start fresh without restarting the interpreter.
        """
        self.global_env.clear()