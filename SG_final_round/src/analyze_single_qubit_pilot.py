"""Summarize returned Aqora pilot counts without decoding syntax placeholders."""
import json
import math
from pathlib import Path
from single_qubit_pilot import ROOT, VARIANTS


def wilson(k,n):
    z=1.959963984540054
    den=1+z*z/n
    center=(k/n+z*z/(2*n))/den
    half=z*math.sqrt((k/n)*(1-k/n)/n+z*z/(4*n*n))/den
    return [max(0,center-half),min(1,center+half)]


def main():
    base=ROOT/'runs/single_qubit_2c64d96fea4bbbac/execute'
    rows=[]
    for name,duration in VARIANTS.items():
        folder=base/name
        job=json.loads((folder/'job.json').read_text())
        row=dict(variant=name,duration_raw=duration,job_id=job['job_id'],status=job.get('job',{}).get('status'),error=job.get('error'))
        if row['status']=='COMPLETED' and not any(r.get('error') for r in job.get('results',[])):
            raw=json.loads((folder/'result_0.txt').read_text())
            assert all(b[0]=='m0' for b in raw['bits'])
            counts=raw['counts_formatted']
            assert all(int(c['bitstring'],2) in [0,1] for c in counts)
            n=sum(c['count'] for c in counts)
            k=sum(c['count'] for c in counts if int(c['bitstring'],2)==1)
            assert n==200
            # Independently cross-check packed shot records against formatted counts.
            packed=raw['shots']['array']
            assert len(packed)==n
            assert sum(any(byte != 0 for byte in shot) for shot in packed)==k
            row.update(shots=n,errors=k,error_rate=k/n,wilson_95=wilson(k,n))
        rows.append(row)
    data=dict(experiment='standalone_X_memory',platform='nexus:H2-1E',virtual_qubit=0,physical_ion='backend assigned',duration_unit='unverified',rows=rows)
    (ROOT/'results/single_qubit_pilot_counts.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))

if __name__=='__main__':
    main()
