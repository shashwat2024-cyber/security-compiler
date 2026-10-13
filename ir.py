
from dataclasses import dataclass, field

from ast_nodes import (
    Program,
    Function,
    VarDecl,
    ExprStmt,
    Call,
    Identifier,
    Number,
    String,
    Assignment,
    Return,
)


@dataclass
class IRInstruction:
    operation: str
    arguments: list = field(default_factory=list)
    line: int = 1


@dataclass
class IRFunction:
    name: str
    return_type: str
    instructions: list = field(default_factory=list)


@dataclass
class IRProgram:
    functions: list = field(default_factory=list)


def expression_to_ir(expression):
    """Convert an AST expression into a simple IR value."""
    if isinstance(expression, Identifier):
        return expression.name

    if isinstance(expression, Number):
        return expression.value

    if isinstance(expression, String):
        return expression.value

    if isinstance(expression, Call):
        return {
            "function": expression.name,
            "arguments": [
                expression_to_ir(arg)
                for arg in expression.arguments
            ],
        }

    if isinstance(expression, Assignment):
        return {
            "target": expression_to_ir(expression.target),
            "value": expression_to_ir(expression.value),
        }

    return str(expression)


def build_ir(ast):
    """Convert the AST into a simplified intermediate representation."""
    if not isinstance(ast, Program):
        raise TypeError("build_ir expects a Program AST")

    ir_program = IRProgram()

    for function in ast.functions:
        ir_function = IRFunction(
            name=function.name,
            return_type=function.return_type,
        )

        for statement in function.body:
            if isinstance(statement, VarDecl):
                ir_function.instructions.append(
                    IRInstruction(
                        operation="DECLARE",
                        arguments=[
                            statement.data_type,
                            statement.name,
                            statement.array_size,
                        ],
                        line=statement.line,
                    )
                )

            elif isinstance(statement, ExprStmt):
                ir_function.instructions.append(
                    IRInstruction(
                        operation="EXPRESSION",
                        arguments=[
                            expression_to_ir(statement.expression)
                        ],
                        line=statement.line,
                    )
                )

            elif isinstance(statement, Return):
                ir_function.instructions.append(
                    IRInstruction(
                        operation="RETURN",
                        arguments=[
                            expression_to_ir(statement.value)
                            if statement.value is not None
                            else None
                        ],
                        line=statement.line,
                    )
                )

        ir_program.functions.append(ir_function)

    return ir_program
