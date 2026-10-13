
from dataclasses import fields, is_dataclass

from lexer import tokenize
from parser import parse
from ir import build_ir
from cfg import build_program_cfg
from call_graph import build_call_graph
from taint_analysis import analyze_taint
from reporter import generate_report


def to_dict(value):
    """Convert Python objects into JSON-compatible data."""
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_dict(getattr(value, field.name))
            for field in fields(value)
        }

    if isinstance(value, dict):
        return {
            str(key): to_dict(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_dict(item) for item in value]

    if isinstance(value, set):
        return sorted(
            (to_dict(item) for item in value),
            key=str
        )

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def ast_to_tree(value):
    """Preserve each AST node's actual class name and its children."""
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "type": type(value).__name__,
            "children": [
                {
                    "field": field.name,
                    "value": ast_to_tree(
                        getattr(value, field.name)
                    ),
                }
                for field in fields(value)
            ],
        }

    if isinstance(value, list):
        return [ast_to_tree(item) for item in value]

    if isinstance(value, tuple):
        return [ast_to_tree(item) for item in value]

    if isinstance(value, dict):
        return {
            str(key): ast_to_tree(item)
            for key, item in value.items()
        }

    return value


def analyze_program(source_code):
    """Run the complete available compiler-analysis pipeline."""
    tokens = tokenize(source_code)
    ast = parse(source_code)

    ir_program = build_ir(ast)
    cfgs = build_program_cfg(ir_program)
    call_graph = build_call_graph(ast)

    taint_result = analyze_taint(ast)
    report = generate_report(taint_result)

    return {
        "tokens": [
            {
                "type": kind,
                "value": value,
                "line": line,
            }
            for kind, value, line in tokens
        ],
        "ast": ast_to_tree(ast),
        "ir": to_dict(ir_program),
        "cfg": to_dict(cfgs),
        "call_graph": {
            function: sorted(callees)
            for function, callees in call_graph.edges.items()
        },
        "report": to_dict(report),
    }
