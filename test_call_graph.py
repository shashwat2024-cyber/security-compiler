
from parser import parse
from call_graph import build_call_graph, print_call_graph


source = """
void helper() {
    strcpy(buffer, input);
}

void main() {
    helper();
}
"""

ast = parse(source)
graph = build_call_graph(ast)

print_call_graph(graph)
