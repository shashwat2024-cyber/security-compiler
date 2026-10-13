
from dataclasses import dataclass, field


@dataclass
class CallGraph:
    # Maps each function to the functions it calls.
    edges: dict = field(default_factory=dict)


def build_call_graph(ast):
    """Build a call graph from the program AST."""
    graph = CallGraph()

    # Register every function, including functions with no calls.
    for function in ast.functions:
        graph.edges[function.name] = set()

    # Inspect expressions for function calls.
    for function in ast.functions:
        for statement in function.body:
            expression = getattr(statement, "expression", None)

            if expression is not None:
                _collect_calls(
                    expression,
                    graph.edges[function.name],
                )

    return graph


def _collect_calls(expression, result):
    """Collect calls nested inside an expression."""
    if expression is None:
        return

    if isinstance(expression, dict):
        function_name = expression.get("function")

        if function_name:
            result.add(function_name)

        for argument in expression.get("arguments", []):
            _collect_calls(argument, result)

        return

    # AST expressions are objects with named attributes.
    class_name = type(expression).__name__

    if class_name == "Call":
        result.add(expression.name)

        for argument in expression.arguments:
            _collect_calls(argument, result)

    elif class_name == "Assignment":
        _collect_calls(expression.value, result)


def print_call_graph(graph):
    """Print the call graph in a readable format."""
    for caller, callees in graph.edges.items():
        if callees:
            for callee in sorted(callees):
                print(f"{caller} -> {callee}")
        else:
            print(f"{caller} -> (no calls)")
