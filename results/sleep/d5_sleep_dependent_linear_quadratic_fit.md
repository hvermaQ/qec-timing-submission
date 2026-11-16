# d=5 sleep-dependent DEM: linear-plus-quadratic idle fit

Uses only T_sleep=1 s sleep-dependent-DEM outcomes: N=2 through 10, 9,667 shots. Excluded N settings: []. The T_sleep=0.5 s experiment is excluded. No provider submissions, decoder retuning or injected faults.

## Model and fitting

Let x=Delta t/(1 second). P_L(x)=C/x*(1+a*x+b*x^2)^alpha, with g=.8 and alpha=g(d+1)/2=2.4 fixed to match the distance-adjusted convention used in the d=3 methodology. C,a,b are fitted by binomial maximum likelihood on failure/shot counts; a,b>=0. Both idle terms are included in the model even if a fitted coefficient reaches zero.

C=0.001652217922; a=0; b=5.423625579. Linear coefficient at boundary: True. This does not imply that the physical linear noise channel is absent.

Differentiating log(P_L) gives -1/x + alpha*(a+2*b*x)/(1+a*x+b*x^2)=0. Therefore (alpha-1)*a*x+(2*alpha-1)*b*x^2=1, or 1.4*a*x+3.8*b*x^2=1. The stable positive root is x*=2/[1.4*a+sqrt((1.4*a)^2+15.2*b)].

Analytical Delta t*=0.220274 s. Conditional 95% parametric-bootstrap interval=0.14711–0.234549 s. Fitted minimum P_L=1.314%. The root was checked against numerical minimization and the stationary equation.

Binomial deviance=2.88267; nominal residual df=6. Boundary-aware parametric-bootstrap goodness-of-fit p=0.879121, from 1000 successful refits, seed=20261105. Bootstrap intervals are conditional on this chosen model and do not establish a physically calibrated optimum.

Descriptive low-probability ansatz with fixed exponent. N rounds but N-1 waits; boundary effects and extraction durations omitted. Conditional bootstrap assumes independent common-probability shots; it excludes batch variation, decoder uncertainty and physical scheduling uncertainty. Coefficients are not microscopic emulator-noise estimates.

## Inputs

| N | Delta t (s) | Failures / shots | Measured P_L | Fitted P_L |
|---:|---:|---:|---:|---:|
| 2 | 1 | 146/1000 | 14.600% | 14.346% |
| 3 | 0.5 | 25/1000 | 2.500% | 2.584% |
| 4 | 0.3333333 | 19/1500 | 1.267% | 1.537% |
| 5 | 0.25 | 17/1500 | 1.133% | 1.332% |
| 6 | 0.2 | 21/1667 | 1.260% | 1.323% |
| 7 | 0.1666667 | 21/1500 | 1.400% | 1.388% |
| 8 | 0.1428571 | 9/500 | 1.800% | 1.488% |
| 9 | 0.125 | 11/500 | 2.200% | 1.607% |
| 10 | 0.1111111 | 10/500 | 2.000% | 1.737% |
