"""
main.py - Complete Stage 5 MiniPyLang interface

Provides both interactive and file-based execution with optional
educational features for learning about control flow implementation.
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError


def print_tree(node, level=0, prefix="Root: "):
    """
    Print AST tree structure for educational purposes.
    
    Shows how MiniPyLang parses and structures programs including control flow.
    """
    if node is None:
        return
    
    indent = "  " * level
    print(f"{indent}{prefix}{node}")
    
    # Handle different node types
    if hasattr(node, 'statements'):
        # Program or Block node - show all statements
        for i, stmt in enumerate(node.statements):
            print_tree(stmt, level + 1, f"Stmt{i+1}: ")
    elif hasattr(node, 'condition') and hasattr(node, 'then_block'):
        # If statement - show condition and branches
        print_tree(node.condition, level + 1, "Condition: ")
        print_tree(node.then_block, level + 1, "Then: ")
        if hasattr(node, 'else_block') and node.else_block:
            print_tree(node.else_block, level + 1, "Else: ")
    elif hasattr(node, 'condition') and hasattr(node, 'body'):
        # While loop - show condition and body
        print_tree(node.condition, level + 1, "Condition: ")
        print_tree(node.body, level + 1, "Body: ")
    elif hasattr(node, 'left') and hasattr(node, 'right'):
        # Binary operation - show left and right
        print_tree(node.left, level + 1, "L── ")
        print_tree(node.right, level + 1, "R── ")
    elif hasattr(node, 'operand'):
        # Unary operation - show operand
        print_tree(node.operand, level + 1, "└── ")
    elif hasattr(node, 'expression'):
        # Assignment, print, or conversion - show expression
        if hasattr(node, 'variable_name'):
            print_tree(node.expression, level + 1, f"Value: ")
        elif hasattr(node, 'conversion_type'):
            print_tree(node.expression, level + 1, f"Convert: ")
        else:
            print_tree(node.expression, level + 1, "Expr: ")
    elif hasattr(node, 'prompt_expression') and node.prompt_expression:
        # Input with prompt
        print_tree(node.prompt_expression, level + 1, "Prompt: ")


def execute_program_with_tree(program_text, show_tree=False, interpreter=None):
    """
    Execute MiniPyLang program with optional educational features.
    
    Args:
        program_text (str): The program source code
        show_tree (bool): Whether to show parsing details
        interpreter (Interpreter): Existing interpreter for persistent variables
    
    Returns:
        Interpreter: The interpreter instance after execution
    """
    if interpreter is None:
        interpreter = Interpreter()
    
    # Show program being executed
    print(f"\nProgramme:")
    for i, line in enumerate(program_text.strip().split('\n'), 1):
        if line.strip() and not line.strip().startswith('#'):
            print(f"  {i}: {line}")
    print("-" * 50)
    
    try:
        # Step 1: Lexical Analysis
        lexer = Lexer(program_text)
        
        # Optional: Show tokens for educational purposes
        if show_tree:
            print("Tokens:")
            temp_lexer = Lexer(program_text)
            tokens = []
            while True:
                token = temp_lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            # Filter out newlines for cleaner display
            meaningful_tokens = [token for token in tokens if token.type != 'NEWLINE']
            print("  " + " → ".join(str(token) for token in meaningful_tokens))
            print()
        
        # Step 2: Parsing
        parser = Parser(lexer)
        ast = parser.parse()
        
        # Optional: Show parse tree structure
        if show_tree:
            print("Abstract Syntax Tree:")
            print_tree(ast)
            print()
        
        # Step 3: Execution
        result = interpreter.interpret(ast)
        
        # Show final result for expressions
        if result is not None:
            print(f"Result: {result}")
        
        # Add spacing for readability
        if not show_tree:
            print()
        
        return interpreter
        
    except (LexerError, ParseError, InterpreterError) as e:
        print(f"MiniPyLang Error: {e}")
        return interpreter
    except Exception as e:
        print(f"Unexpected error: {e}")
        return interpreter


def interactive_mode():
    """
    Interactive REPL with persistent variables and educational features.
    """
    print("=== MiniPyLang Interactive Interpreter ===")
    print("Stage 5: Control Flow Programming")
    print()
    print("Type statements to build programmes with variables and control flow.")
    print("Commands:")
    print("  'tree on' or 'tree off' - toggle educational tree display")
    print("  'vars' - show current variables")
    print("  'clear' - clear all variables")
    print("  'quit' or 'exit' - exit MiniPyLang")
    print("  'help' - show this help message")
    print()
    print("Educational tree display is OFF by default. Use 'tree on' to see")
    print("tokenisation and parse tree details for learning purposes.")
    print()
    print("NEW in Stage 5:")
    print("  • if (condition) { statements }")
    print("  • if (condition) { statements } else { statements }")
    print("  • while (condition) { statements }")
    print("  • input() and input(\"prompt\") for user interaction")
    print()
    
    # Default to clean output mode
    show_tree = False
    interpreter = Interpreter()  # Persistent interpreter
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("Thank you for using MiniPyLang!")
                break
                
            elif user_input.lower() == 'tree on':
                show_tree = True
                print("Educational tree display ENABLED")
                print("You will now see tokenisation and parse tree details.")
                continue
                
            elif user_input.lower() == 'tree off':
                show_tree = False
                print("Educational tree display DISABLED")
                print("You will now see clean programme execution results.")
                continue
                
            elif user_input.lower() == 'vars':
                variables = interpreter.get_environment_state()
                if variables:
                    print("Current variables:")
                    for name, value in variables.items():
                        if isinstance(value, str):
                            print(f"  {name} = \"{value}\"")
                        else:
                            print(f"  {name} = {value}")
                else:
                    print("No variables defined")
                continue
                
            elif user_input.lower() == 'clear':
                interpreter.reset_environment()
                print("All variables cleared")
                continue
                
            elif user_input.lower() == 'help':
                print("\nMiniPyLang Stage 5 Commands:")
                print("  'tree on' - enable educational token and parse tree display")
                print("  'tree off' - disable educational display (default)")
                print("  'vars' - show all current variables and their values")
                print("  'clear' - clear all variables from memory")
                print("  'quit' or 'exit' - exit the interpreter")
                print()
                print("Example statements:")
                print("  x = 5")
                print("  if (x > 0) { print \"positive\" }")
                print("  while (x > 0) { print x; x = x - 1 }")
                print("  name = input(\"Enter your name: \")")
                print("  if (name == \"Alice\") { print \"Hello Alice!\" } else { print \"Hello stranger!\" }")
                print()
                print("Control flow features:")
                print("  • Conditions in parentheses: (x > 5)")
                print("  • Code blocks with braces: { statement1; statement2 }")
                print("  • Nested if statements and loops are supported")
                print("  • Use input() to get user input interactively")
                print()
                print("The 'tree on' command reveals how MiniPyLang processes")
                print("control flow internally - ideal for learning about parsers!")
                continue
            
            # Execute user's program
            interpreter = execute_program_with_tree(user_input, show_tree, interpreter)
            
        except KeyboardInterrupt:
            print("\nThank you for using MiniPyLang!")
            break
        except EOFError:
            print("\nThank you for using MiniPyLang!")
            break


def process_file_with_programs(filename, show_trees=False):
    """
    Process file-based programs with optional educational features.
    
    Args:
        filename (str): Name of file to execute
        show_trees (bool): Whether to show educational features
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()
            
        print(f"Processing MiniPyLang programme from: {filename}")
        print("=" * 60)
        
        # Execute entire file as one program
        interpreter = Interpreter()
        execute_program_with_tree(content, show_trees, interpreter)
        
        # Show final program state
        variables = interpreter.get_environment_state()
        if variables:
            print("Final variable state:")
            for name, value in variables.items():
                if isinstance(value, str):
                    print(f"  {name} = \"{value}\"")
                else:
                    print(f"  {name} = {value}")
        
    except FileNotFoundError:
        print(f"MiniPyLang Error: File '{filename}' not found.")
        print("Please check the filename and path.")
        sys.exit(1)
    except IOError as e:
        print(f"MiniPyLang Error: Cannot read file '{filename}': {e}")
        sys.exit(1)


def main():
    """
    Main function with command-line interface.
    """
    if len(sys.argv) == 1:
        # No arguments - start interactive mode
        interactive_mode()
        
    elif len(sys.argv) == 2:
        argument = sys.argv[1]
        
        if argument in ['-h', '--help']:
            print("MiniPyLang Stage 5 - Programming Language with Control Flow")
            print("=" * 65)
            print()
            print("A clean, educational programming language supporting variables,")
            print("assignments, control flow, and interactive programming.")
            print()
            print("Usage:")
            print("  python main.py                    # Interactive mode (clean output)")
            print("  python main.py <file>             # Execute programme file (clean output)")
            print("  python main.py <file> --tree      # Execute with educational tree display")
            print("  python main.py --interactive      # Force interactive mode")
            print()
            print("Stage 5 features:")
            print("  • Variable assignment: x = 5")
            print("  • Variable usage in expressions: y = x + 3")
            print("  • Print statements: print y")
            print("  • Conditional statements: if (x > 0) { print \"positive\" }")
            print("  • Optional else clauses: if (x > 0) { ... } else { ... }")
            print("  • While loops: while (x > 0) { print x; x = x - 1 }")
            print("  • User input: name = input(\"Enter name: \")")
            print("  • Nested control structures supported")
            print("  • Type conversion functions: str(), int(), float(), bool()")
            print("  • Educational parse tree visualisation (optional)")
            print()
            print("Control flow syntax:")
            print("  • Conditions must be in parentheses: (condition)")
            print("  • Code blocks use braces: { statement1; statement2 }")
            print("  • Single statements don't require braces")
            print("  • Nested structures are fully supported")
            print()
            print("Educational features:")
            print("  In interactive mode, use 'tree on' to see how MiniPyLang")
            print("  processes control flow internally. Use 'tree off' to return")
            print("  to clean output mode.")
            return
            
        elif argument == '--interactive':
            interactive_mode()
            return
        
        # Process file with clean output by default
        process_file_with_programs(argument, show_trees=False)
        
    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        flag = sys.argv[2]
        
        if flag == '--tree':
            # Enable educational tree display
            process_file_with_programs(filename, show_trees=True)
        else:
            print(f"MiniPyLang Error: Unknown option '{flag}'")
            print("Use --tree to enable educational tree display.")
            print("Use -h for complete help information.")
            sys.exit(1)
            
    else:
        print("MiniPyLang Error: Too many arguments.")
        print("Use 'python main.py -h' for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()