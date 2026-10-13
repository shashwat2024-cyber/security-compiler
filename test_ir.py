
from pprint import pprint

from parser import parse
from ir import build_ir


source = """
void main() {
    char buffer[8];
    strcpy(buffer, input);
}
"""

ast = parse(source)
ir_program = build_ir(ast)

pprint(ir_program, sort_dicts=False)
