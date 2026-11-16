# Sleep-dependent phenomenological MWPM: all saved H2-1E d=3 shots

13,000 shots, 18 jobs, N=2,3,4,5,6,7,8,10,20,40. Same fixed-requested-sleep dataset and logical observable as the original PDF. Each raw-file hash and submitted-bitcode hash verified; no duplicate jobs; original baseline failure counts reproduced exactly at every N. No provider access, new jobs, HQCs or injected noise.

Result: the two DEMs have different fault probabilities/weights, but predict identical logical corrections on every recorded shot. Updated probabilities and confidence intervals therefore exactly equal the baseline. This reweighting provides no observed decoding gain; it does not show that the physical idle probability is independent of sleep.

## Fixed model (no training or tuning on outcomes)

Use published H2-1E linear rate r=.0028/s, quadratic frequency nu=.043 cycles/s (units 2*pi rad/s), and stabilizer incoherence factor m=2. Thus p_lin(u)=r*u, p_quad(u)=sin(pi*nu*m*u)^2. Independent Z channels compose by odd parity, p_idle=p_lin+p_quad-2*p_lin*p_quad; two Z faults cancel.

Retain original phenomenological extraction floor p_ext=.002 and symmetric syndrome/final-readout flip probability p_read=.001. These are baseline assumptions, not newly derived from gate specifications. First-round p_data=.002, and the remaining N-1 rounds use p_data=p_ext+p_idle-2*p_ext*p_idle. Exactly N-1 modeled sleep intervals, none before first extraction or after last. The independent ideal-product-check model and PyMatching algorithm are unchanged.

This adds time dependence to matching weights, not to already-recorded shots. The quoted published defaults are not independently confirmed execution-time parameters. Each qubit is assumed to experience exactly u of additional idling per gap; physical parallel overlap and detailed transport/extraction timing remain unverified. Readout asymmetry and gate-correlated faults are not added.

| N | u (s) | p_idle(u) | p_data after sleep | Baseline P_L | Updated failures / shots | Updated P_L | 95% Wilson interval | Corrected / new failures |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 0.07363775 | 0.0753432 | 11.80% | 59/500 | 11.80% | 9.26-14.92% | 0 / 0 |
| 3 | 0.5 | 0.01948737 | 0.02140942 | 3.40% | 17/500 | 3.40% | 2.13-5.38% | 0 / 0 |
| 4 | 0.3333333 | 0.009006952 | 0.01097092 | 1.70% | 34/2000 | 1.70% | 1.22-2.37% | 0 / 0 |
| 5 | 0.25 | 0.005248913 | 0.007227918 | 1.20% | 24/2000 | 1.20% | 0.81-1.78% | 0 / 0 |
| 6 | 0.2 | 0.003473716 | 0.005459821 | 1.40% | 28/2000 | 1.40% | 0.97-2.02% | 0 / 0 |
| 7 | 0.1666667 | 0.002491061 | 0.004481097 | 1.40% | 28/2000 | 1.40% | 0.97-2.02% | 0 / 0 |
| 8 | 0.1428571 | 0.001887775 | 0.003880224 | 1.90% | 38/2000 | 1.90% | 1.39-2.60% | 0 / 0 |
| 10 | 0.1111111 | 0.00121146 | 0.003206614 | 2.20% | 22/1000 | 2.20% | 1.46-3.31% | 0 / 0 |
| 20 | 0.05263158 | 0.0003494991 | 0.002348101 | 3.80% | 19/500 | 3.80% | 2.45-5.86% | 0 / 0 |
| 40 | 0.02564103 | 0.0001197791 | 0.0021193 | 8.60% | 43/500 | 8.60% | 6.45-11.38% | 0 / 0 |

Updated sample minimum: N=5, u=0.25 s, 24/2000=1.20%. This sample minimum is not a uniquely established optimum.

Paired comparison across all recorded shots: 0 baseline failures corrected, 0 new failures introduced, net 0 fewer failures. Exact two-sided McNemar p=1, testing symmetric decoder discordances under independent-shot assumptions. This aggregate describes the actual unequal shot allocation across settings, not a uniform-N average or a memory operating point. Per-setting paired comparisons are exploratory and unadjusted for multiple testing.

Probabilities are per full experiment. The requested-sleep-normalized rate is P_L/(1 s); actual total-time rates remain unknown because extraction duration is neglected. Wilson intervals cover shot sampling only, not model or scheduling uncertainty. No smooth functional fit is used: plotted connecting lines are guides to the eye. A more realistic DEM need not improve this finite dataset, and improvement here does not identify the true backend noise model. The decoder policy was chosen after inspecting prior experiments, so this is an exploratory comparison, despite no numerical training on logical labels.

## Sources and artifacts

- https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html
- https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html
- JSON: all per-setting parameters, raw/bitcode hashes and per-batch failure counts.
- NPZ: baseline/updated per-shot predictions and failure masks, ordered by JSON sources and offsets.
- results/decoders/d3_sleep_dependent/nN.dem: exact matching models; SHA-256 in JSON.
- Baseline files and PDF were preserved.
