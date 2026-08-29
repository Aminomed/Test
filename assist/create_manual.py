"""Erstellt die Bedienungsanleitung als Word-Dokument (.docx)."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

def set_cell_shading(cell, color_hex):
    """Setzt die Hintergrundfarbe einer Tabellenzelle."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def create_manual():
    doc = Document()

    # ── Seitenränder ─────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # ── Standard-Schriftart ──────────────────────────────────────────
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Segoe UI'
    font.size = Pt(10.5)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

    # ── Überschriften-Styles ─────────────────────────────────────────
    for level, (size, color) in enumerate([
        (Pt(26), RGBColor(0x0D, 0x47, 0xA1)),  # Heading 1
        (Pt(16), RGBColor(0x1A, 0x23, 0x7E)),  # Heading 2
        (Pt(13), RGBColor(0x28, 0x35, 0x93)),  # Heading 3
    ], start=1):
        h_style = doc.styles[f'Heading {level}']
        h_style.font.size = size
        h_style.font.color.rgb = color
        h_style.font.name = 'Segoe UI'
        h_style.font.bold = True
        h_style.paragraph_format.space_before = Pt(18 if level == 1 else 14)
        h_style.paragraph_format.space_after = Pt(8)

    # ═══════════════════════════════════════════════════════════════════
    #  TITELSEITE
    # ═══════════════════════════════════════════════════════════════════

    # Leerzeilen für vertikale Zentrierung
    for _ in range(6):
        doc.add_paragraph('')

    # Titel
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('D-Flipflop Frequenzteiler')
    run.font.size = Pt(32)
    run.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)
    run.font.bold = True
    run.font.name = 'Segoe UI'

    # Untertitel
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run('Visuelles Design-Tool')
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(0x42, 0x42, 0x42)
    run.font.name = 'Segoe UI'

    doc.add_paragraph('')

    # Trennlinie
    line = doc.add_paragraph()
    line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = line.add_run('━' * 40)
    run.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)
    run.font.size = Pt(14)

    doc.add_paragraph('')

    # Beschreibung
    desc = doc.add_paragraph()
    desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = desc.add_run('Bedienungsanleitung')
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(0x61, 0x61, 0x61)
    run.font.name = 'Segoe UI'

    doc.add_paragraph('')

    ver = doc.add_paragraph()
    ver.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = ver.add_run('Version 1.0  ·  Juli 2026')
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x90, 0x90, 0x90)
    run.font.name = 'Segoe UI'

    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════════
    #  INHALTSVERZEICHNIS
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('Inhaltsverzeichnis', level=1)

    toc_items = [
        ('1.', 'Überblick'),
        ('2.', 'Systemvoraussetzungen'),
        ('3.', 'Installation und Start'),
        ('4.', 'Benutzeroberfläche'),
        ('5.', 'Bedienung Schritt für Schritt'),
        ('6.', 'Die Ansichten im Detail'),
        ('  6.1', 'Schaltplan'),
        ('  6.2', 'Timing-Diagramm'),
        ('  6.3', 'Boolesche Gleichungen'),
        ('  6.4', 'Wahrheitstabelle'),
        ('7.', 'Beispiele'),
        ('8.', 'Theoretischer Hintergrund'),
        ('9.', 'Fehlerbehebung'),
        ('10.', 'EXE selbst erstellen'),
    ]

    for num, text in toc_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.space_before = Pt(0)
        indent = '    ' if num.startswith(' ') else ''
        run = p.add_run(f'{indent}{num.strip()}  {text}')
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════════
    #  1. ÜBERBLICK
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('1. Überblick', level=1)

    doc.add_paragraph(
        'Der D-Flipflop Frequenzteiler ist ein visuelles Design-Tool, mit dem '
        'Sie beliebige Frequenzteilungen mithilfe von D-Flipflops darstellen '
        'können. Das Programm berechnet die vollständige digitale Schaltung '
        'für einen synchronen Zähler und zeigt:'
    )

    features = [
        ('Schaltplan', 'Visuelle Darstellung der D-Flipflops mit Next-State-Logik, '
         'Ausgangslogik, Taktverteilung und Rückkopplung'),
        ('Timing-Diagramm', 'Digitale Signalverläufe über mehrere Perioden '
         '(CLK, alle Q-Ausgänge, fout)'),
        ('Boolesche Gleichungen', 'Minimierte Gleichungen (Quine-McCluskey-Verfahren) '
         'für alle D-Eingänge und den Ausgang'),
        ('Wahrheitstabelle', 'Vollständige Zustandstabelle mit farbiger '
         'Hervorhebung und CSV-Export'),
    ]

    for title_text, desc_text in features:
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(f'{title_text}: ')
        run.bold = True
        p.add_run(desc_text)

    # ═══════════════════════════════════════════════════════════════════
    #  2. SYSTEMVORAUSSETZUNGEN
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('2. Systemvoraussetzungen', level=1)

    doc.add_heading('Für die EXE-Version:', level=3)
    for item in [
        'Windows 10 oder höher (64-Bit)',
        'Keine zusätzliche Software erforderlich',
        'Ca. 12 MB Festplattenspeicher',
    ]:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_heading('Für die Python-Version:', level=3)
    for item in [
        'Python 3.10 oder höher',
        'tkinter (in Standard-Python enthalten)',
        'Keine zusätzlichen Pakete erforderlich',
    ]:
        doc.add_paragraph(item, style='List Bullet')

    # ═══════════════════════════════════════════════════════════════════
    #  3. INSTALLATION UND START
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('3. Installation und Start', level=1)

    doc.add_heading('EXE-Version (empfohlen)', level=2)
    doc.add_paragraph(
        'Die EXE-Datei benötigt keine Installation. Doppelklicken Sie einfach auf '
        'DFF-Frequenzteiler.exe um das Programm zu starten.'
    )

    # Hinweis-Box
    note = doc.add_paragraph()
    note.paragraph_format.left_indent = Cm(0.5)
    run = note.add_run('ℹ Hinweis: ')
    run.bold = True
    run.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)
    run2 = note.add_run(
        'Beim ersten Start kann Windows SmartScreen eine Warnung anzeigen, '
        'da die EXE nicht digital signiert ist. Klicken Sie auf '
        '"Weitere Informationen" → "Trotzdem ausführen".'
    )
    run2.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_heading('Python-Version', level=2)
    doc.add_paragraph('Öffnen Sie ein Terminal im Projektordner und führen Sie aus:')

    code = doc.add_paragraph()
    code.paragraph_format.left_indent = Cm(1)
    run = code.add_run('py main.py')
    run.font.name = 'Consolas'
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    # ═══════════════════════════════════════════════════════════════════
    #  4. BENUTZEROBERFLÄCHE
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('4. Benutzeroberfläche', level=1)

    doc.add_paragraph(
        'Die Benutzeroberfläche ist in mehrere Bereiche unterteilt:'
    )

    # Tabelle für UI-Bereiche
    table = doc.add_table(rows=6, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    ui_areas = [
        ('Bereich', 'Beschreibung'),
        ('Header', 'Titel und Kurzbeschreibung des Programms'),
        ('Eingabebereich', 'Felder für Teilungsfaktor N und Duty-Cycle-Zähler k, '
         'sowie die Buttons "Generieren" und "Wahrheitstabelle"'),
        ('Tab-Ansicht', 'Drei Tabs: Schaltplan, Timing-Diagramm, Gleichungen'),
        ('Statusleiste', 'Zeigt Informationen zum aktuellen Frequenzteiler '
         'oder Fehlermeldungen an'),
    ]

    # Header-Zeile
    for j, text in enumerate(ui_areas[0]):
        cell = table.rows[0].cells[j]
        cell.text = text
        cell.paragraphs[0].runs[0].bold = True
        set_cell_shading(cell, '0D47A1')
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for i, (area, desc) in enumerate(ui_areas[1:], start=1):
        table.rows[i].cells[0].text = area
        table.rows[i].cells[0].paragraphs[0].runs[0].bold = True
        table.rows[i].cells[1].text = desc
        if i % 2 == 0:
            set_cell_shading(table.rows[i].cells[0], 'E8EAF6')
            set_cell_shading(table.rows[i].cells[1], 'E8EAF6')

    # Letzte leere Zeile entfernen
    table._tbl.remove(table.rows[5]._tr)

    doc.add_paragraph('')

    # ═══════════════════════════════════════════════════════════════════
    #  5. BEDIENUNG SCHRITT FÜR SCHRITT
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('5. Bedienung Schritt für Schritt', level=1)

    steps = [
        ('Teilungsfaktor N eingeben',
         'Geben Sie den gewünschten Teilungsfaktor in das Feld "Teilungsfaktor N" ein. '
         'Dies bestimmt das Verhältnis fout = fin / N.\n'
         'Beispiel: N = 7 bedeutet, die Ausgangsfrequenz ist 1/7 der Eingangsfrequenz.'),

        ('Duty-Cycle-Zähler k eingeben',
         'Geben Sie die Anzahl der Takte ein, in denen der Ausgang HIGH sein soll. '
         'Der Duty-Cycle beträgt dann k/N.\n'
         'Beispiel: k = 4 bei N = 7 ergibt einen Duty-Cycle von 4/7 ≈ 57,1%.'),

        ('Auf "Generieren" klicken',
         'Das Programm berechnet die Schaltung und zeigt sofort den Schaltplan an. '
         'Die Statusleiste zeigt eine Zusammenfassung: Anzahl Flipflops, '
         'genutzte/mögliche Zustände.'),

        ('Zwischen den Tabs wechseln',
         'Klicken Sie auf die Tabs "Schaltplan", "Timing-Diagramm" oder "Gleichungen", '
         'um die verschiedenen Darstellungen zu sehen.'),

        ('Wahrheitstabelle öffnen (optional)',
         'Klicken Sie auf den Button "Wahrheitstabelle", um ein separates Fenster '
         'mit der vollständigen Zustandstabelle zu öffnen. '
         'Von dort können Sie die Tabelle auch als CSV-Datei exportieren.'),
    ]

    for i, (title_text, desc_text) in enumerate(steps, start=1):
        p = doc.add_paragraph()
        run = p.add_run(f'Schritt {i}: {title_text}')
        run.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x1A, 0x23, 0x7E)
        doc.add_paragraph(desc_text)

    # ═══════════════════════════════════════════════════════════════════
    #  6. DIE ANSICHTEN IM DETAIL
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('6. Die Ansichten im Detail', level=1)

    # 6.1 Schaltplan
    doc.add_heading('6.1 Schaltplan', level=2)
    doc.add_paragraph(
        'Der Schaltplan zeigt die vollständige digitale Schaltung des Frequenzteilers. '
        'Folgende Elemente werden dargestellt:'
    )

    circuit_elements = [
        ('D-Flipflops (FF₀, FF₁, ...)',
         'Jedes Flipflop wird als Kasten mit den Pins D (Dateneingang), '
         'Q (Ausgang), Q̄ (invertierter Ausgang) und CLK (Takteingang) dargestellt. '
         'Die Anzahl der Flipflops beträgt ⌈log₂(N)⌉.'),
        ('Next-State-Logik',
         'Eine Box oberhalb der Flipflops zeigt die kombinatorische Logik, '
         'die den nächsten Zustand berechnet. Die minimierten booleschen '
         'Gleichungen für jeden D-Eingang sind darin aufgeführt.'),
        ('Ausgangslogik',
         'Eine Box rechts neben den Flipflops zeigt die Gleichung für den '
         'Ausgang fout.'),
        ('Taktverteilung (CLK)',
         'Eine blaue Leitung am unteren Rand verbindet den Eingang fin '
         'mit allen CLK-Pins der Flipflops.'),
        ('Rückkopplung',
         'Gelbe/goldene Leitungen zeigen, wie die Q-Ausgänge zurück zur '
         'Next-State-Logik geführt werden.'),
    ]

    for title_text, desc_text in circuit_elements:
        p = doc.add_paragraph(style='List Bullet')
        run = p.add_run(f'{title_text}: ')
        run.bold = True
        p.add_run(desc_text)

    doc.add_paragraph(
        'Der Schaltplan ist scrollbar – bei vielen Flipflops können Sie '
        'horizontal und vertikal scrollen.'
    )

    # Farbtabelle
    doc.add_heading('Farbkodierung im Schaltplan:', level=3)
    color_table = doc.add_table(rows=6, cols=2)
    color_table.style = 'Table Grid'
    colors = [
        ('Farbe', 'Bedeutung'),
        ('Blau', 'Taktsignal (CLK / fin)'),
        ('Grün', 'Datenleitungen (D-Eingänge)'),
        ('Orange', 'Ausgangssignal (fout, Q-Ausgänge)'),
        ('Gold/Gelb', 'Rückkopplungsleitungen'),
        ('Lila', 'Logik-Blöcke'),
    ]
    for i, (c, m) in enumerate(colors):
        color_table.rows[i].cells[0].text = c
        color_table.rows[i].cells[1].text = m
        if i == 0:
            for j in range(2):
                color_table.rows[0].cells[j].paragraphs[0].runs[0].bold = True
                set_cell_shading(color_table.rows[0].cells[j], '0D47A1')
                color_table.rows[0].cells[j].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    doc.add_paragraph('')

    # 6.2 Timing-Diagramm
    doc.add_heading('6.2 Timing-Diagramm', level=2)
    doc.add_paragraph(
        'Das Timing-Diagramm zeigt den zeitlichen Verlauf aller Signale '
        'über zwei vollständige Perioden:'
    )
    for item in [
        'CLK (fin): Das Eingangstaktsignal',
        'Q₀, Q₁, ...: Die Ausgänge der einzelnen Flipflops',
        'fout: Das Ausgangssignal nach der Frequenzteilung',
    ]:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph(
        'Oberhalb der Signale sind die Zustandsnummern angezeigt, '
        'sodass Sie nachverfolgen können, in welchem Zustand sich der '
        'Zähler zu jedem Zeitpunkt befindet. Am unteren Rand markieren '
        'Klammern die einzelnen Perioden.'
    )

    # 6.3 Gleichungen
    doc.add_heading('6.3 Boolesche Gleichungen', level=2)
    doc.add_paragraph(
        'Der Gleichungen-Tab zeigt alle minimierten booleschen Gleichungen:'
    )

    eq_table = doc.add_table(rows=4, cols=2)
    eq_table.style = 'Table Grid'
    eq_items = [
        ('Element', 'Beschreibung'),
        ('D₀, D₁, ... (Next-State)', 'Gleichungen für die D-Eingänge '
         'jedes Flipflops als Funktion der aktuellen Zustände Q₀, Q₁, ...'),
        ('fout (Ausgang)', 'Gleichung für das Ausgangssignal'),
        ('Legende', 'Erklärung der Operatoren: · = UND, + = ODER, Q̄ = NICHT'),
    ]
    for i, (e, d) in enumerate(eq_items):
        eq_table.rows[i].cells[0].text = e
        eq_table.rows[i].cells[1].text = d
        if i == 0:
            for j in range(2):
                eq_table.rows[0].cells[j].paragraphs[0].runs[0].bold = True
                set_cell_shading(eq_table.rows[0].cells[j], '0D47A1')
                eq_table.rows[0].cells[j].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    doc.add_paragraph('')
    doc.add_paragraph(
        'Die Gleichungen werden mit dem Quine-McCluskey-Algorithmus minimiert. '
        'Ungenutzte Zustände werden als Don\'t-Care-Terme behandelt, '
        'was zu einfacheren Gleichungen führt.'
    )

    # 6.4 Wahrheitstabelle
    doc.add_heading('6.4 Wahrheitstabelle', level=2)
    doc.add_paragraph(
        'Die Wahrheitstabelle öffnet sich als separates Fenster und zeigt '
        'für jeden möglichen Zustand:'
    )
    for item in [
        'Zustandsnummer (dezimal)',
        'Aktuelle Flipflop-Ausgänge (Q₂, Q₁, Q₀, ...)',
        'Nächste D-Eingangswerte (D₂, D₁, D₀, ...)',
        'Ausgangswert fout (1 oder 0)',
    ]:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_heading('Farbkodierung:', level=3)
    for item in [
        'Grün: Ausgang = 1 (HIGH)',
        'Rot: Ausgang = 0 (LOW)',
        'Grau: Ungenutzter Zustand (wird zu Zustand 0 zurückgesetzt)',
    ]:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_heading('CSV-Export:', level=3)
    doc.add_paragraph(
        'Über den Button "CSV Exportieren" können Sie die Wahrheitstabelle '
        'als CSV-Datei speichern, z.B. für die Weiterverarbeitung in Excel. '
        'Das Trennzeichen ist das Semikolon (;).'
    )

    # ═══════════════════════════════════════════════════════════════════
    #  7. BEISPIELE
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('7. Beispiele', level=1)

    examples = [
        ('Teiler durch 2 (Halbierung)', 'N = 2, k = 1',
         '1 Flipflop, Duty-Cycle 50%. Das einfachste Beispiel: '
         'Ein einzelnes D-Flipflop, dessen invertierter Ausgang Q̄ auf den '
         'D-Eingang rückgekoppelt wird.'),

        ('Teiler durch 3', 'N = 3, k = 1',
         '2 Flipflops, Duty-Cycle 33,3%. Zeigt einen Zähler mit drei '
         'Zuständen (0, 1, 2) und einem ungenutzten Zustand (3).'),

        ('Teiler durch 7 mit 4/7 Duty-Cycle', 'N = 7, k = 4',
         '3 Flipflops, Duty-Cycle 57,1%. Ein typisches Beispiel für eine '
         'nicht-triviale Teilung mit asymmetrischem Duty-Cycle. '
         'Der Ausgang ist für 4 von 7 Takten HIGH.'),

        ('Teiler durch 10 (Dekadenzähler)', 'N = 10, k = 5',
         '4 Flipflops, Duty-Cycle 50%. Entspricht einem BCD-Zähler '
         '(0–9) mit 6 ungenutzten Zuständen (10–15).'),

        ('Teiler durch 12', 'N = 12, k = 6',
         '4 Flipflops, Duty-Cycle 50%. Ein Zähler modulo 12 mit '
         '4 ungenutzten Zuständen.'),
    ]

    for title_text, params, desc_text in examples:
        p = doc.add_paragraph()
        run = p.add_run(f'{title_text}')
        run.bold = True
        run.font.color.rgb = RGBColor(0x1A, 0x23, 0x7E)

        p2 = doc.add_paragraph()
        p2.paragraph_format.left_indent = Cm(0.5)
        run = p2.add_run(f'Parameter: ')
        run.bold = True
        run = p2.add_run(params)
        run.font.name = 'Consolas'
        run.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

        p3 = doc.add_paragraph(desc_text)
        p3.paragraph_format.left_indent = Cm(0.5)
        p3.paragraph_format.space_after = Pt(12)

    # ═══════════════════════════════════════════════════════════════════
    #  8. THEORETISCHER HINTERGRUND
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('8. Theoretischer Hintergrund', level=1)

    doc.add_heading('Synchroner Zähler mit D-Flipflops', level=2)
    doc.add_paragraph(
        'Ein Frequenzteiler durch N wird als synchroner Zähler implementiert. '
        'Der Zähler zählt von 0 bis N−1 und beginnt dann wieder bei 0. '
        'Alle Flipflops werden vom gleichen Taktsignal (fin) getrieben.'
    )

    doc.add_heading('Anzahl der Flipflops', level=2)
    doc.add_paragraph(
        'Die Anzahl der benötigten D-Flipflops berechnet sich als:\n\n'
        '    n = ⌈log₂(N)⌉\n\n'
        'Dabei ist ⌈ ⌉ die Aufrundungsfunktion (Ceiling). '
        'Mit n Flipflops können 2ⁿ Zustände dargestellt werden. '
        'Ist N keine Zweierpotenz, bleiben einige Zustände ungenutzt.'
    )

    doc.add_heading('Duty-Cycle', level=2)
    doc.add_paragraph(
        'Der Duty-Cycle bestimmt, für wie viele der N Zustände der Ausgang '
        'HIGH ist. Bei einem Duty-Cycle von k/N ist der Ausgang für die '
        'ersten k Zustände (0 bis k−1) HIGH und für die restlichen '
        'N−k Zustände (k bis N−1) LOW.'
    )

    doc.add_heading('Quine-McCluskey-Minimierung', level=2)
    doc.add_paragraph(
        'Die booleschen Gleichungen werden mit dem Quine-McCluskey-Algorithmus '
        'minimiert. Dieser Algorithmus:\n\n'
        '1. Gruppiert alle Minterme nach Anzahl der Einsen\n'
        '2. Kombiniert benachbarte Terme (die sich in genau einem Bit unterscheiden)\n'
        '3. Wiederholt dies, bis keine weiteren Kombinationen möglich sind\n'
        '4. Findet die minimale Überdeckung aller Minterme (essentiell + greedy)\n\n'
        'Ungenutzte Zustände werden als Don\'t-Care-Terme behandelt, '
        'was die Minimierung verbessert.'
    )

    doc.add_heading('Ungenutzte Zustände', level=2)
    doc.add_paragraph(
        'Wenn N keine Zweierpotenz ist, gibt es ungenutzte Zustände. '
        'Die Schaltung ist so ausgelegt, dass sie aus jedem ungenutzten '
        'Zustand automatisch in den Zustand 0 zurückkehrt. '
        'Dies sorgt für Selbstkorrektur bei Störungen.'
    )

    # ═══════════════════════════════════════════════════════════════════
    #  9. FEHLERBEHEBUNG
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('9. Fehlerbehebung', level=1)

    problems = [
        ('Fehlermeldung "Teilungsfaktor N muss ≥ 2 sein"',
         'N muss mindestens 2 sein. Ein Teiler durch 1 ergibt keinen Sinn.'),
        ('Fehlermeldung "Duty-Cycle-Zähler k muss zwischen 1 und N−1 liegen"',
         'k muss mindestens 1 und höchstens N−1 sein. Bei k=0 wäre der '
         'Ausgang immer LOW, bei k=N immer HIGH.'),
        ('Schaltplan ist abgeschnitten',
         'Verwenden Sie die Scrollbalken am rechten und unteren Rand '
         'des Schaltplans, um den gesamten Plan zu sehen.'),
        ('EXE startet nicht',
         'Stellen Sie sicher, dass Sie Windows 10/11 64-Bit verwenden. '
         'Falls Windows SmartScreen eine Warnung zeigt, klicken Sie auf '
         '"Weitere Informationen" → "Trotzdem ausführen".'),
        ('Darstellungsprobleme (unscharfer Text)',
         'Das Programm unterstützt DPI-Skalierung. Falls Probleme auftreten, '
         'rechtsklicken Sie auf die EXE → Eigenschaften → Kompatibilität → '
         '"Hohe DPI-Einstellungen ändern".'),
    ]

    for problem, solution in problems:
        p = doc.add_paragraph()
        run = p.add_run(f'Problem: {problem}')
        run.bold = True
        run.font.color.rgb = RGBColor(0xC6, 0x28, 0x28)
        p2 = doc.add_paragraph()
        run2 = p2.add_run(f'Lösung: ')
        run2.bold = True
        p2.add_run(solution)
        p2.paragraph_format.space_after = Pt(10)

    # ═══════════════════════════════════════════════════════════════════
    #  10. EXE SELBST ERSTELLEN
    # ═══════════════════════════════════════════════════════════════════

    doc.add_heading('10. EXE selbst erstellen', level=1)

    doc.add_paragraph(
        'Falls Sie Änderungen am Quellcode vornehmen und eine neue EXE '
        'erstellen möchten:'
    )

    doc.add_heading('Voraussetzungen:', level=3)
    for item in ['Python 3.10+', 'PyInstaller (py -m pip install pyinstaller)']:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_heading('Build-Befehl:', level=3)
    code = doc.add_paragraph()
    code.paragraph_format.left_indent = Cm(1)
    run = code.add_run('py -m PyInstaller --onefile --windowed --name "DFF-Frequenzteiler" main.py')
    run.font.name = 'Consolas'
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x0D, 0x47, 0xA1)

    doc.add_paragraph(
        'Alternativ können Sie die mitgelieferte Datei build.bat per '
        'Doppelklick ausführen. Die fertige EXE wird im Ordner dist\\ abgelegt.'
    )

    doc.add_heading('Projektstruktur:', level=3)
    files_table = doc.add_table(rows=7, cols=2)
    files_table.style = 'Table Grid'
    files = [
        ('Datei', 'Beschreibung'),
        ('main.py', 'Hauptanwendung und Einstiegspunkt'),
        ('circuit_logic.py', 'Kernlogik: Zustandsmaschine und Minimierung'),
        ('circuit_drawer.py', 'Schaltplan-Zeichnung auf Canvas'),
        ('truth_table_view.py', 'Wahrheitstabellen-Popup'),
        ('timing_diagram.py', 'Timing-Diagramm-Zeichnung'),
        ('theme.py', 'Farbschema und Schriftarten'),
    ]
    for i, (f, d) in enumerate(files):
        files_table.rows[i].cells[0].text = f
        files_table.rows[i].cells[1].text = d
        if i == 0:
            for j in range(2):
                files_table.rows[0].cells[j].paragraphs[0].runs[0].bold = True
                set_cell_shading(files_table.rows[0].cells[j], '0D47A1')
                files_table.rows[0].cells[j].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        else:
            files_table.rows[i].cells[0].paragraphs[0].runs[0].font.name = 'Consolas'

    # ═══════════════════════════════════════════════════════════════════
    #  SPEICHERN
    # ═══════════════════════════════════════════════════════════════════

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'Bedienungsanleitung_DFF-Frequenzteiler.docx')
    doc.save(output_path)
    print(f'Bedienungsanleitung erstellt: {output_path}')


if __name__ == '__main__':
    create_manual()
