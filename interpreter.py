"""
interpreter.py - Enhanced Stage 6 interpreter with list and dictionary support

Executes programmes with support for both list and dictionary data structures:
- All existing Stage 5 features
- List literals: [1, 2, 3]
- Dictionary literals: {"key": "value", "age": 25}
- Index/key access: list[0], dict["key"]
- Index/key assignment: list[0] = value, dict["key"] = value
- List functions: append(list, value), remove(list, index), len(list)
- Dictionary functions: keys(dict), values(dict), has_key(dict, key), del_key(dict, key)
"""

import math
from tokens import Token
from ast_nodes import (
    NumberNode, BooleanNode, StringNode, VariableNode,
    BinaryOperationNode, UnaryOperationNode,
    AssignmentNode, PrintNode, ProgrammeNode, DeleteNode, NoneNode,
    ConversionNode, InputNode,
    IfNode, WhileNode, BlockNode,
    # List and Dictionary nodes
    ListNode, DictNode, IndexAccessNode, IndexAssignmentNode, 
    ListFunctionNode, DictFunctionNode
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
    Enhanced value wrapper for type tracking and operations including lists and dictionaries.
    
    Provides explicit type information and operations for all
    MiniPyLang values including the new list and dictionary data types.
    """
    
    # Value type constants
    NUMBER = 'NUMBER'
    BOOLEAN = 'BOOLEAN'
    STRING = 'STRING'
    NONE = 'NONE'
    LIST = 'LIST'
    DICT = 'DICT'  # Dictionary type
    
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
            elif isinstance(value, list):
                self.type = self.LIST
            elif isinstance(value, dict):
                self.type = self.DICT
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
    
    def is_list(self):
        return self.type == self.LIST
    
    def is_dict(self):
        """Check if value is a dictionary"""
        return self.type == self.DICT
    
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
        elif self.is_list():
            return len(self.value) > 0
        elif self.is_dict():
            # Non-empty dictionaries are truthy
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
        elif self.is_list():
            # List string representation
            if len(self.value) == 0:
                return "[]"
            else:
                # Convert each element to string representation
                elements = []
                for item in self.value:
                    if isinstance(item, str):
                        elements.append(f'"{item}"')
                    elif isinstance(item, bool):
                        elements.append("true" if item else "false")
                    elif item is None:
                        elements.append("none")
                    else:
                        elements.append(str(item))
                return "[" + ", ".join(elements) + "]"
        elif self.is_dict():
            # Dictionary string representation
            if len(self.value) == 0:
                return "{}"
            else:
                # Convert each key-value pair to string representation
                pairs = []
                for key, value in self.value.items():
                    # Format key
                    if isinstance(key, str):
                        key_str = f'"{key}"'
                    elif isinstance(key, bool):
                        key_str = "true" if key else "false"
                    elif key is None:
                        key_str = "none"
                    else:
                        key_str = str(key)
                    
                    # Format value
                    if isinstance(value, str):
                        value_str = f'"{value}"'
                    elif isinstance(value, bool):
                        value_str = "true" if value else "false"
                    elif value is None:
                        value_str = "none"
                    else:
                        value_str = str(value)
                    
                    pairs.append(f"{key_str}: {value_str}")
                
                return "{" + ", ".join(pairs) + "}"
        else:
            return str(self.value)


class Interpreter:
    """
    Enhanced Stage 6 interpreter with list and dictionary support for MiniPyLang.
    
    Executes programmes with proper variable management, type checking,
    error handling, type conversion, control flow, and collection operations.
    """
    
    # Floating point comparison tolerance
    EPSILON = 1e-10
    
    # Loop safety limit to prevent infinite loops
    MAX_LOOP_ITERATIONS = 10000
    
    def __init__(self):
        """Initialise interpreter with empty environment"""
        self.global_env = Environment()
        
        # Track loop nesting for safety
        self.loop_iteration_count = 0
        self.in_loop = False
    
    # Helper methods for dictionary operations
    def _is_hashable(self, value):
        """Check if a value can be used as a dictionary key"""
        return isinstance(value, (str, int, float, bool, type(None)))
    
    def _format_key(self, key):
        """Format a key for error messages"""
        if isinstance(key, str):
            return f'"{key}"'
        elif isinstance(key, bool):
            return "true" if key else "false"
        elif key is None:
            return "none"
        else:
            return str(key)
    
    def visit_ProgrammeNode(self, node):
        """Execute programme as sequence of statements"""
        return self._execute_statement_list(node.statements)
    
    def _execute_statement_list(self, statements):
        """Execute list of statements"""
        last_result = None
        
        for statement in statements:
            try:
                result = self.visit(statement)
                
                # Track last expression result for interactive mode
                if not isinstance(statement, (AssignmentNode, PrintNode, DeleteNode, 
                                            IfNode, WhileNode, IndexAssignmentNode)):
                    last_result = result
                    
            except (BreakException, ContinueException):
                # Control flow exceptions should bubble up to loop handlers
                raise
            except InterpreterError as e:
                raise e
            except Exception as e:
                raise InterpreterError(f"Runtime error: {str(e)}", statement)
        
        return last_result
    
    # List-related visitor methods
    def visit_ListNode(self, node):
        """Create list literal: [element1, element2, element3]"""
        try:
            elements = []
            for element_node in node.elements:
                element_value = self.visit(element_node)
                elements.append(element_value)
            
            return elements
            
        except Exception as e:
            raise InterpreterError(f"Error creating list: {str(e)}", node)
    
    # Dictionary-related visitor methods
    def visit_DictNode(self, node):
        """
        Create dictionary literal: {"key1": value1, "key2": value2}
        
        Evaluates all keys and values and creates a Python dictionary.
        Keys must be hashable (strings, numbers, booleans, none).
        """
        try:
            result_dict = {}
            
            for key_node, value_node in node.pairs:
                # Evaluate key and value
                key_value = self.visit(key_node)
                value_value = self.visit(value_node)
                
                # Ensure key is hashable
                if not self._is_hashable(key_value):
                    raise InterpreterError(
                        f"Dictionary key must be hashable (string, number, boolean, or none), got {type(key_value).__name__}",
                        node
                    )
                
                # Store in dictionary
                result_dict[key_value] = value_value
            
            return result_dict
            
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error creating dictionary: {str(e)}", node)
    
    def visit_IndexAccessNode(self, node):
        """
        Access container element: list[index] or dict["key"]
        
        Supports both list indexing and dictionary key access.
        """
        try:
            # Evaluate the container expression
            container_value = self.visit(node.container_expression)
            
            # Evaluate the key/index expression
            key_value = self.visit(node.key_expression)
            
            # Handle list indexing
            if isinstance(container_value, list):
                # Ensure key is a number for lists
                if not isinstance(key_value, (int, float)):
                    raise InterpreterError(
                        f"List indices must be numbers, got {type(key_value).__name__}",
                        node
                    )
                
                # Convert to integer index
                index = int(key_value)
                
                # Check bounds with negative indexing support
                if index < 0:
                    index = len(container_value) + index
                
                if index < 0 or index >= len(container_value):
                    raise InterpreterError(
                        f"List index out of range: index {int(key_value)} for list of length {len(container_value)}",
                        node
                    )
                
                return container_value[index]
            
            # Handle dictionary key access
            elif isinstance(container_value, dict):
                # Ensure key is hashable
                if not self._is_hashable(key_value):
                    raise InterpreterError(
                        f"Dictionary key must be hashable, got {type(key_value).__name__}",
                        node
                    )
                
                # Check if key exists
                if key_value not in container_value:
                    raise InterpreterError(
                        f"Dictionary key not found: {self._format_key(key_value)}",
                        node
                    )
                
                return container_value[key_value]
            
            else:
                raise InterpreterError(
                    f"Cannot index {type(container_value).__name__}, only lists and dictionaries support indexing",
                    node
                )
            
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error accessing container element: {str(e)}", node)
    
    def visit_IndexAssignmentNode(self, node):
        """
        Assign to container element: list[index] = value or dict["key"] = value
        
        Modifies the container in place.
        """
        try:
            # Evaluate the container expression
            container_value = self.visit(node.container_expression)
            
            # Evaluate the key/index expression
            key_value = self.visit(node.key_expression)
            
            # Evaluate the new value
            new_value = self.visit(node.value_expression)
            
            # Handle list index assignment
            if isinstance(container_value, list):
                # Ensure key is a number for lists
                if not isinstance(key_value, (int, float)):
                    raise InterpreterError(
                        f"List indices must be numbers, got {type(key_value).__name__}",
                        node
                    )
                
                # Convert to integer index
                index = int(key_value)
                
                # Check bounds with negative indexing support
                if index < 0:
                    index = len(container_value) + index
                
                if index < 0 or index >= len(container_value):
                    raise InterpreterError(
                        f"List index out of range: index {int(key_value)} for list of length {len(container_value)}",
                        node
                    )
                
                # Assign to the list
                container_value[index] = new_value
            
            # Handle dictionary key assignment
            elif isinstance(container_value, dict):
                # Ensure key is hashable
                if not self._is_hashable(key_value):
                    raise InterpreterError(
                        f"Dictionary key must be hashable, got {type(key_value).__name__}",
                        node
                    )
                
                # Assign to the dictionary (creates new key if it doesn't exist)
                container_value[key_value] = new_value
            
            else:
                raise InterpreterError(
                    f"Cannot assign to index of {type(container_value).__name__}, only lists and dictionaries support index assignment",
                    node
                )
            
            return None
            
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error in container index assignment: {str(e)}", node)
    
    def visit_DictFunctionNode(self, node):
        """
        Handle dictionary function calls: keys(dict), values(dict), has_key(dict, key), del_key(dict, key)
        
        Implements the four core dictionary operations required by the assignment.
        """
        try:
            function_name = node.function_name
            arguments = node.arguments
            
            if function_name == 'keys':
                # keys(dict) - returns list of all keys
                if len(arguments) != 1:
                    raise InterpreterError(f"keys() takes exactly 1 argument ({len(arguments)} given)", node)
                
                dict_value = self.visit(arguments[0])
                
                if not isinstance(dict_value, dict):
                    raise InterpreterError(
                        f"keys() argument must be a dictionary, got {type(dict_value).__name__}",
                        node
                    )
                
                # Return list of keys
                return list(dict_value.keys())
            
            elif function_name == 'values':
                # values(dict) - returns list of all values
                if len(arguments) != 1:
                    raise InterpreterError(f"values() takes exactly 1 argument ({len(arguments)} given)", node)
                
                dict_value = self.visit(arguments[0])
                
                if not isinstance(dict_value, dict):
                    raise InterpreterError(
                        f"values() argument must be a dictionary, got {type(dict_value).__name__}",
                        node
                    )
                
                # Return list of values
                return list(dict_value.values())
            
            elif function_name == 'has_key':
                # has_key(dict, key) - returns true if key exists, false otherwise
                if len(arguments) != 2:
                    raise InterpreterError(f"has_key() takes exactly 2 arguments ({len(arguments)} given)", node)
                
                dict_value = self.visit(arguments[0])
                key_value = self.visit(arguments[1])
                
                if not isinstance(dict_value, dict):
                    raise InterpreterError(
                        f"has_key() first argument must be a dictionary, got {type(dict_value).__name__}",
                        node
                    )
                
                if not self._is_hashable(key_value):
                    raise InterpreterError(
                        f"has_key() second argument must be hashable, got {type(key_value).__name__}",
                        node
                    )
                
                # Return boolean indicating key existence
                return key_value in dict_value
            
            elif function_name == 'del_key':
                # del_key(dict, key) - removes key-value pair from dictionary
                if len(arguments) != 2:
                    raise InterpreterError(f"del_key() takes exactly 2 arguments ({len(arguments)} given)", node)
                
                dict_value = self.visit(arguments[0])
                key_value = self.visit(arguments[1])
                
                if not isinstance(dict_value, dict):
                    raise InterpreterError(
                        f"del_key() first argument must be a dictionary, got {type(dict_value).__name__}",
                        node
                    )
                
                if not self._is_hashable(key_value):
                    raise InterpreterError(
                        f"del_key() second argument must be hashable, got {type(key_value).__name__}",
                        node
                    )
                
                # Check if key exists
                if key_value not in dict_value:
                    raise InterpreterError(
                        f"del_key() key not found: {self._format_key(key_value)}",
                        node
                    )
                
                # Remove and return the deleted value
                deleted_value = dict_value[key_value]
                del dict_value[key_value]
                return deleted_value
            
            else:
                raise InterpreterError(f"Unknown dictionary function: {function_name}", node)
                
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error in dictionary function {node.function_name}(): {str(e)}", node)
    
    # List function visitor
    def visit_ListFunctionNode(self, node):
        """Handle list function calls: append(list, value), remove(list, index), len(list)"""
        try:
            function_name = node.function_name
            arguments = node.arguments
            
            if function_name == 'len':
                # len(container) - returns length of list or dictionary
                if len(arguments) != 1:
                    raise InterpreterError(f"len() takes exactly 1 argument ({len(arguments)} given)", node)
                
                container_value = self.visit(arguments[0])
                
                if isinstance(container_value, (list, dict)):
                    return len(container_value)
                else:
                    raise InterpreterError(
                        f"len() argument must be a list or dictionary, got {type(container_value).__name__}",
                        node
                    )
            
            elif function_name == 'append':
                # append(list, value) - adds value to end of list
                if len(arguments) != 2:
                    raise InterpreterError(f"append() takes exactly 2 arguments ({len(arguments)} given)", node)
                
                list_value = self.visit(arguments[0])
                new_value = self.visit(arguments[1])
                
                if not isinstance(list_value, list):
                    raise InterpreterError(
                        f"append() first argument must be a list, got {type(list_value).__name__}",
                        node
                    )
                
                # Modify list in place
                list_value.append(new_value)
                return list_value
            
            elif function_name == 'remove':
                # remove(list, index) - removes element at index from list
                if len(arguments) != 2:
                    raise InterpreterError(f"remove() takes exactly 2 arguments ({len(arguments)} given)", node)
                
                list_value = self.visit(arguments[0])
                index_value = self.visit(arguments[1])
                
                if not isinstance(list_value, list):
                    raise InterpreterError(
                        f"remove() first argument must be a list, got {type(list_value).__name__}",
                        node
                    )
                
                if not isinstance(index_value, (int, float)):
                    raise InterpreterError(
                        f"remove() second argument must be a number, got {type(index_value).__name__}",
                        node
                    )
                
                # Convert to integer index
                index = int(index_value)
                
                # Check bounds with negative indexing support
                if index < 0:
                    index = len(list_value) + index
                
                if index < 0 or index >= len(list_value):
                    raise InterpreterError(
                        f"remove() index out of range: index {int(index_value)} for list of length {len(list_value)}",
                        node
                    )
                
                # Remove and return the removed element
                removed_value = list_value.pop(index)
                return removed_value
            
            else:
                raise InterpreterError(f"Unknown list function: {function_name}", node)
                
        except InterpreterError:
            raise
        except Exception as e:
            raise InterpreterError(f"Error in list function {node.function_name}(): {str(e)}", node)
    
    # Control flow visitor methods (unchanged from Stage 5)
    def visit_IfNode(self, node):
        """Execute conditional statement with proper boolean evaluation."""
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
        """Execute while loop with safety limits and proper termination."""
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
        """Handle input function calls with optional prompts."""
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
    
    # Enhanced type conversion with dictionary support
    def visit_ConversionNode(self, node):
        """Handle type conversion function calls with comprehensive error handling."""
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
                elif isinstance(value, list):
                    # Convert list to string representation
                    minipy_val = MiniPyValue(value)
                    return str(minipy_val)
                elif isinstance(value, dict):
                    # Convert dictionary to string representation
                    minipy_val = MiniPyValue(value)
                    return str(minipy_val)
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
                elif isinstance(value, list):
                    # Convert list length to integer
                    return len(value)
                elif isinstance(value, dict):
                    # Convert dictionary length to integer
                    return len(value)
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
                elif isinstance(value, list):
                    # Convert list length to float
                    return float(len(value))
                elif isinstance(value, dict):
                    # Convert dictionary length to float
                    return float(len(value))
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
                elif isinstance(value, list):
                    # List truthiness: empty list is false, non-empty is true
                    return len(value) > 0
                elif isinstance(value, dict):
                    # Dictionary truthiness: empty dict is false, non-empty is true
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
    
    # Helper methods (enhanced with dictionary support)
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
        
        # List concatenation
        elif isinstance(left_value, list) and isinstance(right_value, list):
            return left_value + right_value
        
        # Type mismatch error
        else:
            left_type = type(left_value).__name__
            right_type = type(right_value).__name__
            raise InterpreterError(
                f"Cannot add {left_type} and {right_type}. "
                f"Numbers, strings, and lists can only be added to their own type. "
                f"Use explicit conversion if mixing is intended.",
                node
            )
    
    def _handle_equality(self, left_value, right_value):
        """Handle equality with floating point awareness and collection support"""
        # Different types are never equal (except numbers)
        if type(left_value) != type(right_value):
            # Allow int/float comparison
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                return abs(float(left_value) - float(right_value)) < self.EPSILON
            return False
        
        # Floating point comparison with epsilon
        if isinstance(left_value, float) and isinstance(right_value, float):
            return abs(left_value - right_value) < self.EPSILON
        
        # Mixed int/float comparison
        if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
            return abs(float(left_value) - float(right_value)) < self.EPSILON
        
        # List equality (element-wise comparison)
        if isinstance(left_value, list) and isinstance(right_value, list):
            if len(left_value) != len(right_value):
                return False
            
            for i in range(len(left_value)):
                if not self._handle_equality(left_value[i], right_value[i]):
                    return False
            return True
        
        # Dictionary equality (key-value comparison)
        if isinstance(left_value, dict) and isinstance(right_value, dict):
            if len(left_value) != len(right_value):
                return False
            
            # Check all keys exist in both dictionaries
            if set(left_value.keys()) != set(right_value.keys()):
                return False
            
            # Check all values are equal
            for key in left_value:
                if not self._handle_equality(left_value[key], right_value[key]):
                    return False
            return True
        
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
            raise InterpreterError("Cannot interpret empty programme")
        
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