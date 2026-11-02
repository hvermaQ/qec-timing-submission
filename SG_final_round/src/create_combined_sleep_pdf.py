"""Generate the two-emulator teammate summary from saved analyses."""
from pathlib import Path
import json
# Reuse the established fonts and layout helpers without running its authoring section.
base=Path(__file__).with_name('create_h2_2e_summary_pdf.py').read_text()
exec(base.split("p('Sleep-dependent logical errors'")[0])
OUT=RESULTS/'h2_1e_h2_2e_d3_sleep_summary.pdf'
a=json.loads((RESULTS/'d3_sleep_five_point_h2_1e_1000.json').read_text())
b=json.loads((RESULTS/'d3_sleep_five_point_h2_2e_1000.json').read_text())
ca=json.loads((RESULTS/'d3_sleep_five_point_h2_1e_noise_characterization.json').read_text())
cb=json.loads((RESULTS/'d3_sleep_five_point_h2_2e_noise_characterization.json').read_text())
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
