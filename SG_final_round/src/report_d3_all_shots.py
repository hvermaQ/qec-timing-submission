"""Fit the combined idle ansatz and create the shareable d=3 methodology PDF.

Run `fit` with the existing scientific Python, then `pdf` with bundled ReportLab.
No provider operations and no changes to decoder results.
"""
import argparse
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'
SOURCE=RESULTS/'d3_fixed_sleep_all_shots.json'
FIT=RESULTS/'d3_fixed_sleep_linear_quadratic_fit.json'
PDF=RESULTS/'d3_h2_1e_full_methodology_all_shots.pdf'


def fit_and_plot():
    import numpy as np
    from scipy.optimize import minimize
    from scipy.special import xlogy
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    data=json.loads(SOURCE.read_text());rows=data['rows']
    x=np.array([r['delta_t_seconds'] for r in rows])
    k=np.array([r['logical_failures'] for r in rows]);n=np.array([r['shots'] for r in rows])
    alpha=1.6
    def pred(t,u):
        return np.clip(np.exp(t[0])/u*(1+t[1]*u+t[2]*u*u)**alpha,1e-12,1-1e-12)
    def objective(t,counts):
        p=pred(t,x)
        return -float(np.sum(xlogy(counts,p)+xlogy(n-counts,1-p)))
    def fit(counts,starts):
        trials=[minimize(objective,s,args=(counts,),method='L-BFGS-B',
                         bounds=[(-18,0),(0,1000),(0,1000)]) for s in starts]
        success=[r for r in trials if r.success]
        assert success
        return min(success,key=lambda r:r.fun)
    best=fit(k,[[math.log(.0017),a,b] for a,b in [(0,10),(1,10),(10,10),(10,0)]])
    def optimum(t):
        a,b=t[1:]
        return 2/(math.sqrt(((alpha-1)*a)**2+4*(2*alpha-1)*b)+(alpha-1)*a)
    saturated=-float(np.sum(xlogy(k,k/n)+xlogy(n-k,1-k/n)))
    dev=2*(best.fun-saturated)
    rng=np.random.default_rng(20261104)
    opts=[];ds=[];linear=[]
    for i in range(1000):
        kb=rng.binomial(n,pred(best.x,x))
        br=fit(kb,[best.x,[math.log(.0017),0,10]])
        sat=-float(np.sum(xlogy(kb,np.clip(kb/n,1e-12,1-1e-12))+xlogy(n-kb,np.clip(1-kb/n,1e-12,1-1e-12))))
        opts.append(optimum(br.x));ds.append(2*(br.fun-sat));linear.append(float(br.x[1]))
    out=dict(form='P_L(x)=C/x*(1+a*x+b*x^2)^alpha; x=Delta_t/(1 second)',
        source=str(SOURCE),shots=sum(r['shots'] for r in rows),
        C=float(np.exp(best.x[0])),a=float(best.x[1]),b=float(best.x[2]),alpha=alpha,
        nonnegative_coefficients=True,linear_coefficient_at_boundary=bool(best.x[1]<1e-6),
        deviance=float(dev),bootstrap_gof_p=(1+sum(d>=dev for d in ds))/1001,
        bootstrap_replicates=1000,bootstrap_seed=20261104,
        optimum_seconds=optimum(best.x),conditional_optimum_95=np.quantile(opts,[.025,.975]).tolist(),
        fitted_minimum_probability=float(pred(best.x,optimum(best.x))),
        note='Descriptive low-probability ansatz; linear term unresolved, not evidence that the physical linear channel is absent. Bounds and intervals exclude systematic errors.')
    FIT.write_text(json.dumps(out,indent=2)+'\n')
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    for zoom,name in [(False,'full'),(True,'zoom')]:
        fig,ax=plt.subplots(figsize=(9.6,4.4),layout='constrained')
        u=np.geomspace(.024,1.03,500)
        ax.plot(u,pred(best.x,u),color='#21836b',lw=2.3,label='Linear + quadratic idle ansatz (qualitative fit)')
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
        fig.savefig(RESULTS/f'figures/d3_idle_linear_quadratic_{name}.png',dpi=250)
        fig.savefig(RESULTS/f'figures/d3_idle_linear_quadratic_{name}.svg')
        plt.close(fig)
    print(json.dumps(out,indent=2))


def create_pdf():
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    data=json.loads(SOURCE.read_text());fit=json.loads(FIT.read_text());rows=data['rows']
    navy=colors.HexColor('#16384b');teal=colors.HexColor('#21836b');muted=colors.HexColor('#526571')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleCustom',fontName='Helvetica-Bold',fontSize=23,leading=27,textColor=navy,spaceAfter=12))
    styles.add(ParagraphStyle(name='Deck',fontSize=11,leading=16,textColor=muted,spaceAfter=12))
    styles.add(ParagraphStyle(name='SectionCustom',fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=navy,spaceBefore=12,spaceAfter=7))
    styles.add(ParagraphStyle(name='BodyCustom',fontSize=9.5,leading=13.7,spaceAfter=7,textColor=colors.HexColor('#213642')))
    styles.add(ParagraphStyle(name='SmallCustom',fontSize=8,leading=11,spaceAfter=6,textColor=muted))
    styles.add(ParagraphStyle(name='FormulaCustom',fontName='Helvetica',fontSize=11,leading=16,textColor=navy,spaceBefore=5,spaceAfter=8,leftIndent=10))
    story=[]
    def para(text,style='BodyCustom'):
        return Paragraph(text,styles[style])
    def p(text,style='BodyCustom'):
        story.append(para(text,style))
    def heading(text):p(text,'SectionCustom')
    def table(values,widths,small=False):
        ts='SmallCustom' if small else 'BodyCustom'
        cells=[[para(str(c),ts) for c in row] for row in values]
        t=Table(cells,colWidths=widths,hAlign='LEFT',repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0f3')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ('LINEBELOW',(0,0),(-1,0),.7,navy),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#dae3e8'))]))
        story.append(t)
    def banner(text):
        t=Table([[para(text)]],colWidths=[499])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#edf6f2')),('BOX',(0,0),(-1,-1),.5,teal),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),11),('RIGHTPADDING',(0,0),(-1,-1),11)]))
        story.append(t)
    def page():story.append(PageBreak())
    p('d=3 quantum memory<br/>Syndrome-timing experiment','TitleCustom')
    p('H2-1E emulator via Aqora | X-memory sector | All 13,000 shots<br/>Methodology, decoding, logical error probabilities and timing tradeoff<br/>3 November 2026','Deck')
    banner('<b>Key result.</b> The sample minimum is 24/2,000 = <b>1.20%</b> at N=5 (Delta t=0.25 s). N=6 and N=7 are both 1.40%; a unique best setting is not resolved. A descriptive linear + quadratic idle ansatz places its smooth minimum near 0.20 s.')
    heading('1. What was tested')
    p('A distance-3 rotated surface-code <b>X-memory sector</b> with nine data qubits (q0-q8) and one reused syndrome ancilla (q9). This probes dephasing-induced logical failure using four X-type checks per round. It does <b>not</b> include alternating X- and Z-check extraction or characterize both logical sectors.')
    p('Data indexing is row-major on a 3 x 3 grid: (0,1,2), (3,4,5), (6,7,8). The four X-check supports, in recorded order, are {1,2,4,5}, {3,4,6,7}, {0,1} and {7,8}. The logical X representative is X0 X3 X6.')
    heading('2. Per-shot protocol')
    p('<b>Prepare all nine data qubits in |+&gt; - extract four X checks - [sleep block - extract four X checks] repeated N-1 times - measure every data qubit in X.</b> Each check uses ancilla preparation, native entangling gates, measurement and reset. Syndromes are recorded for offline decoding; no physical logical recovery is applied during the run.')
    p('Each inter-round sleep block contains an explicit QIR <font name="Courier" size="8">__quantum__qis__sleep__body</font> call on each data qubit, all with the same argument u. A 10-qubit barrier brackets the block. Under static QIR, a null qubit pointer denotes virtual q0. Physical ion assignment is performed by the backend.')
    p('The native QIR was generated in Python from pinned extraction blocks, assembled to bitcode and checked by bitcode round-trip. The final extraction block retains the compiler-moved final basis rotations. N changes the number of repeated extraction blocks; sleep is not added after the final round.')
    heading('3. Time budget and execution settings')
    p('<b>u = Delta t = 1/(N-1) seconds; T_sleep = (N-1)u = 1 second per data qubit.</b> Sleep units are seconds by the agreed interpretation. This fixes requested sleep, not measured wall-clock memory duration. Extraction time is neglected, and physical parallel overlap of all nine sleep calls has not been independently verified.')
    p('All execution jobs target <b>nexus:H2-1E</b> through Aqora, with stabilizer simulation, noisy simulation enabled, optimization disabled, and idle/transport dephasing enabled. No artificial Pauli faults or offline record flips were injected. Default emulator noise channels remained active. No jobs were submitted or changed to produce this report.','SmallCustom')
    page()
    p('Error models and decoding','TitleCustom')
    p('The emulator noise, decoder assumptions and plotted analytical fit are three distinct models.','Deck')
    heading('4. Noise generating the measurements')
    p('H2-1E generates the recorded shots using its noisy circuit-level emulator. Gate, preparation, measurement/reset and cross-talk faults can affect the data or syndrome information. Idle and transport dephasing act during scheduled durations. Only selected options were overridden; the provider documentation states that other error channels remain enabled [2].')
    p('The documented memory model includes linear dephasing, with Z-fault probability p_lin(t)=r t, and a quadratic channel with probability p_quad(t)=sin<super>2</super>(f t/2). For stabilizer simulation the quadratic contribution is represented by stochastic Z faults; its frequency is adjusted by the incoherence multiplier. Both channels may be applied together [2].')
    p('For small durations/probabilities a useful qualitative description is p_idle(t) approximately gamma t + c t<super>2</super>. This is a local approximation, not a calibrated replacement for the emulator. Physical durations include scheduled idling/transport beyond the explicit sleep instruction. No backend timing trace or exact noise-parameter snapshot was used to infer microscopic coefficients here.')
    heading('5. Minimum-weight perfect matching (MWPM) model')
    table([['Decoder component','Assumed model / value'],
        ['Data faults','Independent Pauli Z fault on each data qubit before each ideal extraction round: p_data,DEM = 0.002.'],
        ['Syndrome readout','Independent classical flip of each check outcome: p_read,DEM = 0.001.'],
        ['Final data readout','Independent classical flip of each final X-readout bit: 0.001.'],
        ['Idle dependence in DEM','lambda_DEM = 0. Weights do not depend on u; probabilities were not fitted to these shots.'],
        ['Construction / algorithm','Stim ideal product-check circuit generates a graphlike detector error model (DEM), passed to PyMatching MWPM. A separate graph is built for each N with unchanged assumed probabilities.']], [120,379],True)
    p('The DEM is the paper-style phenomenological model, <b>not a Quantinuum specification-sheet model or a native-gate circuit-level DEM</b>. Ideal extraction plus independent faults approximates the real extraction circuit; it omits detailed hook faults, transport scheduling and circuit-level correlations. DEM edge weights are log-likelihood ratios derived from its fault mechanisms, conventionally log[(1-p_edge)/p_edge].','SmallCustom')
    heading('6. Detection events and logical failure')
    p('For check c, D[0,c]=s[0,c] relative to the ideal + initial check value; later D[r,c]=s[r,c] XOR s[r-1,c]. Final boundary detectors compare the last syndrome to the corresponding parity reconstructed from the nine final X outcomes. There are 4(N+1) detectors per shot.')
    p('The measured logical bit is m0 XOR m3 XOR m6. MWPM predicts whether the inferred correction flips that observable. A shot fails when the measured logical bit XOR the decoder prediction is 1. All syndromes are used; no shots are postselected away. Individual qubit faults do not each count as a logical failure: the statistic is one binary logical outcome per full shot.')
    p('Sensitivity checks retained p_read=0.001 and changed p_data,DEM to 0.02 or 0.1. They changed pooled failures by at most two shots at any setting and retained N=5 as the sample minimum. This limited robustness check does not validate the DEM as a hardware model.','SmallCustom')
    page()
    p('All-shot results','TitleCustom')
    p('Ten settings | 18 unique jobs | 13,000 shots | No postselection','Deck')
    story.append(Image(str(RESULTS/'figures/d3_idle_linear_quadratic_full.png'),width=499,height=229))
    p('<b>Figure 1.</b> Markers show pooled logical error probabilities; bars are 95% Wilson binomial intervals. The green line is the descriptive linear + quadratic idle ansatz, not a calibrated provider-noise prediction. The horizontal axis is logarithmic.','SmallCustom')
    values=[['N','Delta t (s)','Failures / shots','P_L','95% interval','R_sleep (s^-1)']]
    for r in rows:
        lo,hi=r['wilson_95']
        values.append([str(r['rounds']),f"{r['delta_t_seconds']:.6g}",f"{r['logical_failures']}/{r['shots']:,}",f"{100*r['logical_error_probability']:.2f}%",f"{100*lo:.2f}-{100*hi:.2f}%",f"{r['logical_error_probability']:.3f}"])
    table(values,[30,75,96,59,114,125],True)
    heading('7. Probability versus logical error rate')
    p('<b>P_L = failures / shots</b> is the logical error probability per complete experiment. Here we also report the requested-sleep-normalized rate <b>R_sleep = P_L / T_sleep = P_L / (1 s)</b>. Its numerical value equals P_L, but its unit is s<super>-1</super>. Wilson limits divide by the same one second. This is a probability/time metric, not an inferred exponential-decay hazard.')
    p('A rate normalized by actual total memory duration would instead use T_actual approximately 1 s + N t_ext plus preparation/readout time. Because t_ext and the scheduled sleep overlap are unmeasured, R_sleep must not be presented as a calibrated total-physical-time logical rate.','SmallCustom')
    page()
    p('Fit, interpretation and conclusion','TitleCustom')
    story.append(Image(str(RESULTS/'figures/d3_idle_linear_quadratic_zoom.png'),width=499,height=229))
    p('<b>Figure 2.</b> Zoom of the intermediate intervals. Nearby marker uncertainties overlap; the lowest observed point and the minimum of a smooth fitted curve need not coincide.','SmallCustom')
    heading('8. Linear + quadratic idle ansatz')
    p('Let x=Delta t/(1 s). Retain both nonnegative idle terms in the paper-inspired low-probability ansatz, with alpha=g(d+1)/2=1.6 from g=0.8 and d=3:')
    p('P_L(x) approximately (C/x) (1 + a x + b x<super>2</super>)<super>1.6</super>','FormulaCustom')
    p(f"Binomial maximum likelihood over all ten pooled counts gives <b>C={fit['C']:.6g}, a={fit['a']:.3g}, b={fit['b']:.6g}</b>. The linear coefficient reaches the nonnegative boundary: the curve is effectively quadratic in its idle contribution. This does not show that the physical linear channel is absent; these logical observations do not separately resolve it.")
    lo,hi=fit['conditional_optimum_95']
    p(f"The stationary condition is 2.2 b x*<super>2</super> + 0.6 a x* - 1 = 0. It gives <b>Delta t*={fit['optimum_seconds']:.3f} s</b>, with conditional 95% parametric-bootstrap interval <b>{lo:.3f}-{hi:.3f} s</b>. The fitted minimum P_L is {100*fit['fitted_minimum_probability']:.2f}%. Deviance={fit['deviance']:.2f}; boundary-aware parametric-bootstrap goodness-of-fit p={fit['bootstrap_gof_p']:.2f} (1,000 replicates). This is an acceptable descriptive curve, not evidence for uniquely identified microscopic parameters.")
    heading('9. Relation to the paper and limits')
    p('The paper [1], Eqs. 5-6, uses linear idle growth and predicts Delta t*=1/[lambda(alpha-1)], or 1/(0.6 lambda) at the chosen d and g. Its fixed-g linear-only curve fits this dataset poorly (deviance 114.5 on 8 degrees of freedom). The combined fit is an empirical extension. A lambda inferred from these same logical shots would not independently test the prediction, and one distance cannot test 1/d scaling.')
    p('The fit uses the small-P_L approximation and an asymptotic round-frequency factor 1/x, while the experiment has N rounds but N-1 intervals; small-N boundary effects can matter. Bootstrap and Wilson intervals cover shot sampling under their models, not extraction duration, scheduling, decoder mismatch or drift. Settings were refined after earlier outcomes, so optimum comparisons are exploratory.','SmallCustom')
    banner('<b>Conclusion.</b> For this d=3 X-memory implementation and fixed decoder, intermediate intervals outperform both tested extremes. The sample minimum is N=5 (0.25 s); N=5,6,7 are not clearly distinguished. The combined idle ansatz suggests a smooth optimum around 0.20 s. The experiment supports the qualitative timing tradeoff, but does not yet provide an independently calibrated verification of the paper optimum.')
    page()
    p('Data integrity and references','TitleCustom')
    heading('10. Pooling and reproducibility')
    p('All fixed-total-requested-sleep H2-1E shots from the three compatible batches were included exactly once. Earlier variable-total-sleep two-round sweeps and H2-2E data were excluded. Repeated N values used identical bitcode and matching emulator options. Raw payload hashes were verified, packed shot records agreed with formatted counts, and the final logical parity was cross-checked directly from q0,q3,q6.')
    table([['Batch','N settings','Shots'],
        ['Original coarse','2,5,10,20,40','500 each; N=40 has two 250-shot jobs'],
        ['Refinement','4,5,6,7,8','1,000 each except 500 for N=5'],
        ['Resolution','3,4,5,6,7,8,10','1,000 each except 500 for N=3 and N=10']], [105,130,264],True)
    p('Pooling uses sums of failures and shots, not averages of percentages. A pooled repeated-setting homogeneity check gives deviance 12.56 on 8 degrees of freedom (p=0.128); this does not establish that all emulator conditions were stationary. Nearby N=5 versus N=6 or N=7 each has exploratory two-sided Fisher p=0.676, consistent with the unresolved local ordering.')
    heading('Saved evidence (relative to SG_final_round)')
    for text in [
        '<b>Decoded data and provenance:</b> results/d3_fixed_sleep_all_shots.json. Records each job ID, per-batch shot and failure counts, source directory, raw SHA-256 and bitcode SHA-256.',
        '<b>Combined fit:</b> results/d3_fixed_sleep_linear_quadratic_fit.json. Records the retained linear/quadratic form, parameter estimates and bootstrap settings.',
        '<b>QIR construction:</b> src/fixed_sleep_d3.py; pinned source artifact results/hardware/programs/d3_X_r2_p0.ll is relative to the repository root.',
        '<b>Decoder and analysis:</b> src/analyze_fixed_sleep_all.py; stored DEMs in results/decoders/d3_fixed_sleep_all_shots/.',
        '<b>Report reproduction:</b> src/report_d3_all_shots.py, fit and pdf actions. The fit action uses the saved pooled counts without re-decoding, retuning matching weights or contacting Aqora.',
        '<b>Raw batches:</b> runs/d3_fixed_sleep_690baca08b24dfd2; runs/d3_fixed_sleep_refinement_3bb6e107a0ff6de3; runs/d3_fixed_sleep_resolution_c2380924e8c69578.']:
        p(text,'SmallCustom')
    heading('References')
    p('[1] T. Haug, K. Bharti and L. Aolita. <i>Exponential logical-error reduction in quantum memories via optimal syndrome-measurement timing.</i> arXiv:2608.06242v2 (30 September 2026), Eqs. 1-6 and discussion of finite measurement duration.<br/><link href="https://arxiv.org/html/2608.06242v2" color="#185e87">https://arxiv.org/html/2608.06242v2</link>','SmallCustom')
    p('[2] Quantinuum Systems. <i>Emulator Noise Model</i>, physical-noise and dephasing sections. Documents retained default channels, linear and quadratic memory noise, and stabilizer treatment. Defaults are subject to provider updates.<br/><link href="https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html" color="#185e87">Quantinuum emulator noise-model documentation</link>','SmallCustom')
    p('Report scope: saved H2-1E d=3 fixed-requested-sleep execution data through the resolution batch. The phenomenological matching probabilities and the fitted logical-curve coefficients are assumptions/estimates for analysis, not artificial faults injected into the submitted programs.','SmallCustom')
    def footer(canvas,doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#d7e3e9'));canvas.line(48,42,547,42)
        canvas.setFont('Helvetica',8);canvas.setFillColor(muted)
        canvas.drawString(48,29,'d=3 X-memory | H2-1E | Fixed requested sleep: 1 s')
        canvas.drawRightString(547,29,f'{doc.page}')
        canvas.restoreState()
    doc=SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=40,bottomMargin=55,
                          title='d=3 H2-1E X-memory: full methodology and all-shot timing results',author='QEC timing experiment')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(PDF)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['fit','pdf'])
    args=parser.parse_args()
    fit_and_plot() if args.action=='fit' else create_pdf()
