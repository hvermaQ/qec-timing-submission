"""Generate the teammate-facing explanation of the explicit QIR sleep probe."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sleep_parameter_explanation.pdf'
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
preview=ROOT/'results/pdf_preview'
preview.mkdir(exist_ok=True)
doc=pdfium.PdfDocument(str(OUT))
for i,page in enumerate(doc): page.render(scale=1.5).to_pil().save(preview/f'sleep_explanation_{i+1}.png')
print(OUT)
print('Pages:',len(reader.pages))
