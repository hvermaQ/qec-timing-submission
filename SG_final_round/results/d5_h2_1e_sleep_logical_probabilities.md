# d=5 H2-1E sleep experiments: logical error probabilities

Status: {'REJECTED': 28, 'COMPLETED': 5, 'WAITING': 1} across 34 unique execution attempts. Completed shots: 2667. Rejected requests are not counted as zero-failure experiments. Waiting jobs have no logical estimate. No provider submissions were made during analysis.

Fixed phenomenological MWPM: p_data=.002, p_read=.001, lambda=0, final readout .001; d=5 topology. No weights were optimized using these outcomes. These are probabilities per complete experiment, not per-round or per-second rates.

| Requested sleep T (s) | N | Delta t (s) | Failures / shots | P_L | 95% Wilson interval |
|---:|---:|---:|---:|---:|---:|
| 1.0 | 2 | 1 | 72/500 | 14.400% | 11.594–17.749% |
| 1.0 | 3 | 0.5 | 6/500 | 1.200% | 0.551–2.593% |
| 1.0 | 4 | 0.3333333 | 3/500 | 0.600% | 0.204–1.749% |
| 1.0 | 5 | 0.25 | 4/500 | 0.800% | 0.312–2.039% |
| 1.0 | 6 | 0.2 | 2/667 | 0.300% | 0.082–1.087% |

Raw packed shots match provider-formatted joint counts; all outputs are Boolean with the expected 25 data tags and 12 syndrome tags per round. Bitcode and raw-result hashes were verified. The measured logical parity was independently checked on q0,q5,q10,q15,q20. Ideal and logical-Z boundary cases were checked for every decoder. Sensitivity counts at p_data=.02,.1 are retained in JSON.

Extraction duration is neglected; physical overlap of the all-data sleeps is unverified. The decoder is phenomenological, not a calibrated circuit-level model. Wilson intervals cover independent shot sampling only. T=1 and T=0.5 experiments are kept separate. Missing settings near 0.15 s prevent a resolved optimum claim.

## All execution attempts

| N | Requested sleep T (s) | Shots | State | Job ID |
|---:|---:|---:|---|---|
| 10 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9iK3cuK59BWB1zUo0A |
| 10 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9irrc5Oy6Rirz_lVnQ |
| 10 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9jN4cGGXUP8knXS_kg |
| 10 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9jwLcnCWLjhUkCT3Nw |
| 15 | 1 | 250 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9kYJf7ObRfJdgEOS_A |
| 15 | 1 | 250 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9k8yfOG_cSlARv8gOg |
| 20 | 1 | 250 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9lfucLKDjtIjg0HJHQ |
| 20 | 1 | 250 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9mEwfZCiyHyVfkucJQ |
| 2 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGh9ZhIdJKUHjfzj6faKQ |
| 3 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGh9aIpeOCwZYpJAaxv0A |
| 4 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGh9azpeLGTJGRxMyDT9g |
| 5 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGh9bNPfRKRYbLP8CHB1A |
| 6 | 1 | 667 | COMPLETED | AFByb3ZpZGVySm9iAaGh9boXefKot0ydZs8b_g |
| 6 | 1 | 667 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9cCpc-KAS2IUCMhHpw |
| 6 | 1 | 666 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9ceocMOdDJp_8suX8Q |
| 7 | 1 | 667 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9c9hfSOTqmh-A025aA |
| 7 | 1 | 667 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9dxOenOJWfSwJ581PA |
| 7 | 1 | 666 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9ePMfyG474vJxxk8rw |
| 8 | 1 | 667 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9exbdyKKSB_WN4nDJw |
| 8 | 1 | 667 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9fOPdIGcuM-BstWgbg |
| 8 | 1 | 666 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9fq8cHGX6AAV1dZxiQ |
| 9 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9gIcfIKvPnIZM-L69w |
| 9 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9gl7ekKA1Vfv7HVUqA |
| 9 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9hEafOCZNWgGwBLx-g |
| 9 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh9hjDfjCjVdpTCjVZ4g |
| 3 | 0.5 | 500 | WAITING | AFByb3ZpZGVySm9iAaGiJxjQcFGyRWIw7DeXng |
| 4 | 0.5 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGiJyCKefGbdVOiWWhP5g |
| 5 | 0.5 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGiJymRdgCZZZjwNN-wdA |
| 6 | 0.5 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGiJzNJfFOtCJb0tPfnCA |
| 10 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_dbTdWCnwYHAmMvzPg |
| 15 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_eAme2K1z37mueIhtA |
| 7 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_btJc1OSp-sympp0wQ |
| 8 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_cTddPCWfnpLGd-2ng |
| 9 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_czneAKE7ptaWtC-tA |
