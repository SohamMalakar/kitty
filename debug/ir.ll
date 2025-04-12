; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

define i32 @"main"()
{
main_entry:
  ret i32 0
}

define i32 @"add"()
{
add_entry:
  %".2" = alloca i32
  store i32 2, i32* %".2"
  %".4" = alloca i32
  store i32 8, i32* %".4"
  %".6" = load i32, i32* %".2"
  %".7" = load i32, i32* %".4"
  %".8" = add i32 %".6", %".7"
  ret i32 %".8"
}
