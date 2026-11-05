; ModuleID = 'T5_rounds5_on'
source_filename = "T5_rounds5_on"

@0 = internal constant [2 x i8] c"m\00"
@1 = internal constant [2 x i8] c"s\00"

define void @main() #0 {
entry:
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr null)
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 4 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 5 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 6 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 7 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 8 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 10 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 11 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 13 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 14 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 16 to ptr))
  call void @__quantum__qis__barrier18__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 4 to ptr), ptr inttoptr (i64 5 to ptr), ptr inttoptr (i64 6 to ptr), ptr inttoptr (i64 7 to ptr), ptr inttoptr (i64 8 to ptr), ptr inttoptr (i64 9 to ptr), ptr inttoptr (i64 10 to ptr), ptr inttoptr (i64 11 to ptr), ptr inttoptr (i64 12 to ptr), ptr inttoptr (i64 13 to ptr), ptr inttoptr (i64 14 to ptr), ptr inttoptr (i64 15 to ptr), ptr inttoptr (i64 16 to ptr), ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 10 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 13 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %0 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %1 = zext i1 %0 to i64
  %2 = mul i64 %1, 1
  %3 = or i64 %2, 0
  %4 = sub i64 1, %1
  %5 = mul i64 %4, 1
  %6 = xor i64 9223372036854775807, %5
  %7 = and i64 %6, %3
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 11 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 14 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %8 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %9 = zext i1 %8 to i64
  %10 = mul i64 %9, 2
  %11 = or i64 %10, %7
  %12 = sub i64 1, %9
  %13 = mul i64 %12, 2
  %14 = xor i64 9223372036854775807, %13
  %15 = and i64 %14, %11
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 8 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %16 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %17 = zext i1 %16 to i64
  %18 = mul i64 %17, 4
  %19 = or i64 %18, %15
  %20 = sub i64 1, %17
  %21 = mul i64 %20, 4
  %22 = xor i64 9223372036854775807, %21
  %23 = and i64 %22, %19
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 16 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %24 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %25 = zext i1 %24 to i64
  %26 = mul i64 %25, 8
  %27 = or i64 %26, %23
  %28 = sub i64 1, %25
  %29 = mul i64 %28, 8
  %30 = xor i64 9223372036854775807, %29
  %31 = and i64 %30, %27
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 10 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 13 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %32 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %33 = zext i1 %32 to i64
  %34 = mul i64 %33, 16
  %35 = or i64 %34, %31
  %36 = sub i64 1, %33
  %37 = mul i64 %36, 16
  %38 = xor i64 9223372036854775807, %37
  %39 = and i64 %38, %35
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 11 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 14 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %40 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %41 = zext i1 %40 to i64
  %42 = mul i64 %41, 32
  %43 = or i64 %42, %39
  %44 = sub i64 1, %41
  %45 = mul i64 %44, 32
  %46 = xor i64 9223372036854775807, %45
  %47 = and i64 %46, %43
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 8 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %48 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %49 = zext i1 %48 to i64
  %50 = mul i64 %49, 64
  %51 = or i64 %50, %47
  %52 = sub i64 1, %49
  %53 = mul i64 %52, 64
  %54 = xor i64 9223372036854775807, %53
  %55 = and i64 %54, %51
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 16 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %56 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %57 = zext i1 %56 to i64
  %58 = mul i64 %57, 128
  %59 = or i64 %58, %55
  %60 = sub i64 1, %57
  %61 = mul i64 %60, 128
  %62 = xor i64 9223372036854775807, %61
  %63 = and i64 %62, %59
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 10 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 13 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %64 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %65 = zext i1 %64 to i64
  %66 = mul i64 %65, 256
  %67 = or i64 %66, %63
  %68 = sub i64 1, %65
  %69 = mul i64 %68, 256
  %70 = xor i64 9223372036854775807, %69
  %71 = and i64 %70, %67
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 11 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 14 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %72 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %73 = zext i1 %72 to i64
  %74 = mul i64 %73, 512
  %75 = or i64 %74, %71
  %76 = sub i64 1, %73
  %77 = mul i64 %76, 512
  %78 = xor i64 9223372036854775807, %77
  %79 = and i64 %78, %75
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 8 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %80 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %81 = zext i1 %80 to i64
  %82 = mul i64 %81, 1024
  %83 = or i64 %82, %79
  %84 = sub i64 1, %81
  %85 = mul i64 %84, 1024
  %86 = xor i64 9223372036854775807, %85
  %87 = and i64 %86, %83
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 16 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %88 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %89 = zext i1 %88 to i64
  %90 = mul i64 %89, 2048
  %91 = or i64 %90, %87
  %92 = sub i64 1, %89
  %93 = mul i64 %92, 2048
  %94 = xor i64 9223372036854775807, %93
  %95 = and i64 %94, %91
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 10 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 13 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %96 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %97 = zext i1 %96 to i64
  %98 = mul i64 %97, 4096
  %99 = or i64 %98, %95
  %100 = sub i64 1, %97
  %101 = mul i64 %100, 4096
  %102 = xor i64 9223372036854775807, %101
  %103 = and i64 %102, %99
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 11 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 14 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %104 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %105 = zext i1 %104 to i64
  %106 = mul i64 %105, 8192
  %107 = or i64 %106, %103
  %108 = sub i64 1, %105
  %109 = mul i64 %108, 8192
  %110 = xor i64 9223372036854775807, %109
  %111 = and i64 %110, %107
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 8 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %112 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %113 = zext i1 %112 to i64
  %114 = mul i64 %113, 16384
  %115 = or i64 %114, %111
  %116 = sub i64 1, %113
  %117 = mul i64 %116, 16384
  %118 = xor i64 9223372036854775807, %117
  %119 = and i64 %118, %115
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 16 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %120 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %121 = zext i1 %120 to i64
  %122 = mul i64 %121, 32768
  %123 = or i64 %122, %119
  %124 = sub i64 1, %121
  %125 = mul i64 %124, 32768
  %126 = xor i64 9223372036854775807, %125
  %127 = and i64 %126, %123
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 10 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 13 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %128 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %129 = zext i1 %128 to i64
  %130 = mul i64 %129, 65536
  %131 = or i64 %130, %127
  %132 = sub i64 1, %129
  %133 = mul i64 %132, 65536
  %134 = xor i64 9223372036854775807, %133
  %135 = and i64 %134, %131
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 11 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 12 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 14 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %136 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %137 = zext i1 %136 to i64
  %138 = mul i64 %137, 131072
  %139 = or i64 %138, %135
  %140 = sub i64 1, %137
  %141 = mul i64 %140, 131072
  %142 = xor i64 9223372036854775807, %141
  %143 = and i64 %142, %139
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 8 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 9 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %144 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %145 = zext i1 %144 to i64
  %146 = mul i64 %145, 262144
  %147 = or i64 %146, %143
  %148 = sub i64 1, %145
  %149 = mul i64 %148, 262144
  %150 = xor i64 9223372036854775807, %149
  %151 = and i64 %150, %147
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 15 to ptr))
  call void @__quantum__qis__cnot__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 16 to ptr))
  call void @__quantum__qis__h__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 17 to ptr), ptr inttoptr (i64 17 to ptr))
  %152 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 17 to ptr))
  %153 = zext i1 %152 to i64
  %154 = mul i64 %153, 524288
  %155 = or i64 %154, %151
  %156 = sub i64 1, %153
  %157 = mul i64 %156, 524288
  %158 = xor i64 9223372036854775807, %157
  %159 = and i64 %158, %155
  call void @__quantum__qis__reset__body(ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__barrier18__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 4 to ptr), ptr inttoptr (i64 5 to ptr), ptr inttoptr (i64 6 to ptr), ptr inttoptr (i64 7 to ptr), ptr inttoptr (i64 8 to ptr), ptr inttoptr (i64 9 to ptr), ptr inttoptr (i64 10 to ptr), ptr inttoptr (i64 11 to ptr), ptr inttoptr (i64 12 to ptr), ptr inttoptr (i64 13 to ptr), ptr inttoptr (i64 14 to ptr), ptr inttoptr (i64 15 to ptr), ptr inttoptr (i64 16 to ptr), ptr inttoptr (i64 17 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr null)
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 4 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 5 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 6 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 7 to ptr))
  call void @__quantum__qis__mz__body(ptr null, ptr null)
  %160 = call i1 @__quantum__qis__read_result__body(ptr null)
  %161 = zext i1 %160 to i64
  %162 = mul i64 %161, 1
  %163 = or i64 %162, 0
  %164 = sub i64 1, %161
  %165 = mul i64 %164, 1
  %166 = xor i64 9223372036854775807, %165
  %167 = and i64 %166, %163
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 1 to ptr))
  %168 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 1 to ptr))
  %169 = zext i1 %168 to i64
  %170 = mul i64 %169, 2
  %171 = or i64 %170, %167
  %172 = sub i64 1, %169
  %173 = mul i64 %172, 2
  %174 = xor i64 9223372036854775807, %173
  %175 = and i64 %174, %171
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 2 to ptr))
  %176 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 2 to ptr))
  %177 = zext i1 %176 to i64
  %178 = mul i64 %177, 4
  %179 = or i64 %178, %175
  %180 = sub i64 1, %177
  %181 = mul i64 %180, 4
  %182 = xor i64 9223372036854775807, %181
  %183 = and i64 %182, %179
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 3 to ptr))
  %184 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 3 to ptr))
  %185 = zext i1 %184 to i64
  %186 = mul i64 %185, 8
  %187 = or i64 %186, %183
  %188 = sub i64 1, %185
  %189 = mul i64 %188, 8
  %190 = xor i64 9223372036854775807, %189
  %191 = and i64 %190, %187
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 4 to ptr), ptr inttoptr (i64 4 to ptr))
  %192 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 4 to ptr))
  %193 = zext i1 %192 to i64
  %194 = mul i64 %193, 16
  %195 = or i64 %194, %191
  %196 = sub i64 1, %193
  %197 = mul i64 %196, 16
  %198 = xor i64 9223372036854775807, %197
  %199 = and i64 %198, %195
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 5 to ptr), ptr inttoptr (i64 5 to ptr))
  %200 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 5 to ptr))
  %201 = zext i1 %200 to i64
  %202 = mul i64 %201, 32
  %203 = or i64 %202, %199
  %204 = sub i64 1, %201
  %205 = mul i64 %204, 32
  %206 = xor i64 9223372036854775807, %205
  %207 = and i64 %206, %203
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 6 to ptr), ptr inttoptr (i64 6 to ptr))
  %208 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 6 to ptr))
  %209 = zext i1 %208 to i64
  %210 = mul i64 %209, 64
  %211 = or i64 %210, %207
  %212 = sub i64 1, %209
  %213 = mul i64 %212, 64
  %214 = xor i64 9223372036854775807, %213
  %215 = and i64 %214, %211
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 7 to ptr), ptr inttoptr (i64 7 to ptr))
  %216 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 7 to ptr))
  %217 = zext i1 %216 to i64
  %218 = mul i64 %217, 128
  %219 = or i64 %218, %215
  %220 = sub i64 1, %217
  %221 = mul i64 %220, 128
  %222 = xor i64 9223372036854775807, %221
  %223 = and i64 %222, %219
  call void @__quantum__rt__int_record_output(i64 %223, ptr @0)
  call void @__quantum__rt__int_record_output(i64 %159, ptr @1)
  ret void
}

declare i1 @__quantum__qis__read_result__body(ptr)

declare void @__quantum__rt__int_record_output(i64, ptr)

declare void @__quantum__qis__phasedx__body(double, double, ptr)

declare void @__quantum__qis__barrier18__body(ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr, ptr)

declare void @__quantum__qis__h__body(ptr)

declare void @__quantum__qis__cnot__body(ptr, ptr)

declare void @__quantum__qis__mz__body(ptr, ptr writeonly) #1

declare void @__quantum__qis__reset__body(ptr)

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="custom" "required_num_qubits"="18" "required_num_results"="18" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 2}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
