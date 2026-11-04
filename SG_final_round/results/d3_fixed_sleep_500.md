# d=3 X memory: fixed requested sleep of one second

H2-1E through Aqora; 500 shots planned per setting; available-shot denominators shown below. Extraction duration is neglected. Sleep arguments are treated as seconds; overlap remains unverified. Logical probabilities are per complete experiment.

| Rounds N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |
|---|---:|---:|---:|---:|
| 2 | 1 | 59 / 500 | 0.1180 | 0.0926 - 0.1492 |
| 5 | 0.25 | 7 / 500 | 0.0140 | 0.0068 - 0.0286 |
| 10 | 0.111111111 | 12 / 500 | 0.0240 | 0.0138 - 0.0415 |
| 20 | 0.0526315789 | 19 / 500 | 0.0380 | 0.0245 - 0.0586 |
| 40 | 0.0256410256 | 43 / 500 | 0.0860 | 0.0645 - 0.1138 |

Lowest observed probability: N=5, Delta t=0.25 s. This is a sample minimum, not automatically a statistically resolved interior optimum.

Decode with the same phenomenological MWPM prescription across N; compare sensitivity counts in JSON. All packed shots cross-checked against formatted counts. No postselection or artificial faults. One job per setting except N=40 split into two 250-shot jobs; these samples do not establish run-to-run stability. Interpretation must account for unequal extraction durations, decoder mismatch and uncertainty. Do not claim a U-shaped curve unless both sides are supported by data.
