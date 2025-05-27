README.txt - MiniPyLang Usage Guide
====================================

OVERVIEW:
MiniPyLang is a complete programming language interpreter supporting:
- Arithmetic and boolean expressions
- String operations and text manipulation
- Variables and assignments
- Control flow (if/else, while loops)
- Data structures (lists and dictionaries)
- Built-in functions and type conversions
- Interactive programming environment

USAGE:

1. INTERACTIVE MODE:
   python main.py
   
   Starts the interactive interpreter where you can type statements directly.
   
   Special commands in interactive mode:
   - 'tree on'  - Enable parse tree display for educational purposes
   - 'tree off' - Disable tree display (default)
   - 'vars'     - Show all current variables
   - 'clear'    - Clear all variables
   - 'help'     - Show help information
   - 'quit'     - Exit the interpreter

2. FILE MODE:
   python main.py filename.minipy
   
   Executes a MiniPyLang programme from a file.

3. EDUCATIONAL MODE:
   python main.py filename.minipy --tree
   
   Executes file with parse tree display enabled.

LANGUAGE SYNTAX:

Variables:
   myVar = 42
   name = "Alice"
   isReady = true

Arithmetic:
   result = (10 + 5) * 2 - 3
   average = (a + b + c) / 3

Strings:
   greeting = "Hello " + "World"
   message = "Number: " + str(42)

Booleans:
   isEqual = (5 == 5)
   canProceed = (age >= 18) and (hasPermission == true)

Lists:
   numbers = [1, 2, 3, 4, 5]
   mixed = [1, "hello", true, 3.14]
   item = numbers[0]
   numbers[1] = 10
   append(numbers, 6)
   removed = remove(numbers, 2)
   size = len(numbers)

Dictionaries:
   person = {"name": "Bob", "age": 25, "city": "London"}
   name = person["name"]
   person["phone"] = "123-456-7890"
   allKeys = keys(person)
   allValues = values(person)
   exists = has_key(person, "email")
   deleted = del_key(person, "age")

Control Flow:
   if (condition) {
       # statements
   } else {
       # statements
   }
   
   while (condition) {
       # statements
   }

Built-in Functions:
   print expression        # Display values
   input("prompt")         # Get user input
   str(value)             # Convert to string
   int(value)             # Convert to integer
   float(value)           # Convert to float
   bool(value)            # Convert to boolean
   len(collection)        # Get length
   del variableName       # Delete variable

EXAMPLES:
See the provided example files:
- example1.minipy: Basic arithmetic and expressions
- example2.minipy: Variables and control flow
- example3.minipy: String operations and functions
- example4.minipy: List operations and manipulation
- example5.minipy: Dictionary operations and complex programme

LANGUAGE FEATURES:
- Dynamic typing with type safety
- Proper operator precedence
- Nested expressions and control structures
- Comprehensive error messages
- Memory management with variable environments
- Support for negative array indexing
- Heterogeneous collections (mixed-type lists/dictionaries)
- Interactive development environment

ERROR HANDLING:
The interpreter provides detailed error messages including:
- Syntax errors with line numbers
- Type mismatch errors
- Undefined variable errors
- Index out of bounds errors
- Division by zero protection
- Invalid operation errors

EDUCATIONAL FEATURES:
Use 'tree on' in interactive mode to see:
- How expressions are tokenised
- Abstract syntax tree structure
- Step-by-step programme execution
- Internal language processing

This helps understand how programming languages work internally.