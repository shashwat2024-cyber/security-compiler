
from pprint import pprint

from parser import parse
from ir import build_ir
from cfg import build_program_cfg


source = """
void main() {
    char buffer[8];
    strcpy(buffer, input);
}
"""

ast = parse(source)
ir_program = build_ir(ast)
graphs = build_program_cfg(ir_program)

pprint(graphs, sort_dicts=False)
