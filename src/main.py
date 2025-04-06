import sys
import json
# import llvmlite

from Lexer import Lexer
from Parser import Parser

LEXER_DEBUG = True
PARSER_DEBUG = True

# print(llvmlite.__version__)

if len(sys.argv) != 2:
    print("Usage: kitty <filename>")
    sys.exit(1)

filename = sys.argv[1]

with open(filename) as f:
    src = f.read()

lexer = Lexer(src, path=filename)
tokens = lexer.make_tokens()

if LEXER_DEBUG:
    print("===== SOURCE CODE =====")
    print(src, "\n")

    print("===== LEXER TOKENS =====")
    for token in tokens:
        print(token)
    print()

if not lexer.error_handler.report():
    sys.exit(1)

parser = Parser(tokens, lexer.error_handler)
ast = parser.parse_program()

if not parser.error_handler.report():
    sys.exit(2)

if PARSER_DEBUG:
    with open("debug/ast.json", "w") as f:
        json.dump(ast.json(), f, indent=4)
