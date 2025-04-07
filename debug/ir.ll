; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

define i32 @"main"()
{
main_entry:
  %".2" = add i32 10, 7
  %".3" = mul i32 5, %".2"
  %".4" = sdiv i32 %".3", 5
  ret i32 69
}
