"""Decode the fixed-one-second-sleep experiment after all jobs finish."""
import argparse
import json
from dataclasses import replace
import numpy as np
import fixed_sleep_d3 as f
from analyze_d3_sleep_sweep import unpack
from analyze_single_qubit_pilot import wilson
from qec_timing.hardware.providers import _register_builtins
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.records import bits_from_shots,record_from_bits
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder


def main(allow_partial=False):
 _register_builtins()
 base=spec_from_json(json.loads(f.SOURCE.with_suffix('.json').read_text())['spec'])
 rows=[]
 for p in f.PLAN:
  n=p['rounds'];shots=[];ids=[]
  for plan,name,count in f.jobs('execute'):
   if plan['rounds']!=n:continue
   dest=f.RUNS/'execute'/name
   j=json.loads((dest/'job.json').read_text())
   if not f.accepted(j):
    if allow_partial:continue
    raise RuntimeError(f'Incomplete {name}')
   shots+=unpack(json.loads((dest/'result_0.txt').read_text()),shots=count,n_rounds=n)
   ids.append(j['job_id'])
  if not shots:continue
  if not allow_partial:assert len(shots)==500
  total=len(shots)
  spec=replace(base,schedule=Schedule.rounds(p['delta_t_seconds'],n),shots=total)
  syn,dat=bits_from_shots(shots,n,4,9);rec=record_from_bits(spec,syn,dat)
  counts={}
  for assumed_p in [.002,.02,.1]:
   dem=dem_for(paper_graph(spec,assumed_p,0,.001))
   (f.BUILD/f'decoder_n{n}_p{assumed_p}.dem').write_text(dem)
   predicted=PyMatchingDecoder(dem).decode_batch(rec.detectors)
   counts[str(assumed_p)]=int(np.any(predicted!=rec.observables,axis=1).sum())
  k=counts['0.002']
  rows.append(dict(rounds=n,delta_t_seconds=p['delta_t_seconds'],total_requested_sleep_seconds=1,
   shots=total,complete=(total==500),logical_failures=k,logical_error_probability=k/total,wilson_95=wilson(k,total),
   raw_logical_parity_flips=int(rec.observables.sum()),decoder_sensitivity_failures=counts,
   mean_data_error=float(dat.mean()),detector_rates=rec.detectors.mean(axis=0).tolist(),job_ids=ids))
 result=dict(f.CONFIG,rows=rows,primary_decoder='fixed historical MWPM p_data=.002 p_read=.001; same prescription across N',
  interpretation='Fixed requested sleep only; extraction duration neglected; no minimum presumed')
 suffix='_partial' if allow_partial else ''
 (f.ROOT/('results/d3_fixed_sleep_500'+suffix+'.json')).write_text(json.dumps(result,indent=2)+'\n')
 lines=['# d=3 X memory: fixed requested sleep of one second','',
  'H2-1E through Aqora; 500 shots planned per setting; available-shot denominators shown below. Extraction duration is neglected. Sleep arguments are treated as seconds; overlap remains unverified. Logical probabilities are per complete experiment.','',
  '| Rounds N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |',
  '|---|---:|---:|---:|---:|']
 for r in rows:
  lo,hi=r['wilson_95'];lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.9g} | {r['logical_failures']} / {r['shots']} | {r['logical_error_probability']:.4f} | {lo:.4f} - {hi:.4f} |")
 best=min(rows,key=lambda r:r['logical_error_probability'])
 lines+=['',f"Lowest observed probability: N={best['rounds']}, Delta t={best['delta_t_seconds']:.9g} s. This is a sample minimum, not automatically a statistically resolved interior optimum.",'',
  'Decode with the same phenomenological MWPM prescription across N; compare sensitivity counts in JSON. All packed shots cross-checked against formatted counts. No postselection or artificial faults. One job per setting except N=40 split into two 250-shot jobs; these samples do not establish run-to-run stability. Interpretation must account for unequal extraction durations, decoder mismatch and uncertainty. Do not claim a U-shaped curve unless both sides are supported by data.']
 (f.ROOT/('results/d3_fixed_sleep_500'+suffix+'.md')).write_text('\n'.join(lines)+'\n')
 print(json.dumps(result,indent=2))


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--allow-partial',action='store_true')
 main(parser.parse_args().allow_partial)
