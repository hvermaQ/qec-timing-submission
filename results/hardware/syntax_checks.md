# Syntax checks on H2-1SC (2026-10-14)

Submitted through aqora as organisation `q_sq`; the syntax checker validates the QIR and returns
all-zero placeholder results, executes nothing, and (via aqora) returns no HQC price. Raw job
records: `store/hardware/<dir>/` (gitignored, local). Summary data: `syntax_checks.json`.

| program | status | errors | output (registers / bits / shots) | job id |
| --- | --- | --- | --- | --- |
| d3_X_r2_p0.05 (first attempt) | NOT SUBMITTED (refused: not authorized as personal account) | - | - / - / - | `-` |
| d3_X_r2_p0.05 | COMPLETED | - | 17 / 1088 / 100 | `AFByb3ZpZGVySm9iAaE5j2epfqOSWTk9CkY6Yg` |
| readout | COMPLETED | - | 16 / 1024 / 100 | `AFByb3ZpZGVySm9iAaE5kUXvfFC3IecROuKY0Q` |
| idle_X_L0 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kYuzfqCRZC7c9Ir-_A` |
| idle_X_L16 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kc86eQCEfIHFNpd6Uw` |
| idle_X_L2 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5khNrcaOLGIT2SkfnDA` |
| idle_X_L32 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kl9reICrINTQr5a5LA` |
| idle_X_L4 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kqI5f_KF91WxvQMtFA` |
| idle_X_L64 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kuc3fBOUxOBkXghNuw` |
| idle_X_L8 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lDkXcFCOqFjrFM9jiw` |
| idle_Z_L0 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lH7ad0Oui6Ga7AxVHQ` |
| idle_Z_L16 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lMbnf2GDqbu5v_z9cQ` |
| idle_Z_L2 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lQ12eKCn3ClKuO2I5w` |
| idle_Z_L32 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lVB3fxG5GUoXUpsZCg` |
| idle_Z_L4 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lZTmcjCB7vuzJPkf4Q` |
| idle_Z_L64 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5ldm3cwGN-uXRB3Rz2Q` |
| idle_Z_L8 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5liDwdYCN1zkmlslnfg` |
