"""Generate a readable security report."""

from security_rules import get_rule


def generate_report(taint_result):
    """Convert taint findings into structured report data."""
    report = {
        "project": "Security Compiler",
        "summary": {
            "total_findings": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
        "findings": [],
    }

    for finding in taint_result.findings:
        rule = get_rule(finding.sink)

        # Ignore findings without a configured security rule.
        if rule is None:
            continue

        item = {
            "rule_id": rule["id"],
            "severity": rule["severity"],
            "function": finding.function,
            "sink": finding.sink,
            "line": finding.line,
            "tainted_variables": finding.tainted_variables,
            "message": finding.message,
            "description": rule["description"],
            "recommendation": rule["recommendation"],
        }

        # Include buffer details when the analysis has identified them.
        if getattr(finding, "destination_buffer", None) is not None:
            item["destination_buffer"] = finding.destination_buffer

        if getattr(finding, "buffer_size", None) is not None:
            item["buffer_size"] = finding.buffer_size

        report["findings"].append(item)
        report["summary"]["total_findings"] += 1

        severity = rule["severity"].lower()
        if severity in report["summary"]:
            report["summary"][severity] += 1

    return report


def print_report(report):
    """Print the report in a readable format."""
    print("\n" + "=" * 48)
    print("       SECURITY COMPILER REPORT")
    print("=" * 48)

    print(f"Project: {report['project']}")
    print(f"Total findings: {report['summary']['total_findings']}")
    print(f"High: {report['summary']['high']}")
    print(f"Medium: {report['summary']['medium']}")
    print(f"Low: {report['summary']['low']}")

    if not report["findings"]:
        print("\nNo findings matched the configured security rules.")

    for index, finding in enumerate(report["findings"], start=1):
        print(f"\nFinding #{index}")
        print(f"Rule: {finding['rule_id']}")
        print(f"Severity: {finding['severity']}")
        print(f"Function: {finding['function']}")
        print(f"Sink: {finding['sink']}")
        print(f"Line: {finding['line']}")
        print(
            "Tainted variables: "
            + ", ".join(finding["tainted_variables"])
        )

        if "destination_buffer" in finding:
            print(f"Destination buffer: {finding['destination_buffer']}")

        if "buffer_size" in finding:
            print(f"Buffer capacity: {finding['buffer_size']} bytes")

        print(f"Details: {finding['message']}")
        print(f"Description: {finding['description']}")
        print(f"Recommendation: {finding['recommendation']}")

    print("\n" + "=" * 48)
