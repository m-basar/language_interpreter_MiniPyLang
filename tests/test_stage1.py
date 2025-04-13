import unittest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter

class TestStage1(unittest.TestCase):
    def evaluate(self, expression):
        lexer = Lexer(expression)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        interpreter = Interpreter(parser)
        return interpreter.interpret()
    
    def test_simple_addition(self):
        self.assertEqual(self.evaluate("1 + 2"), 3)
    
    def test_simple_subtraction(self):
        self.assertEqual(self.evaluate("1 - 2"), -1)
    
    def test_simple_multiplication(self):
        self.assertEqual(self.evaluate("2 * 3"), 6)
    
    def test_simple_division(self):
        self.assertEqual(self.evaluate("6 / 2"), 3)
    
    def test_example1(self):
        self.assertEqual(self.evaluate("1 - 2"), -1)
    
    def test_example2(self):
        self.assertEqual(self.evaluate("2.5 + 2.5 - 1.25"), 3.75)
    
    def test_example3(self):
        self.assertEqual(self.evaluate("(10 * 2) / 6"), 10 * 2 / 6)
    
    def test_example4(self):
        self.assertEqual(self.evaluate("8.5 / (2 * 9) - -3"), 8.5 / (2 * 9) - (-3))
    
    def test_unary_operators(self):
        self.assertEqual(self.evaluate("-5"), -5)
        self.assertEqual(self.evaluate("+5"), 5)
        self.assertEqual(self.evaluate("--5"), 5)
    
    def test_complex_expressions(self):
        self.assertEqual(self.evaluate("2 * (3 + 4)"), 14)
        self.assertEqual(self.evaluate("2 * 3 + 4"), 10)
        self.assertEqual(self.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(self.evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(self.evaluate("2 * (3 + 4 * 5)"), 46)

if __name__ == "__main__":
    unittest.main()