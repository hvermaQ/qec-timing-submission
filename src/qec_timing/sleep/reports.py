"""Markdown reports (to results/sleep/) and shareable PDFs (to results/sleep/figures/).

Text is verbatim from SG_final_round/src/ (including the prose's hard-coded numbers and its
references to the old SG_final_round/ layout); only the output paths changed.

    fixed_sleep_all_md(result)       analyze_fixed_sleep_all.py `write_report` -> d3_fixed_sleep_all_shots.md
    redecode_d3_md(result)           redecode_d3_sleep_dependent.py `report`   -> d3_sleep_dependent_redecode.md
    redecode_d5_md(result)           redecode_d5_sleep_dependent.py `report`   -> d5_sleep_dependent_redecode.md
    d5_sleep_dependent_md(d, path)   fit_d5_sleep_dependent.py `report`        -> d5_sleep_dependent_linear_quadratic_fit[_n3_plus].md
    d3_methodology_pdf()             report_d3_all_shots.py `pdf`              -> figures/d3_h2_1e_full_methodology_all_shots.pdf
    h2_2e_summary_pdf()              create_h2_2e_summary_pdf.py               -> figures/h2_2e_d3_sleep_summary.pdf
    combined_sleep_pdf()             create_combined_sleep_pdf.py              -> figures/h2_1e_h2_2e_d3_sleep_summary.pdf
    sleep_explanation_pdf()          create_sleep_explanation_pdf.py           -> figures/sleep_parameter_explanation.pdf + figures/pdf_preview/

The PDFs need reportlab (and pypdf, pypdfium2), imported inside the functions so the package
imports without them. h2_2e_summary_pdf and combined_sleep_pdf also need the macOS Arial
fonts under /System/Library/Fonts. The committed PDFs are not regression targets.
"""
import json
from types import SimpleNamespace

from . import paths

R = paths.RESULTS


# --------------------------------------------------------------------------- markdown

def fixed_sleep_all_md(result):
    lines=['# All-shot d=3 X-memory fixed-requested-sleep analysis','',
        'H2-1E, 18 unique execution jobs, 13,000 shots. Only the coarse, refinement and resolution fixed-sleep batches are pooled; no two-round variable-total-sleep sweep or H2-2E shots. Raw hashes and formatted/packed counts verified. Repeated N used identical bitcode across batches; platform, requested interval and emulator options match. No provider jobs submitted or modified.','',
        'Nine data qubits, four X stabilizer checks per extraction round with a reused ancilla, initial logical + state and final X readout. N rounds separated by N-1 sleep blocks. u=Delta t=1/(N-1) seconds, total requested sleep one second per data qubit. Extraction duration is neglected; physical parallel overlap of the nine sleep calls remains unverified.','',
        result['primary_decoder']+'. The same weights are retained for every batch and have not been optimized on these outcomes. Failure is decoder-predicted logical flip XOR final X parity on q0,3,6.','',
        '| N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |',
        '|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        lo,hi=r['wilson_95']
        lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% |")
    best=min(result['rows'],key=lambda r:r['logical_error_probability'])
    lines+=['',f"Sample minimum: N={best['rounds']}, Delta t={best['delta_t_seconds']:.6g} s. Neighboring settings must be compared with sampling uncertainty; selection was adaptive after earlier batches, so minimum claims are exploratory.",'',
        '## Analytical fits','',
        'Binomial maximum likelihood on all ten pooled failure counts; no least-squares fit to percentages. Fix alpha=g(d+1)/2=1.6 using the paper g=.8, extrapolated to d=3. Probabilities are modeled directly using the paper low-probability approximation P_L approximately R T with T_sleep=1 s; no saturation correction. C absorbs all distance/prefactor factors. This is a descriptive fit, not extraction of microscopic error parameters.','',
        'Paper-shaped linear-idle ansatz: P_L(u)=C(1+a u)^1.6/u; u*=1/(.6a). Quadratic-idle extension: P_L(u)=C(1+a u^2)^1.6/u; u*=1/sqrt(2.2a). The latter substitutes quadratic growth for linear growth; it is an empirical extension, not Eq. 6 of the paper or the full Quantinuum noise model. Both have two fitted positive parameters.','']
    for fit_ in result['fits']:
        lo,hi=fit_['conditional_optimum_95_bootstrap']
        lines.append(f"- {fit_['model']}: C={fit_['C']:.8g}, a={fit_['a']:.8g}; u*={fit_['optimum_seconds']:.5g} s (conditional 95% parametric-bootstrap interval {lo:.5g}–{hi:.5g} s); binomial deviance={fit_['deviance']:.4g}, df={fit_['dof']}; asymptotic goodness-of-fit p={fit_['asymptotic_gof_p']:.5g}, bootstrap p={fit_['bootstrap_gof_p']:.5g} (1,000 replicates, seed 20261103). If a model fails goodness of fit, its optimum interval is not a reliable physical confidence interval.")
    h=result['batch_homogeneity']
    lines+=['',f"Pooled-batch homogeneity check: deviance={h['deviance']:.5g}, df={h['dof']}, asymptotic p={h['asymptotic_p']:.5g}. This is a limited check for between-batch differences at repeated N, not proof of independence or stationary noise.",'',
        '## Conclusion','',
        'The sample minimum is 1.20% at N=5 (u=.25 s), while N=6 and N=7 are both 1.40%. These neighboring settings do not establish a unique discrete optimum. Both tails are substantially higher, supporting an interior region of improved memory performance for this implementation and decoder.','',
        'The paper-shaped fit with fixed g=.8 is strongly rejected by the pooled data (deviance 114.51 on 8 degrees of freedom). The quadratic-idle extension gives an acceptable descriptive fit (deviance 9.75 on 8 degrees of freedom) and a smooth optimum near .198 s, conditional 95% bootstrap interval .181–.225 s. Its minimum fitted probability is about 1.63%. The bootstrap bounds are conditional on the chosen curve, fixed exponent, independent binomial shots and neglected extraction duration; they exclude systematic uncertainty.','',
        '[Quantinuum documentation](https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html) describes both linear and quadratic dephasing, with quadratic dephasing represented by stochastic Z faults in stabilizer simulation. This motivates trying a quadratic extension; its success alone does not identify a microscopic noise law.']
    lines+=['','## Comparison with the paper','',
        '[Haug, Bharti and Aolita, arXiv:2608.06242v2](https://arxiv.org/html/2608.06242v2), Eqs. 5–6, predicts u*=2/[lambda(g(d+1)-2)]; d=3, g=.8 gives u*=1/(.6 lambda). Its assumptions include approximately linear idle probability, small logical probability and sufficiently many rounds to suppress time-like faults. The physical idle slope is p lambda, so lambda is relative to extraction noise, not simply an absolute idle rate or the sleep-unit conversion.','',
        'Fitting lambda to these same logical probabilities and substituting it into Eq. 6 is an internal consistency calculation, not an independent prediction. We have no separately calibrated phenomenological p, lambda and g for this circuit/backend. Quantinuum circuit-level noise includes gate/readout/transport contributions and non-linear dephasing; the decoder is deliberately phenomenological and mismatched. Small N has substantial finite-round and boundary effects (N rounds but N-1 intervals). Thus disagreement with the simple paper fit need not contradict its derivation.','',
        'The two tails versus intermediate intervals can support a timing tradeoff within this decoder/setup. They cannot establish the paper 1/d scaling from a single distance, a unique best intermediate N, or a physically calibrated optimum. Error bars cover independent shot sampling only, not decoder mismatch, batching drift, uncertain overlap or extraction duration. The quadratic extension was selected after examining this experiment and its known non-linear idle model; model comparisons are exploratory.','',
        '## Provenance and reproducibility','',
        'The JSON beside this report records each job ID, source directory, raw SHA-256 and per-batch decoded failures. All stored DEMs are under results/decoders/d3_fixed_sleep_all_shots. Run the companion analysis with the established NumPy/Stim/PyMatching/SciPy environment. Preserve earlier reports; this report supersedes their shot totals only for the same fixed-sleep protocol.']
    paths.write_text(R/'d3_fixed_sleep_all_shots.md', '\n'.join(lines)+'\n')


def redecode_d3_md(result):
    from .decoder import LEGACY_SOURCES as SOURCES
    lines=['# Sleep-dependent phenomenological MWPM: all saved H2-1E d=3 shots','',
        '13,000 shots, 18 jobs, N=2,3,4,5,6,7,8,10,20,40. Same fixed-requested-sleep dataset and logical observable as the original PDF. Each raw-file hash and submitted-bitcode hash verified; no duplicate jobs; original baseline failure counts reproduced exactly at every N. No provider access, new jobs, HQCs or injected noise.','',
        '## Fixed model (no training or tuning on outcomes)','',
        'Use published H2-1E linear rate r=.0028/s, quadratic frequency nu=.043 cycles/s (units 2*pi rad/s), and stabilizer incoherence factor m=2. Thus p_lin(u)=r*u, p_quad(u)=sin(pi*nu*m*u)^2. Independent Z channels compose by odd parity, p_idle=p_lin+p_quad-2*p_lin*p_quad; two Z faults cancel.','',
        'Retain original phenomenological extraction floor p_ext=.002 and symmetric syndrome/final-readout flip probability p_read=.001. These are baseline assumptions, not newly derived from gate specifications. First-round p_data=.002, and the remaining N-1 rounds use p_data=p_ext+p_idle-2*p_ext*p_idle. Exactly N-1 modeled sleep intervals, none before first extraction or after last. The independent ideal-product-check model and PyMatching algorithm are unchanged.','',
        'This adds time dependence to matching weights, not to already-recorded shots. The quoted published defaults are not independently confirmed execution-time parameters. Each qubit is assumed to experience exactly u of additional idling per gap; physical parallel overlap and detailed transport/extraction timing remain unverified. Readout asymmetry and gate-correlated faults are not added.','',
        '| N | u (s) | p_idle(u) | p_data after sleep | Baseline P_L | Updated failures / shots | Updated P_L | 95% Wilson interval | Corrected / new failures |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        lo,hi=r['wilson_95']
        lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['p_idle']:.7g} | {r['p_data_after_sleep']:.7g} | {100*r['baseline_probability']:.2f}% | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.2f}% | {100*lo:.2f}-{100*hi:.2f}% | {r['corrected_baseline_failures']} / {r['new_failures']} |")
    best=min(result['rows'],key=lambda r:r['logical_error_probability'])
    paired=result['paired_aggregate']
    lines+=['',f"Updated sample minimum: N={best['rounds']}, u={best['delta_t_seconds']:.7g} s, {best['logical_failures']}/{best['shots']}={100*best['logical_error_probability']:.2f}%. This sample minimum is not a uniquely established optimum.",'',
        f"Paired comparison across all recorded shots: {paired['corrected']} baseline failures corrected, {paired['new_failures']} new failures introduced, net {paired['net_failure_reduction']} fewer failures. Exact two-sided McNemar p={paired['exact_mcnemar_p']:.6g}, testing symmetric decoder discordances under independent-shot assumptions. This aggregate describes the actual unequal shot allocation across settings, not a uniform-N average or a memory operating point. Per-setting paired comparisons are exploratory and unadjusted for multiple testing.",'',
        'Probabilities are per full experiment. The requested-sleep-normalized rate is P_L/(1 s); actual total-time rates remain unknown because extraction duration is neglected. Wilson intervals cover shot sampling only, not model or scheduling uncertainty. No smooth functional fit is used: plotted connecting lines are guides to the eye. A more realistic DEM need not improve this finite dataset, and improvement here does not identify the true backend noise model. The decoder policy was chosen after inspecting prior experiments, so this is an exploratory comparison, despite no numerical training on logical labels.','',
        '## Sources and artifacts','',
        *[f'- {url}' for url in SOURCES],
        '- JSON: all per-setting parameters, raw/bitcode hashes and per-batch failure counts.',
        '- NPZ: baseline/updated per-shot predictions and failure masks, ordered by JSON sources and offsets.',
        '- results/decoders/d3_sleep_dependent/nN.dem: exact matching models; SHA-256 in JSON.',
        '- Baseline files and PDF were preserved.']
    if paired['corrected']+paired['new_failures']==0:
        lines.insert(4,'Result: the two DEMs have different fault probabilities/weights, but predict identical logical corrections on every recorded shot. Updated probabilities and confidence intervals therefore exactly equal the baseline. This reweighting provides no observed decoding gain; it does not show that the physical idle probability is independent of sleep.\n')
    paths.write_text(R/'d3_sleep_dependent_redecode.md', '\n'.join(lines)+'\n')


def redecode_d5_md(result):
    lines=['# d=5 H2-1E: pooled raw data and sleep-dependent DEM comparison','',
        f"{result['unique_jobs']} unique completed jobs; {result['total_shots']} total shots. All completed d=5 H2-1E sleep runs recorded locally are included once. Total requested sleep is retained as a grouping key; T=1 and T=0.5 are never pooled together. No jobs submitted.",'',
        '## Decoder policy','',
        'Fixed baseline: p_data=.002 before each ideal extraction round; syndrome and final data readout flips .001. Sleep-dependent: retain p_ext=.002 and readout .001; p_lin(u)=.0028u, p_quad(u)=sin(pi*.043*2*u)^2, p_idle=p_lin+p_quad-2*p_lin*p_quad. First extraction has p_ext only; each later extraction has p_ext+p_idle-2*p_ext*p_idle. There are exactly N-1 sleep contributions. This reproduces the existing d=3 sleep-dependent prescription with d=5 code geometry, with no fitting to d=5 logical labels. Published-default assumptions transferred by this policy are not execution-time calibration parameters. Gate correlations, detailed transport/extraction durations and readout asymmetry are omitted.','',
        '## Paired comparison on the same expanded dataset','',
        '| T (s) | N | Delta t (s) | Shots | Fixed failures | Fixed P_L | Sleep failures | Sleep P_L | Sleep 95% Wilson CI | Change in failures | Corrected / introduced |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        lo,hi=r['sleep_wilson_95']
        lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['shots']} | {r['fixed_failures']} | {100*r['fixed_probability']:.3f}% | {r['sleep_failures']} | {100*r['sleep_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% | {r['failure_count_change']:+d} | {r['corrected_baseline_failures']} / {r['introduced_failures']} |")
    lines+=['','## Distinguishing new shots from new decoder weights','',
        'All downloaded repeats are pooled by requested total sleep and extraction count. Differences between the earlier report and the new fixed column are due to this additional data. Differences between fixed and sleep-dependent columns above are solely from re-decoding identical shots. Every previously reported per-job fixed count was reproduced exactly.','',
        '| T (s) | N | Earlier reported fixed failures / shots | Added shots | Expanded fixed failures / shots |','|---:|---:|---:|---:|---:|']
    for r in result['rows']:lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {r['previous_report_failures']}/{r['previous_report_shots']} | {r['newly_added_shots']} | {r['fixed_failures']}/{r['shots']} |")
    a=result['paired_aggregate'];lines+=['',f"Across all groups, {a['corrected']} fixed-decoder failures were corrected and {a['introduced']} failures were introduced; net failure-count change {a['net_failure_change']:+d}. Exact paired McNemar p={a['exact_mcnemar_p']:.6g}. This aggregate reflects this shot allocation across different N and T; it is not an operating-point probability. Per-N paired tests are exploratory and unadjusted for multiple comparisons.",'',
        'Probabilities are per complete experiment. Wilson intervals assume independent common-probability shots and exclude decoder/calibration uncertainty and batch drift. The N=6 original/repeat discrepancy remains relevant after pooling; all per-batch counts are retained below. The model is more sleep-aware but is not guaranteed to improve every setting or match the backend. A sample minimum is not a resolved optimum.','',
        '## Per-batch provenance','', '| T (s) | N | Job ID | Shots | Fixed failures | Sleep failures |','|---:|---:|---|---:|---:|---:|']
    for r in result['rows']:
        for s in r['sources']:lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {s['job_id']} | {s['shots']} | {s['fixed_failures']} | {s['sleep_failures']} |")
    lines+=['','Artifacts: JSON contains all parameters, per-job provenance, offsets, hashes, DEM paths and paired tests. NPZ contains paired per-shot predictions and failure masks. The separate pooled-raw NPZ contains syndrome arrays, final data readouts and per-shot source-job indices. Original provider payload files and earlier analysis snapshot were preserved.','']
    # The original wrote this report without a final newline after the joined lines.
    paths.write_text(R/'d5_sleep_dependent_redecode.md', '\n'.join(lines))


def d5_sleep_dependent_md(d, path):
    lo,hi=d['conditional_optimum_95']
    lines=['# d=5 sleep-dependent DEM: linear-plus-quadratic idle fit','',
        f"Uses only T_sleep=1 s sleep-dependent-DEM outcomes: N={d['min_rounds']} through 10, {d['shots']:,} shots. Excluded N settings: {d['excluded_rounds']}. The T_sleep=0.5 s experiment is excluded. No provider submissions, decoder retuning or injected faults.",'',
        '## Model and fitting','',
        'Let x=Delta t/(1 second). P_L(x)=C/x*(1+a*x+b*x^2)^alpha, with g=.8 and alpha=g(d+1)/2=2.4 fixed to match the distance-adjusted convention used in the d=3 methodology. C,a,b are fitted by binomial maximum likelihood on failure/shot counts; a,b>=0. Both idle terms are included in the model even if a fitted coefficient reaches zero.','',
        f"C={d['C']:.10g}; a={d['a']:.10g}; b={d['b']:.10g}. Linear coefficient at boundary: {d['linear_at_boundary']}. This does not imply that the physical linear noise channel is absent.",'',
        'Differentiating log(P_L) gives -1/x + alpha*(a+2*b*x)/(1+a*x+b*x^2)=0. Therefore (alpha-1)*a*x+(2*alpha-1)*b*x^2=1, or 1.4*a*x+3.8*b*x^2=1. The stable positive root is x*=2/[1.4*a+sqrt((1.4*a)^2+15.2*b)].','',
        f"Analytical Delta t*={d['optimum_seconds']:.6g} s. Conditional 95% parametric-bootstrap interval={lo:.6g}–{hi:.6g} s. Fitted minimum P_L={100*d['fitted_minimum_probability']:.4g}%. The root was checked against numerical minimization and the stationary equation.",'',
        f"Binomial deviance={d['binomial_deviance']:.6g}; nominal residual df={d['nominal_residual_df']}. Boundary-aware parametric-bootstrap goodness-of-fit p={d['bootstrap_gof_p']:.6g}, from {d['bootstrap_successes']} successful refits, seed={d['bootstrap_seed']}. Bootstrap intervals are conditional on this chosen model and do not establish a physically calibrated optimum.",'',
        d['caveats'],'',
        '## Inputs','', '| N | Delta t (s) | Failures / shots | Measured P_L | Fitted P_L |','|---:|---:|---:|---:|---:|']
    for r,p in zip(d['rows'],d['fitted_probabilities']):lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['sleep_failures']}/{r['shots']} | {100*r['sleep_probability']:.3f}% | {100*p:.3f}% |")
    paths.write_text(path, '\n'.join(lines)+'\n')


# --------------------------------------------------------------------------- PDFs (reportlab)

def d3_methodology_pdf():
    """Shareable d=3 H2-1E methodology PDF (report_d3_all_shots.py `pdf`); needs fits.d3_linear_quadratic first."""
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    SOURCE=R/'d3_fixed_sleep_all_shots.json';FIT=R/'d3_fixed_sleep_linear_quadratic_fit.json'
    PDF=paths.figure('d3_h2_1e_full_methodology_all_shots.pdf')
    data=json.loads(paths.read_text(SOURCE));fit=json.loads(paths.read_text(FIT));rows=data['rows']
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
    story.append(Image(str(paths.figure('d3_idle_linear_quadratic_full.png')),width=499,height=229))
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
    story.append(Image(str(paths.figure('d3_idle_linear_quadratic_zoom.png')),width=499,height=229))
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
    return PDF


def _summary_kit():
    """Fonts, styles and helpers shared by the two emulator summary PDFs.

    This is the part of create_h2_2e_summary_pdf.py that create_combined_sleep_pdf.py used to
    exec(); both now call it. Needs reportlab and the macOS Arial fonts.
    """
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.colors import HexColor, white
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('Arial', '/System/Library/Fonts/Supplemental/Arial.ttf'))
    pdfmetrics.registerFont(TTFont('ArialBold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='ArialBold', italic='Arial', boldItalic='ArialBold')
    NAVY, BLUE, GREY = map(HexColor, ['#17334D', '#156C9E', '#526575'])
    styles = {
     'title': ParagraphStyle('title', fontName='ArialBold', fontSize=23, leading=27, textColor=NAVY, spaceAfter=7),
     'sub': ParagraphStyle('sub', fontName='Arial', fontSize=9, leading=12, textColor=GREY, spaceAfter=12),
     'h': ParagraphStyle('h', fontName='ArialBold', fontSize=11.5, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=5),
     'body': ParagraphStyle('body', fontName='Arial', fontSize=9.5, leading=12.7, spaceAfter=7),
     'small': ParagraphStyle('small', fontName='Arial', fontSize=8.3, leading=11.5, textColor=GREY, spaceAfter=7),
     'cell': ParagraphStyle('cell', fontName='Arial', fontSize=9.5, leading=13),
     'th': ParagraphStyle('th', fontName='ArialBold', fontSize=9, leading=12, textColor=white),
     'formula': ParagraphStyle('formula', fontName='ArialBold', fontSize=14, leading=22, textColor=NAVY, spaceAfter=6),
    }
    story=[]
    def p(text, style='body'):
        story.append(Paragraph(text, styles[style]))

    def box(content, background='#EDF4F8'):
        t=Table([[Paragraph(text, styles[style])] for text,style in content], colWidths=[491])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),HexColor(background)),
            ('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        story.append(t);story.append(Spacer(1,8))
    return SimpleNamespace(NAVY=NAVY, BLUE=BLUE, GREY=GREY, styles=styles, story=story, p=p, box=box, white=white, HexColor=HexColor)


def h2_2e_summary_pdf():
    """Two-page H2-2E d=3 sleep-sweep summary (was output/pdf/h2_2e_d3_sleep_summary.pdf)."""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.pagesizes import A4
    from pypdf import PdfReader
    OUT = paths.figure('h2_2e_d3_sleep_summary.pdf')
    data = json.loads(paths.read_text(R/'d3_sleep_five_point_h2_2e_1000.json'))
    noise = json.loads(paths.read_text(R/'d3_sleep_five_point_h2_2e_noise_characterization.json'))
    kit = _summary_kit()
    NAVY, GREY, styles, story, p, box, white, HexColor = kit.NAVY, kit.GREY, kit.styles, kit.story, kit.p, kit.box, kit.white, kit.HexColor
    p('Sleep-dependent logical errors', 'title')
    p('H2-2E emulator via Aqora  |  Distance-3 X-memory experiment  |  2 November 2026', 'sub')
    box([('<b>Measured quantity:</b> logical error probability per complete two-round experiment. No division by time has been performed.', 'body')])
    p('What was tested', 'h')
    p('<b>Code:</b> distance d = 3 rotated surface-code geometry, with nine data qubits and one ancilla reused serially. Each extraction round measures the four X stabilizers. This tests the X-memory sector; Z-stabilizer extraction and arbitrary encoded states were not tested.')
    p('<b>Preparation and readout:</b> prepare all nine data qubits in |+&gt; and read them out in the X basis at the end. Record all eight syndrome outcomes and all nine final data outcomes (17 Boolean outputs per shot).')
    box([('Prepare |+&gt; on nine data qubits<br/>→ X-stabilizer round 1 → all-data sleep block<br/>→ X-stabilizer round 2 → final X readout → offline decoding', 'body')])
    p('<b>Wait:</b> insert one explicit QIR sleep call on each data qubit, with a common raw argument u, between the two extraction rounds. Ten-qubit barriers bound the block; the ancilla has no sleep call. Even u = 0 retains nine explicit sleep calls. Physical units and simultaneous overlap of the nine waits remain unverified.')
    p('<b>Sweep:</b> u = 0, 0.1, 0.5, 0.75, 1; 1,000 shots per setting (5,000 total). No artificial Pauli faults or offline measurement flips were added.')
    p('Logical error probabilities', 'h')
    headers=['Raw argument u','Failures / shots','P<sub>L</sub>(u)','95% Wilson interval']
    rows=[[Paragraph(x, styles['th']) for x in headers]]
    for row in data['rows']:
        lo,hi=row['wilson_95']
        vals=[f"{row['duration_raw']:g}",f"{row['logical_failures']} / {row['shots']}",
              f"{row['logical_error_rate']:.3f} ({100*row['logical_error_rate']:.2f}%)",f"{100*lo:.2f}% - {100*hi:.2f}%"]
        rows.append([Paragraph(v,styles['cell']) for v in vals])
    t=Table(rows,colWidths=[100,116,137,138],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#F0F4F7'),white]),
     ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
     ('LEFTPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,-1),(-1,-1),.5,HexColor('#CCD8E0'))]))
    story.append(t);story.append(Spacer(1,8))
    p('P<sub>L</sub> = decoded failures / shots. A failure is the final logical-X parity on data qubits 0, 3, 6 XOR the decoder’s predicted logical correction. The probabilities above are not per-round or per-second quantities.', 'small')
    p('<b>Decoder:</b> fixed minimum-weight perfect matching with assumed p<sub>data</sub> = 0.002 per round and p<sub>read</sub> = 0.001, identical across settings. Using p<sub>data</sub> = 0.02 or 0.1 gave the same failure counts. These assumptions specify decoder weights, not injected noise. All 5,000 packed shots were verified against returned joint counts.', 'small')

    story.append(PageBreak())
    p('Physical errors and interpretation', 'title')
    p('Probability notation, raw-argument scaling, and the connection to future timing experiments', 'sub')
    p('Physical data-error probability p<sub>data</sub>(u)', 'h')
    p('Here p<sub>data</sub>(u) denotes the <b>mean final X-readout error probability per data qubit</b>, averaged across the nine qubits and 1,000 shots. It includes background circuit errors; it is not a directly isolated idle-channel probability. It is distinct from P<sub>L</sub>(u).')
    vals='; '.join(f"u = {r['duration_raw']:g}: <b>{100*r['mean_data_error']:.3f}%</b>" for r in noise['rows'])
    p(vals+'.')
    box([('p<sub>data</sub>(u) ≈ 0.001333 + 0.015245 u + 0.084495 u<super>2</super>', 'formula'),
         ('u is the raw sleep argument, with no verified physical-time unit. Fitted values are probabilities, not percentages. Valid only as a descriptive interpolation over 0 ≤ u ≤ 1.', 'small')])
    p('This unweighted fit fixes its intercept to the measured u = 0 background. Its coefficients are <b>not calibrated physical rates</b>. Unknown pre-existing idle time can turn quadratic dephasing into an apparent linear contribution as well. The fit does not establish an exact noise law, T<sub>2</sub>, independent faults, or parallel timing.')
    p('Overall error model and what the sweep supports', 'h')
    p('Jobs requested noisy stabilizer simulation, optimization disabled, and both idle and transport dephasing enabled. Other backend-default errors remained enabled, including gate, preparation, readout and crosstalk faults. Quantinuum documents stochastic Z memory faults with linear-duration and short-time-quadratic contributions in stabilizer mode [1].')
    p('The inter-round mean detector probability rises from <b>0.450% to 23.975%</b>, while the first-round mean stays between 0.250% and 0.500%. This localizes the dominant increase across the inserted wait. The physical-error curvature is consistent with a substantial quadratic contribution. The u = 0.1 logical comparison is inconclusive at this shot count; the larger waits show clear increases.')
    p('The data do not uniquely isolate idle dephasing from transport, background faults, scheduling changes and decoder effects. Confirmed units and timing plus matched noise-channel controls are needed to infer physical idle rates. One job per setting does not measure run-to-run variation.')
    p('Probability now; time-normalized metric later', 'h')
    p('For a future R-round experiment with a physical wait Δt between adjacent rounds, measure P<sub>L</sub>(R, Δt) and the total duration T. The planned time-normalized metric is <b>r<sub>L</sub><super>eff</super> = P<sub>L</sub>(R, Δt) / T</b>, with units of inverse time. Specify whether T includes preparation/readout and extraction time; storage-and-extraction time is approximately Rτ<sub>syn</sub> + (R - 1)Δt. This metric is not automatically a constant-hazard parameter, and the present two-round probabilities cannot simply be extrapolated to many rounds.')
    p('[1] Quantinuum: <link href="https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html" color="#156C9E">Emulator Noise Model</link> and <link href="https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html" color="#156C9E">H2 Emulator Defaults</link>.<br/>Evidence: saved Aqora H2-2E five-point run, build 67d11d0348065703; decoded-count and noise-characterization JSON records in SG_final_round/results/.', 'small')
    box([('Conclusion', 'h'),('Increasing the raw sleep argument produces a pronounced increase in physical data-error probability and decoded logical error probability in this d = 3, two-round X-memory experiment. The growth is compatible with the emulator’s memory-noise model, but does not establish a pure idle-noise rate, physical sleep units, or simultaneous waits. Future many-round experiments will report time-normalized logical error only after total physical duration is defined and verified.', 'body')], '#EAF3EF')

    def footer(canvas, doc):
        canvas.setStrokeColor(HexColor('#D3DDE5'));canvas.line(52,37,A4[0]-52,37)
        canvas.setFont('Arial',8);canvas.setFillColor(GREY)
        canvas.drawString(52,24,'H2-2E | d = 3 | Logical error probability per experiment')
        canvas.drawRightString(A4[0]-52,24,f'{doc.page} / 2')

    SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=52,rightMargin=52,topMargin=40,bottomMargin=48,
     title='H2-2E distance-3 sleep sweep: logical error probabilities',author='QEC timing experiment team').build(story,onFirstPage=footer,onLaterPages=footer)
    reader=PdfReader(str(OUT))
    assert len(reader.pages)==2, f'Expected two pages, got {len(reader.pages)}'
    text='\n'.join(page.extract_text() for page in reader.pages)
    for expected in ['0.015245','0.084495','140 / 1000','Conclusion','probability']:
        assert expected in text, expected
    print(OUT)
    return OUT


def combined_sleep_pdf():
    """Two-emulator (H2-1E + H2-2E) d=3 summary PDF; was never committed."""
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.pagesizes import A4
    from pypdf import PdfReader
    kit = _summary_kit()
    NAVY, GREY, styles, story, p, box, white, HexColor = kit.NAVY, kit.GREY, kit.styles, kit.story, kit.p, kit.box, kit.white, kit.HexColor
    OUT=paths.figure('h2_1e_h2_2e_d3_sleep_summary.pdf')
    a=json.loads(paths.read_text(R/'d3_sleep_five_point_h2_1e_1000.json'))
    b=json.loads(paths.read_text(R/'d3_sleep_five_point_h2_2e_1000.json'))
    ca=json.loads(paths.read_text(R/'d3_sleep_five_point_h2_1e_noise_characterization.json'))
    cb=json.loads(paths.read_text(R/'d3_sleep_five_point_h2_2e_noise_characterization.json'))
    p('Distance-3 sleep sweep','title')
    p('H2-1E and H2-2E emulators via Aqora | 2 November 2026','sub')
    p('Protocol and measured quantities','h')
    p('Both sweeps use the same distance d = 3 rotated surface-code geometry: nine data qubits and one reused ancilla, with four X-stabilizer checks per round. This is an X-memory-sector test; Z-stabilizer extraction and arbitrary encoded states were not tested.')
    box([('Prepare |+&gt; on all nine data qubits<br/>→ X-stabilizer round 1 → all-data sleep block<br/>→ X-stabilizer round 2 → final X readout → offline matching decoding','body')])
    p('The block contains nine explicit QIR sleep calls with common raw argument u, bounded by ten-qubit barriers. The ancilla has no sleep call. The u = 0 control retains all nine calls. Physical units and simultaneous overlap remain unverified.')
    p('Each emulator ran 1,000 shots at each u = 0, 0.1, 0.5, 0.75, 1: 5,000 shots per emulator. No artificial faults or offline flips were added. The earlier three-point H2-1E experiment is not pooled into these results.')
    p('<b>P<sub>L</sub>(u)</b> is decoded logical error probability per complete two-round experiment. <b>p<sub>data</sub>(u)</b> is final X-readout error probability averaged across all nine data qubits, including background circuit errors. Neither is divided by time.')
    p('Results: probabilities per experiment','h')
    rows=[[Paragraph(v,styles['th']) for v in ['Raw u','H2-1E<br/>P<sub>L</sub>','H2-2E<br/>P<sub>L</sub>','H2-1E<br/>mean p<sub>data</sub>','H2-2E<br/>mean p<sub>data</sub>']]]
    for x,y,z,w in zip(a['rows'],b['rows'],ca['rows'],cb['rows']):
        vals=[f"{x['duration_raw']:g}",f"{x['logical_error_rate']:.3f}",f"{y['logical_error_rate']:.3f}",f"{z['mean_data_error']:.6f}",f"{w['mean_data_error']:.6f}"]
        rows.append([Paragraph(v,styles['cell']) for v in vals])
    t=Table(rows,colWidths=[63,100,100,114,114]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#F0F4F7'),white]),('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(t);story.append(Spacer(1,10))
    p('All table entries are probabilities: for example, 0.115 = 11.5%. H2-1E logical failures were 3, 4, 16, 46, 115 out of 1,000; H2-2E failures were 2, 5, 17, 48, 140 out of 1,000.','small')
    p('Decoder and uncertainty','h')
    p('The same fixed minimum-weight perfect matching decoder was used for both sweeps: assumed data-fault probability 0.002 per round and readout probability 0.001. Varying the assumed data probability to 0.02 or 0.1 produced identical counts. These specify decoder weights, not injected faults. All 10,000 packed shots were cross-checked against returned joint counts.')
    p('At u = 1, 95% Wilson intervals for P<sub>L</sub> are 9.67%-13.63% (H2-1E) and 11.99%-16.29% (H2-2E). One job per setting does not measure run-to-run variability.','small')
    story.append(PageBreak())
    p('Physical scaling and conclusions','title')
    p('Raw-argument fits | Noise interpretation | Future time normalization','sub')
    p('Fitted physical error probabilities','h')
    box([('H2-1E: p<sub>data</sub>(u) ≈ 0.002778 + 0.010631 u + 0.087958 u<super>2</super>','formula'),('H2-2E: p<sub>data</sub>(u) ≈ 0.001333 + 0.015245 u + 0.084495 u<super>2</super>','formula')])
    p('<b>u is the raw sleep argument, with no verified physical-time unit.</b> Outputs are probabilities, not percentages. Each fit is an unweighted least-squares interpolation over 0 ≤ u ≤ 1, with its intercept fixed to the measured zero-control background. The coefficients are not calibrated physical rates, exact backend parameters, or a basis for extrapolation.')
    p('What the comparison shows','h')
    p('The mean physical error probabilities are very similar at the larger waits. At u = 1 they are 0.101444 (H2-1E) and 0.101333 (H2-2E). Both fits show substantial positive curvature, compatible with a quadratic memory-noise contribution.')
    p('The dominant syndrome increase occurs across the inserted wait. Mean inter-round detector probabilities rise from 0.0050 to 0.2395 on H2-1E and from 0.0045 to 0.23975 on H2-2E. First-round means remain below 0.0051 for both sweeps.')
    p('H2-1E has P<sub>L</sub> = 0.115 versus 0.140 for H2-2E at u = 1, but the two-sided Fisher comparison gives p = 0.107. None of the five corresponding logical comparisons resolves an emulator difference at the conventional 5% level. This does not prove equivalence or that H2-1E is superior. The u = 0.1 logical increase over zero is inconclusive in each sweep.')
    p('Overall noise model and inference limits','h')
    p('Both jobs requested noisy stabilizer simulation, disabled optimization, and enabled idle and transport dephasing. Other default gate, preparation, readout and crosstalk faults remained enabled. Quantinuum documents stochastic Z memory faults with linear-duration and short-time-quadratic contributions; the published dephasing parameters match across these emulators [1, 2].')
    p('The observations support sleep-dependent memory degradation, but cannot uniquely isolate idle dephasing, verify parallel waits, establish physical seconds per argument, or determine T<sub>2</sub>. Quadratic noise acting over an existing duration d<sub>0</sub> yields an increment proportional to 2d<sub>0</sub>u + u², so an apparent linear fit term need not equal the linear idle-noise rate.')
    p('Probability now; time-normalized metric later','h')
    p('For many rounds separated by a physical wait Δt, measure P<sub>L</sub>(R, Δt) and total duration T before forming the planned effective metric P<sub>L</sub>/T. Include extraction time under a stated timing convention. The present two-round probabilities cannot simply be extrapolated to many rounds or interpreted as constant-hazard parameters.')
    p('[1] <link href="https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html" color="#156C9E">Quantinuum Emulator Noise Model</link>. [2] <link href="https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html" color="#156C9E">H2 Emulator Defaults</link>.<br/>Evidence: saved five-point runs a2588f7078f6e696 (H2-1E), 67d11d0348065703 (H2-2E); decoded and noise-characterization JSON records in SG_final_round/results/.','small')
    box([('Conclusion','h'),('Both emulators show closely matching physical-error growth and a pronounced increase in decoded logical error probability as raw sleep argument u increases. The results are compatible with substantial quadratic memory noise. Calibrated idle rates require verified timing and matched noise-channel controls; time-normalized logical-error metrics require a measured total duration.','body')],'#EAF3EF')
    def footer(c,doc):
        c.setFont('Arial',8);c.setFillColor(GREY);c.drawString(52,24,'H2-1E + H2-2E | d = 3 | Probabilities per two-round experiment');c.drawRightString(A4[0]-52,24,f'{doc.page} / 2')
    SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=52,rightMargin=52,topMargin=40,bottomMargin=48,title='Combined H2-1E and H2-2E distance-3 sleep sweep').build(story,onFirstPage=footer,onLaterPages=footer)
    assert len(PdfReader(str(OUT)).pages)==2
    print(OUT)
    return OUT


def sleep_explanation_pdf():
    """Teammate-facing explanation of the explicit QIR sleep probe, plus preview PNGs.

    The committed results/sleep/sleep_parameter_explanation.pdf stays where it is (moved data);
    a rerun writes figures/sleep_parameter_explanation.pdf and figures/pdf_preview/.
    """
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from pypdf import PdfReader
    import pypdfium2 as pdfium
    OUT=paths.figure('sleep_parameter_explanation.pdf')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleCustom',fontName='Helvetica-Bold',fontSize=21,leading=25,textColor=HexColor('#17334D'),spaceAfter=9))
    styles.add(ParagraphStyle(name='Sub',fontName='Helvetica',fontSize=9,leading=12,textColor=HexColor('#526575'),spaceAfter=17))
    styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=9))
    styles.add(ParagraphStyle(name='HeadCustom',fontName='Helvetica-Bold',fontSize=11,leading=14,textColor=HexColor('#17334D'),spaceBefore=9,spaceAfter=6))
    styles.add(ParagraphStyle(name='CodeCustom',fontName='Courier',fontSize=8.3,leading=11,backColor=HexColor('#F0F4F7'),borderPadding=10,spaceBefore=7,spaceAfter=15))
    story=[]
    def p(text,style='BodyCustom'): story.append(Paragraph(text,styles[style]))
    p('How we added explicit sleep','TitleCustom')
    p('Single-qubit memory experiment | Aqora / Quantinuum H2-1E | Team explanation','Sub')
    p('<b>The sleep instruction was written directly into QIR, not Guppy.</b> A local Python script generates the QIR text. LLVM/Clang assembles it into .bc bitcode, which is submitted to H2-1E through Aqora.')
    p('1. The one-qubit memory circuit','HeadCustom')
    p('<b>Prepare |0&gt; &nbsp; → &nbsp; Ry(π/2) &nbsp; → &nbsp; sleep(t) &nbsp; → &nbsp; Ry(-π/2) &nbsp; → &nbsp; measure Z</b>')
    p('The first rotation prepares |+&gt;. The second converts an X-basis measurement into a Z-basis measurement, making the probe sensitive to dephasing during the wait. Without errors, the recorded bit is 0; a recorded 1 is an X-memory error. The rotations are implemented using native phased-X QIR calls.')
    p('2. The exact sleep instruction','HeadCustom')
    story.append(Preformatted('declare void @__quantum__qis__sleep__body(%Qubit*, double)\n\n; Example: raw sleep argument 0.5 on virtual qubit 0\ncall void @__quantum__qis__sleep__body(\n    %Qubit* null,\n    double 5.00000000000000000e-01\n)',styles['CodeCustom']))
    p('Under the static QIR convention, <font face="Courier">%Qubit* null</font> identifies <b>virtual qubit 0</b>; it does not mean “no qubit.” The backend assigns the physical ion. The <font face="Courier">double</font> is the raw sleep argument. The declaration specifies the function signature; the call applies it between the two rotations.')
    p('3. How the sweep was executed','HeadCustom')
    p('Five otherwise identical programs used explicit sleep arguments <b>0, 0.1, 0.5, 0.75 and 1</b>, with 1,000 shots each. The zero-duration control also contains a sleep call. Each program retained both rotations and its requested sleep argument after assembly and bitcode round-trip, and all passed the H2-1SC syntax checker.')
    p('The jobs requested noisy stabilizer simulation, idle and transport dephasing enabled, and optimization disabled (<font face="Courier">no_opt=true</font>) to preserve the sequence. <b>No artificial errors were injected.</b> We measured the emulator output after supplying the explicit sleep instruction.')
    p('4. What this establishes','HeadCustom')
    p('All five H2-1E jobs completed. The measured error counts were <b>0, 1, 21, 55 and 92 out of 1,000</b>, respectively. This shows a clear dependence on the sleep argument in this probe. It does <b>not</b> independently establish the argument’s physical units, a calibrated scaling law, or the backend’s internal noise implementation.')
    p('Implementation and saved evidence','HeadCustom')
    p('<font face="Courier" size="8.5">SG_final_round/src/single_qubit_pilot.py</font> - reusable QIR template.<br/><font face="Courier" size="8.5">SG_final_round/src/single_qubit_sweep.py</font> - build, submit, fetch and analyze.<br/><font face="Courier" size="8.5">SG_final_round/results/single_qubit_sweep_1000.json</font> - counts and job IDs.')
    def footer(c,doc):
        c.setStrokeColor(HexColor('#D5DEE5')); c.line(44,38,A4[0]-44,38)
        c.setFont('Helvetica',8); c.setFillColor(HexColor('#526575'))
        c.drawString(44,25,'SG final round | Explicit QIR sleep probe')
        c.drawRightString(A4[0]-44,25,str(doc.page))
    SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=38,bottomMargin=50,title='Explicit sleep in the H2-1E single-qubit memory probe',author='SG final-round experiment team').build(story,onFirstPage=footer,onLaterPages=footer)
    reader=PdfReader(str(OUT))
    text='\n'.join(page.extract_text() for page in reader.pages)
    assert '__quantum__qis__sleep__body' in text and '92' in text
    preview=paths.figure('pdf_preview')
    preview.mkdir(exist_ok=True)
    doc=pdfium.PdfDocument(str(OUT))
    for i,page in enumerate(doc): page.render(scale=1.5).to_pil().save(preview/f'sleep_explanation_{i+1}.png')
    print(OUT)
    print('Pages:',len(reader.pages))
    return OUT
