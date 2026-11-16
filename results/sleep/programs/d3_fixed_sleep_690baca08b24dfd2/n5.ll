; ModuleID = 'hugr-qir'
source_filename = "hugr-qir"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128"
target triple = "aarch64-unknown-linux-gnu"

%Qubit = type opaque
%Result = type opaque

@tag_0 = private constant [5 x i8] c"s0_0\00"
@tag_1 = private constant [5 x i8] c"s0_1\00"
@tag_2 = private constant [5 x i8] c"s0_2\00"
@tag_3 = private constant [5 x i8] c"s0_3\00"
@tag_4 = private constant [5 x i8] c"s1_0\00"
@tag_5 = private constant [5 x i8] c"s1_1\00"
@tag_6 = private constant [5 x i8] c"s1_2\00"
@tag_7 = private constant [5 x i8] c"s1_3\00"
@tag_8 = private constant [5 x i8] c"s2_0\00"
@tag_9 = private constant [5 x i8] c"s2_1\00"
@tag_10 = private constant [5 x i8] c"s2_2\00"
@tag_11 = private constant [5 x i8] c"s2_3\00"
@tag_12 = private constant [5 x i8] c"s3_0\00"
@tag_13 = private constant [5 x i8] c"s3_1\00"
@tag_14 = private constant [5 x i8] c"s3_2\00"
@tag_15 = private constant [5 x i8] c"s3_3\00"
@tag_16 = private constant [5 x i8] c"s4_0\00"
@tag_17 = private constant [5 x i8] c"s4_1\00"
@tag_18 = private constant [5 x i8] c"s4_2\00"
@tag_19 = private constant [5 x i8] c"s4_3\00"
@tag_20 = private constant [3 x i8] c"m0\00"
@tag_21 = private constant [3 x i8] c"m1\00"
@tag_22 = private constant [3 x i8] c"m2\00"
@tag_23 = private constant [3 x i8] c"m3\00"
@tag_24 = private constant [3 x i8] c"m4\00"
@tag_25 = private constant [3 x i8] c"m5\00"
@tag_26 = private constant [3 x i8] c"m6\00"
@tag_27 = private constant [3 x i8] c"m7\00"
@tag_28 = private constant [3 x i8] c"m8\00"
define dso_local void @__hugr__.main.1() local_unnamed_addr #0 {
alloca_block:
  tail call void @__quantum__rt__initialize(i8* null)
  %shot = tail call i64 @___get_current_shot()
  %0 = add i64 %shot, 7000000
  tail call void @___random_seed(i64 %0)
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* null)
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r0_v1 = tail call i1 @__quantum__rt__read_result(%Result* null)
  br i1 %r0_v1, label %r0_cond_941_case_1, label %r0_cond_exit_941

r0_cond_941_case_1:                                  
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r0_cond_exit_941

r0_cond_exit_941:                                    
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 1 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r0_v2 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 1 to %Result*))
  br i1 %r0_v2, label %r0_cond_1060_case_1, label %r0_cond_exit_1060

r0_cond_1060_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r0_cond_exit_1060

r0_cond_exit_1060:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 2 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r0_v3 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 2 to %Result*))
  br i1 %r0_v3, label %r0_cond_1145_case_1, label %r0_cond_exit_1145

r0_cond_1145_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r0_cond_exit_1145

r0_cond_exit_1145:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 3 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r0_v4 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 3 to %Result*))
  br i1 %r0_v4, label %r0_cond_1230_case_1, label %r0_cond_exit_1230

r0_cond_1230_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r0_cond_exit_1230

r0_cond_exit_1230:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__sleep__body(%Qubit* null, double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 1 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 2 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 3 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 4 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 5 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 6 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 7 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 8 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 4 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r1_v1 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 4 to %Result*))
  br i1 %r1_v1, label %r1_cond_941_case_1, label %r1_cond_exit_941

r1_cond_941_case_1:                                  
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r1_cond_exit_941

r1_cond_exit_941:                                    
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 5 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r1_v2 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 5 to %Result*))
  br i1 %r1_v2, label %r1_cond_1060_case_1, label %r1_cond_exit_1060

r1_cond_1060_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r1_cond_exit_1060

r1_cond_exit_1060:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 6 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r1_v3 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 6 to %Result*))
  br i1 %r1_v3, label %r1_cond_1145_case_1, label %r1_cond_exit_1145

r1_cond_1145_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r1_cond_exit_1145

r1_cond_exit_1145:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 7 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r1_v4 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 7 to %Result*))
  br i1 %r1_v4, label %r1_cond_1230_case_1, label %r1_cond_exit_1230

r1_cond_1230_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r1_cond_exit_1230

r1_cond_exit_1230:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__sleep__body(%Qubit* null, double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 1 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 2 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 3 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 4 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 5 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 6 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 7 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 8 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 8 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r2_v1 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 8 to %Result*))
  br i1 %r2_v1, label %r2_cond_941_case_1, label %r2_cond_exit_941

r2_cond_941_case_1:                                  
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r2_cond_exit_941

r2_cond_exit_941:                                    
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 9 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r2_v2 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 9 to %Result*))
  br i1 %r2_v2, label %r2_cond_1060_case_1, label %r2_cond_exit_1060

r2_cond_1060_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r2_cond_exit_1060

r2_cond_exit_1060:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 10 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r2_v3 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 10 to %Result*))
  br i1 %r2_v3, label %r2_cond_1145_case_1, label %r2_cond_exit_1145

r2_cond_1145_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r2_cond_exit_1145

r2_cond_exit_1145:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 11 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r2_v4 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 11 to %Result*))
  br i1 %r2_v4, label %r2_cond_1230_case_1, label %r2_cond_exit_1230

r2_cond_1230_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r2_cond_exit_1230

r2_cond_exit_1230:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__sleep__body(%Qubit* null, double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 1 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 2 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 3 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 4 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 5 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 6 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 7 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 8 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 12 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r3_v1 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 12 to %Result*))
  br i1 %r3_v1, label %r3_cond_941_case_1, label %r3_cond_exit_941

r3_cond_941_case_1:                                  
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r3_cond_exit_941

r3_cond_exit_941:                                    
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 13 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r3_v2 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 13 to %Result*))
  br i1 %r3_v2, label %r3_cond_1060_case_1, label %r3_cond_exit_1060

r3_cond_1060_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r3_cond_exit_1060

r3_cond_exit_1060:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 14 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r3_v3 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 14 to %Result*))
  br i1 %r3_v3, label %r3_cond_1145_case_1, label %r3_cond_exit_1145

r3_cond_1145_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r3_cond_exit_1145

r3_cond_exit_1145:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 15 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r3_v4 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 15 to %Result*))
  br i1 %r3_v4, label %r3_cond_1230_case_1, label %r3_cond_exit_1230

r3_cond_1230_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r3_cond_exit_1230

r3_cond_exit_1230:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  call void @__quantum__qis__sleep__body(%Qubit* null, double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 1 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 2 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 3 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 4 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 5 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 6 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 7 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 8 to %Qubit*), double 2.50000000000000000e-01)
  call void @__quantum__qis__barrier10__body(%Qubit* null, %Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 2 to %Qubit*), %Qubit* inttoptr (i64 3 to %Qubit*), %Qubit* inttoptr (i64 4 to %Qubit*), %Qubit* inttoptr (i64 5 to %Qubit*), %Qubit* inttoptr (i64 6 to %Qubit*), %Qubit* inttoptr (i64 7 to %Qubit*), %Qubit* inttoptr (i64 8 to %Qubit*), %Qubit* inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 16 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r4_v5 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 16 to %Result*))
  br i1 %r4_v5, label %r4_cond_1349_case_1, label %r4_cond_exit_1349

r4_cond_1349_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r4_cond_exit_1349

r4_cond_exit_1349:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 17 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r4_v6 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 17 to %Result*))
  br i1 %r4_v6, label %r4_cond_1468_case_1, label %r4_cond_exit_1468

r4_cond_1468_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r4_cond_exit_1468

r4_cond_exit_1468:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 18 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r4_v7 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 18 to %Result*))
  br i1 %r4_v7, label %r4_cond_1553_case_1, label %r4_cond_exit_1553

r4_cond_1553_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r4_cond_exit_1553

r4_cond_exit_1553:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 19 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %r4_v8 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 19 to %Result*))
  br i1 %r4_v8, label %r4_cond_1638_case_1, label %r4_cond_exit_1638

r4_cond_1638_case_1:                                 
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %r4_cond_exit_1638

r4_cond_exit_1638:                                   
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__rt__bool_record_output(i1 %r0_v1, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_0, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r0_v2, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_1, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r0_v3, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_2, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r0_v4, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_3, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r1_v1, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_4, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r1_v2, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_5, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r1_v3, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_6, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r1_v4, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_7, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r2_v1, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_8, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r2_v2, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_9, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r2_v3, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_10, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r2_v4, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_11, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r3_v1, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_12, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r3_v2, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_13, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r3_v3, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_14, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r3_v4, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_15, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r4_v5, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_16, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r4_v6, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_17, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r4_v7, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_18, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %r4_v8, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @tag_19, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* null, %Result* nonnull inttoptr (i64 20 to %Result*))
  %final_v9 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 20 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v9, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_20, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 1 to %Qubit*), %Result* nonnull inttoptr (i64 21 to %Result*))
  %final_v10 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 21 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v10, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_21, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 2 to %Qubit*), %Result* nonnull inttoptr (i64 22 to %Result*))
  %final_v11 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 22 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v11, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_22, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 3 to %Qubit*), %Result* nonnull inttoptr (i64 23 to %Result*))
  %final_v12 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 23 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v12, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_23, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 4 to %Qubit*), %Result* nonnull inttoptr (i64 24 to %Result*))
  %final_v13 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 24 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v13, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_24, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 5 to %Qubit*), %Result* nonnull inttoptr (i64 25 to %Result*))
  %final_v14 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 25 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v14, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_25, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 6 to %Qubit*), %Result* nonnull inttoptr (i64 26 to %Result*))
  %final_v15 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 26 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v15, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_26, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 7 to %Qubit*), %Result* nonnull inttoptr (i64 27 to %Result*))
  %final_v16 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 27 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v16, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_27, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 8 to %Qubit*), %Result* nonnull inttoptr (i64 28 to %Result*))
  %final_v17 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 28 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %final_v17, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @tag_28, i64 0, i64 0))
  ret void
}
declare i64 @___get_current_shot() local_unnamed_addr

declare void @___random_seed(i64) local_unnamed_addr

declare void @__quantum__qis__phasedx__body(double, double, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__rz__body(double, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__rzz__body(double, %Qubit*, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__mz__body(%Qubit*, %Result* writeonly) local_unnamed_addr #1

declare void @__quantum__qis__reset__body(%Qubit*) local_unnamed_addr

declare i1 @__quantum__rt__read_result(%Result* readonly) local_unnamed_addr

declare void @__quantum__rt__bool_record_output(i1, i8*) local_unnamed_addr

declare void @__quantum__rt__initialize(i8*) local_unnamed_addr

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="adaptive_profile" "required_num_qubits"="10" "required_num_results"="29" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}

declare void @__quantum__qis__sleep__body(%Qubit*, double)
declare void @__quantum__qis__barrier10__body(%Qubit*, %Qubit*, %Qubit*, %Qubit*, %Qubit*, %Qubit*, %Qubit*, %Qubit*, %Qubit*, %Qubit*)
