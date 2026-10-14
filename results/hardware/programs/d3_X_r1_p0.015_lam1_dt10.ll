; ModuleID = 'hugr-qir'
source_filename = "hugr-qir"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128"
target triple = "aarch64-unknown-linux-gnu"

%Qubit = type opaque
%Result = type opaque

@0 = private unnamed_addr constant [5 x i8] c"s0_0\00", align 1
@1 = private unnamed_addr constant [5 x i8] c"s0_1\00", align 1
@2 = private unnamed_addr constant [5 x i8] c"s0_2\00", align 1
@3 = private unnamed_addr constant [5 x i8] c"s0_3\00", align 1
@4 = private unnamed_addr constant [3 x i8] c"m0\00", align 1
@5 = private unnamed_addr constant [3 x i8] c"m1\00", align 1
@6 = private unnamed_addr constant [3 x i8] c"m2\00", align 1
@7 = private unnamed_addr constant [3 x i8] c"m3\00", align 1
@8 = private unnamed_addr constant [3 x i8] c"m4\00", align 1
@9 = private unnamed_addr constant [3 x i8] c"m5\00", align 1
@10 = private unnamed_addr constant [3 x i8] c"m6\00", align 1
@11 = private unnamed_addr constant [3 x i8] c"m7\00", align 1
@12 = private unnamed_addr constant [3 x i8] c"m8\00", align 1
@gen_name = private unnamed_addr constant [8 x i8] c"hugr-qir", section ",qir_generator"
@gen_version = private unnamed_addr constant [5 x i8] c"0.1.2", section ",qir_generator"

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
  %rintb = tail call i32 @___random_int_bounded(i32 1048576)
  %1 = icmp slt i32 %rintb, 159596
  br i1 %1, label %bb, label %cond_exit_878

bb:                                               ; preds = %alloca_block
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* null)
  br label %cond_exit_878

cond_935_case_1:                                  ; preds = %cond_exit_878, %bb0
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  %rintb384 = tail call i32 @___random_int_bounded(i32 1048576)
  %2 = icmp slt i32 %rintb384, 159596
  br i1 %2, label %bb1, label %cond_992_case_1

cond_exit_878:                                    ; preds = %bb, %alloca_block
  %rintb284 = tail call i32 @___random_int_bounded(i32 1048576)
  %3 = icmp slt i32 %rintb284, 159596
  br i1 %3, label %bb0, label %cond_935_case_1

bb0:                                              ; preds = %cond_exit_878
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  br label %cond_935_case_1

cond_992_case_1:                                  ; preds = %cond_935_case_1, %bb1
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  %rintb491 = tail call i32 @___random_int_bounded(i32 1048576)
  %4 = icmp slt i32 %rintb491, 159596
  br i1 %4, label %bb2, label %cond_exit_1049

bb1:                                              ; preds = %cond_935_case_1
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 2 to %Qubit*))
  br label %cond_992_case_1

bb2:                                              ; preds = %cond_992_case_1
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 3 to %Qubit*))
  br label %cond_exit_1049

cond_1106_case_1:                                 ; preds = %cond_exit_1049, %bb3
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  %rintb674 = tail call i32 @___random_int_bounded(i32 1048576)
  %5 = icmp slt i32 %rintb674, 159596
  br i1 %5, label %bb4, label %cond_1435_case_1

cond_exit_1049:                                   ; preds = %bb2, %cond_992_case_1
  %rintb574 = tail call i32 @___random_int_bounded(i32 1048576)
  %6 = icmp slt i32 %rintb574, 159596
  br i1 %6, label %bb3, label %cond_1106_case_1

bb3:                                              ; preds = %cond_exit_1049
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 4 to %Qubit*))
  br label %cond_1106_case_1

cond_1435_case_1:                                 ; preds = %cond_1106_case_1, %bb4
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* null)
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %7 = tail call i1 @__quantum__rt__read_result(%Result* null)
  br i1 %7, label %cond_1417_case_1, label %cond_exit_1417

bb4:                                              ; preds = %cond_1106_case_1
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 5 to %Qubit*))
  br label %cond_1435_case_1

cond_1417_case_1:                                 ; preds = %cond_1435_case_1
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %cond_exit_1417

cond_exit_1417:                                   ; preds = %cond_1435_case_1, %cond_1417_case_1
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
  %rintb892 = tail call i32 @___random_int_bounded(i32 1048576)
  %8 = icmp slt i32 %rintb892, 159596
  br i1 %8, label %bb5, label %cond_1220_case_1

cond_1220_case_1:                                 ; preds = %cond_exit_1417, %bb5
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  %rintb999 = tail call i32 @___random_int_bounded(i32 1048576)
  %9 = icmp slt i32 %rintb999, 159596
  br i1 %9, label %bb6, label %cond_1554_case_1

bb5:                                              ; preds = %cond_exit_1417
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 6 to %Qubit*))
  br label %cond_1220_case_1

cond_1554_case_1:                                 ; preds = %cond_1220_case_1, %bb6
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 1 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %10 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 1 to %Result*))
  br i1 %10, label %cond_1536_case_1, label %cond_exit_1536

bb6:                                              ; preds = %cond_1220_case_1
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 7 to %Qubit*))
  br label %cond_1554_case_1

cond_1536_case_1:                                 ; preds = %cond_1554_case_1
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %cond_exit_1536

cond_exit_1536:                                   ; preds = %cond_1554_case_1, %cond_1536_case_1
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
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 2 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %11 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 2 to %Result*))
  br i1 %11, label %cond_1621_case_1, label %cond_exit_1621

cond_1621_case_1:                                 ; preds = %cond_exit_1536
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %cond_exit_1621

cond_exit_1621:                                   ; preds = %cond_exit_1536, %cond_1621_case_1
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
  %rintb1297 = tail call i32 @___random_int_bounded(i32 1048576)
  %12 = icmp slt i32 %rintb1297, 159596
  br i1 %12, label %bb7, label %cond_1724_case_1

cond_1724_case_1:                                 ; preds = %cond_exit_1621, %bb7
  tail call void @__quantum__qis__phasedx__body(double 0xBFF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rzz__body(double 0x3FF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*), %Result* nonnull inttoptr (i64 3 to %Result*))
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  %13 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 3 to %Result*))
  br i1 %13, label %cond_1706_case_1, label %cond_exit_1706

bb7:                                              ; preds = %cond_exit_1621
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 8 to %Qubit*))
  br label %cond_1724_case_1

cond_1706_case_1:                                 ; preds = %cond_1724_case_1
  tail call void @__quantum__qis__phasedx__body(double 0x400921FB54442D18, double 0.000000e+00, %Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  br label %cond_exit_1706

cond_exit_1706:                                   ; preds = %cond_1724_case_1, %cond_1706_case_1
  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))
  tail call void @__quantum__rt__bool_record_output(i1 %7, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @0, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %10, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @1, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %11, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @2, i64 0, i64 0))
  tail call void @__quantum__rt__bool_record_output(i1 %13, i8* getelementptr inbounds ([5 x i8], [5 x i8]* @3, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* null, %Result* nonnull inttoptr (i64 4 to %Result*))
  %14 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 4 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %14, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @4, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 1 to %Qubit*), %Result* nonnull inttoptr (i64 5 to %Result*))
  %15 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 5 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %15, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @5, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 2 to %Qubit*), %Result* nonnull inttoptr (i64 6 to %Result*))
  %16 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 6 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %16, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @6, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 3 to %Qubit*), %Result* nonnull inttoptr (i64 7 to %Result*))
  %17 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 7 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %17, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @7, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 4 to %Qubit*), %Result* nonnull inttoptr (i64 8 to %Result*))
  %18 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 8 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %18, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @8, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 5 to %Qubit*), %Result* nonnull inttoptr (i64 9 to %Result*))
  %19 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 9 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %19, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @9, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 6 to %Qubit*), %Result* nonnull inttoptr (i64 10 to %Result*))
  %20 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 10 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %20, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @10, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 7 to %Qubit*), %Result* nonnull inttoptr (i64 11 to %Result*))
  %21 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 11 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %21, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @11, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 8 to %Qubit*), %Result* nonnull inttoptr (i64 12 to %Result*))
  %22 = tail call i1 @__quantum__rt__read_result(%Result* nonnull inttoptr (i64 12 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %22, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @12, i64 0, i64 0))
  ret void
}

declare i64 @___get_current_shot() local_unnamed_addr

declare void @___random_seed(i64) local_unnamed_addr

declare void @__quantum__qis__phasedx__body(double, double, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__rz__body(double, %Qubit*) local_unnamed_addr

declare i32 @___random_int_bounded(i32) local_unnamed_addr

declare void @__quantum__qis__rzz__body(double, %Qubit*, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__mz__body(%Qubit*, %Result* writeonly) local_unnamed_addr #1

declare void @__quantum__qis__reset__body(%Qubit*) local_unnamed_addr

declare i1 @__quantum__rt__read_result(%Result* readonly) local_unnamed_addr

declare void @__quantum__rt__bool_record_output(i1, i8*) local_unnamed_addr

declare void @__quantum__rt__initialize(i8*) local_unnamed_addr

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="adaptive_profile" "required_num_qubits"="10" "required_num_results"="13" }
attributes #1 = { "irreversible" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
