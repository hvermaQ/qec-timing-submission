; ModuleID = 'T4_transport_L64_off'
source_filename = "T4_transport_L64_off"

@0 = internal constant [2 x i8] c"c\00"

define void @main() #0 {
entry:
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr null)
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr null)
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr null, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__rzz__body(double 0.000000e+00, ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__barrier4__body(ptr null, ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr null)
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 1 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 2 to ptr))
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x4012D97C7F3321D2, ptr inttoptr (i64 3 to ptr))
  call void @__quantum__qis__mz__body(ptr null, ptr null)
  %0 = call i1 @__quantum__qis__read_result__body(ptr null)
  %1 = zext i1 %0 to i64
  %2 = mul i64 %1, 1
  %3 = or i64 %2, 0
  %4 = sub i64 1, %1
  %5 = mul i64 %4, 1
  %6 = xor i64 9223372036854775807, %5
  %7 = and i64 %6, %3
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 1 to ptr), ptr inttoptr (i64 1 to ptr))
  %8 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 1 to ptr))
  %9 = zext i1 %8 to i64
  %10 = mul i64 %9, 2
  %11 = or i64 %10, %7
  %12 = sub i64 1, %9
  %13 = mul i64 %12, 2
  %14 = xor i64 9223372036854775807, %13
  %15 = and i64 %14, %11
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 2 to ptr), ptr inttoptr (i64 2 to ptr))
  %16 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 2 to ptr))
  %17 = zext i1 %16 to i64
  %18 = mul i64 %17, 4
  %19 = or i64 %18, %15
  %20 = sub i64 1, %17
  %21 = mul i64 %20, 4
  %22 = xor i64 9223372036854775807, %21
  %23 = and i64 %22, %19
  call void @__quantum__qis__mz__body(ptr inttoptr (i64 3 to ptr), ptr inttoptr (i64 3 to ptr))
  %24 = call i1 @__quantum__qis__read_result__body(ptr inttoptr (i64 3 to ptr))
  %25 = zext i1 %24 to i64
  %26 = mul i64 %25, 8
  %27 = or i64 %26, %23
  %28 = sub i64 1, %25
  %29 = mul i64 %28, 8
  %30 = xor i64 9223372036854775807, %29
  %31 = and i64 %30, %27
  call void @__quantum__rt__int_record_output(i64 %31, ptr @0)
  ret void
}

declare i1 @__quantum__qis__read_result__body(ptr)

declare void @__quantum__rt__int_record_output(i64, ptr)

declare void @__quantum__qis__phasedx__body(double, double, ptr)

declare void @__quantum__qis__barrier4__body(ptr, ptr, ptr, ptr)

declare void @__quantum__qis__rzz__body(double, ptr, ptr)

declare void @__quantum__qis__mz__body(ptr, ptr writeonly) #1

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="custom" "required_num_qubits"="4" "required_num_results"="4" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 2}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
