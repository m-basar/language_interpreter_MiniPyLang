# Custom Language Interpreter

This is a custom programming language interpreter created for the Language Design and Implementation module (6CC509).

## Language Features

The language currently supports the following features:

### Stage 1: Basic Calculator
- Arithmetic operations (addition, subtraction, multiplication, division)
- Parentheses for grouping
- Unary operators (positive, negative)
- Real number support (integers and floating-point)

## How to Use

### Running a Source File

To run a source file through the interpreter:

```
python src/main.py your_source_file.txt
```

### Language Syntax

#### Basic Arithmetic:

```
1 + 2          # Addition
3 - 4          # Subtraction
5 * 6          # Multiplication
7 / 8          # Division
-9             # Unary negation
(10 + 11) * 12 # Grouping with parentheses
```

### Example Files

The `examples/` directory contains several example files showing valid syntax for each stage of the language:

- `stage1_example1.txt`: Basic arithmetic operations

## Future Development

This language interpreter is under active development, with the following features planned:

- Boolean logic
- Text values
- Global variables
- Control flow structures
- Additional data structures and functions