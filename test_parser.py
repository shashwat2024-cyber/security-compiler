
from pprint import pprint

from parser import parse

source = """
void main() {
    char buffer[8];
    strcpy(buffer, input);
}
"""

ast = parse(source)
pprint(ast, sort_dicts=False)
