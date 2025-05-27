"""
main.py - Complete Stage 6 MiniPyLang interface with List support

Provides both interactive and file-based execution with optional
tree features for learning about list implementation.
"""

import sys
from lexer import Lexer, LexerError
from parser import Parser, ParseError
from interpreter import Interpreter, InterpreterError


def print_tree(node, level=0, prefix="Root: "):
    """
    Print AST tree structure.
    
    Shows how MiniPyLang parses and structures programmes including lists.
    """
    if node is None:
        return
    
    indent = "  " * level
    print(f"{indent}{prefix}{node}")
    
    # Handle different node types
    if hasattr(node, 'statements'):
        # Programme or Block node - show all statements
        for i, stmt in enumerate(node.statements):
            print_tree(stmt, level + 1, f"Stmt{i+1}: ")
    elif hasattr(node, 'elements'):
        # List node - show all elements
        for i, elem in enumerate(node.elements):
            print_tree(elem, level + 1, f"Elem{i}: ")
    elif hasattr(node, 'list_expression') and hasattr(node, 'index_expression'):
        # Index access or assignment - show list and index
        print_tree(node.list_expression, level + 1, "List: ")
        print_tree(node.index_expression, level + 1, "Index: ")
        if hasattr(node, 'value_expression'):
            print_tree(node.value_expression, level + 1, "Value: ")
    elif hasattr(node, 'arguments'):
        # Function call - show all arguments
        for i, arg in enumerate(node.arguments):
            print_tree(arg, level + 1, f"Arg{i}: ")
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


def execute_programme_with_tree(programme_text, show_tree=False, interpreter=None):
    """
    Execute MiniPyLang programme with optional educational features.
    
    Args:
        programme_text (str): The programme source code
        show_tree (bool): Whether to show parsing details
        interpreter (Interpreter): Existing interpreter for persistent variables
    
    Returns:
        Interpreter: The interpreter instance after execution
    """
    if interpreter is None:
        interpreter = Interpreter()
    
    # Show programme being executed with dynamic context
    # Determine what type of code we're executing
    if any('=' in line and not '==' in line and not '!=' in line and not '<=' in line and not '>=' in line 
           for line in programme_text.split('\n') if line.strip()):
        print(f"\nExecuting Statements:")
    elif any(keyword in programme_text.lower() for keyword in ['if', 'while', 'else']):
        print(f"\nRunning Control Flow:")
    elif '[' in programme_text and ']' in programme_text:
        print(f"\nProcessing Lists:")
    elif any(func in programme_text.lower() for func in ['append', 'remove', 'len']):
        print(f"\nExecuting List Operations:")
    elif any(func in programme_text.lower() for func in ['str(', 'int(', 'float(', 'bool(']):
        print(f"\nPerforming Type Conversions:")
    elif 'input(' in programme_text.lower():
        print(f"\nRunning Interactive Code:")
    elif 'print' in programme_text.lower():
        print(f"\nExecuting Output Statements:")
    else:
        print(f"\nEvaluating Expressions:")
    
    for i, line in enumerate(programme_text.strip().split('\n'), 1):
        if line.strip() and not line.strip().startswith('#'):
            print(f"  {i}: {line}")
    print("-" * 50)
    
    try:
        # Step 1: Lexical Analysis
        lexer = Lexer(programme_text)
        
        # Optional: Show tokens for educational purposes
        if show_tree:
            print("Tokens:")
            temp_lexer = Lexer(programme_text)
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
    Interactive REPL with persistent variables and tree features.
    """
    print("=== MiniPyLang Interactive Interpreter ===")
    print("Stage 6: Programming with Lists")
    print()
    print("Type statements to build programmes with variables, control flow, and lists.")
    print("Commands:")
    print("  'tree on' or 'tree off' - toggle tree display")
    print("  'vars' - show current variables")
    print("  'clear' - clear all variables")
    print("  'quit' or 'exit' - exit MiniPyLang")
    print("  'help' - show this help message")
    print()
    print("Tree display is OFF by default. Use 'tree on' to see")
    print("tokenisation and parse tree details.")
    print()
    print("NEW in Stage 6:")
    print("  • List literals: [1, 2, 3, \"hello\"]")
    print("  • Index access: list[0], list[-1]")
    print("  • Index assignment: list[0] = \"new value\"")
    print("  • List functions: append(list, value), remove(list, index), len(list)")
    print("  • List concatenation: [1, 2] + [3, 4]")
    print("  • Mixed-type lists supported")
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
                print("Tree display ENABLED")
                print("You will now see tokenisation and parse tree details.")
                continue
                
            elif user_input.lower() == 'tree off':
                show_tree = False
                print("Tree display DISABLED")
                print("You will now see clean programme execution results.")
                continue
                
            elif user_input.lower() == 'vars':
                variables = interpreter.get_environment_state()
                if variables:
                    print("Current variables:")
                    for name, value in variables.items():
                        if isinstance(value, str):
                            print(f"  {name} = \"{value}\"")
                        elif isinstance(value, list):
                            # Format list display nicely
                            list_str = str(value).replace("'", '"')
                            print(f"  {name} = {list_str}")
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
                print("\nMiniPyLang Stage 6 Commands:")
                print("  'tree on' - enable token and parse tree display")
                print("  'tree off' - disable tree display (default)")
                print("  'vars' - show all current variables and their values")
                print("  'clear' - clear all variables from memory")
                print("  'quit' or 'exit' - exit the interpreter")
                print()
                print("Example statements:")
                print("  numbers = [1, 2, 3, 4, 5]")
                print("  print numbers[0]")
                print("  numbers[1] = 10")
                print("  append(numbers, 6)")
                print("  print \"Length: \" + str(len(numbers))")
                print("  mixed = [1, \"hello\", true, 3.14]")
                print("  fruits = [\"apple\", \"banana\", \"cherry\"]")
                print()
                print("List features:")
                print("  • Create: [element1, element2, element3]")
                print("  • Access: list[index] (supports negative indices)")
                print("  • Modify: list[index] = new_value")
                print("  • Append: append(list, value)")
                print("  • Remove: removed = remove(list, index)")
                print("  • Length: len(list)")
                print("  • Combine: list1 + list2")
                print()
                print("The 'tree on' command reveals how MiniPyLang processes")
                print("list operations internally - ideal for learning about parsers!")
                continue
            
            # Execute user's programme
            interpreter = execute_programme_with_tree(user_input, show_tree, interpreter)
            
        except KeyboardInterrupt:
            print("\nThank you for using MiniPyLang!")
            break
        except EOFError:
            print("\nThank you for using MiniPyLang!")
            break


def process_file_with_programmes(filename, show_trees=False):
    """
    Process file-based programmes with optional features.
    
    Args:
        filename (str): Name of file to execute
        show_trees (bool): Whether to show tree features
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()
            
        print(f"Processing MiniPyLang programme from: {filename}")
        print("=" * 60)
        
        # Execute entire file as one programme
        interpreter = Interpreter()
        execute_programme_with_tree(content, show_trees, interpreter)
        
        # Show final programme state
        variables = interpreter.get_environment_state()
        if variables:
            print("Final variable state:")
            for name, value in variables.items():
                if isinstance(value, str):
                    print(f"  {name} = \"{value}\"")
                elif isinstance(value, list):
                    # Format list display nicely
                    list_str = str(value).replace("'", '"')
                    print(f"  {name} = {list_str}")
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
            print("MiniPyLang Stage 6 - Programming Language with Lists")
            print("=" * 60)
            print()
            print("A clean, programming language supporting variables,")
            print("assignments, control flow, and list data structures.")
            print()
            print("Usage:")
            print("  python main.py                    # Interactive mode (clean output)")
            print("  python main.py <file>             # Execute programme file (clean output)")
            print("  python main.py <file> --tree      # Execute with tree display")
            print("  python main.py --interactive      # Force interactive mode")
            print()
            print("Stage 6 features (all previous stages plus):")
            print("  • List literals: [1, 2, 3, \"hello\", true]")
            print("  • Index access: list[0], list[-1]")
            print("  • Index assignment: list[0] = new_value")
            print("  • Back-insertion: append(list, value)")
            print("  • Random removal: remove(list, index)")
            print("  • Length function: len(list)")
            print("  • List concatenation: [1, 2] + [3, 4]")
            print("  • Mixed-type lists with proper equality")
            print("  • Integration with existing type system")
            print()
            print("List syntax:")
            print("  • Creation: my_list = [1, 2, 3]")
            print("  • Access: value = my_list[0]")
            print("  • Modify: my_list[1] = \"new\"")
            print("  • Append: append(my_list, \"item\")")
            print("  • Remove: removed = remove(my_list, 2)")
            print("  • Length: size = len(my_list)")
            print("  • Negative indexing: last = my_list[-1]")
            print()
            print("Educational features:")
            print("  In interactive mode, use 'tree on' to see how MiniPyLang")
            print("  processes list operations internally. Use 'tree off' to return")
            print("  to clean output mode.")
            return
            
        elif argument == '--interactive':
            interactive_mode()
            return
        
        # Process file with clean output by default
        process_file_with_programmes(argument, show_trees=False)
        
    elif len(sys.argv) == 3:
        filename = sys.argv[1]
        flag = sys.argv[2]
        
        if flag == '--tree':
            # Enable tree display
            process_file_with_programmes(filename, show_trees=True)
        else:
            print(f"MiniPyLang Error: Unknown option '{flag}'")
            print("Use --tree to enable tree display.")
            print("Use -h for complete help information.")
            sys.exit(1)
            
    else:
        print("MiniPyLang Error: Too many arguments.")
        print("Use 'python main.py -h' for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()