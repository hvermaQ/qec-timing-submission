# All-shot d=3 X-memory fixed-requested-sleep analysis

H2-1E, 18 unique execution jobs, 13,000 shots. Only the coarse, refinement and resolution fixed-sleep batches are pooled; no two-round variable-total-sleep sweep or H2-2E shots. Raw hashes and formatted/packed counts verified. Repeated N used identical bitcode across batches; platform, requested interval and emulator options match. No provider jobs submitted or modified.

Nine data qubits, four X stabilizer checks per extraction round with a reused ancilla, initial logical + state and final X readout. N rounds separated by N-1 sleep blocks. u=Delta t=1/(N-1) seconds, total requested sleep one second per data qubit. Extraction duration is neglected; physical parallel overlap of the nine sleep calls remains unverified.

Fixed phenomenological MWPM: p_data=.002, p_read=.001, lambda=0; not calibrated circuit-level DEM. The same weights are retained for every batch and have not been optimized on these outcomes. Failure is decoder-predicted logical flip XOR final X parity on q0,3,6.

| N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |
|---:|---:|---:|---:|---:|
| 2 | 1 | 59/500 | 11.800% | 9.259–14.923% |
| 3 | 0.5 | 17/500 | 3.400% | 2.133–5.377% |
| 4 | 0.3333333 | 34/2000 | 1.700% | 1.219–2.366% |
| 5 | 0.25 | 24/2000 | 1.200% | 0.808–1.779% |
| 6 | 0.2 | 28/2000 | 1.400% | 0.970–2.016% |
| 7 | 0.1666667 | 28/2000 | 1.400% | 0.970–2.016% |
| 8 | 0.1428571 | 38/2000 | 1.900% | 1.387–2.597% |
| 10 | 0.1111111 | 22/1000 | 2.200% | 1.457–3.309% |
| 20 | 0.05263158 | 19/500 | 3.800% | 2.446–5.858% |
| 40 | 0.02564103 | 43/500 | 8.600% | 6.447–11.384% |

Sample minimum: N=5, Delta t=0.25 s. Neighboring settings must be compared with sampling uncertainty; selection was adaptive after earlier batches, so minimum claims are exploratory.

## Analytical fits

Binomial maximum likelihood on all ten pooled failure counts; no least-squares fit to percentages. Fix alpha=g(d+1)/2=1.6 using the paper g=.8, extrapolated to d=3. Probabilities are modeled directly using the paper low-probability approximation P_L approximately R T with T_sleep=1 s; no saturation correction. C absorbs all distance/prefactor factors. This is a descriptive fit, not extraction of microscopic error parameters.

Paper-shaped linear-idle ansatz: P_L(u)=C(1+a u)^1.6/u; u*=1/(.6a). Quadratic-idle extension: P_L(u)=C(1+a u^2)^1.6/u; u*=1/sqrt(2.2a). The latter substitutes quadratic growth for linear growth; it is an empirical extension, not Eq. 6 of the paper or the full Quantinuum noise model. Both have two fitted positive parameters.

- paper_linear: C=0.00084330725, a=8.9881408; u*=0.18543 s (conditional 95% parametric-bootstrap interval 0.12145–0.27666 s); binomial deviance=114.5, df=8; asymptotic goodness-of-fit p=4.5034e-21, bootstrap p=0.000999 (1,000 replicates, seed 20261103). If a model fails goodness of fit, its optimum interval is not a reliable physical confidence interval.
- quadratic_extension: C=0.0017706343, a=11.585533; u*=0.19808 s (conditional 95% parametric-bootstrap interval 0.18072–0.22474 s); binomial deviance=9.75, df=8; asymptotic goodness-of-fit p=0.28301, bootstrap p=0.31169 (1,000 replicates, seed 20261103). If a model fails goodness of fit, its optimum interval is not a reliable physical confidence interval.

Pooled-batch homogeneity check: deviance=12.561, df=8, asymptotic p=0.12787. This is a limited check for between-batch differences at repeated N, not proof of independence or stationary noise.

## Conclusion

The sample minimum is 1.20% at N=5 (u=.25 s), while N=6 and N=7 are both 1.40%. These neighboring settings do not establish a unique discrete optimum. Both tails are substantially higher, supporting an interior region of improved memory performance for this implementation and decoder.

The paper-shaped fit with fixed g=.8 is strongly rejected by the pooled data (deviance 114.51 on 8 degrees of freedom). The quadratic-idle extension gives an acceptable descriptive fit (deviance 9.75 on 8 degrees of freedom) and a smooth optimum near .198 s, conditional 95% bootstrap interval .181–.225 s. Its minimum fitted probability is about 1.63%. The bootstrap bounds are conditional on the chosen curve, fixed exponent, independent binomial shots and neglected extraction duration; they exclude systematic uncertainty.

[Quantinuum documentation](https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html) describes both linear and quadratic dephasing, with quadratic dephasing represented by stochastic Z faults in stabilizer simulation. This motivates trying a quadratic extension; its success alone does not identify a microscopic noise law.

## Comparison with the paper

[Haug, Bharti and Aolita, arXiv:2608.06242v2](https://arxiv.org/html/2608.06242v2), Eqs. 5–6, predicts u*=2/[lambda(g(d+1)-2)]; d=3, g=.8 gives u*=1/(.6 lambda). Its assumptions include approximately linear idle probability, small logical probability and sufficiently many rounds to suppress time-like faults. The physical idle slope is p lambda, so lambda is relative to extraction noise, not simply an absolute idle rate or the sleep-unit conversion.

Fitting lambda to these same logical probabilities and substituting it into Eq. 6 is an internal consistency calculation, not an independent prediction. We have no separately calibrated phenomenological p, lambda and g for this circuit/backend. Quantinuum circuit-level noise includes gate/readout/transport contributions and non-linear dephasing; the decoder is deliberately phenomenological and mismatched. Small N has substantial finite-round and boundary effects (N rounds but N-1 intervals). Thus disagreement with the simple paper fit need not contradict its derivation.

The two tails versus intermediate intervals can support a timing tradeoff within this decoder/setup. They cannot establish the paper 1/d scaling from a single distance, a unique best intermediate N, or a physically calibrated optimum. Error bars cover independent shot sampling only, not decoder mismatch, batching drift, uncertain overlap or extraction duration. The quadratic extension was selected after examining this experiment and its known non-linear idle model; model comparisons are exploratory.

## Provenance and reproducibility

The JSON beside this report records each job ID, source directory, raw SHA-256 and per-batch decoded failures. All stored DEMs are under results/decoders/d3_fixed_sleep_all_shots. Run the companion analysis with the established NumPy/Stim/PyMatching/SciPy environment. Preserve earlier reports; this report supersedes their shot totals only for the same fixed-sleep protocol.
