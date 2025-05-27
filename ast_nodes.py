"""
ast_nodes.py - Enhanced Stage 6 AST nodes with list support

Adds list data structure nodes to the existing Stage 5 AST:
- ListNode for list literals [1, 2, 3]
- IndexAccessNode for list[index] operations
- IndexAssignmentNode for list[index] = value operations
- ListFunctionNode for append(), remove(), len() functions
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


# NEW: List literal node
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


# NEW: Index access node
class IndexAccessNode(ASTNode):
    """
    Index access: list[index]
    
    Represents accessing an element from a list by index.
    The list can be any expression that evaluates to a list.
    """
    
    def __init__(self, list_expression, index_expression):
        self.list_expression = list_expression    # Expression that should evaluate to a list
        self.index_expression = index_expression  # Expression that should evaluate to a number
    
    def __str__(self):
        return f'IndexAccess({self.list_expression}[{self.index_expression}])'


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


# NEW: List function call node
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


# NEW: Index assignment node
class IndexAssignmentNode(ASTNode):
    """
    Index assignment: list[index] = value
    
    Assigns a value to a specific index in a list.
    Modifies the list in place.
    """
    
    def __init__(self, list_expression, index_expression, value_expression):
        self.list_expression = list_expression    # Expression that should evaluate to a list
        self.index_expression = index_expression  # Expression that should evaluate to a number
        self.value_expression = value_expression  # Expression for the new value
    
    def __str__(self):
        return f'IndexAssignment({self.list_expression}[{self.index_expression}] = {self.value_expression})'


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


# Control flow nodes (unchanged from Stage 5)
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