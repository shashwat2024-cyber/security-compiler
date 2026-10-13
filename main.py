
import sys
from pathlib import Path

from parser import parse
from taint_analysis import analyze_taint
from reporter import generate_report, print_report


def analyze_file(file_path):
    """Read a source file and run the security analysis."""
    path = Path(file_path)

    if not path.is_file():
        print(f"Error: File not found: {path}")
        return 1

    try:
        source_code = path.read_text(encoding="utf-8")

        ast = parse(source_code)
        taint_result = analyze_taint(ast)
        report = generate_report(taint_result)

        print_report(report)
        return 0

    except Exception as error:
        print(f"Analysis failed: {error}")
        return 1


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_file>")
        print("Example: python main.py sample.c")
        return 1

    return analyze_file(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
