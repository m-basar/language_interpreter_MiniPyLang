class NodeVisitor:
    """Base class for AST node visitors."""
    def visit(self, node):
        """
        Visits a node and calls the appropriate visit method.
        
        Args:
            node: The node to visit
        """
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """Default behavior for unimplemented node types."""
        raise Exception(f"No visit_{node.__class__.__name__} method defined")

class Interpreter(NodeVisitor):
    """
    Interprets the AST and evaluates expressions.
    """
    def __init__(self, parser):
        self.parser = parser
    
    def visit_BinOp(self, node):
        """Handles binary operations."""
        if node.op == '+':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == '-':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == '*':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == '/':
            return self.visit(node.left) / self.visit(node.right)
    
    def visit_UnaryOp(self, node):
        """Handles unary operations."""
        if node.op == '+':
            return +self.visit(node.expr)
        elif node.op == '-':
            return -self.visit(node.expr)
    
    def visit_Num(self, node):
        """Handles numeric values."""
        return node.value
    
    def interpret(self):
        """
        Interprets the program and returns the result.
        
        Returns:
            The result of the program
        """
        tree = self.parser.parse()
        return self.visit(tree)