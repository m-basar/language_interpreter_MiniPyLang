"""
ast_nodes.py - Enhanced AST nodes supporting variables and statements

Stage 4 introduces the critical distinction between expressions and statements:
- Expressions produce values (like 5 + 3 or variable lookups)
- Statements perform actions (like assignments or print operations)

This distinction shapes how we think about program execution and control flow.
"""


class ASTNode:
    """Base class for all AST nodes - provides common interface"""
    pass


# Expression nodes (produce values)
class NumberNode(ASTNode):
    """Numeric literal - unchanged from previous stages"""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f'Number({self.value})'


class BooleanNode(ASTNode):
    """Boolean literal - unchanged from previous stages"""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        return f'Boolean({self.value})'


class StringNode(ASTNode):
    """String literal - unchanged from Stage 3"""
    
    def __init__(self, token):
        self.token = token
        self.value = token.value
    
    def __str__(self):
        if len(self.value) > 20:
            return f'String("{self.value[:17]}...")'
        else:
            return f'String("{self.value}")'


class VariableNode(ASTNode):
    """
    Variable reference in an expression context.
    
    This node represents looking up a variable's value within an expression.
    It's the bridge between the program's memory (environment) and
    expression evaluation.
    """
    
    def __init__(self, token):
        self.token = token
        self.name = token.value  # The variable name
    
    def __str__(self):
        return f'Variable({self.name})'


class BinaryOperationNode(ASTNode):
    """Binary operations - enhanced but structurally unchanged"""
    
    def __init__(self, left, operator_token, right):
        self.left = left
        self.token = self.operator = operator_token
        self.right = right
    
    def __str__(self):
        return f'BinaryOp({self.operator.value})'


class UnaryOperationNode(ASTNode):
    """Unary operations - unchanged from previous stages"""
    
    def __init__(self, operator_token, operand):
        self.token = self.operator = operator_token
        self.operand = operand
    
    def __str__(self):
        return f'UnaryOp({self.operator.value})'


# Statement nodes (perform actions)
class AssignmentNode(ASTNode):
    """
    Variable assignment statement.
    
    Assignment represents the fundamental operation of storing a value
    in the program's memory. It's a statement because it performs an
    action (changing state) rather than producing a value.
    """
    
    def __init__(self, variable_name, expression):
        self.variable_name = variable_name  # String: the variable name
        self.expression = expression        # ASTNode: expression to evaluate
    
    def __str__(self):
        return f'Assignment({self.variable_name} = {self.expression})'


class PrintNode(ASTNode):
    """
    Print statement for program output.
    
    Print statements represent the primary way programs communicate
    with users. They evaluate an expression and display the result.
    """
    
    def __init__(self, expression):
        self.expression = expression  # ASTNode: expression to evaluate and print
    
    def __str__(self):
        return f'Print({self.expression})'


class ProgramNode(ASTNode):
    """
    Program root node containing a sequence of statements.
    
    The program node represents the top level of our language's structure.
    It contains a list of statements that execute in sequence, which
    transforms our language from single-expression evaluation to
    full program execution.
    """
    
    def __init__(self, statements):
        self.statements = statements  # List of statement nodes
    
    def __str__(self):
        if len(self.statements) == 1:
            return f'Program(1 statement)'
        else:
            return f'Program({len(self.statements)} statements)'