"""
main.py – Arithmetic expression calculator with tree visualisation

This enhanced version allows you to see the Abstract Syntax Tree structure,
which is invaluable for understanding how expressions are parsed.
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError

def print_tree(node, level=0, prefix="Root: "):
    """
    Print a visual representation of the Abstract Syntax Tree.
    
    This function recursively traverses the tree and prints each node
    with appropriate indentation to indicate the tree structure.
    
    Args:
        node: The current AST node to print
        level: The current depth in the tree (for indentation)
        prefix: A string prefix to indicate the relationship to parent nodes
    """
    if node is None:
        return

    # Create indentation based on tree level
    indent = "  " * level

    # Print the current node
    print(f"{indent}{prefix}{node}")

    # Handle different types of nodes and their children
    if hasattr(node, 'left') and hasattr(node, 'right'):
        # Binary operation node – has left and right children
        print_tree(node.left, level + 1, "L── ")
        print_tree(node.right, level + 1, "R── ")

    elif hasattr(node, 'operand'):
        # Unary operation node – has one operand
        print_tree(node.operand, level + 1, "└── ")

def evaluate_expression_with_tree(expression_text, show_tree=False):
    """
    Evaluate an arithmetic expression and optionally display the AST.
    
    This enhanced version offers visibility into how your parser
    interprets the expression by displaying the tree structure.
    
    Args:
        expression_text: String containing the arithmetic expression
        show_tree: Whether to display the Abstract Syntax Tree
        
    Returns:
        The numerical result of the expression
    """
    print(f"\nExpression: {expression_text}")
    print("-" * (len(expression_text) + 12))
    
    try:
        # Step 1: Tokenise the input
        lexer = Lexer(expression_text)

        # Optional: Show tokens (useful for debugging lexer issues)
        if show_tree:
            print("Tokens:")
            temp_lexer = Lexer(expression_text)  # Temporary lexer
            tokens = []
            while True:
                token = temp_lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            print("  " + " → ".join(str(token) for token in tokens))
            print()

        # Step 2: Parse tokens into an AST
        parser = Parser(lexer)
        ast = parser.parse()

        # Step 3: Display the tree structure if requested
        if show_tree:
            print("Abstract Syntax Tree:")
            print_tree(ast)
            print()

        # Step 4: Interpret the AST to obtain the result
        interpreter = Interpreter()
        result = interpreter.interpret(ast)

        print(f"Result: {result}")
        return result

    except (LexerError, ParseError, InterpreterError) as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def interactive_mode():
    """
    Run the calculator in interactive mode.
    
    This allows direct input of expressions and displays their trees,
    which is ideal for experimentation and learning.
    """
    print("=== Interactive Arithmetic Calculator ===")
    print("Type expressions to see their parse trees and results.")
    print("Commands:")
    print("  'tree on' or 'tree off' – toggle tree display")
    print("  'quit' or 'exit' – exit the programme")
    print("  'help' – show this help message")
    print()
    
    show_tree = True  # Start with tree display enabled

    while True:
        try:
            user_input = input(">>> ").strip()   # CHANGED to >>> for better visibility
            
            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'tree on':
                show_tree = True
                print("Tree display enabled")
                continue
            elif user_input.lower() == 'tree off':
                show_tree = False
                print("Tree display disabled")
                continue
            elif user_input.lower() == 'help':
                print("\nCommands:")
                print("  'tree on' or 'tree off' – toggle tree display")
                print("  'quit' or 'exit' – exit the programme")
                print("  Or simply type any arithmetic expression!")
                print()
                continue

            # Evaluate the expression
            evaluate_expression_with_tree(user_input, show_tree)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

def process_file_with_trees(filename, show_trees=False):
    """
    Process a file containing arithmetic expressions, optionally showing trees.
    
    Args:
        filename: Path to the input file
        show_trees: Whether to display Abstract Syntax Trees for each expression
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

                print(f"\n{'='*60}")
                print(f"Line {line_number}")
                result = evaluate_expression_with_tree(line, show_trees)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{filename}': {e}")
        sys.exit(1)

def main():
    """Enhanced main entry point with multiple modes of operation."""

    if len(sys.argv) == 1:
        # No arguments – run in interactive mode
        interactive_mode()

    elif len(sys.argv) == 2:
        filename = sys.argv[1]

        if filename in ['-h', '--help']:
            print("Arithmetic Expression Calculator")
            print("\nUsage:")
            print("  python main.py                    # Interactive mode")
            print("  python main.py <file>             # Process file without trees")
            print("  python main.py <file> --tree      # Process file with trees")
            print("  python main.py --interactive      # Force interactive mode")
            print("\nIn interactive mode, you may type expressions and see their parse trees.")
            return

        elif filename == '--interactive':
            interactive_mode()
            return

        # Process file without trees
        print(f"Processing expressions from: {filename}")
        process_file_with_trees(filename, show_trees=False)

    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        flag = sys.argv[2]

        if flag == '--tree':
            # Process file with trees
            print(f"Processing expressions from: {filename} (with tree visualisation)")
            process_file_with_trees(filename, show_trees=True)
        else:
            print("Unknown flag. Use --tree to show parse trees.")
            sys.exit(1)

    else:
        print("Too many arguments. Use -h for help.")
        sys.exit(1)

if __name__ == "__main__":
    main()
