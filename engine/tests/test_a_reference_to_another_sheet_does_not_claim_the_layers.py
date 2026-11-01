"""A reference to another sheet names no system, and cannot make the sheet's own pipe layers another system's.

A section mark writes the sheet the section is drawn on, "V50-02-271", and that has a label's shape, and its V50 is the very prefix every layer of the set
carries: `v50_p270|V-56512`. Counted among the systems the sheet names, it made each pipe layer "V50's layer",
every pipe label on it a conflict with V50, and a whole sheet measured nothing. Only what names a pipe - what
the sheet's own list lets through - can say that a layer belongs to another pipe.
"""
import pymupdf

from vvs_engine import rules
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import analyze_page

PEN = 0.72
LEAD = 0.24
LEGEND = [("KBXX-3", "KOLDBARARE, KOPPAR"), ("KBXX-6", "KOLDBARARE, ROSTFRITT STAL"),
          ("KVXX-3", "KALLVATTENLEDNING, KOPPAR"), ("VVXX-3", "VARMVATTENLEDNING, KOPPAR"),
          ("VSXX-22", "VARMEBARARE, SEKUNDAR STALROR"), ("S54", "SPILLVATTENLEDNING, PP-ROR"),
          ("BV", "BACKVENTIL"), ("XX", "AVSER SYSTEMBETECKNING")]


def _label(page, x, y, text, to):
    page.insert_text((x, y), text, fontsize=9, fontname="helv")
    page.draw_line((x, y + 3), (x + 62, y + 3), width=LEAD, color=(0, 0, 0))
    page.draw_line((x + 62, y + 3), to, width=LEAD, color=(0, 0, 0))
    page.draw_line((to[0] - 2, to[1] + 2), (to[0] + 2, to[1] - 2), width=LEAD, color=(0, 0, 0))


def _sheet(path):
    doc = pymupdf.open()
    page = doc.new_page(width=1191, height=842)
    vs = doc.add_ocg("v50_p270|V-56512")
    kb = doc.add_ocg("v50_p270|V-55512")
    page.draw_line((100, 300), (700, 300), width=PEN, color=(0, 0, 0), oc=vs)
    page.draw_line((100, 450), (700, 450), width=PEN, color=(0, 0, 0), oc=kb)
    for x in (150.0, 350.0, 550.0):
        _label(page, x, 250.0, "VS02-22-15", (x + 70, 300.0))
        _label(page, x, 400.0, "KB02-3-35", (x + 70, 450.0))
    for x in (200.0, 500.0, 800.0):
        page.insert_text((x, 600), "V50-02-271", fontsize=9, fontname="helv")       # a section's sheet
    page.insert_text((900, 90), "FORKLARINGAR", fontsize=11, fontname="helv")
    for i, (code, text) in enumerate(LEGEND):
        page.insert_text((900, 110 + i * 13), code, fontsize=8, fontname="helv")
        page.insert_text((960, 110 + i * 13), text, fontsize=8, fontname="helv")
    page.insert_text((100, 800), "SKALA 1:100", fontsize=10, fontname="helv")
    doc.save(path)
    doc.close()
    return path


def _rows(path, overrides=None):
    with rules.using(overrides):
        pa = analyze_page(extract_document(path).pages[0])
    return {q["designation"]: q["confirmed_horizontal_m"] for q in pa.quantities}


def test_the_pipes_are_measured_beside_a_reference_to_another_sheet(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf")))
    assert rows.get("VS02-22-15", 0) > 15 and rows.get("KB02-3-35", 0) > 15, rows


def test_counted_as_a_system_the_reference_takes_the_layers(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf")), {"pipeline.CONFLICT_ONLY_WITH_PIPE_LABELS": False})
    assert rows.get("VS02-22-15", 0) < 1 and rows.get("KB02-3-35", 0) < 1, rows
