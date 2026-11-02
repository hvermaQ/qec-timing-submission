; ModuleID = '/Users/harshank_s/qec-timing-submission/SG_final_round/programs/single_qubit_2c64d96fea4bbbac/no_sleep.bc'
source_filename = "single_qubit_memory"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128"
target triple = "aarch64-unknown-linux-gnu"

@label = private constant [3 x i8] c"m0\00"

define void @main() #0 {
  call void @__quantum__rt__initialize(ptr null)
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr null)
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, ptr null)
  call void @__quantum__qis__mz__body(ptr null, ptr null)
  %bit = call i1 @__quantum__rt__read_result(ptr null)
  call void @__quantum__rt__bool_record_output(i1 %bit, ptr @label)
  ret void
}

declare void @__quantum__rt__initialize(ptr)

declare void @__quantum__qis__phasedx__body(double, double, ptr)

declare void @__quantum__qis__mz__body(ptr, ptr writeonly) #1

declare i1 @__quantum__rt__read_result(ptr readonly)

declare void @__quantum__rt__bool_record_output(i1, ptr)

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="adaptive_profile" "required_num_qubits"="1" "required_num_results"="1" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
