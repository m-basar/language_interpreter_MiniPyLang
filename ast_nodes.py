"""
ast_nodes.py - Enhanced Stage 6 AST nodes with list and dictionary support

Adds list and dictionary data structure nodes to the existing Stage 5 AST:
- ListNode for list literals [1, 2, 3]
- DictNode for dictionary literals {"key": value}
- IndexAccessNode for list[index] and dict["key"] operations
- IndexAssignmentNode for list[index] = value and dict["key"] = value operations
- ListFunctionNode for append(), remove(), len() functions
- DictFunctionNode for keys(), values(), has_key(), del_key() functions
"""


class ASTNode:
    """Base class for all AST nodes"""
    pass


# ============================================================================
# EXPRESSION NODES (produce values)
# ============================================================================

class NumberNode(ASTNode):
    """Numeric literal: 42, 3.14"""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f'Number({self.value})'


class BooleanNode(ASTNode):
    """Boolean literal: true, false"""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f'Boolean({self.value})'


class StringNode(ASTNode):
    """String literal: "hello world" """
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        if len(self.value) > 20:
            return f'String("{self.value[:17]}...")'
        else:
            return f'String("{self.value}")'


class NoneNode(ASTNode):
    """None literal: none"""
    
    def __init__(self, token):
        self.token = token
        self.value = None
    
    def __str__(self):
        return 'None(none)'


class ListNode(ASTNode):
    """
    List literal: [1, 2, 3, "hello"]
    
    Represents a list literal with elements of potentially different types.
    Supports heterogeneous lists like Python.
    """
    
    def __init__(self, elements):
        self.elements = elements  # List of expression nodes
    
    def __str__(self):
        if len(self.elements) == 0:
            return 'List(empty)'
        elif len(self.elements) == 1:
            return f'List(1 element)'
        else:
            return f'List({len(self.elements)} elements)'


class DictNode(ASTNode):
    """
    Dictionary literal: {"name": "Alice", "age": 25, 1: "number key"}
    
    Represents a dictionary literal with key-value pairs.
    Supports any type as keys and values (like Python).
    """
    
    def __init__(self, pairs):
        self.pairs = pairs  # List of (key_expr, value_expr) tuples
    
    def __str__(self):
        if len(self.pairs) == 0:
            return 'Dict(empty)'
        elif len(self.pairs) == 1:
            return f'Dict(1 pair)'
        else:
            return f'Dict({len(self.pairs)} pairs)'


class VariableNode(ASTNode):
    """
    Variable reference: myVariable
    
    Represents looking up a variable's value in an expression.
    """
    
    def __init__(self, token):
        self.token = token
        self.name = token.value
    
    def __str__(self):
        return f'Variable({self.name})'


class IndexAccessNode(ASTNode):
    """
    Index access: list[index] or dict["key"]
    
    Represents accessing an element from a list by index or dictionary by key.
    The container can be any expression that evaluates to a list or dictionary.
    """
    
    def __init__(self, container_expression, key_expression):
        self.container_expression = container_expression    # Expression that should evaluate to a list/dict
        self.key_expression = key_expression  # Expression that should evaluate to an index/key
    
    def __str__(self):
        return f'IndexAccess({self.container_expression}[{self.key_expression}])'


class BinaryOperationNode(ASTNode):
    """
    Binary operation: left operator right
    
    Represents operations like 5 + 3, x == y, etc.
    """
    
    def __init__(self, left, operator_token, right):
        self.left = left
        self.token = self.operator = operator_token
        self.right = right
    
    def __str__(self):
        return f'BinaryOp({self.operator.value})'


class UnaryOperationNode(ASTNode):
    """
    Unary operation: operator operand
    
    Represents operations like -5, !flag, +x, etc.
    """
    
    def __init__(self, operator_token, operand):
        self.token = self.operator = operator_token
        self.operand = operand
    
    def __str__(self):
        return f'UnaryOp({self.operator.value})'


class ConversionNode(ASTNode):
    """
    Type conversion function call: str(value), int(value), etc.
    
    Represents explicit type conversions that allow safe mixing
    of types when the programmer's intent is clear.
    """
    
    def __init__(self, conversion_type, expression):
        self.conversion_type = conversion_type  # 'str', 'int', 'float', 'bool'
        self.expression = expression            # Expression to convert
    
    def __str__(self):
        return f'Convert({self.conversion_type}, {self.expression})'


class InputNode(ASTNode):
    """
    Input function call: input("prompt")
    
    Represents getting user input with an optional prompt string.
    """
    
    def __init__(self, prompt_expression=None):
        self.prompt_expression = prompt_expression  # Optional prompt string
    
    def __str__(self):
        if self.prompt_expression:
            return f'Input({self.prompt_expression})'
        else:
            return 'Input()'


class ListFunctionNode(ASTNode):
    """
    List function call: append(list, value), remove(list, index), len(list)
    
    Represents built-in list manipulation functions.
    Different functions have different argument requirements:
    - append(list, value): adds value to end of list
    - remove(list, index): removes element at index from list
    - len(list): returns length of list
    """
    
    def __init__(self, function_name, arguments):
        self.function_name = function_name  # 'append', 'remove', 'len'
        self.arguments = arguments          # List of expression nodes
    
    def __str__(self):
        arg_count = len(self.arguments)
        return f'ListFunc({self.function_name}, {arg_count} args)'


class DictFunctionNode(ASTNode):
    """
    Dictionary function call: keys(dict), values(dict), has_key(dict, key), del_key(dict, key)
    
    Represents built-in dictionary manipulation functions.
    Different functions have different argument requirements:
    - keys(dict): returns list of all keys
    - values(dict): returns list of all values
    - has_key(dict, key): returns true if key exists, false otherwise
    - del_key(dict, key): removes key-value pair from dictionary
    """
    
    def __init__(self, function_name, arguments):
        self.function_name = function_name  # 'keys', 'values', 'has_key', 'del_key'
        self.arguments = arguments          # List of expression nodes
    
    def __str__(self):
        arg_count = len(self.arguments)
        return f'DictFunc({self.function_name}, {arg_count} args)'


# ============================================================================
# STATEMENT NODES (perform actions)
# ============================================================================

class AssignmentNode(ASTNode):
    """
    Variable assignment: variable = expression
    
    Stores a value in the programme's memory.
    """
    
    def __init__(self, variable_name, expression):
        self.variable_name = variable_name  # String
        self.expression = expression        # ASTNode
    
    def __str__(self):
        return f'Assignment({self.variable_name} = {self.expression})'


class IndexAssignmentNode(ASTNode):
    """
    Index assignment: list[index] = value or dict["key"] = value
    
    Assigns a value to a specific index in a list or key in a dictionary.
    Modifies the container in place.
    """
    
    def __init__(self, container_expression, key_expression, value_expression):
        self.container_expression = container_expression    # Expression that should evaluate to a list/dict
        self.key_expression = key_expression  # Expression that should evaluate to an index/key
        self.value_expression = value_expression  # Expression for the new value
    
    def __str__(self):
        return f'IndexAssignment({self.container_expression}[{self.key_expression}] = {self.value_expression})'


class PrintNode(ASTNode):
    """
    Print statement: print expression
    
    Evaluates an expression and displays the result.
    """
    
    def __init__(self, expression):
        self.expression = expression  # ASTNode
    
    def __str__(self):
        return f'Print({self.expression})'


class DeleteNode(ASTNode):
    """
    Variable deletion: del variable_name
    
    Removes a variable from the programme's memory.
    """
    
    def __init__(self, variable_name):
        self.variable_name = variable_name  # String
    
    def __str__(self):
        return f'Delete({self.variable_name})'


class BlockNode(ASTNode):
    """
    Block of statements: { statement1; statement2; ... }
    
    Represents a grouped sequence of statements for control flow.
    """
    
    def __init__(self, statements):
        self.statements = statements  # List of statement nodes
    
    def __str__(self):
        if len(self.statements) == 1:
            return f'Block(1 statement)'
        else:
            return f'Block({len(self.statements)} statements)'


class IfNode(ASTNode):
    """
    Conditional statement: if (condition) { ... } else { ... }
    
    Represents conditional execution with optional else clause.
    """
    
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition      # Expression that evaluates to boolean
        self.then_block = then_block    # Block to execute if condition is true
        self.else_block = else_block    # Optional block for else clause
    
    def __str__(self):
        if self.else_block:
            return f'If({self.condition}) then {self.then_block} else {self.else_block}'
        else:
            return f'If({self.condition}) then {self.then_block}'


class WhileNode(ASTNode):
    """
    Loop statement: while (condition) { ... }
    
    Represents repetitive execution while condition remains true.
    """
    
    def __init__(self, condition, body):
        self.condition = condition  # Expression that evaluates to boolean
        self.body = body           # Block to execute repeatedly
    
    def __str__(self):
        return f'While({self.condition}) do {self.body}'


class ProgrammeNode(ASTNode):
    """
    Programme root: sequence of statements
    
    Represents the entire programme as a list of statements.
    """
    
    def __init__(self, statements):
        self.statements = statements  # List of statement nodes
    
    def __str__(self):
        if len(self.statements) == 1:
            return f'Programme(1 statement)'
        else:
            return f'Programme({len(self.statements)} statements)'