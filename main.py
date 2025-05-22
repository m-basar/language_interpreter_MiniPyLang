"""
main.py - MiniPyLang Interactive Interpreter and File Processor

MiniPyLang is an educational programming language that demonstrates
fundamental concepts in arithmetic and boolean expression evaluation.
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError


def print_tree(node, level=0, prefix="Root: "):
    """
    Print a visual representation of the Abstract Syntax Tree.
    
    This function helps users understand how MiniPyLang parses expressions
    by showing the tree structure that represents operator precedence and
    grouping relationships.
    """
    if node is None:
        return
    
    indent = "  " * level
    print(f"{indent}{prefix}{node}")
    
    if hasattr(node, 'left') and hasattr(node, 'right'):
        print_tree(node.left, level + 1, "L── ")
        print_tree(node.right, level + 1, "R── ")
    elif hasattr(node, 'operand'):
        print_tree(node.operand, level + 1, "└── ")


def evaluate_expression_with_tree(expression_text, show_tree=False):
    """
    Evaluate a MiniPyLang expression and optionally display its parse tree.
    
    This function demonstrates the complete pipeline of language processing:
    lexical analysis, parsing, and interpretation.
    """
    print(f"\nExpression: {expression_text}")
    print("-" * (len(expression_text) + 12))
    
    try:
        # Step 1: Lexical Analysis - Convert text into tokens
        lexer = Lexer(expression_text)
        
        # Optional: Show the tokenization process for educational purposes
        if show_tree:
            print("Tokens:")
            temp_lexer = Lexer(expression_text)
            tokens = []
            while True:
                token = temp_lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            print("  " + " → ".join(str(token) for token in tokens))
            print()
        
        # Step 2: Parsing - Build Abstract Syntax Tree from tokens
        parser = Parser(lexer)
        ast = parser.parse()
        
        # Step 3: Show tree structure to illustrate parsing decisions
        if show_tree:
            print("Abstract Syntax Tree:")
            print_tree(ast)
            print()
        
        # Step 4: Interpretation - Execute the parsed expression
        interpreter = Interpreter()
        result = interpreter.interpret(ast)
        
        print(f"Result: {result}")
        return result
        
    except (LexerError, ParseError, InterpreterError) as e:
        print(f"MiniPyLang Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in MiniPyLang: {e}")
        return None


def interactive_mode():
    """
    Run MiniPyLang in interactive mode for exploration and learning.
    
    Interactive mode allows users to experiment with expressions immediately,
    making it an excellent tool for understanding language concepts.
    """
    print("=== MiniPyLang Interactive Interpreter ===")
    print("An educational programming language for arithmetic and boolean expressions")
    print()
    print("Type expressions to see their parse trees and results.")
    print("Commands:")
    print("  'tree on' or 'tree off' - toggle tree display")
    print("  'quit' or 'exit' - exit MiniPyLang")
    print("  'help' - show this help message")
    print("  'about' - learn about MiniPyLang")
    print()
    
    show_tree = True  # Start with educational tree display enabled
    
    while True:
        try:
            # Use the distinctive MiniPyLang prompt
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands that make the language more user-friendly
            if user_input.lower() in ['quit', 'exit']:
                print("Thank you for using MiniPyLang!")
                break
            elif user_input.lower() == 'tree on':
                show_tree = True
                print("Parse tree display enabled - you'll see how expressions are structured")
                continue
            elif user_input.lower() == 'tree off':
                show_tree = False
                print("Parse tree display disabled - showing results only")
                continue
            elif user_input.lower() == 'help':
                print("\nMiniPyLang Commands:")
                print("  'tree on' or 'tree off' - toggle parse tree visualization")
                print("  'quit' or 'exit' - exit the interpreter")
                print("  'about' - information about MiniPyLang")
                print("  Or type any arithmetic or boolean expression!")
                print("\nExample expressions:")
                print("  5 + 3 * 2")
                print("  (10 > 5) and true")
                print("  !(false or (3 < 1))")
                print()
                continue
            elif user_input.lower() == 'about':
                print("\nAbout MiniPyLang:")
                print("MiniPyLang is an educational programming language designed to demonstrate")
                print("fundamental concepts in language implementation, including:")
                print("  • Lexical analysis and tokenization")
                print("  • Recursive descent parsing")
                print("  • Abstract syntax tree construction")
                print("  • Tree-walking interpretation")
                print("  • Operator precedence and associativity")
                print("  • Type checking and error handling")
                print()
                print("It supports arithmetic expressions, boolean logic, and comparisons")
                print("with proper operator precedence and comprehensive error reporting.")
                print()
                continue
            
            # Process the user's MiniPyLang expression
            evaluate_expression_with_tree(user_input, show_tree)
            
        except KeyboardInterrupt:
            print("\nThank you for using MiniPyLang!")
            break
        except EOFError:
            print("\nThank you for using MiniPyLang!")
            break


def process_file_with_trees(filename, show_trees=False):
    """
    Process a file containing MiniPyLang expressions.
    
    File processing mode is ideal for testing multiple expressions
    and demonstrating language capabilities systematically.
    """
    try:
        with open(filename, 'r') as file:
            line_number = 0
            
            print(f"Processing MiniPyLang expressions from: {filename}")
            print("=" * 60)
            
            for line in file:
                line_number += 1
                line = line.strip()
                
                # Skip empty lines and comments (lines starting with #)
                if not line or line.startswith('#'):
                    continue
                
                print(f"\nLine {line_number}")
                result = evaluate_expression_with_tree(line, show_trees)
                
    except FileNotFoundError:
        print(f"MiniPyLang Error: File '{filename}' not found.")
        print("Please check the filename and try again.")
        sys.exit(1)
    except IOError as e:
        print(f"MiniPyLang Error: Cannot read file '{filename}': {e}")
        sys.exit(1)


def main():
    """
    MiniPyLang main entry point with comprehensive command-line interface.
    
    This function demonstrates professional command-line tool design
    with clear help messages and multiple operation modes.
    """
    
    if len(sys.argv) == 1:
        # No arguments - start interactive mode for exploration
        interactive_mode()
    
    elif len(sys.argv) == 2:
        argument = sys.argv[1]
        
        if argument in ['-h', '--help']:
            print("MiniPyLang - Educational Programming Language Interpreter")
            print("=" * 55)
            print()
            print("MiniPyLang is designed to demonstrate fundamental concepts")
            print("in programming language implementation through a clean,")
            print("understandable codebase supporting arithmetic and boolean expressions.")
            print()
            print("Usage:")
            print("  python main.py                    # Interactive mode")
            print("  python main.py <file>             # Process file")
            print("  python main.py <file> --tree      # Process file with parse trees")
            print("  python main.py --interactive      # Force interactive mode")
            print("  python main.py --version          # Show version information")
            print()
            print("In interactive mode, you can see parse trees and experiment")
            print("with expressions to understand how the language works.")
            return
        
        elif argument == '--version':
            print("MiniPyLang Version 1.0")
            print("Educational Programming Language Interpreter")
            print("Supports arithmetic expressions and boolean logic")
            return
        
        elif argument == '--interactive':
            interactive_mode()
            return
        
        # Process file without parse trees for clean output
        process_file_with_trees(argument, show_trees=False)
    
    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        flag = sys.argv[2]
        
        if flag == '--tree':
            # Process file with parse trees for educational insight
            process_file_with_trees(filename, show_trees=True)
        else:
            print(f"MiniPyLang Error: Unknown option '{flag}'")
            print("Use --tree to show parse trees, or -h for help.")
            sys.exit(1)
    
    else:
        print("MiniPyLang Error: Too many arguments.")
        print("Use 'python main.py -h' for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()