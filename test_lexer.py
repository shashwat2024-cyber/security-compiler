
from lexer import tokenize

source = """
void main() {
    char buffer[8];
    strcpy(buffer, input);
}
"""

for token in tokenize(source):
    print(token)
