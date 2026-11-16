"""Figures for the sleep experiments. Every figure and PDF goes to results/sleep/figures/.

The drawing code is verbatim from SG_final_round/src/; only the output folder changed
(the originals wrote to results/, results/figures/, outputs/ and the repo-level output/pdf/).
Functions that take arguments are called by the analysis or fit that computes their data;
the others read committed results from results/sleep/.

    fixed_sleep_combined(rows)          analyze_fixed_sleep_refinement.py  -> d3_fixed_sleep_combined.{png,svg}
    fixed_sleep_all(result)             analyze_fixed_sleep_all.py         -> d3_fixed_sleep_all_shots.{png,svg}
    redecode_d3(result)                 redecode_d3_sleep_dependent.py     -> d3_sleep_dependent_redecode.{png,svg}
    d3_linear_quadratic(...)            report_d3_all_shots.py `fit`       -> d3_idle_linear_quadratic_{full,zoom}.{png,svg}
    d5_sleep_dependent_fit(...)         fit_d5_sleep_dependent.py          -> d5_sleep_dependent_linear_quadratic_fit[_n3_plus].{png,svg}
    d5_sleep_dependent_comparison()     plot_d5_sleep_dependent.py         -> d5_sleep_dependent_comparison.{png,svg}
    d5_sleep_results()                  plot_d5_sleep_results.py           -> d5_h2_1e_t1_n2_to_n10.{png,svg} + results/sleep/d5_h2_1e_t1_n2_to_n10.json
    free_idle_fits()                    plot_free_idle_fits.py             -> d3_d5_free_idle_fit_comparison.{png,pdf}
    g1_stacked(panels)                  plot_g1_stacked.py (plot part)     -> d3_d5_g1_stacked_fits.{pdf,png} (+ _render.png with PyMuPDF)
    h2_2_hardware_pooled(rows)          analyze_h2_2_hardware_pooled.py    -> h2_2_hardware_d3_all_shots.png
    h2_2_combined(sweep)                combine_h2_2_updated_decoder.py    -> h2_2_hardware_p_ext_0_00117_10750_shots.png
    h2_2_decoder_sensitivity(...)       test_h2_2_decoder_sensitivity.py   -> h2_2_decoder_sensitivity.png
    h2_2_g1(ctx)                        fit_h2_2_g1.py                     -> h2_2_d3_g1_linear_quadratic_fit.png
    h2_2_free_g(ctx)                    fit_h2_2_free_g.py                 -> h2_2_d3_free_g_linear_quadratic_fit.png
    h2_2_g1_pdf()                       plot_h2_2_g1_pdf.py                -> h2_2_d3_g1_fixed_fit.{pdf,png}
    d5_h2_2_raw_qubit_errors()          plot_d5_h2_2_raw_qubit_errors.py   -> d5_h2_2_raw_error_by_qubit.{png,pdf,json}  (original mapping)
    h2_2_d3_d5_skip5_g1()               plot_h2_2_d3_d5_skip5_g1.py        -> h2_2_d3_d5_skip5_g1_fitted_curves.pdf      (d=3 and skip-5 d=5 in separate panels)
"""
import hashlib
import json

import numpy as np

from . import paths

R = paths.RESULTS


def _pyplot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    return plt


# --------------------------------------------------------------------------- d=3 H2-1E

def fixed_sleep_combined(rows):
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,6),layout='constrained')
    ax.plot([r['delta_t_seconds'] for r in rows],[r['logical_error_probability'] for r in rows],color='#78909c',linestyle='--',linewidth=1.4,label='Guide to the eye',zorder=1)
    for nshots,color,marker in [(1000,'#15689b','o'),(500,'#7a4d94','s')]:
        vals=[r for r in rows if r['shots']==nshots]
        ax.errorbar([r['delta_t_seconds'] for r in vals],[r['logical_error_probability'] for r in vals],yerr=[[r['logical_error_probability']-r['wilson_95'][0] for r in vals],[r['wilson_95'][1]-r['logical_error_probability'] for r in vals]],fmt=marker,color=color,capsize=4,elinewidth=1.5,markersize=7,label=f'{nshots:,} shots per setting',zorder=3)
    for r in rows:
        ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,9),textcoords='offset points',ha='center',fontsize=10)
    ax.set_xscale('log');ax.minorticks_off()
    ax.set_xticks([1/39,1/19,1/9,1/7,1/6,.2,.25,1/3,1]);ax.set_xticklabels(['0.02564','0.05263','0.1111','0.1429','0.1667','0.2','0.25','0.3333','1'],rotation=40,ha='right')
    ax.set_xlim(.020,1.35);ax.set_ylim(0,.18);ax.set_yticks(np.arange(0,.181,.02));ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.grid(axis='y',alpha=.2)
    ax.set_xlabel('Sleep interval Δt (seconds; logarithmic axis)');ax.set_ylabel('Decoded logical error probability')
    ax.set_title('d=3 X-memory on H2-1E: combined coarse and refinement results\nFixed total requested sleep: 1 second',loc='left',fontsize=14,pad=16)
    ax.legend(loc='upper center',frameon=False,fontsize=10)
    fig.text(.5,-.025,'Error bars: 95% Wilson intervals. Extraction duration neglected. Connecting line is not a fitted model.',ha='center',fontsize=9,color='#4c5660')
    path=paths.figure('d3_fixed_sleep_combined')
    fig.savefig(path.with_suffix('.png'),dpi=190,bbox_inches='tight');fig.savefig(path.with_suffix('.svg'),bbox_inches='tight')


def fixed_sleep_all(result):
    from .fits import fixed_sleep_all_probability as probability
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,(ax,zoom)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={'width_ratios':[1.5,1]},layout='constrained')
    rows=sorted(result['rows'],key=lambda x:x['delta_t_seconds'])
    x=np.array([r['delta_t_seconds'] for r in rows]);y=np.array([r['logical_error_probability'] for r in rows])
    err=np.array([[r['logical_error_probability']-r['wilson_95'][0] for r in rows],[r['wilson_95'][1]-r['logical_error_probability'] for r in rows]])
    for a in [ax,zoom]:
        a.errorbar(x,y,yerr=err,fmt='o',color='#17658a',capsize=3,label='Pooled shots; 95% Wilson CI',zorder=4)
        grid=np.geomspace(.024,1.05,500)
        for fit_,color,ls,label in zip(result['fits'],['#ac5352','#23845b'],['--','-'],['Paper linear-idle fit','Quadratic-idle extension']):
            a.plot(grid,probability(grid,np.array(fit_['theta']),fit_['model']),color=color,ls=ls,lw=2,label=label)
        a.yaxis.set_major_formatter(PercentFormatter(1));a.grid(alpha=.18)
        a.set_xlabel('Sleep interval Δt (seconds)')
    for r in rows:
        ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
    ax.set_xscale('log');ax.set_xlim(.022,1.2);ax.set_ylim(0,.17)
    ax.set_ylabel('Logical error probability per experiment')
    ax.set_title('All ten settings (logarithmic interval axis)',loc='left',fontsize=12)
    zoom.set_xlim(.09,.38);zoom.set_ylim(0,.045)
    zoom.set_title('Intermediate intervals',loc='left',fontsize=12)
    for r in rows:
        if .09<r['delta_t_seconds']<.38:
            zoom.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,6),textcoords='offset points',ha='center',fontsize=9)
    ax.legend(loc='upper center',fontsize=8,frameon=False)
    fig.suptitle('d=3 X-memory on H2-1E • 13,000 shots • total requested sleep = 1 s',fontsize=14)
    fig.supxlabel('Fixed phenomenological decoder. Extraction duration neglected. Fits are descriptive, not independent predictions.',fontsize=9)
    dest=paths.figure('d3_fixed_sleep_all_shots')
    fig.savefig(dest.with_suffix('.png'),dpi=190,bbox_inches='tight')
    fig.savefig(dest.with_suffix('.svg'),bbox_inches='tight')


def redecode_d3(result):
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    rows=sorted(result['rows'],key=lambda r:r['delta_t_seconds'])
    x=np.array([r['delta_t_seconds'] for r in rows])
    fig,(ax,zoom)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={'width_ratios':[1.4,1]},layout='constrained')
    for a in [ax,zoom]:
        for field,interval,color,marker,label in [
            ('baseline_probability','baseline_wilson_95','#8a9097','s','Original fixed DEM'),
            ('logical_error_probability','wilson_95','#147c68','o','Sleep-dependent DEM')]:
            y=np.array([r[field] for r in rows]);error=np.array([[r[field]-r[interval][0] for r in rows],[r[interval][1]-r[field] for r in rows]])
            a.plot(x,y,ls=':',color=color,alpha=.65,lw=1)
            a.errorbar(x,y,yerr=error,fmt=marker,mfc='white' if field=='baseline_probability' else color,color=color,
                       ms=6,capsize=3,elinewidth=1.1,label=label,zorder=3 if field=='baseline_probability' else 4)
        a.set_xlabel('Sleep interval Delta t (seconds)');a.grid(axis='y',alpha=.2)
        a.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xscale('log');ax.set_xlim(.022,1.25);ax.set_ylim(0,.17)
    ax.set_ylabel('Logical error probability per experiment')
    ax.set_title('All settings (logarithmic interval axis)',loc='left',fontsize=12)
    ax.legend(frameon=False,loc='upper center',fontsize=10)
    if result['paired_aggregate']['corrected']+result['paired_aggregate']['new_failures']==0:
        ax.text(.5,.77,'Both decoders agree on all recorded shots',transform=ax.transAxes,
                ha='center',fontsize=9,color='#52636c')
    zoom.set_xlim(.09,.38)
    top=max(r['wilson_95'][1] for r in rows if .09<r['delta_t_seconds']<.38)
    zoom.set_ylim(0,max(.042,top*1.25))
    zoom.set_title('Intermediate intervals',loc='left',fontsize=12)
    for r in rows:
        v=max(r['baseline_wilson_95'][1],r['wilson_95'][1])
        ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],v),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
        if .09<r['delta_t_seconds']<.38:
            zoom.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],v),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)
    fig.suptitle('d=3 X-memory on H2-1E: re-decoding the same 13,000 shots',fontsize=14)
    fig.supxlabel('95% Wilson intervals. Dotted lines: guides only. Requested sleep = 1 s; extraction duration neglected.',fontsize=9)
    path=paths.figure('d3_sleep_dependent_redecode')
    fig.savefig(path.with_suffix('.png'),dpi=200,bbox_inches='tight')
    fig.savefig(path.with_suffix('.svg'),bbox_inches='tight')


def d3_linear_quadratic(rows,x,k,n,theta):
    from .fits import d3_linear_quadratic_predict as pred
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    for zoom,name in [(False,'full'),(True,'zoom')]:
        fig,ax=plt.subplots(figsize=(9.6,4.4),layout='constrained')
        u=np.geomspace(.024,1.03,500)
        ax.plot(u,pred(theta,u),color='#21836b',lw=2.3,label='Linear + quadratic idle ansatz (qualitative fit)')
        ax.errorbar(x,k/n,yerr=np.array([[r['logical_error_probability']-r['wilson_95'][0] for r in rows],[r['wilson_95'][1]-r['logical_error_probability'] for r in rows]]),
                    fmt='o',color='#185e87',ms=6,capsize=3,label='Pooled measurements; 95% Wilson intervals',zorder=3)
        for r in rows:
            if not zoom or .09<r['delta_t_seconds']<.38:
                ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,6),textcoords='offset points',ha='center',fontsize=8)
        if zoom:
            ax.set_xlim(.09,.38);ax.set_ylim(0,.044)
        else:
            ax.set_xscale('log');ax.set_xlim(.022,1.2);ax.set_ylim(0,.17)
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.17)
        ax.set_xlabel('Sleep interval Delta t (seconds)'+('' if zoom else '; logarithmic axis'))
        ax.set_ylabel('Logical error probability per experiment')
        ax.legend(frameon=False,fontsize=8,loc='upper right' if zoom else 'upper center')
        fig.savefig(paths.figure(f'd3_idle_linear_quadratic_{name}.png'),dpi=250)
        fig.savefig(paths.figure(f'd3_idle_linear_quadratic_{name}.svg'))
        plt.close(fig)


# --------------------------------------------------------------------------- d=5 H2-1E

def d5_sleep_dependent_fit(d,theta,name):
    from .fits import d5_sleep_dependent_probability as probability
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter,NullFormatter
    rows=d['rows'];fig,axes=plt.subplots(1,2,figsize=(11.4,4.8),layout='constrained')
    lo,hi=d['conditional_optimum_95']
    for ax,zoom in zip(axes,[False,True]):
        selected=[r for r in rows if not zoom or r['rounds']>=4]
        x=np.array([r['delta_t_seconds'] for r in selected]);y=np.array([r['sleep_probability'] for r in selected])
        err=np.array([[r['sleep_probability']-r['sleep_wilson_95'][0] for r in selected],[r['sleep_wilson_95'][1]-r['sleep_probability'] for r in selected]])
        maximum=max(r['delta_t_seconds'] for r in rows)
        grid=np.linspace(.10,.37,500) if zoom else np.geomspace(.1,maximum*1.03,700)
        ax.plot(grid,probability(theta,grid),color='#21836b',lw=2,label='Linear + quadratic idle fit')
        ax.errorbar(x,y,yerr=err,fmt='o',color='#185e87',ms=5.5,capsize=3,label='Sleep-dependent DEM; 95% Wilson CI',zorder=3)
        ax.axvline(d['optimum_seconds'],color='#ad6d19',ls='--',lw=1.2,label=f"Analytical Δt* = {d['optimum_seconds']:.3f} s")
        if zoom:ax.axvspan(lo,hi,color='#ad6d19',alpha=.10,label='Conditional 95% interval for Δt*')
        for r in selected:
            if not zoom and r['rounds']>=7:continue
            ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['sleep_wilson_95'][1]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.17);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
        ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability per experiment')
        if zoom:
            ax.set_xlim(.10,.37);ax.set_ylim(0,.052);ax.set_title('Intermediate intervals',loc='left',fontsize=11)
        else:
            ax.set_xscale('log');ax.set_xlim(.095,maximum*1.1)
            top=max(r['sleep_wilson_95'][1] for r in rows)
            ax.set_ylim(0,top*1.25)
            ticks=[v for v in [1/9,1/6,.25,.5,1] if v<=maximum]
            ax.set_xticks(ticks);ax.set_xticklabels([f'{v:.3g}' for v in ticks]);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_title('Fitted range · logarithmic horizontal axis',loc='left',fontsize=11)
        ax.legend(frameon=False,fontsize=7.5,loc='upper left' if not zoom else 'upper right')
    fig.suptitle(f"d=5 H2-1E · sleep-dependent DEM · N≥{d['min_rounds']} fit · T_sleep=1 s",fontsize=14,fontweight='bold')
    fig.supxlabel('Descriptive binomial fit; optimum interval excludes batch and decoder uncertainty.',fontsize=9)
    for suffix in ['png','svg']:fig.savefig(paths.figure(f'{name}.{suffix}'),dpi=220)


def d5_sleep_dependent_comparison():
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter,NullFormatter
    d=json.loads(paths.read_text(R/'d5_sleep_dependent_redecode.json'))
    rows=sorted([r for r in d['rows'] if r['total_requested_sleep_seconds']==1],key=lambda r:r['delta_t_seconds'])
    fig,axes=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
    for ax,zoom in zip(axes,[False,True]):
        selected=[r for r in rows if not zoom or r['rounds']>=4]
        x=np.array([r['delta_t_seconds'] for r in selected])
        for field,interval,color,marker,label in [('fixed_probability','fixed_wilson_95','#8b9299','s','Fixed DEM'),('sleep_probability','sleep_wilson_95','#147c68','o','Sleep-dependent DEM')]:
            y=np.array([r[field] for r in selected]);lo=np.array([r[interval][0] for r in selected]);hi=np.array([r[interval][1] for r in selected])
            assert np.all(lo<=y) and np.all(y<=hi)
            ax.errorbar(x,y,yerr=[y-lo,hi-y],fmt=marker,color=color,mfc='white' if marker=='s' else color,ms=5.5,capsize=3,elinewidth=1,label=label,alpha=.9,zorder=2 if marker=='s' else 3)
        for r in selected:
            if not zoom and r['rounds']>=7:continue
            ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],max(r['fixed_wilson_95'][1],r['sleep_wilson_95'][1])),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.18);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
        ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability per experiment')
        if zoom:
            ax.set_xlim(.10,.36);ax.set_ylim(0,max(max(r['fixed_wilson_95'][1],r['sleep_wilson_95'][1]) for r in selected)*1.25);ax.set_title('Intermediate intervals',loc='left',fontsize=11)
        else:
            ax.set_xscale('log');ax.set_xlim(.095,1.15);ax.set_ylim(0,.21);ax.set_xticks([1/9,1/6,.25,.5,1]);ax.set_xticklabels(['0.111','0.167','0.25','0.50','1.00']);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_title('Full range · logarithmic horizontal axis',loc='left',fontsize=11);ax.legend(frameon=False,fontsize=9,loc='upper left')
    fig.suptitle('d=5 H2-1E · same pooled 7,667 shots · T_sleep=1 s',fontweight='bold',fontsize=14)
    fig.supxlabel('95% Wilson intervals; decoder and batch uncertainty are excluded.',fontsize=9)
    for suffix in ['png','svg']:fig.savefig(paths.figure(f'd5_sleep_dependent_comparison.{suffix}'),dpi=220)
    print('Plot uses',sum(r['shots'] for r in rows),'shots')


def d5_sleep_results():
    """Reviewed d=5, T_sleep=1 s probabilities without fitting a curve; also writes the summary JSON.

    The committed d5_h2_1e_t1_n2_to_n10.json was made from an older
    d5_h2_1e_sleep_logical_probabilities.json (S4), so it is not a regression target.
    """
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter,NullFormatter
    source=R/'d5_h2_1e_sleep_logical_probabilities.json'
    d=json.loads(paths.read_text(source))
    rows=sorted([r for r in d['rows'] if r['total_requested_sleep_seconds']==1 and 2<=r['rounds']<=10],key=lambda r:r['delta_t_seconds'])
    assert {r['rounds'] for r in rows}==set(range(2,11))
    fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
    for ax,zoom in zip(axes,[False,True]):
        selected=[r for r in rows if not zoom or r['rounds']>=4]
        x=np.array([r['delta_t_seconds'] for r in selected]);y=np.array([r['logical_error_probability'] for r in selected])
        lo=np.array([r['wilson_95'][0] for r in selected]);hi=np.array([r['wilson_95'][1] for r in selected])
        assert np.all(lo<=y) and np.all(y<=hi)
        ax.errorbar(x,y,yerr=[y-lo,hi-y],fmt='o',markersize=5.5,capsize=3,color='#176385',label='Measurements; 95% Wilson intervals')
        for r in selected:
            if not zoom and r['rounds']>=7:continue
            ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.18);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
        ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability per experiment')
        if zoom:
            ax.set_xlim(.10,.36);ax.set_ylim(0,max(hi)*1.3);ax.set_title('Near the expected minimum',loc='left',fontsize=11)
        else:
            ax.set_xscale('log');ax.set_xlim(.095,1.15);ax.set_ylim(0,max(hi)*1.18);ax.set_xticks([.111111,.166667,.25,.5,1]);ax.set_xticklabels(['0.111','0.167','0.25','0.50','1.00']);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_title('Full range · logarithmic horizontal axis',loc='left',fontsize=11)
            ax.legend(frameon=False,fontsize=8,loc='upper left')
    fig.suptitle('d=5 H2-1E · total requested sleep T=1 s',fontweight='bold',fontsize=14)
    for suffix in ['png','svg']:fig.savefig(paths.figure(f'd5_h2_1e_t1_n2_to_n10.{suffix}'),dpi=220)
    summary=dict(source=str(source),total_requested_sleep_seconds=1,total_shots=sum(r['shots'] for r in rows),total_failures=sum(r['logical_failures'] for r in rows),rows=rows,primary_decoder=d['primary_decoder'])
    paths.write_json(R/'d5_h2_1e_t1_n2_to_n10.json', summary)
    print('T=1 s:',summary['total_shots'],'shots;',summary['total_failures'],'failures')
    return summary


# --------------------------------------------------------------------------- d=3 + d=5 fits

def free_idle_fits():
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(15.8,7.8))
    fig.subplots_adjust(left=.065,right=.98,top=.86,bottom=.35,wspace=.22)
    styles={3:('#176baf','o'),5:('#c45b19','s')}
    handles=[];labels=[]
    for d in [3,5]:
        result=json.loads(paths.read_text(R/f'd{d}_free_idle_g_fit.json'))
        color,marker=styles[d]
        rows=result['rows'];u=np.array([r['delta_t_seconds'] for r in rows]);p=np.array([r['logical_error_probability'] for r in rows])
        ci=np.array([r['wilson_95'] for r in rows]);err=np.array([p-ci[:,0],ci[:,1]-p])
        g=result['g'];a=result['a'];b=result['b'];pe=result['p_ext'];c=result['C'];l1=result['lambda_1'];l2=result['lambda_2'];star=result['delta_t_star']
        def curve(t):return c/t*(1+l1*t+l2*t*t)**(g*(d+1)/2)
        grid=np.geomspace(min(u),max(u),1200)
        for ax in axes:
            ax.errorbar(u,p,yerr=err,fmt=marker,color=color,mfc='white',mew=1.4,ms=6,capsize=3,elinewidth=1.1,zorder=3)
            line,=ax.plot(grid,curve(grid),color=color,lw=2.2)
            ax.axvline(star,color=color,ls='--',lw=1.2,alpha=.8)
            ax.plot(star,curve(star),marker='*',ms=15,color=color,mec='white',mew=.7,zorder=5)
        handles.append(line)
        labels.append(f'd = {d}  ({marker} data markers)\n'
                      f'g = {g:.8f} (upper bound);  a = {a:.8e} s⁻¹ (≈ 0)\n'
                      f'b = {b:.8f} s⁻²;  p_ext = {pe:.11f}\n'
                      f'C = {c:.9f};  analytical Δt* = {star:.8f} s')
        axes[1].annotate(f'd = {d}: Δt* = {star:.5f} s',xy=(star,curve(star)),xytext=(.29,.030 if d==3 else .025),color=color,fontsize=10,arrowprops=dict(arrowstyle='->',color=color,lw=1),ha='left')
    for ax in axes:
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        ax.grid(alpha=.2)
        ax.set_xlabel('Sleep interval Δt (s)')
        ax.set_ylabel('Decoded logical error probability')
    axes[0].set_xscale('log');axes[0].set_xlim(.022,1.12);axes[0].set_ylim(0,.18)
    axes[0].set_title('All measured intervals',loc='left',fontweight='bold')
    axes[1].set_xlim(.1,.55);axes[1].set_ylim(.005,.055)
    axes[1].set_title('Detail around the fitted minima',loc='left',fontweight='bold')
    fig.suptitle('H2-1E X-memory · d = 3 and d = 5\nFixed total requested sleep T = 1 s · sleep-dependent MWPM decoding',fontsize=16,y=.97)
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.075),ncol=2,frameon=False,fontsize=10,handlelength=2.5,columnspacing=3)
    fig.text(.5,.025,'Error bars: 95% Wilson intervals. Stars and dashed lines mark analytical minima.\nSeparate binomial fits; 0 < g < 1 and a, b ≥ 0. Both g estimates reach the numerical upper bound. Coefficients are effective logical-fit parameters.',ha='center',fontsize=9,color='#444444')
    out=paths.figure('d3_d5_free_idle_fit_comparison')
    fig.savefig(out.with_suffix('.png'),dpi=190)
    fig.savefig(out.with_suffix('.pdf'))
    print(out.with_suffix('.png'))


def g1_stacked(panels):
    """The stacked g=1 portrait (fits.g1_stacked computes the panels)."""
    from .fits import g1_stacked_predict
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(2,1,figsize=(8.27,11.69))
    fig.subplots_adjust(left=.13,right=.96,top=.76,bottom=.19,hspace=1.02)
    for ax,panel,color in zip(axes,panels,['#176baf','#c45b19']):
        d=panel['distance'];rows=panel['rows'];u=panel['u'];n=panel['n'];p=panel['p'];alpha=panel['alpha']
        x=panel['x'];pe=panel['pe'];b=panel['b'];star=panel['star']
        grid=np.geomspace(min(u),max(u),1000)
        ci=np.array([r['wilson_95'] for r in rows]);err=np.array([p-ci[:,0],ci[:,1]-p])
        ax.errorbar(u,p,yerr=err,fmt='o',color=color,mfc='none',mew=1.2,ms=5,capsize=3,elinewidth=1.1,label='Observed data (95% interval)',zorder=3)
        ax.plot(grid,g1_stacked_predict(x,grid,alpha),color=color,lw=2.2,label='Fit with g = 1')
        ax.axvline(star,color=color,ls='--',lw=1.2)
        ax.annotate(f'Δt* = {star:.5f} s',xy=(star,0),xycoords=ax.get_xaxis_transform(),
                    xytext=(0,-20),textcoords='offset points',ha='center',va='top',fontsize=11,color=color)
        ax.set_xscale('log');ax.set_xlim(.022,1.13);ax.set_ylim(0,.18)
        ax.set_xticks([.025,.05,.1,.2,.5,1]);ax.set_xticklabels(['0.025','0.05','0.1','0.2','0.5','1'])
        ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.set_yticks([0,.04,.08,.12,.16]);ax.grid(alpha=.18)
        ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)',labelpad=32);ax.set_ylabel('Logical error probability')
        ax.set_title(f'd = {d}  |  {sum(n):,} shots',loc='left',fontsize=15,fontweight='bold',pad=8)
        position=ax.get_position()
        fig.text(position.x0,position.y0-.09,
                 f'Fitted   a ≈ 0 s⁻¹     b = {b:.8f} s⁻²     C = {np.exp(x[0]):.9f}\n'
                 f'Fixed    g = 1     p_ext = {pe:.11f}',
                 fontsize=11,va='top',linespacing=1.5)
        ax.legend(loc='upper left',fontsize=10,frameon=False)
    fig.suptitle('Observed logical errors and fitted curves',fontsize=17,fontweight='bold',y=.985)
    fig.text(.5,.935,'H2-1E X-memory  |  Total requested sleep T = 1 s\nSleep-dependent MWPM decoding',ha='center',fontsize=11,linespacing=1.5)
    fig.text(.13,.902,'Logical error model',fontsize=12,fontweight='bold')
    fig.text(.13,.866,r'$P_L(d,u)=\frac{T}{u}C\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}\,q(u)\right]^{g(d+1)/2}$',
             fontsize=15)
    fig.text(.13,.829,r'$q(u)=au+bu^2$, where $u=\Delta t$ is the sleep interval.',
             fontsize=11)
    fig.text(.13,.025,'Error bars are 95% Wilson intervals. Dashed lines mark analytical minima.\nThe idle coefficients are fitted separately for each distance.',fontsize=9.5,color='#444444')
    out=paths.figure('d3_d5_g1_stacked_fits.pdf')
    fig.savefig(out)
    fig.savefig(out.with_suffix('.png'),dpi=160)
    try:
        import fitz
        doc=fitz.open(out);doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(out.with_name('d3_d5_g1_stacked_fits_render.png')))
        print('PDF rendered')
    except ImportError:
        print('PyMuPDF unavailable')


# --------------------------------------------------------------------------- physical H2-2 d=3

def h2_2_hardware_pooled(rows):
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    ordered = sorted(rows, key=lambda r:r['interval_seconds'])
    x = np.array([r['interval_seconds'] for r in ordered])
    y = np.array([r['logical_error_probability'] for r in ordered])
    bounds = np.array([r['logical_wilson_95'] for r in ordered])
    fig, ax = plt.subplots(figsize=(7.2, 4.4), layout='constrained')
    ax.errorbar(x, y, yerr=[y-bounds[:,0], bounds[:,1]-y], fmt='o',
                mfc='none', color='#176baf', capsize=4, markersize=6)
    ax.set_xscale('log')
    ax.set_xticks(x, [f'{u:.4g}' for u in x], rotation=30)
    ax.set_xlabel('Requested sleep interval Δt (s)')
    ax.set_ylabel('Logical error probability')
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylim(0, max(bounds[:,1])*1.23)
    for r in ordered:
        ax.annotate(f"N={r['rounds']}\n{r['logical_failures']}/{r['shots']}",
                    (r['interval_seconds'], r['logical_wilson_95'][1]),
                    xytext=((-8, 8) if r['rounds'] == 6 else (8, 8) if r['rounds'] == 5 else (0, 6)),
                    textcoords='offset points',
                    ha=('right' if r['rounds'] == 6 else 'left' if r['rounds'] == 5 else 'center'), fontsize=9)
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y', alpha=.2)
    ax.set_title('Physical H2-2 · d=3 X-memory · all 6,750 shots\nTotal requested sleep 1 s · frozen sleep-dependent MWPM · 95% Wilson intervals', fontsize=11)
    fig.savefig(paths.figure('h2_2_hardware_d3_all_shots.png'), dpi=170)


def h2_2_combined(sweep):
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    fig,axes=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
    ordered=sorted(sweep,key=lambda r:r['interval_seconds']);x=np.array([r['interval_seconds'] for r in ordered])
    for ax,field,ci,title,color in [(axes[0],'raw_data_error_probability','raw_data_shot_bootstrap_95','Raw final data-bit errors','#176baf'),(axes[1],'logical_error_probability','logical_wilson_95','Decoded logical errors','#ad541b')]:
        y=np.array([r[field] for r in ordered]);bounds=np.array([r[ci] for r in ordered])
        ax.errorbar(x,y,yerr=np.maximum([y-bounds[:,0],bounds[:,1]-y],0),fmt='o',mfc='white',color=color,capsize=3)
        ax.set_xscale('log');ax.set_xticks(x,[f'{v:.3g}' for v in x],rotation=40)
        ax.set_xlabel('Requested sleep interval (s)');ax.set_ylabel('Error probability');ax.set_title(title)
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,max(bounds[:,1])*1.3);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
        for i,r in enumerate(ordered):
            ax.annotate(f"N={r['rounds']}",(x[i],bounds[i,1]),xytext=(0,5),textcoords='offset points',ha='center',fontsize=8)
    fig.suptitle('Physical H2-2 · d=3 X-memory · 9,750 shots · total requested sleep 1 s\nSleep-dependent MWPM: p_ext=0.00117 · 95% sampling intervals',fontsize=12)
    fig.savefig(paths.figure('h2_2_hardware_p_ext_0_00117_10750_shots.png'),dpi=180)


def h2_2_decoder_sensitivity(summary,results):
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
    x=np.arange(len(summary));shots=np.array([r['shots'] for r in summary])
    for rangeidx,color,label in [(0,'#82b1d5','Joint factors 0.5–2 (81 combinations)')]:
        lo=np.array([r['ranges'][rangeidx]['minimum_failures'] for r in summary])/shots
        hi=np.array([r['ranges'][rangeidx]['maximum_failures'] for r in summary])/shots
        ax.vlines(x,lo,hi,color=color,lw=16 if rangeidx==1 else 8,label=label)
    y=np.array([r['baseline_failures'] for r in summary])/shots
    ax.plot(x,y,'o',color='#172c40',label='Frozen decoder')
    ax.set_xticks(x,[f"N={r['rounds']}\n{1/(r['rounds']-1):.3g} s" for r in summary])
    ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylabel('Logical error probability');ax.set_xlabel('Extraction rounds and requested sleep interval')
    ax.set_title('H2-2 · d=3 X-memory · decoder sensitivity on 6,750 saved shots')
    ax.plot(x,[next(c for c in results if c['parameters']['name']=='no_idle')['rows'][j]['probability'] for j in range(len(summary))], 'x', color='#bd5c25',label='No idle contribution');ax.legend(frameon=False);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.subplots_adjust(bottom=.23) if not fig.get_constrained_layout() else None
    fig.text(.5,-.045,'Ranges show parameter sensitivity, not statistical confidence intervals. No additional hardware runs.',ha='center',fontsize=9)
    fig.savefig(paths.figure('h2_2_decoder_sensitivity.png'),dpi=180,bbox_inches='tight')


def h2_2_g1(ctx):
    from .fits import h2_2_g1_predict as predict
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    rows=ctx['rows'];u=ctx['u'];n=ctx['n'];k=ctx['k'];theta=ctx['theta'];star=ctx['star'];a=ctx['a'];b=ctx['b'];ci=ctx['ci'];dev=ctx['dev'];gof=ctx['gof'];P_EXT=ctx['p_ext']
    plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(8.27,8.8));fig.subplots_adjust(left=.13,right=.96,top=.69,bottom=.25)
    fig.suptitle('Observed logical errors and fitted curve',fontsize=17,fontweight='bold',y=.98)
    fig.text(.5,.92,'Physical H2-2 X-memory | d = 3 | 9,750 shots\nTotal requested sleep T = 1 s | Sleep-dependent MWPM',ha='center',fontsize=11,linespacing=1.5)
    fig.text(.13,.835,r'$P_L(u)=\frac{T}{u}C\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}(au+bu^2)\right]^2$',fontsize=16)
    fig.text(.13,.785,f'Fixed: d = 3, g = 1, p_ext = {P_EXT:.5f}. Fit: C, a, b; a,b >= 0.',fontsize=11)
    p=k/n;bounds=np.array([row['logical_wilson_95'] for row in rows]);color='#176baf'
    ax.errorbar(u,p,yerr=[p-bounds[:,0],bounds[:,1]-p],fmt='o',mfc='white',color=color,capsize=3,label='Observed (95% Wilson intervals)')
    grid=np.geomspace(min(u),max(u),1000);ax.plot(grid,predict(theta,grid),color=color,lw=2,label='Binomial likelihood fit')
    ax.axvline(star,color=color,ls='--',label=f'Minimum: {star:.4f} s')
    ax.set_xscale('log');ax.set_xlim(.022,1.15);ax.set_ylim(0,.095);ax.set_xticks([.025,.05,.1,.2,.5,1],['0.025','0.05','0.1','0.2','0.5','1']);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)');ax.set_ylabel('Logical error probability');ax.grid(alpha=.18);ax.legend(frameon=False,fontsize=10)
    fig.text(.13,.17,f'Fitted: a = {a:.5g} s⁻¹, b = {b:.6g} s⁻², C = {np.exp(theta[0]):.7g}\nΔt* = {star:.4f} s; conditional 95% bootstrap: {ci[0]:.4f}-{ci[1]:.4f} s\nBinomial deviance = {dev:.3f}; nominal df = 5; bootstrap GOF p = {gof:.3f}',fontsize=11,linespacing=1.6,va='top')
    fig.text(.13,.035,'All eight fixed-T settings included; zero-sleep control excluded.\nUncertainty is conditional on the model and fixed parameters; drift and calibration\nuncertainty are excluded. Curve parameters are effective, not calibrated idle rates.',fontsize=9,color='#444444',linespacing=1.5)
    fig.savefig(paths.figure('h2_2_d3_g1_linear_quadratic_fit.png'),dpi=180)


def h2_2_free_g(ctx):
    from .fits import h2_2_free_g_predict as predict, h2_2_free_g_star as star
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    rows=ctx['rows'];u=ctx['u'];n=ctx['n'];k=ctx['k'];xfix=ctx['xfix'];best_x=ctx['best'];g=ctx['g'];fixed=ctx['fixed']
    fig,ax=plt.subplots(figsize=(8,5),layout='constrained');p=k/n;ci=np.array([r['logical_wilson_95'] for r in rows]);grid=np.geomspace(min(u),max(u),1000)
    ax.errorbar(u,p,yerr=[p-ci[:,0],ci[:,1]-p],fmt='o',mfc='white',color='#333333',capsize=3,label='Observed (95% Wilson)')
    ax.plot(grid,predict(xfix,grid,g=1),label=f"g=1: Δt*={fixed['delta_t_star_seconds']:.3f} s",color='#176baf')
    ax.plot(grid,predict(best_x,grid),label=f'g={g:.3f}: Δt*={star(best_x):.3f} s',color='#b45c21',ls='--')
    ax.set_xscale('log');ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability');ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,.095);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False)
    ax.set_title('Physical H2-2 · d=3 · p_ext=0.00117 · 9,750 shots\nLinear + quadratic idle model: fixed versus fitted g',fontsize=12)
    fig.savefig(paths.figure('h2_2_d3_free_g_linear_quadratic_fit.png'),dpi=180)


def h2_2_g1_pdf():
    """The saved fixed-g hardware fit in the emulator report style (was written to output/pdf/)."""
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    r=json.loads(paths.read_text(R/'h2_2_d3_g1_linear_quadratic_fit.json'))
    assert r['g']==1 and r['distance']==3 and r['p_ext']==.00117
    plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,ax=plt.subplots(figsize=(8.27,11.69));fig.subplots_adjust(left=.13,right=.96,top=.70,bottom=.32)
    fig.suptitle('Observed logical errors and fitted curve',fontsize=17,fontweight='bold',y=.975)
    fig.text(.5,.91,'Physical H2-2 X-memory | d = 3 | 9,750 shots\nTotal requested sleep T = 1 s | Sleep-dependent MWPM decoding',ha='center',fontsize=11,linespacing=1.6)
    fig.text(.13,.845,'Logical error model',fontsize=12,fontweight='bold')
    fig.text(.13,.80,r'$P_L(d,u)=\frac{T}{u}C\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}\,q(u)\right]^{g(d+1)/2}$',fontsize=15)
    fig.text(.13,.762,r'$q(u)=au+bu^2$, where $u=\Delta t$ is the sleep interval.',fontsize=11)
    rows=r['rows'];u=np.array([x['interval_seconds'] for x in rows]);p=np.array([x['logical_error_probability'] for x in rows]);ci=np.array([x['logical_wilson_95'] for x in rows]);color='#176baf'
    def curve(t):return r['C']/t*(1+r['lambda_1']*t+r['lambda_2']*t*t)**2
    ax.errorbar(u,p,yerr=[p-ci[:,0],ci[:,1]-p],fmt='o',color=color,mfc='none',mew=1.2,ms=5,capsize=3,elinewidth=1.1,label='Observed data (95% Wilson interval)',zorder=3)
    grid=np.geomspace(min(u),max(u),1000);ax.plot(grid,curve(grid),color=color,lw=2.2,label='Fit with g = 1')
    star=r['delta_t_star_seconds'];ax.axvline(star,color=color,ls='--',lw=1.2)
    ax.annotate(f'Δt* = {star:.5f} s',xy=(star,0),xycoords=ax.get_xaxis_transform(),xytext=(0,-21),textcoords='offset points',ha='center',va='top',fontsize=11,color=color)
    ax.set_xscale('log');ax.set_xlim(.022,1.13);ax.set_ylim(0,.09);ax.set_xticks([.025,.05,.1,.2,.5,1],['0.025','0.05','0.1','0.2','0.5','1']);ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.set_yticks([0,.02,.04,.06,.08]);ax.grid(alpha=.18);ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)',labelpad=32);ax.set_ylabel('Logical error probability');ax.set_title('d = 3 | Physical H2-2',loc='left',fontsize=15,fontweight='bold',pad=8);ax.legend(loc='upper center',fontsize=10,frameon=False)
    lo,hi=r['delta_t_star_conditional_95_seconds']
    fig.text(.13,.215,f"Fitted   a = {r['a_per_second']:.8f} s⁻¹     b = {r['b_per_second_squared']:.8f} s⁻²\n            C = {r['C']:.10f}\nFixed    g = 1     d = 3     p_ext = {r['p_ext']:.5f}",fontsize=11,va='top',linespacing=1.6)
    fig.text(.13,.127,f'Δt* = {star:.5f} s (conditional 95% bootstrap: {lo:.5f}-{hi:.5f} s)\nFitted minimum logical error = {100*r["minimum_fitted_probability"]:.3f}%\nBinomial deviance = {r["binomial_deviance"]:.3f}; nominal df = 5; bootstrap GOF p = {r["parametric_bootstrap_gof_p"]:.3f}',fontsize=10,va='top',linespacing=1.6)
    fig.text(.13,.035,'All eight fixed-T settings included; zero-sleep control excluded.\nIntervals condition on the model and fixed parameters; calibration and drift uncertainty\nare excluded. Fitted a and b are effective coefficients, not calibrated physical idle rates.',fontsize=9,color='#444444',linespacing=1.5)
    out=paths.figure('h2_2_d3_g1_fixed_fit.pdf');fig.savefig(out);fig.savefig(out.with_suffix('.png'),dpi=180);print(out)


# --------------------------------------------------------------------------- physical H2-2 d=5

def d5_h2_2_raw_qubit_errors():
    """All 25 final-data raw error probabilities for the ORIGINAL-mapping H2-2 d=5 sweep (no decoder)."""
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    from matplotlib.lines import Line2D
    SOURCE=R/'d5_h2_2_t1_p_ext_0_004_3500_shots.json'
    OUT=paths.figure('d5_h2_2_raw_error_by_qubit')
    s=json.loads(paths.read_text(SOURCE));rows=s['rows']
    x=np.array([r['rounds'] for r in rows]);shots=np.array([r['shots'] for r in rows])
    counts=np.array([r['data_bit_errors_by_qubit'] for r in rows]);p=counts/shots[:,None]
    assert counts.shape==(5,25) and x.tolist()==[2,3,4,6,10]
    assert np.array_equal(counts.sum(axis=1),[r['raw_data_bit_errors'] for r in rows])
    assert np.allclose(p.mean(axis=1),[r['raw_data_error_probability'] for r in rows])
    # Emphasis is descriptive: highlight qubits reaching at least 14%, not a test.
    high=set(np.flatnonzero(p.max(axis=0)>=.14).tolist())
    colors={i:plt.get_cmap('tab20')(i%20) for i in range(25)}
    colors.update({5:'#d14936',6:'#167b8c',7:'#7c4ca5',2:'#d08b16',0:'#2763a2',15:'#48823c'})
    markers=['o','s','^','D','v']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(12.8,7.1));fig.subplots_adjust(left=.085,right=.76,top=.81,bottom=.24)
    for q in sorted(range(25),key=lambda q:q in high):
        ax.plot(x,p[:,q],color=colors[q],marker=markers[q//5],markersize=5 if q in high else 3.5,lw=2.2 if q in high else 1,alpha=1 if q in high else .4,zorder=3 if q in high else 1)
    ax.set_xticks(x,[f'{n}\n{1/(n-1):.3g} s' for n in x]);ax.set_xlabel('Extraction rounds N / requested sleep interval',labelpad=12)
    ax.set_ylabel('Raw final-data error probability');ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,.53);ax.set_xlim(1.7,10.7)
    ax.set_yticks(np.arange(0,.51,.05));ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    # Direct labels emphasize the largest features without obscuring all 25 traces.
    ax.annotate('Q5: 42–48% for N ≥ 3',xy=(6,p[3,5]),xytext=(5,.505),color=colors[5],fontsize=12,fontweight='bold',arrowprops=dict(arrowstyle='-',color=colors[5],lw=1.2))
    ax.annotate('Q2: 21.2%',xy=(2,p[0,2]),xytext=(2.65,.275),color=colors[2],arrowprops=dict(arrowstyle='-',color=colors[2]))
    for q,dy in [(6,7),(7,6),(15,-1),(0,-8)]:
        ax.annotate(f'Q{q}',xy=(10,p[-1,q]),xytext=(8,dy),textcoords='offset points',color=colors[q],fontweight='bold',fontsize=10)
    handles=[Line2D([0],[0],color=colors[q],marker=markers[q//5],lw=2 if q in high else 1,alpha=1 if q in high else .5,markersize=5,label=f'Q{q}') for q in range(25)]
    ax.legend(handles=handles,title='Data-qubit index',ncol=2,loc='upper left',bbox_to_anchor=(1.03,1.015),frameon=False,fontsize=9.5,columnspacing=1.2,handlelength=1.6,labelspacing=.8)
    fig.text(.085,.94,'Physical H2-2 · d=5 · raw errors by data qubit',fontsize=18,fontweight='bold')
    fig.text(.085,.885,'Total requested sleep T = 1 s · all 25 data qubits · no postselection',fontsize=11,color='#444444')
    fig.text(.085,.05,'Shots at N = 2, 3, 4, 6, 10: 500, 750, 1,000, 750, 500. Raw rates do not depend on decoder settings.\nEach point is errors / shots for that qubit; lines guide the eye. Bold traces reach ≥14%; this is descriptive, not a statistical outlier test.',fontsize=9,color='#555555',linespacing=1.6)
    for suffix in ['.png','.pdf']:fig.savefig(OUT.with_suffix(suffix),dpi=190)
    paths.write_json(OUT.with_suffix('.json'), dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),rounds=x.tolist(),shots=shots.tolist(),counts=counts.tolist(),probabilities=p.tolist(),highlighted_qubits=sorted(high)))
    print(OUT.with_suffix('.png'))


def h2_2_d3_d5_skip5_g1():
    """Physical H2-2 g=1 fits: d=3 and SKIP-5 d=5 on one page, in separate panels (never pooled)."""
    plt = _pyplot()
    from matplotlib.ticker import PercentFormatter
    d3=json.loads(paths.read_text(R/'h2_2_d3_g1_linear_quadratic_fit.json'))
    d5all=json.loads(paths.read_text(R/'h2_2_d5_skip5_g1_rounded_n10_fit.json'));d5=d5all['exact_count_sensitivity_fit']
    r5=json.loads(paths.read_text(R/'d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json'))['rows']+[json.loads(paths.read_text(paths.RUNS/'d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json'))]
    plt.rcParams.update({'font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig=plt.figure(figsize=(8.27,11.69))
    fig.suptitle('Observed logical errors and fitted curves',fontsize=17,fontweight='bold',y=.978)
    fig.text(.5,.943,'Physical H2-2 X-memory | Total requested sleep T = 1 s\nSleep-dependent MWPM decoding',ha='center',va='top',fontsize=11,linespacing=1.5)
    fig.text(.13,.887,'Logical error model',fontsize=12,fontweight='bold')
    fig.text(.13,.849,r'$P_L(d,u)=\frac{C}{u}\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}(au+bu^2)\right]^{g(d+1)/2}$',fontsize=16)
    fig.text(.13,.813,r'$u=\Delta t=T/(N-1)$ in seconds; $g=1$; $a,b\geq0$. $C$ absorbs fixed $T=1$ s.',fontsize=10)
    for d,fit,rows,pe,color,box in [(3,d3,d3['rows'],.00117,'#176baf',[.13,.565,.83,.18]),(5,d5,r5,.005,'#c45b19',[.13,.18,.83,.18])]:
        ax=fig.add_axes(box);u=np.array([r['interval_seconds'] for r in rows]);p=np.array([r['logical_error_probability'] for r in rows]);ci=np.array([r['logical_wilson_95'] for r in rows])
        assert all(r['decoder_policy']['p_ext']==pe for r in rows) if d==5 else True
        def curve(t):return fit['C']/t*(1+fit['lambda_1']*t+fit['lambda_2']*t*t)**((d+1)/2)
        grid=np.geomspace(.1 if d==5 else .025,1,1000);star=fit['delta_t_star_seconds'];minimum=fit['minimum_fitted_probability']
        assert abs(float(curve(star))-minimum)<1e-10
        ax.errorbar(u,p,yerr=[p-ci[:,0],ci[:,1]-p],fmt='o',mfc='none',color=color,mew=1.2,ms=5,capsize=3,elinewidth=1.1,label='Observed data (95% Wilson interval)',zorder=3)
        ax.plot(grid,curve(grid),lw=2.2,color=color,label='Fit with g = 1')
        ax.axvline(star,color=color,ls='--',lw=1.2)
        ax.annotate(f'Δt* = {star:.5f} s',xy=(star,0),xycoords=ax.get_xaxis_transform(),xytext=(0,-17),textcoords='offset points',ha='center',va='top',fontsize=10,color=color)
        ax.set_xscale('log');ax.set_xlim(.022,1.13);ax.set_ylim(0,.12 if d==3 else .06)
        ax.set_xticks([.025,.05,.1,.2,.5,1]);ax.set_xticklabels(['0.025','0.05','0.1','0.2','0.5','1'])
        ax.set_yticks([0,.04,.08,.12] if d==3 else [0,.02,.04,.06]);ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.grid(alpha=.18)
        ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)',labelpad=29);ax.set_ylabel('Logical error probability')
        shots=sum(r['shots'] for r in rows);title=f'd = {d} | {shots:,} shots'
        ax.set_title(title,loc='left',fontweight='bold',fontsize=14,pad=9);ax.legend(loc='upper left',frameon=False,fontsize=9)
        y=box[1]-(.079 if d==5 else .091)
        summary=(
            rf"Fitted   $C={fit['C']:.8f}\,\mathrm{{s}}$    $a={fit['a_per_second']:.8f}\,\mathrm{{s}}^{{-1}}$    $b={fit['b_per_second_squared']:.8f}\,\mathrm{{s}}^{{-2}}$"
            + '\n' + rf"Fixed    $g=1$    $p_{{\mathrm{{ext}}}}={pe:g}$    $p_{{\mathrm{{read}}}}=0.001$"
            + '\n' + rf"Optimum   $\Delta t^*={star:.5f}\,\mathrm{{s}}$    $P_L(\Delta t^*)={100*minimum:.4f}\%$"
        )
        fig.text(.13,y,summary,fontsize=9.7,va='top',linespacing=1.6)
    fig.text(.13,.005,'All finite-sleep settings included; zero-sleep controls excluded. d=5 N=10: 2/160 = 1.25%.\nShot-count binomial fits; dashed lines mark analytical minima. No postselection.\nOptima are model-dependent; fitted idle coefficients are effective, not calibrated physical rates.',fontsize=8.7,color='#444444',linespacing=1.4)
    out=paths.figure('h2_2_d3_d5_skip5_g1_fitted_curves.pdf');fig.savefig(out);plt.close(fig);print(out)
