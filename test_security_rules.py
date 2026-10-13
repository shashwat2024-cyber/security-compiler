
from security_rules import get_rule, print_rules

strcpy_rule = get_rule("strcpy")

assert strcpy_rule is not None
assert strcpy_rule["id"] == "SC001"
assert strcpy_rule["severity"] == "HIGH"

assert get_rule("unknown_function") is None

print_rules()
print("\nTEST PASSED")
