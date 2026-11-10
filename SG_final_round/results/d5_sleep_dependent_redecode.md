# d=5 H2-1E: pooled raw data and sleep-dependent DEM comparison

20 unique completed jobs; 10167 total shots. All completed d=5 H2-1E sleep runs recorded locally are included once. Total requested sleep is retained as a grouping key; T=1 and T=0.5 are never pooled together. No jobs submitted.

## Decoder policy

Fixed baseline: p_data=.002 before each ideal extraction round; syndrome and final data readout flips .001. Sleep-dependent: retain p_ext=.002 and readout .001; p_lin(u)=.0028u, p_quad(u)=sin(pi*.043*2*u)^2, p_idle=p_lin+p_quad-2*p_lin*p_quad. First extraction has p_ext only; each later extraction has p_ext+p_idle-2*p_ext*p_idle. There are exactly N-1 sleep contributions. This reproduces the existing d=3 sleep-dependent prescription with d=5 code geometry, with no fitting to d=5 logical labels. Published-default assumptions transferred by this policy are not execution-time calibration parameters. Gate correlations, detailed transport/extraction durations and readout asymmetry are omitted.

## Paired comparison on the same expanded dataset

| T (s) | N | Delta t (s) | Shots | Fixed failures | Fixed P_L | Sleep failures | Sleep P_L | Sleep 95% Wilson CI | Change in failures | Corrected / introduced |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | 3 | 0.25 | 500 | 1 | 0.200% | 0 | 0.000% | 0.000–0.762% | -1 | 1 / 0 |
| 1.0 | 2 | 1 | 1000 | 148 | 14.800% | 146 | 14.600% | 12.547–16.924% | -2 | 3 / 1 |
| 1.0 | 3 | 0.5 | 1000 | 25 | 2.500% | 25 | 2.500% | 1.699–3.665% | +0 | 2 / 2 |
| 1.0 | 4 | 0.3333333 | 1500 | 19 | 1.267% | 19 | 1.267% | 0.812–1.970% | +0 | 3 / 3 |
| 1.0 | 5 | 0.25 | 1500 | 22 | 1.467% | 17 | 1.133% | 0.709–1.808% | -5 | 5 / 0 |
| 1.0 | 6 | 0.2 | 1667 | 19 | 1.140% | 21 | 1.260% | 0.825–1.918% | +2 | 1 / 3 |
| 1.0 | 7 | 0.1666667 | 1500 | 22 | 1.467% | 21 | 1.400% | 0.917–2.131% | -1 | 2 / 1 |
| 1.0 | 8 | 0.1428571 | 500 | 9 | 1.800% | 9 | 1.800% | 0.950–3.385% | +0 | 0 / 0 |
| 1.0 | 9 | 0.125 | 500 | 11 | 2.200% | 11 | 2.200% | 1.233–3.896% | +0 | 0 / 0 |
| 1.0 | 10 | 0.1111111 | 500 | 10 | 2.000% | 10 | 2.000% | 1.090–3.642% | +0 | 0 / 0 |

## Distinguishing new shots from new decoder weights

All downloaded repeats are pooled by requested total sleep and extraction count. Differences between the earlier report and the new fixed column are due to this additional data. Differences between fixed and sleep-dependent columns above are solely from re-decoding identical shots. Every previously reported per-job fixed count was reproduced exactly.

| T (s) | N | Earlier reported fixed failures / shots | Added shots | Expanded fixed failures / shots |
|---:|---:|---:|---:|---:|
| 0.5 | 3 | 1/500 | 0 | 1/500 |
| 1.0 | 2 | 72/500 | 500 | 148/1000 |
| 1.0 | 3 | 6/500 | 500 | 25/1000 |
| 1.0 | 4 | 3/500 | 1000 | 19/1500 |
| 1.0 | 5 | 4/500 | 1000 | 22/1500 |
| 1.0 | 6 | 13/1167 | 500 | 19/1667 |
| 1.0 | 7 | 14/1000 | 500 | 22/1500 |
| 1.0 | 8 | 9/500 | 0 | 9/500 |
| 1.0 | 9 | 11/500 | 0 | 11/500 |
| 1.0 | 10 | 10/500 | 0 | 10/500 |

Across all groups, 17 fixed-decoder failures were corrected and 10 failures were introduced; net failure-count change -7. Exact paired McNemar p=0.247789. This aggregate reflects this shot allocation across different N and T; it is not an operating-point probability. Per-N paired tests are exploratory and unadjusted for multiple comparisons.

Probabilities are per complete experiment. Wilson intervals assume independent common-probability shots and exclude decoder/calibration uncertainty and batch drift. The N=6 original/repeat discrepancy remains relevant after pooling; all per-batch counts are retained below. The model is more sleep-aware but is not guaranteed to improve every setting or match the backend. A sample minimum is not a resolved optimum.

## Per-batch provenance

| T (s) | N | Job ID | Shots | Fixed failures | Sleep failures |
|---:|---:|---|---:|---:|---:|
| 0.5 | 3 | AFByb3ZpZGVySm9iAaGiJxjQcFGyRWIw7DeXng | 500 | 1 | 0 |
| 1.0 | 2 | AFByb3ZpZGVySm9iAaGh9ZhIdJKUHjfzj6faKQ | 500 | 72 | 71 |
| 1.0 | 2 | AFByb3ZpZGVySm9iAaGryB9geWGIbBY4dHZ1ww | 500 | 76 | 75 |
| 1.0 | 3 | AFByb3ZpZGVySm9iAaGh9aIpeOCwZYpJAaxv0A | 500 | 6 | 7 |
| 1.0 | 3 | AFByb3ZpZGVySm9iAaGryCY-dAKTG0COOdEjew | 500 | 19 | 18 |
| 1.0 | 4 | AFByb3ZpZGVySm9iAaGh9azpeLGTJGRxMyDT9g | 500 | 3 | 4 |
| 1.0 | 4 | AFByb3ZpZGVySm9iAaGryCzRdQOG8a2sG7U1Tw | 500 | 8 | 8 |
| 1.0 | 4 | AFByb3ZpZGVySm9iAaGv6EbJeTKvBA-Q9WkKbQ | 500 | 8 | 7 |
| 1.0 | 5 | AFByb3ZpZGVySm9iAaGh9bNPfRKRYbLP8CHB1A | 500 | 4 | 3 |
| 1.0 | 5 | AFByb3ZpZGVySm9iAaGryDOLfmCKlw7lMR61nA | 500 | 9 | 8 |
| 1.0 | 5 | AFByb3ZpZGVySm9iAaGv6E4ccRCljMC6g2enaA | 500 | 9 | 6 |
| 1.0 | 6 | AFByb3ZpZGVySm9iAaGh9boXefKot0ydZs8b_g | 667 | 2 | 2 |
| 1.0 | 6 | AFByb3ZpZGVySm9iAaGraNgndfKmvFzoRE9qSA | 500 | 11 | 12 |
| 1.0 | 6 | AFByb3ZpZGVySm9iAaGv6FVnflOnZPZ72gOJkQ | 500 | 6 | 7 |
| 1.0 | 7 | AFByb3ZpZGVySm9iAaGrME4YcAOsrYEdogemeg | 500 | 8 | 7 |
| 1.0 | 7 | AFByb3ZpZGVySm9iAaGraN-BeKK5t0wHR8-q-A | 500 | 6 | 5 |
| 1.0 | 7 | AFByb3ZpZGVySm9iAaGv6F0af1O0ml6Uj54GWg | 500 | 8 | 9 |
| 1.0 | 8 | AFByb3ZpZGVySm9iAaGrMc27dICj6c3unJaTMA | 500 | 9 | 9 |
| 1.0 | 9 | AFByb3ZpZGVySm9iAaGrMdU5dnGPvqZKW5OjFA | 500 | 11 | 11 |
| 1.0 | 10 | AFByb3ZpZGVySm9iAaGrMd0ne9GRdlyOgakfww | 500 | 10 | 10 |

Artifacts: JSON contains all parameters, per-job provenance, offsets, hashes, DEM paths and paired tests. NPZ contains paired per-shot predictions and failure masks. The separate pooled-raw NPZ contains syndrome arrays, final data readouts and per-shot source-job indices. Original provider payload files and earlier analysis snapshot were preserved.
