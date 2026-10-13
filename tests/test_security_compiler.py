
from parser import parse
from taint_analysis import analyze_taint
from reporter import generate_report


def test_tainted_input_to_strcpy_is_reported():
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
    report = generate_report(result)

    assert report["summary"]["total_findings"] == 1
    assert report["summary"]["high"] == 1
    assert report["findings"][0]["rule_id"] == "SC001"


def test_clean_input_does_not_trigger_taint_rule():
    source = """
void main() {
    char buffer[8];
    copy = 123;
    strcpy(buffer, copy);
}
"""
    ast = parse(source)
    result = analyze_taint(ast)
    report = generate_report(result)

    assert report["summary"]["total_findings"] == 0
