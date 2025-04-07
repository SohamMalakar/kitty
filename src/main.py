import sys
import json

from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int, c_float

LEXER_DEBUG = True
PARSER_DEBUG = True
COMPILER_DEBUG = True

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

c: Compiler = Compiler()
c.compile(node=ast)

module: ir.Module = c.module
module.triple = llvm.get_default_triple()

if COMPILER_DEBUG:
    with open("debug/ir.ll", "w") as f:
        f.write(str(module))
        print("Successfully wrote IR to debug/ir.ll")