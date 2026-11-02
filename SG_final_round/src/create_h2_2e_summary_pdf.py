"""Create the shareable two-page H2-2E experiment summary from saved results."""
import json
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO/'SG_final_round/results'
OUT = REPO/'output/pdf/h2_2e_d3_sleep_summary.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
data = json.loads((RESULTS/'d3_sleep_five_point_h2_2e_1000.json').read_text())
noise = json.loads((RESULTS/'d3_sleep_five_point_h2_2e_noise_characterization.json').read_text())
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
