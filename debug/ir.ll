; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

@"true" = constant i1 1
@"false" = constant i1 0
define i32 @"main"()
{
main_entry:
  ret i32 69
}

define i32 @"func"()
{
func_entry:
  %".2" = alloca i32
  store i32 0, i32* %".2"
  %".4" = icmp sgt i32 1, 2
  br i1 %".4", label %"func_entry.if", label %"func_entry.else"
func_entry.if:
  %".6" = fadd float 0x4023666660000000, 0x3fe0000000000000
  %".7" = add i32 10, 7
  %".8" = add i32 %".7", 9
  store i32 %".8", i32* %".2"
  br label %"func_entry.endif"
func_entry.else:
  %".11" = icmp sgt i32 2, 3
  br i1 %".11", label %"func_entry.else.if", label %"func_entry.else.else"
func_entry.endif:
  %".25" = load i32, i32* %".2"
  ret i32 %".25"
func_entry.else.if:
  store i32 0, i32* %".2"
  br label %"func_entry.else.endif"
func_entry.else.else:
  %".15" = icmp sgt i32 3, 2
  br i1 %".15", label %"func_entry.else.else.if", label %"func_entry.else.else.else"
func_entry.else.endif:
  br label %"func_entry.endif"
func_entry.else.else.if:
  %".17" = add i32 5, 5
  %".18" = mul i32 %".17", 9
  store i32 %".18", i32* %".2"
  br label %"func_entry.else.else.endif"
func_entry.else.else.else:
  %".21" = sdiv i32 10, 2
  br label %"func_entry.else.else.endif"
func_entry.else.else.endif:
  br label %"func_entry.else.endif"
}
