"""
main.py - Enhanced MiniPyLang interpreter supporting Stage 4 programs

The main program now handles multi-statement execution with proper
variable management and enhanced user feedback. The shift from expression
evaluation to program execution represents a fundamental change in how
we think about language processing.
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError


def print_tree(node, level=0, prefix="Root: "):
    """Enhanced tree printing that handles all Stage 4 node types"""
    if node is None:
        return
    
    indent = "  " * level
    print(f"{indent}{prefix}{node}")
    
    # Handle different node types and their structure
    if hasattr(node, 'statements'):
        # ProgramNode - show all statements
        for i, stmt in enumerate(node.statements):
            print_tree(stmt, level + 1, f"Stmt{i+1}: ")
    elif hasattr(node, 'left') and hasattr(node, 'right'):
        # BinaryOperationNode
        print_tree(node.left, level + 1, "L── ")
        print_tree(node.right, level + 1, "R── ")
    elif hasattr(node, 'operand'):
        # UnaryOperationNode
        print_tree(node.operand, level + 1, "└── ")
    elif hasattr(node, 'expression'):
        # AssignmentNode or PrintNode
        if hasattr(node, 'variable_name'):
            print_tree(node.expression, level + 1, f"Value: ")
        else:
            print_tree(node.expression, level + 1, "Expr: ")


def execute_program_with_tree(program_text, show_tree=False, interpreter=None):
    """
    Execute a MiniPyLang program with optional tree visualization.
    
    This function handles the complete pipeline of program execution:
    lexical analysis, parsing, and interpretation with comprehensive
    error handling and user feedback.
    """
    if interpreter is None:
        interpreter = Interpreter()
    
    print(f"\nProgram:")
    for i, line in enumerate(program_text.strip().split('\n'), 1):
        if line.strip():
            print(f"  {i}: {line}")
    print("-" * 50)
    
    try:
        # Step 1: Lexical Analysis
        lexer = Lexer(program_text)
        
        # Optional: Show tokenization for educational purposes
        if show_tree:
            print("Tokens:")
            temp_lexer = Lexer(program_text)
            tokens = []
            while True:
                token = temp_lexer.get_next_token()
                tokens.append(token)
                if token.type == 'EOF':
                    break
            print("  " + " → ".join(str(token) for token in tokens if token.type != 'NEWLINE'))
            print()
        
        # Step 2: Parsing
        parser = Parser(lexer)
        ast = parser.parse()
        
        # Step 3: Show tree structure if requested
        if show_tree:
            print("Abstract Syntax Tree:")
            print_tree(ast)
            print()
        
        # Step 4: Program Execution
        result = interpreter.interpret(ast)
        
        # Show final result if it's an expression (not a statement)
        if result is not None:
            print(f"Result: {result}")
        
        print()  # Add spacing between programs
        return interpreter
        
    except (LexerError, ParseError, InterpreterError) as e:
        print(f"MiniPyLang Error: {e}")
        return interpreter
    except Exception as e:
        print(f"Unexpected error: {e}")
        return interpreter


def interactive_mode():
    """Enhanced interactive mode supporting programs and variables"""
    print("=== MiniPyLang Interactive Interpreter ===")
    print("Stage 4: Programming with Variables and Statements")
    print()
    print("Type statements to build programs with persistent variable storage.")
    print("Commands:")
    print("  'tree on' or 'tree off' - toggle tree display")
    print("  'vars' - show current variables")
    print("  'clear' - clear all variables")
    print("  'quit' or 'exit' - exit MiniPyLang")
    print("  'help' - show this help message")
    print()
    
    show_tree = True
    interpreter = Interpreter()  # Persistent interpreter for variable storage
    
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
                print("Parse tree display enabled")
                continue
            elif user_input.lower() == 'tree off':
                show_tree = False
                print("Parse tree display disabled")
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
                print("  'tree on' or 'tree off' - toggle parse tree visualization")
                print("  'vars' - show all current variables")
                print("  'clear' - clear all variables")
                print("  'quit' or 'exit' - exit the interpreter")
                print("\nExample statements:")
                print("  x = 5")
                print("  y = x + 3")
                print("  print y")
                print("  message = \"Hello \" + \"World\"")
                print()
                continue
            
            # Execute the user's program
            interpreter = execute_program_with_tree(user_input, show_tree, interpreter)
            
        except KeyboardInterrupt:
            print("\nThank you for using MiniPyLang!")
            break
        except EOFError:
            print("\nThank you for using MiniPyLang!")
            break


def process_file_with_programs(filename, show_trees=False):
    """Process a file containing MiniPyLang programs"""
    try:
        with open(filename, 'r') as file:
            content = file.read()
            
        print(f"Processing MiniPyLang program from: {filename}")
        print("=" * 60)
        
        # Execute the entire file as one program
        interpreter = Interpreter()
        execute_program_with_tree(content, show_trees, interpreter)
        
        # Show final variable state
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
        sys.exit(1)
    except IOError as e:
        print(f"MiniPyLang Error: Cannot read file '{filename}': {e}")
        sys.exit(1)


def main():
    """Enhanced main function supporting Stage 4 capabilities"""
    if len(sys.argv) == 1:
        interactive_mode()
    elif len(sys.argv) == 2:
        argument = sys.argv[1]
        
        if argument in ['-h', '--help']:
            print("MiniPyLang Stage 4 - Programming Language with Variables")
            print("=" * 60)
            print()
            print("Now supporting variables, assignments, and multi-statement programs!")
            print()
            print("Usage:")
            print("  python main.py                    # Interactive mode")
            print("  python main.py <file>             # Execute program file")
            print("  python main.py <file> --tree      # Execute with parse trees")
            print()
            print("New Stage 4 features:")
            print("  • Variable assignment: x = 5")
            print("  • Variable usage: y = x + 3")
            print("  • Print statements: print y")
            print("  • Multi-statement programs")
            return
        elif argument == '--interactive':
            interactive_mode()
            return
        
        process_file_with_programs(argument, show_trees=False)
    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        flag = sys.argv[2]
        
        if flag == '--tree':
            process_file_with_programs(filename, show_trees=True)
        else:
            print(f"MiniPyLang Error: Unknown option '{flag}'")
            sys.exit(1)
    else:
        print("MiniPyLang Error: Too many arguments.")
        print("Use 'python main.py -h' for help.")
        sys.exit(1)


if __name__ == "__main__":
    main()