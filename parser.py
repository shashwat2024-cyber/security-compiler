
import ply.yacc as yacc

from lexer import tokens, lexer
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


start = "program"


def p_program(p):
    "program : function_list"
    p[0] = Program(functions=p[1])


def p_function_list_multiple(p):
    "function_list : function_list function"
    p[0] = p[1] + [p[2]]


def p_function_list_single(p):
    "function_list : function"
    p[0] = [p[1]]


def p_function(p):
    "function : type_spec IDENTIFIER LPAREN parameter_list_opt RPAREN LBRACE statement_list RBRACE"
    p[0] = Function(
        return_type=p[1],
        name=p[2],
        body=p[7],
        line=p.lineno(2),
    )


def p_parameter_list_opt(p):
    """parameter_list_opt : parameter_list
                          | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_parameter_list_multiple(p):
    "parameter_list : parameter_list COMMA parameter"
    p[0] = p[1] + [p[3]]


def p_parameter_list_single(p):
    "parameter_list : parameter"
    p[0] = [p[1]]


def p_parameter(p):
    "parameter : type_spec IDENTIFIER"
    p[0] = VarDecl(p[1], p[2], line=p.lineno(2))


def p_type_spec(p):
    """type_spec : INT
                 | CHAR
                 | VOID"""
    p[0] = p[1]


def p_statement_list_multiple(p):
    "statement_list : statement_list statement"
    p[0] = p[1] + [p[2]]


def p_statement_list_single(p):
    "statement_list : statement"
    p[0] = [p[1]]


def p_statement_list_empty(p):
    "statement_list : empty"
    p[0] = []


def p_statement_decl(p):
    "statement : declaration"
    p[0] = p[1]


def p_statement_expr(p):
    "statement : expression SEMICOLON"
    p[0] = ExprStmt(p[1], line=p.lineno(2))


def p_statement_return(p):
    "statement : RETURN expression_opt SEMICOLON"
    p[0] = Return(p[2], line=p.lineno(1))


def p_declaration(p):
    "declaration : type_spec IDENTIFIER array_opt SEMICOLON"
    p[0] = VarDecl(
        data_type=p[1],
        name=p[2],
        array_size=p[3],
        line=p.lineno(2),
    )


def p_array_opt(p):
    """array_opt : LBRACKET NUMBER RBRACKET
                 | empty"""
    p[0] = p[2] if len(p) == 4 else None


def p_expression_opt(p):
    """expression_opt : expression
                      | empty"""
    p[0] = p[1]


def p_expression_call(p):
    "expression : IDENTIFIER LPAREN argument_list_opt RPAREN"
    p[0] = Call(
        name=p[1],
        arguments=p[3],
        line=p.lineno(1),
    )


def p_expression_assignment(p):
    "expression : IDENTIFIER ASSIGN expression"
    p[0] = Assignment(
        target=Identifier(p[1], line=p.lineno(1)),
        value=p[3],
        line=p.lineno(2),
    )


def p_expression_identifier(p):
    "expression : IDENTIFIER"
    p[0] = Identifier(p[1], line=p.lineno(1))


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Number(p[1], line=p.lineno(1))


def p_expression_string(p):
    "expression : STRING"
    p[0] = String(p[1], line=p.lineno(1))


def p_argument_list_opt(p):
    """argument_list_opt : argument_list
                         | empty"""
    p[0] = p[1] if p[1] is not None else []


def p_argument_list_multiple(p):
    "argument_list : argument_list COMMA expression"
    p[0] = p[1] + [p[3]]


def p_argument_list_single(p):
    "argument_list : expression"
    p[0] = [p[1]]


def p_empty(p):
    "empty :"
    p[0] = None


def p_error(p):
    if p is None:
        raise SyntaxError("Unexpected end of input")
    raise SyntaxError(
        f"Syntax error near {p.value!r} "
        f"at line {p.lineno}"
    )


parser = yacc.yacc()


def parse(source_code):
    lexer.lineno = 1
    return parser.parse(source_code, lexer=lexer)
