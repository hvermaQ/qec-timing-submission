# Syntax checks on H2-1SC

Submitted through aqora as organisation `q_sq`; the syntax checker validates the QIR and returns
all-zero placeholder results, executes nothing, and (via aqora) returns no HQC price. Raw job
records: `store/hardware/<dir>/` (gitignored, local). Summary data: `syntax_checks.json`.

| date (UTC) | program | status | errors | output (registers / bits / shots) | job id |
| --- | --- | --- | --- | --- | --- |
| 20261014 | d3_X_r2_p0.05 (first attempt) | NOT SUBMITTED (refused: not authorized as personal account) | - | - / - / - | `-` |
| 20261014 | d3_X_r2_p0.05 | COMPLETED | - | 17 / 1088 / 100 | `AFByb3ZpZGVySm9iAaE5j2epfqOSWTk9CkY6Yg` |
| 20261014 | readout | COMPLETED | - | 16 / 1024 / 100 | `AFByb3ZpZGVySm9iAaE5kUXvfFC3IecROuKY0Q` |
| 20261014 | idle_X_L0 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kYuzfqCRZC7c9Ir-_A` |
| 20261014 | idle_X_L16 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kc86eQCEfIHFNpd6Uw` |
| 20261014 | idle_X_L2 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5khNrcaOLGIT2SkfnDA` |
| 20261014 | idle_X_L32 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kl9reICrINTQr5a5LA` |
| 20261014 | idle_X_L4 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kqI5f_KF91WxvQMtFA` |
| 20261014 | idle_X_L64 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5kuc3fBOUxOBkXghNuw` |
| 20261014 | idle_X_L8 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lDkXcFCOqFjrFM9jiw` |
| 20261014 | idle_Z_L0 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lH7ad0Oui6Ga7AxVHQ` |
| 20261014 | idle_Z_L16 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lMbnf2GDqbu5v_z9cQ` |
| 20261014 | idle_Z_L2 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lQ12eKCn3ClKuO2I5w` |
| 20261014 | idle_Z_L32 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lVB3fxG5GUoXUpsZCg` |
| 20261014 | idle_Z_L4 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5lZTmcjCB7vuzJPkf4Q` |
| 20261014 | idle_Z_L64 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5ldm3cwGN-uXRB3Rz2Q` |
| 20261014 | idle_Z_L8 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE5liDwdYCN1zkmlslnfg` |
| 20261014 | d3_X_r2_p0.05 (first attempt) | NOT SUBMITTED (refused: not authorized as personal account) | - | - / - / - | `-` |
| 20261014 | d3_X_r2_p0 | COMPLETED | - | 17 / 1088 / 100 | `AFByb3ZpZGVySm9iAaE5yRtgfHOPea8Ntwvc1Q` |
| 20261014 | idleT_X_L0 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6HrR0erCJB7UhtJIMRw` |
| 20261014 | idleT_X_L2 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6Hvm-ckOhQm91qUU9WQ` |
| 20261014 | idleT_X_L4 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6Hz3ldGOQjaeqh3ES8g` |
| 20261014 | idleT_X_L8 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6H4WxeEO8NnvKjy7llQ` |
| 20261014 | idleT_X_L16 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6H8nMeoG1MOYvC43pEw` |
| 20261014 | idleT_Z_L0 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6IA2QfcCBqZz1muCdpQ` |
| 20261014 | idleT_Z_L2 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6IFEkf0CirkPqdbKs4A` |
| 20261014 | idleT_Z_L4 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6IJjScdKNM5MIAgIZGQ` |
| 20261014 | idleT_Z_L8 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6INwwf4KdNWP4fInl2Q` |
| 20261014 | idleT_Z_L16 | COMPLETED | - | 9 / 576 / 100 | `AFByb3ZpZGVySm9iAaE6ISV7f2OtKl0Jdv0ZHg` |
