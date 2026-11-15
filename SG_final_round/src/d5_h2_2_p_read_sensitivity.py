"""Offline p_read sensitivity on the five saved physical H2-2 d=5 jobs."""
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import numpy as np
from analyze_d5_h2_2_zero_sleep_control import unpack_hardware
from h2_2_decoder import round_probabilities
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots,record_from_bits
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/d5_h2_2_t1_p_ext_0_004_3500_shots'
OUT=ROOT/'results/d5_h2_2_p_read_sensitivity'
VALUES=[.0001,.00025,.0005,.001,.002,.004,.01]


def main():
    _register_builtins()
    baseline=json.loads(SOURCE.with_suffix('.json').read_text());saved=np.load(SOURCE.with_suffix('.npz'))
    policy=json.loads((ROOT/'configs/h2_2_d5_decoder.json').read_text())
    assert baseline['decoder_policy']==policy and policy['p_ext']==.004 and policy['p_read']==.001
    base=spec_from_json(json.loads((ROOT.parent/'results/hardware/programs/d5_X_r5_p0.json').read_text())['spec'])
    records={};provenance=[]
    for row in baseline['rows']:
        n,count,u=row['rounds'],row['shots'],row['interval_seconds'];path=Path(row['raw_path']);raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['raw_sha256']
        syn,data=bits_from_shots(unpack_hardware(json.loads(raw),count,n),n,12,25)
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=count);rec=record_from_bits(spec,syn,data)
        assert np.array_equal(rec.detectors,saved[f'n{n}_detectors']) and np.array_equal(data,saved[f'n{n}_data'])
        records[n]=(spec,rec,saved[f'n{n}_prediction'],saved[f'n{n}_failure'])
        provenance.append(dict(job_id=row['job_id'],raw_sha256=row['raw_sha256'],raw_path=row['raw_path']))
    configs=[];predictions={}
    demdir=ROOT/'results/decoders/d5_h2_2_p_read_sensitivity';demdir.mkdir(parents=True,exist_ok=True)
    for pr in VALUES:
        varied=dict(policy,p_read=pr);rows=[]
        for row in baseline['rows']:
            n,u=row['rounds'],row['interval_seconds'];spec,rec,oldpred,oldfail=records[n]
            noise=round_probabilities(n,u,policy=varied)
            assert [x.p_data for x in noise]==row['round_data_probabilities']
            dem=dem_for(paper_graph(spec,.004,0,pr),noise=noise)
            dempath=demdir/f'p_read_{pr:g}_n{n}.dem';dempath.write_text(dem)
            pred=PyMatchingDecoder(dem).decode_batch(rec.detectors);fail=np.any(pred!=rec.observables,axis=1)
            if pr==.001:
                assert dem==Path(row['dem_path']).read_text() and np.array_equal(pred,oldpred)
                assert int(fail.sum())==row['logical_failures']
            rows.append(dict(rounds=n,shots=len(fail),logical_failures=int(fail.sum()),logical_error_probability=float(fail.mean()),changed_predictions=int(np.any(pred!=oldpred,axis=1).sum()),corrected=int((oldfail & ~fail).sum()),harmed=int((~oldfail & fail).sum()),dem_path=str(dempath),dem_sha256=hashlib.sha256(dem.encode()).hexdigest()))
            predictions[f'p_read_{pr:g}_n{n}']=pred
        configs.append(dict(p_read=pr,rows=rows))
        print('Decoded p_read',pr,':',[r['logical_failures'] for r in rows],flush=True)
    rawrows=[{k:r[k] for k in ['rounds','shots','interval_seconds','raw_data_bit_errors','data_bits','raw_data_error_probability','data_bit_errors_by_qubit']} for r in baseline['rows']]
    out=dict(description='Offline decoder-weight sensitivity, varying syndrome and final-readout p_read together. No added record flips, postselection, or new hardware jobs. Parameter range is a stress test, not calibrated uncertainty; baseline remains p_read=0.001.',baseline_policy=policy,source=str(SOURCE.with_suffix('.json')),source_sha256=hashlib.sha256(SOURCE.with_suffix('.json').read_bytes()).hexdigest(),provenance=provenance,configurations=configs,raw_errors=rawrows)
    OUT.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');np.savez_compressed(OUT.with_suffix('.npz'),**predictions)
    lines=['# d=5 physical H2-2 readout-weight sensitivity','','p_ext=0.004; fixed sleep model; p_read varied jointly for syndrome and final readout. All data qubits retained.','', '| N | '+' | '.join(f'p_read={v:g}' for v in VALUES)+' |','|---:|'+'---:|'*len(VALUES)]
    for i,r in enumerate(rawrows):lines.append('| '+str(r['rounds'])+' | '+' | '.join(f"{100*c['rows'][i]['logical_error_probability']:.3f}% ({c['rows'][i]['logical_failures']})" for c in configs)+' |')
    OUT.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(rawrows,indent=2),flush=True)


if __name__=='__main__':main()
