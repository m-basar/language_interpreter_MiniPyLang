"""
main.py - Enhanced MiniPyLang with user-controlled tree visualisation

This version implements a more refined user experience where educational
features like token display and parse tree visualisation are available
when requested but do not clutter the default programme execution experience.
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError


def print_tree(node, level=0, prefix="Root: "):
    """
    Enhanced tree printing that handles all Stage 4 node types.
    
    This function provides detailed visualisation of how MiniPyLang
    parses and structures programmes, which is invaluable for learning
    about language implementation but optional for everyday use.
    """
    if node is None:
        return
    
    indent = "  " * level
    print(f"{indent}{prefix}{node}")
    
    # Handle different node types and their hierarchical structure
    if hasattr(node, 'statements'):
        # ProgramNode - show all statements with clear numbering
        for i, stmt in enumerate(node.statements):
            print_tree(stmt, level + 1, f"Stmt{i+1}: ")
    elif hasattr(node, 'left') and hasattr(node, 'right'):
        # BinaryOperationNode - show left and right operands
        print_tree(node.left, level + 1, "L── ")
        print_tree(node.right, level + 1, "R── ")
    elif hasattr(node, 'operand'):
        # UnaryOperationNode - show the single operand
        print_tree(node.operand, level + 1, "└── ")
    elif hasattr(node, 'expression'):
        # AssignmentNode or PrintNode - show the expression being processed
        if hasattr(node, 'variable_name'):
            print_tree(node.expression, level + 1, f"Value: ")
        else:
            print_tree(node.expression, level + 1, "Expr: ")


def execute_program_with_tree(program_text, show_tree=False, interpreter=None):
    """
    Execute a MiniPyLang programme with optional educational features.
    
    This function demonstrates the progressive disclosure principle:
    basic execution is clean and focused, while educational features
    like tokenisation and parse tree display are available when requested.
    
    The show_tree parameter controls whether we display the internal
    processing details or just the programme results.
    """
    if interpreter is None:
        interpreter = Interpreter()
    
    # Always show the programme being executed for context
    print(f"\nProgramme:")
    for i, line in enumerate(program_text.strip().split('\n'), 1):
        if line.strip() and not line.strip().startswith('#'):
            print(f"  {i}: {line}")
    print("-" * 50)
    
    try:
        # Step 1: Lexical Analysis
        lexer = Lexer(program_text)
        
        # Optional: Show tokenisation details only when educational mode is enabled
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
        
        # Optional: Show parse tree structure only when educational mode is enabled
        if show_tree:
            print("Abstract Syntax Tree:")
            print_tree(ast)
            print()
        
        # Step 3: Programme Execution (always happens)
        result = interpreter.interpret(ast)
        
        # Show final result for expressions (not statements)
        if result is not None:
            print(f"Result: {result}")
        
        # Add spacing between programme executions for readability
        if not show_tree:
            print()  # Minimal spacing when not showing trees
        
        return interpreter
        
    except (LexerError, ParseError, InterpreterError) as e:
        print(f"MiniPyLang Error: {e}")
        return interpreter
    except Exception as e:
        print(f"Unexpected error: {e}")
        return interpreter


def interactive_mode():
    """
    Enhanced interactive mode with user-controlled educational features.
    
    This implementation demonstrates how to provide both beginner-friendly
    default behaviour and advanced educational features that users can
    enable when they want to learn about language internals.
    """
    print("=== MiniPyLang Interactive Interpreter ===")
    print("Stage 4: Programming with Variables and Statements")
    print()
    print("Type statements to build programmes with persistent variable storage.")
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
    
    # Default to clean output mode - educational features are opt-in
    show_tree = False
    interpreter = Interpreter()  # Persistent interpreter for variable storage
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            # Handle special commands with clear feedback
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
                print("\nMiniPyLang Stage 4 Commands:")
                print("  'tree on' - enable educational token and parse tree display")
                print("  'tree off' - disable educational display (default)")
                print("  'vars' - show all current variables and their values")
                print("  'clear' - clear all variables from memory")
                print("  'quit' or 'exit' - exit the interpreter")
                print()
                print("Example statements:")
                print("  x = 5")
                print("  y = x + 3")
                print("  print y")
                print("  message = \"Hello \" + \"World\"")
                print()
                print("The 'tree on' command reveals how MiniPyLang processes")
                print("your code internally - ideal for learning about parsers!")
                continue
            
            # Execute the user's programme with current tree display setting
            interpreter = execute_program_with_tree(user_input, show_tree, interpreter)
            
        except KeyboardInterrupt:
            print("\nThank you for using MiniPyLang!")
            break
        except EOFError:
            print("\nThank you for using MiniPyLang!")
            break


def process_file_with_programs(filename, show_trees=False):
    """
    Process file-based programmes with optional educational features.
    
    This function maintains the same progressive disclosure principle
    for file-based execution: clean results by default, with educational
    features available through command-line flags.
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()
            
        print(f"Processing MiniPyLang programme from: {filename}")
        print("=" * 60)
        
        # Execute the entire file as one cohesive programme
        interpreter = Interpreter()
        execute_program_with_tree(content, show_trees, interpreter)
        
        # Show final programme state for educational value
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
    Enhanced main function implementing progressive disclosure of features.
    
    This implementation demonstrates how command-line interfaces should
    provide sensible defaults while making advanced features easily
    accessible through clear, memorable flags and commands.
    """
    if len(sys.argv) == 1:
        # No arguments - start interactive mode with clean defaults
        interactive_mode()
        
    elif len(sys.argv) == 2:
        argument = sys.argv[1]
        
        if argument in ['-h', '--help']:
            print("MiniPyLang Stage 4 - Programming Language with Variables")
            print("=" * 60)
            print()
            print("A clean, educational programming language supporting variables,")
            print("assignments, and multi-statement programmes.")
            print()
            print("Usage:")
            print("  python main.py                    # Interactive mode (clean output)")
            print("  python main.py <file>             # Execute programme file (clean output)")
            print("  python main.py <file> --tree      # Execute with educational tree display")
            print("  python main.py --interactive      # Force interactive mode")
            print()
            print("Stage 4 features:")
            print("  • Variable assignment: x = 5")
            print("  • Variable usage in expressions: y = x + 3")
            print("  • Print statements: print y")
            print("  • Multi-statement programmes with comments")
            print("  • Educational parse tree visualisation (optional)")
            print()
            print("Educational features:")
            print("  In interactive mode, use 'tree on' to see how MiniPyLang")
            print("  processes your code internally. Use 'tree off' to return")
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
            # Enable educational tree display for file processing
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
