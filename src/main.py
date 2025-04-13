import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

def interactive_mode():
    """
    Run the interpreter in interactive mode.
    User can type expressions and see results immediately.
    """
    print("Interactive Mode - Custom Language Interpreter")
    print("Type 'exit' to quit")
    
    while True:
        try:
            expr = input('> ')
            if expr.lower() == 'exit':
                break
                
            if not expr.strip():  # Skip empty lines
                continue
                
            lexer = Lexer(expr)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """
    Main function that runs the interpreter on a given source file
    or starts interactive mode if no file is provided.
    """
    if len(sys.argv) == 1:
        # No arguments provided, run in interactive mode
        interactive_mode()
        return
        
    if len(sys.argv) != 2:
        print("Usage: python main.py [source_file]")
        print("       python main.py (for interactive mode)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        with open(file_path, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    try:
        # Process each line separately
        lines = source_code.strip().split('\n')
        for line_num, line in enumerate(lines, 1):
            if not line.strip():  # Skip empty lines
                continue
                
            try:
                lexer = Lexer(line)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                interpreter = Interpreter(parser)
                result = interpreter.interpret()
                print(f"Line {line_num}: {line} = {result}")
            except Exception as e:
                print(f"Error on line {line_num}: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()