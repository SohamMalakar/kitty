import sys
import json
import time

from Lexer import Lexer
from Parser import Parser
from Compiler import Compiler

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE, c_int, c_float

LEXER_DEBUG = True
PARSER_DEBUG = True
COMPILER_DEBUG = True
RUN_CODE = True

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

if RUN_CODE:
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    try:
        llvm_ir_parsed = llvm.parse_assembly(str(module))
        llvm_ir_parsed.verify()
    except Exception as e:
        print(e)
        raise

    target_machine = llvm.Target.from_default_triple().create_target_machine()

    engine = llvm.create_mcjit_compiler(llvm_ir_parsed, target_machine)
    engine.finalize_object()

    # Run the function with the name 'main'. This is the entry point function of the entire program
    entry = engine.get_function_address('main')
    cfunc = CFUNCTYPE(c_int)(entry)

    st = time.time()

    result = cfunc()

    et = time.time()

    print(f'\n\nProgram returned: {result}\n=== Executed in {round((et - st) * 1000, 6)} ms. ===')
