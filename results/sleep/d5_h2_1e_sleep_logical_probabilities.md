# d=5 H2-1E sleep experiments: logical error probabilities

Status: {'REJECTED': 34, 'COMPLETED': 20} across 54 unique execution attempts. Completed shots: 10167. Rejected requests are not counted as zero-failure experiments. Waiting jobs have no logical estimate. No provider submissions were made during analysis.

Sleep-dependent phenomenological MWPM: p_ext=.002, p_read=.001, p_lin=.0028*u, p_quad=sin(pi*.043*2*u)^2; independent flip composition; first extraction has no sleep; d=5 topology. No weights were optimized using these outcomes. These are probabilities per complete experiment, not per-round or per-second rates.

| Requested sleep T (s) | N | Delta t (s) | Failures / shots | P_L | 95% Wilson interval |
|---:|---:|---:|---:|---:|---:|
| 0.5 | 3 | 0.25 | 0/500 | 0.000% | 0.000–0.762% |
| 1.0 | 2 | 1 | 146/1000 | 14.600% | 12.547–16.924% |
| 1.0 | 3 | 0.5 | 25/1000 | 2.500% | 1.699–3.665% |
| 1.0 | 4 | 0.3333333 | 19/1500 | 1.267% | 0.812–1.970% |
| 1.0 | 5 | 0.25 | 17/1500 | 1.133% | 0.709–1.808% |
| 1.0 | 6 | 0.2 | 21/1667 | 1.260% | 0.825–1.918% |
| 1.0 | 7 | 0.1666667 | 21/1500 | 1.400% | 0.917–2.131% |
| 1.0 | 8 | 0.1428571 | 9/500 | 1.800% | 0.950–3.385% |
| 1.0 | 9 | 0.125 | 11/500 | 2.200% | 1.233–3.896% |
| 1.0 | 10 | 0.1111111 | 10/500 | 2.000% | 1.090–3.642% |

Raw packed shots match provider-formatted joint counts; all outputs are Boolean with the expected 25 data tags and 12 syndrome tags per round. Bitcode and raw-result hashes were verified. The measured logical parity was independently checked on q0,q5,q10,q15,q20. Ideal and logical-Z boundary cases were checked for every decoder. Fixed-DEM sensitivity counts at p_data=.002,.02,.1 are retained in JSON.

Extraction duration is neglected; physical overlap of the all-data sleeps is unverified. The decoder is phenomenological, not a calibrated circuit-level model. Wilson intervals cover independent shot sampling only. T=1 and T=0.5 experiments are kept separate. Nearby settings have few failures and overlapping sampling intervals; the observed minimum does not establish a unique optimum.

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
| 10 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGrMd0ne9GRdlyOgakfww |
| 8 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGrMc27dICj6c3unJaTMA |
| 9 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGrMdU5dnGPvqZKW5OjFA |
| 3 | 0.5 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGiJxjQcFGyRWIw7DeXng |
| 4 | 0.5 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGiJyCKefGbdVOiWWhP5g |
| 5 | 0.5 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGiJymRdgCZZZjwNN-wdA |
| 6 | 0.5 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGiJzNJfFOtCJb0tPfnCA |
| 10 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGq39nKflO9amddS-lGKw |
| 7 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGq38HYcwOsAfg6F5_7hg |
| 8 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGq38piceGCgFM9sTHrHA |
| 9 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGq39HIfOOx8NHn3VxBcA |
| 10 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_dbTdWCnwYHAmMvzPg |
| 15 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_eAme2K1z37mueIhtA |
| 7 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_btJc1OSp-sympp0wQ |
| 8 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_cTddPCWfnpLGd-2ng |
| 9 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGh_czneAKE7ptaWtC-tA |
| 7 | 1 | 100 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGrBBykcRCUvPyJjdPP_A |
| 7 | 1 | 500 | Job cost exceeds allowed cost (code: 1002) | AFByb3ZpZGVySm9iAaGrAP2_edKvWuXitEdbbw |
| 7 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGrME4YcAOsrYEdogemeg |
| 6 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGraNgndfKmvFzoRE9qSA |
| 7 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGraN-BeKK5t0wHR8-q-A |
| 2 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGryB9geWGIbBY4dHZ1ww |
| 3 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGryCY-dAKTG0COOdEjew |
| 4 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGryCzRdQOG8a2sG7U1Tw |
| 5 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGryDOLfmCKlw7lMR61nA |
| 4 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGv6EbJeTKvBA-Q9WkKbQ |
| 5 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGv6E4ccRCljMC6g2enaA |
| 6 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGv6FVnflOnZPZ72gOJkQ |
| 7 | 1 | 500 | COMPLETED | AFByb3ZpZGVySm9iAaGv6F0af1O0ml6Uj54GWg |
