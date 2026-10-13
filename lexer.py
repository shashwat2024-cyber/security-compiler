
import ply.lex as lex

# Reserved keywords in our restricted C-like language
reserved = {
    "int": "INT",
    "char": "CHAR",
    "void": "VOID",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "return": "RETURN",
}

tokens = [
    "IDENTIFIER",
    "NUMBER",
    "STRING",
    "ASSIGN",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
    "LBRACKET",
    "RBRACKET",
    "SEMICOLON",
    "COMMA",
] + list(reserved.values())

t_ASSIGN = r"="
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_SEMICOLON = r";"
t_COMMA = r","

t_ignore = " \t\r"


def t_STRING(t):
    r'"([^\\\n]|(\\.))*?"'
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_IDENTIFIER(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFIER")
    return t


def t_COMMENT(t):
    r"//[^\n]*"
    pass


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    raise SyntaxError(
        f"Illegal character {t.value[0]!r} "
        f"at line {t.lexer.lineno}"
    )


lexer = lex.lex()


def tokenize(source_code):
    lexer.lineno = 1
    lexer.input(source_code)

    result = []

    while True:
        token = lexer.token()
        if token is None:
            break

        result.append(
            (token.type, token.value, token.lineno)
        )

    return result
