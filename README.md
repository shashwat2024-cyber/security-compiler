# Security Compiler

A compiler-design-based static security analyzer for a restricted C-like language. It demonstrates lexical analysis, syntax parsing, AST construction, intermediate representation, control-flow analysis, call graphs, and taint-based security checks through a Flask web interface.

## Features

- **Lexical analysis:** identifies tokens and source locations.
- **Syntax analysis:** parses supported C-like program syntax.
- **Abstract Syntax Tree (AST):** displays the parsed program structure.
- **Intermediate Representation (IR):** presents simplified compiler instructions.
- **Control-Flow Graph (CFG):** represents basic blocks and their successors.
- **Call Graph:** displays caller-to-callee relationships.
- **Taint analysis:** tracks selected input sources through assignments to selected unsafe calls.
- **Security rules:** reports potential issues such as unsafe `strcpy` and `system` usage.
- **Security report:** includes severity, source line, explanation, and recommendations.
- **Web interface:** supports source analysis, filtering, and JSON report export.

## Technology Stack

- Python
- PLY (Python Lex-Yacc)
- Flask
- HTML, CSS, and JavaScript
- pytest

## Requirements

- Python 3.10 or later
- pip

## Setup on Windows

Clone the repository and open its directory in PowerShell.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install Flask ply pytest
```

Run the application:

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Run Tests

```powershell
python -m pytest -q
```

## Example

The included `sample.c` demonstrates input being read, assigned to another variable, and passed to `strcpy`.

The analyzer can flag the potentially unsafe call and, when supported by the analysis, report the destination buffer's declared capacity.

## Architecture

1. Source code input
2. Lexer and token stream
3. Parser and Abstract Syntax Tree
4. Intermediate Representation
5. Control-Flow Graph and Call Graph
6. Taint analysis and security rules
7. Structured report and web interface

## Limitations

This project supports a restricted C-like language, not the complete C standard. Its taint analysis is intentionally limited and does not comprehensively model branches, loops, or interprocedural data flow. A declared buffer size alone does not establish whether an overflow occurs; the source length and runtime behavior also matter.

The findings are potential security warnings intended for educational analysis, not proof of exploitability.

## Academic Purpose

Developed as a Compiler Design project to demonstrate how compiler stages can support basic static security analysis.
