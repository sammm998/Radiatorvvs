"""On a sheet with layer names, a pen is a peer of the pipes only if its layer is named the way theirs are.

A peer is a pen measured against the best pen: on a sheet where no layer name says which pens are pipe, several
pens each carrying a fair share of the label ends are several systems. The rule held on sheets with layer names
too. A cooling plan whose pipes lie on `v50_p270|V-55512` and `v50_p270|V-56512` had two labels whose leaders
ended on a toilet's wall, drawn on the architect's `A30_p270|A040`: the walls were taken as a peer, and the
toilets measured ninety-one metres of water pipe, the facade sixty-eight of heating.

The sheet drawn here: two pipes on the sheet's own pipe layers, each with its labels, and a room's walls on the
architect's layer that two labels' leaders end on with a tick. The pipes are measured; the walls are not.
"""
import pymupdf

from vvs_engine import rules
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import analyze_page

PEN = 0.72
WALL = 0.24
LEAD = 0.24


def _label(page, x, y, text, to):
    page.insert_text((x, y), text, fontsize=9, fontname="helv")
    page.draw_line((x, y + 3), (x + 58, y + 3), width=LEAD, color=(0, 0, 0))
    page.draw_line((x + 58, y + 3), to, width=LEAD, color=(0, 0, 0))
    page.draw_line((to[0] - 2, to[1] + 2), (to[0] + 2, to[1] - 2), width=LEAD, color=(0, 0, 0))


def _sheet(path, interior=False):
    doc = pymupdf.open()
    page = doc.new_page(width=1191, height=842)
    kb = doc.add_ocg("v50_p270|V-55512")
    vs = doc.add_ocg("v50_p270|V-56512")
    wall = doc.add_ocg("A30_p270|A040")
    page.draw_line((100, 300), (700, 300), width=PEN, color=(0, 0, 0), oc=kb)
    page.draw_line((100, 400), (700, 400), width=PEN, color=(0, 0, 0), oc=vs)
    for a, b in (((800, 200), (1000, 200)), ((1000, 200), (1000, 500)), ((1000, 500), (800, 500)),
                 ((800, 500), (800, 200))):
        page.draw_line(a, b, width=WALL, color=(0, 0, 0), oc=wall)
    for x in (110.0, 200.0, 290.0, 380.0, 470.0, 560.0):
        _label(page, x, 250.0, "KB02-3-35", (x + 70, 300.0))
    for x in (110.0, 200.0, 290.0, 380.0, 470.0, 560.0):
        _label(page, x, 360.0, "VS02-22-15", (x + 70, 400.0))
    for y in (260.0, 420.0):
        _label(page, 1040.0, y - 40, "VV02-3-20", (1000.0, y))
    if interior:
        # the interior designer's fittings on their own xref: five labels' ticks land on its long lines
        fit = doc.add_ocg("I40_p270|I050")
        page.draw_line((100, 600), (700, 600), width=WALL, color=(0, 0, 0), oc=fit)
        for x in (110.0, 230.0, 350.0, 470.0, 590.0):
            _label(page, x, 560.0, "VV02-3-16", (x + 70, 600.0))
    page.insert_text((100, 800), "SKALA 1:100", fontsize=10, fontname="helv")
    doc.save(path)
    doc.close()
    return path


def _rows(path, overrides=None):
    with rules.using(overrides):
        pa = analyze_page(extract_document(path).pages[0])
    return {q["designation"]: q["confirmed_horizontal_m"] for q in pa.quantities}


def test_the_pipes_are_measured_and_the_walls_are_not(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf")))
    assert rows.get("KB02-3-35", 0) > 15 and rows.get("VS02-22-15", 0) > 15, rows
    assert rows.get("VV02-3-20", 0) < 1.0, rows


def test_without_the_rule_the_walls_become_pipe(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf")), {"pipeline.PEER_FOLLOWS_THE_BEST_LAYERS": False})
    assert rows.get("VV02-3-20", 0) > 5.0, rows


def test_a_pen_with_a_share_of_the_ticks_on_another_template_is_not_pipe(tmp_path):
    """Five ticks on the interior designer's lines are a good share of the sheet's ticks, and still no pipe."""
    rows = _rows(_sheet(str(tmp_path / "plan.pdf"), interior=True))
    assert rows.get("KB02-3-35", 0) > 15 and rows.get("VS02-22-15", 0) > 15, rows
    assert rows.get("VV02-3-16", 0) < 1.0, rows


def test_without_the_rule_the_interior_lines_become_pipe(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf"), interior=True), {"pipeline.PEER_FOLLOWS_THE_BEST_LAYERS": False})
    assert rows.get("VV02-3-16", 0) > 5.0, rows
