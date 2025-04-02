import sys
import json
# import llvmlite

from Lexer import Lexer
from Parser import Parser

# print(llvmlite.__version__)

if len(sys.argv) != 2:
    print("Usage: kitty <filename>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename) as f:
    src = f.read()

print(src)

lexer = Lexer(src)
tokens = lexer.make_tokens()

for token in tokens:
    print(token)

parser = Parser(tokens)
ast = parser.parse_program()

with open("debug/ast.json", "w") as f:
    json.dump(ast.json(), f, indent=4)
