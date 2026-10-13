
from dataclasses import dataclass, field


@dataclass
class Program:
    functions: list = field(default_factory=list)


@dataclass
class Function:
    return_type: str
    name: str
    body: list
    line: int = 1


@dataclass
class VarDecl:
    data_type: str
    name: str
    array_size: int = None
    line: int = 1


@dataclass
class ExprStmt:
    expression: object
    line: int = 1


@dataclass
class Call:
    name: str
    arguments: list
    line: int = 1


@dataclass
class Identifier:
    name: str
    line: int = 1


@dataclass
class Number:
    value: int
    line: int = 1


@dataclass
class String:
    value: str
    line: int = 1


@dataclass
class Assignment:
    target: object
    value: object
    line: int = 1


@dataclass
class Return:
    value: object = None
    line: int = 1
