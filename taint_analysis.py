
from dataclasses import dataclass, field

from ast_nodes import (
    Program,
    VarDecl,
    Call,
    Identifier,
    Assignment,
    Return,
)


# Functions whose return values we treat as untrusted.
TAINT_SOURCES = {
    "read_input",
    "get_input",
    "gets",
}

# Functions we inspect for unsafe data use.
# The index identifies the argument to inspect.
TAINT_SINKS = {
    "strcpy": 1,
    "system": 0,
}


@dataclass
class TaintFinding:
    function: str
    sink: str
    line: int
    tainted_variables: list = field(default_factory=list)
    message: str = ""
    destination_buffer: str = ""
    buffer_size: int | None = None


@dataclass
class TaintResult:
    tainted_variables: dict = field(default_factory=dict)
    findings: list = field(default_factory=list)


def _is_tainted(expression, tainted):
    """Check whether an expression contains data from a known taint source."""
    if expression is None:
        return False

    if isinstance(expression, Identifier):
        return expression.name in tainted

    if isinstance(expression, Call):
        if expression.name in TAINT_SOURCES:
            return True

        return any(
            _is_tainted(argument, tainted)
            for argument in expression.arguments
        )

    if isinstance(expression, Assignment):
        return _is_tainted(expression.value, tainted)

    return False


def _tainted_names(expression, tainted):
    """Return the names of tainted variables used by an expression."""
    names = set()

    if isinstance(expression, Identifier):
        if expression.name in tainted:
            names.add(expression.name)

    elif isinstance(expression, Call):
        for argument in expression.arguments:
            names.update(_tainted_names(argument, tainted))

    elif isinstance(expression, Assignment):
        names.update(_tainted_names(expression.value, tainted))

    return sorted(names)


def _get_buffer_sizes(function):
    """
    Collect fixed array capacities declared directly in a function body.

    Example:
        char buffer[8];

    Produces:
        {"buffer": 8}
    """
    buffer_sizes = {}

    for statement in function.body:
        if not isinstance(statement, VarDecl):
            continue

        size = statement.array_size

        if (
            isinstance(size, int)
            and not isinstance(size, bool)
            and size > 0
        ):
            buffer_sizes[statement.name] = size

    return buffer_sizes


def analyze_taint(ast):
    """
    Perform basic, intraprocedural taint analysis.

    Tracks assignments from configured sources and checks configured sinks.
    Also attaches known fixed destination-array capacities to strcpy findings.
    """
    if not isinstance(ast, Program):
        raise TypeError("analyze_taint expects a Program AST")

    result = TaintResult()

    for function in ast.functions:
        tainted = set()
        findings = []
        buffer_sizes = _get_buffer_sizes(function)

        for statement in function.body:

            # Declarations are not automatically tainted.
            if isinstance(statement, VarDecl):
                continue

            if isinstance(statement, Return):
                continue

            expression = getattr(statement, "expression", None)

            if expression is None:
                continue

            # Track assignments such as:
            # input = read_input();
            # copy = input;
            if isinstance(expression, Assignment):
                target = expression.target

                if isinstance(target, Identifier):
                    if _is_tainted(expression.value, tainted):
                        tainted.add(target.name)
                    else:
                        tainted.discard(target.name)

                # Inspect calls on the right-hand side as well.
                if isinstance(expression.value, Call):
                    _inspect_call(
                        expression.value,
                        tainted,
                        findings,
                        function.name,
                        buffer_sizes,
                    )

            # Inspect standalone function calls.
            elif isinstance(expression, Call):
                _inspect_call(
                    expression,
                    tainted,
                    findings,
                    function.name,
                    buffer_sizes,
                )

        result.tainted_variables[function.name] = sorted(tainted)
        result.findings.extend(findings)

    return result


def _inspect_call(
    call,
    tainted,
    findings,
    function_name,
    buffer_sizes=None,
):
    """Check a function call against configured taint sinks."""
    sink_name = call.name

    if sink_name not in TAINT_SINKS:
        return

    argument_index = TAINT_SINKS[sink_name]

    if argument_index >= len(call.arguments):
        return

    argument = call.arguments[argument_index]

    if not _is_tainted(argument, tainted):
        return

    names = _tainted_names(argument, tainted)

    destination_buffer = ""
    buffer_size = None
    message = (
        f"Potentially unsafe use of tainted data "
        f"in call to {sink_name}."
    )

    # For strcpy(destination, source), inspect the destination array.
    if sink_name == "strcpy" and call.arguments:
        destination = call.arguments[0]

        if isinstance(destination, Identifier):
            destination_buffer = destination.name
            buffer_size = (buffer_sizes or {}).get(destination.name)

            if buffer_size is not None:
                message += (
                    f" Destination '{destination.name}' has a declared "
                    f"capacity of {buffer_size} bytes, but the source "
                    f"length is not established by this analysis."
                )
            else:
                message += (
                    " The destination's fixed array capacity was not "
                    "identified by this analysis."
                )

    findings.append(
        TaintFinding(
            function=function_name,
            sink=sink_name,
            line=call.line,
            tainted_variables=names,
            message=message,
            destination_buffer=destination_buffer,
            buffer_size=buffer_size,
        )
    )


def print_taint_report(result):
    """Print taint analysis results in a readable format."""
    print("=== Taint Analysis Report ===")

    for function, variables in result.tainted_variables.items():
        print(f"Function: {function}")
        print(f"  Tainted variables: {variables}")

    if not result.findings:
        print("No configured tainted-sink patterns detected.")
        return

    print("\nPotential security findings:")

    for finding in result.findings:
        print(f"  Function: {finding.function}")
        print(f"  Sink: {finding.sink}")
        print(f"  Line: {finding.line}")
        print(f"  Tainted variables: {finding.tainted_variables}")
        print(f"  Details: {finding.message}")

        if finding.destination_buffer:
            print(f"  Destination buffer: {finding.destination_buffer}")

        if finding.buffer_size is not None:
            print(f"  Declared buffer capacity: {finding.buffer_size} bytes")

