
"""Security rules for the Security Compiler."""

RULES = {
    "strcpy": {
        "id": "SC001",
        "severity": "HIGH",
        "description": (
            "strcpy does not check the destination buffer capacity."
        ),
        "recommendation": (
            "Validate input length and use a safer bounded-copy "
            "approach appropriate to the program."
        ),
    },
    "system": {
        "id": "SC002",
        "severity": "HIGH",
        "description": (
            "system executes a command through the host environment."
        ),
        "recommendation": (
            "Avoid constructing commands from untrusted input; "
            "use safer APIs and validate arguments."
        ),
    },
}


def get_rule(function_name):
    """Return the security rule for a function, if configured."""
    return RULES.get(function_name)


def print_rules():
    """Display the configured security rules."""
    print("=== Configured Security Rules ===")

    for function_name, rule in RULES.items():
        print(f"\nRule ID: {rule['id']}")
        print(f"Function: {function_name}")
        print(f"Severity: {rule['severity']}")
        print(f"Description: {rule['description']}")
        print(f"Recommendation: {rule['recommendation']}")
