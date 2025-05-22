"""
main.py – Main programme for the arithmetic expression calculator

This file ties together all components and provides the command-line interface.
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError

def evaluate_expression(expression_text):
    """
    Evaluate a single arithmetic expression and return the result.

    Args:
        expression_text: String containing the arithmetic expression

    Returns:
        The numerical result of the expression

    Raises:
        Various exceptions if the expression is invalid.
    """
    # Step 1: Tokenise the input
    lexer = Lexer(expression_text)

    # Step 2: Parse tokens into an AST
    parser = Parser(lexer)
    ast = parser.parse()

    # Step 3: Interpret the AST to obtain the result
    interpreter = Interpreter()
    result = interpreter.interpret(ast)

    return result

def process_file(filename):
    """
    Process a file containing arithmetic expressions, one per line.

    Args:
        filename: Path to the input file.
    """
    try:
        with open(filename, 'r') as file:
            line_number = 0

            for line in file:
                line_number += 1
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                try:
                    result = evaluate_expression(line)
                    print(f"{line} = {result}")

                except (LexerError, ParseError, InterpreterError) as e:
                    print(f"Error on line {line_number}: {e}")
                    print(f"  Expression: {line}")

                except Exception as e:
                    print(f"Unexpected error on line {line_number}: {e}")
                    print(f"  Expression: {line}")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    except IOError as e:
        print(f"Error reading file '{filename}': {e}")
        sys.exit(1)

def main():
    """Main entry point of the programme."""

    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        print("\nExample:")
        print("  python main.py expressions.txt")
        sys.exit(1)

    filename = sys.argv[1]

    print(f"Processing arithmetic expressions from: {filename}")
    print("=" * 50)

    process_file(filename)

    print("=" * 50)
    print("Completed.")

if __name__ == "__main__":
    main()
