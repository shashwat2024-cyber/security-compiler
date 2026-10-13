
from parser import parse
from taint_analysis import analyze_taint
from reporter import generate_report, print_report


source = """
void main() {
    char buffer[8];
    input = read_input();
    copy = input;
    strcpy(buffer, copy);
}
"""

ast = parse(source)
taint_result = analyze_taint(ast)

report = generate_report(taint_result)
print_report(report)

assert report["summary"]["total_findings"] == 1
assert report["summary"]["high"] == 1
assert report["findings"][0]["rule_id"] == "SC001"
assert report["findings"][0]["sink"] == "strcpy"

print("\nTEST PASSED")
