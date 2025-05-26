"""
ast_nodes.py – Stage 5 AST nodes with control flow

Adds control flow nodes to the existing Stage 4 AST:
- IfNode for conditional statements
- WhileNode for loop statements
- BlockNode for grouped statements
- InputNode for user input
"""


class ASTNode:
    """Base class for all AST nodes."""
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


class VariableNode(ASTNode):
    """
    Variable reference: myVariable

    Represents retrieving a variable’s value within an expression.
    """

    def __init__(self, token):
        self.token = token
        self.name = token.value

    def __str__(self):
        return f'Variable({self.name})'


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
    of types when the programmer’s intent is clear.
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
        self.prompt_expression = prompt_expression

    def __str__(self):
        if self.prompt_expression:
            return f'Input({self.prompt_expression})'
        else:
            return 'Input()'


# ============================================================================
# STATEMENT NODES (perform actions)
# ============================================================================

class AssignmentNode(ASTNode):
    """
    Variable assignment: variable = expression

    Stores a value in the programme’s memory for later use.
    """

    def __init__(self, variable_name, expression):
        self.variable_name = variable_name
        self.expression = expression

    def __str__(self):
        return f'Assignment({self.variable_name} = {self.expression})'


class PrintNode(ASTNode):
    """
    Print statement: print expression

    Evaluates an expression and displays the result on screen.
    """

    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return f'Print({self.expression})'


class DeleteNode(ASTNode):
    """
    Variable deletion: del variable_name

    Removes a variable from the programme’s memory.
    """

    def __init__(self, variable_name):
        self.variable_name = variable_name

    def __str__(self):
        return f'Delete({self.variable_name})'


class BlockNode(ASTNode):
    """
    Block of statements: { statement1; statement2; ... }

    Represents a grouped sequence of statements for control flow.
    """

    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        if len(self.statements) == 1:
            return f'Block(1 statement)'
        else:
            return f'Block({len(self.statements)} statements)'


class IfNode(ASTNode):
    """
    Conditional statement: if (condition) { ... } else { ... }

    Represents conditional execution with an optional else clause.
    """

    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __str__(self):
        if self.else_block:
            return f'If({self.condition}) then {self.then_block} else {self.else_block}'
        else:
            return f'If({self.condition}) then {self.then_block}'


class WhileNode(ASTNode):
    """
    Loop statement: while (condition) { ... }

    Executes the contained block repeatedly while the condition remains true.
    """

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __str__(self):
        return f'While({self.condition}) do {self.body}'


class ProgramNode(ASTNode):
    """
    Programme root: sequence of statements

    Represents the entire programme as a list of sequential statements.
    """

    def __init__(self, statements):
        self.statements = statements

    def __str__(self):
        if len(self.statements) == 1:
            return f'Program(1 statement)'
        else:
            return f'Program({len(self.statements)} statements)'
