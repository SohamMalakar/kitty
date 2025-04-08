; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

define i32 @"main"()
{
main_entry:
  %".2" = add i32 10, 7
  %".3" = mul i32 5, %".2"
  %".4" = sdiv i32 %".3", 5
  %".5" = fmul float 0x40179999a0000000, 0x4014666660000000
  ret i32 69
}
