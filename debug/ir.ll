; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

define i32 @"main"()
{
main_entry:
  %".2" = mul i32 5, 8
  %".3" = add i32 5, %".2"
  ret i32 0
}
