# d=3 fixed requested sleep: combined refinement results

H2-1E; total requested sleep one second. Extraction duration neglected. Fixed phenomenological PyMatching decoder, p_data=.002, p_read=.001, lambda=0. These are decoder assumptions, not injected noise.

| N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |
|---|---:|---:|---:|---:|
| 40 | 0.0256410256 | 43 / 500 | 8.60% | 6.45% - 11.38% |
| 20 | 0.0526315789 | 19 / 500 | 3.80% | 2.45% - 5.86% |
| 10 | 0.111111111 | 12 / 500 | 2.40% | 1.38% - 4.15% |
| 8 | 0.142857143 | 24 / 1000 | 2.40% | 1.62% - 3.55% |
| 7 | 0.166666667 | 12 / 1000 | 1.20% | 0.69% - 2.09% |
| 6 | 0.2 | 19 / 1000 | 1.90% | 1.22% - 2.95% |
| 5 | 0.25 | 12 / 1000 | 1.20% | 0.69% - 2.09% |
| 4 | 0.333333333 | 11 / 1000 | 1.10% | 0.62% - 1.96% |
| 2 | 1 | 59 / 500 | 11.80% | 9.26% - 14.92% |

Lowest observed probability: N=4, Delta t=0.333333333 s. This does not establish a unique optimal interval.

N=5 pools only its original fixed-sleep 500 shots with the new 500 shots; N=4,6,7,8 use new 1,000-shot batches. N=2,10,20,40 retain original 500-shot results, with both N=40 partitions included. No data are counted twice. All new/refinement packed shots match formatted counts and saved hashes. The original coarse analysis is unchanged. Error bars reflect shot sampling, not systematic decoder mismatch, scheduling uncertainty or run-to-run drift. The refinement was selected after the coarse sweep; minimum comparisons are exploratory.
