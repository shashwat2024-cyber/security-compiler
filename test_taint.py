
from parser import parse
from taint_analysis import analyze_taint, print_taint_report


source = """
void main() {
    char buffer[8];
    input = read_input();
    copy = input;
    strcpy(buffer, copy);
}
"""

ast = parse(source)
result = analyze_taint(ast)
print_taint_report(result)

assert "input" in result.tainted_variables["main"]
assert "copy" in result.tainted_variables["main"]
assert any(
    finding.sink == "strcpy"
    for finding in result.findings
)

print("\nTEST PASSED")
