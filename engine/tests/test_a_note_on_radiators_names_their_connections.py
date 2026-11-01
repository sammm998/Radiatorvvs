"""A sheet's note on radiators names the connections it does not label.

    RADIATORER ANSLUTES MED DIM. 12 OM ANNAT EJ ANGIVES.

A set of plans draws every radiator connection - the short branch from the heating pipe to the radiator - without
a label: the note is its label. The heating main is named (VS02-22-15); its branches were not, and half the
heating pen went unmeasured. A short unnamed branch on the heating pen that meets one heating name takes that
name's stem in the note's size. A longer run is a main whose label was not reached; a branch of a pipe the list
does not call heating keeps no name; without the note nothing is named.
"""
import pymupdf

from vvs_engine import rules
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import analyze_page
from vvs_engine.semantics.declarations import _declared_branch

PEN, LEAD = 0.72, 0.24
M = 72 / 25.4 * 10            # pt per metre at 1:100
LEGEND = [("KBXX-3", "KOLDBARARE, KOPPAR"), ("KVXX-3", "KALLVATTENLEDNING, KOPPAR"),
          ("VVXX-3", "VARMVATTENLEDNING, KOPPAR"), ("VSXX-22", "VARMEBARARE, SEKUNDAR STALROR"),
          ("S54", "SPILLVATTENLEDNING, PP-ROR"), ("BV", "BACKVENTIL"), ("XX", "AVSER SYSTEMBETECKNING")]


def _label(page, x, y, text, to):
    page.insert_text((x, y), text, fontsize=9, fontname="helv")
    page.draw_line((x, y + 3), (x + 62, y + 3), width=LEAD, color=(0, 0, 0))
    page.draw_line((x + 62, y + 3), to, width=LEAD, color=(0, 0, 0))
    page.draw_line((to[0] - 2, to[1] + 2), (to[0] + 2, to[1] - 2), width=LEAD, color=(0, 0, 0))


def _sheet(path, note=True, code="VS02-22-15"):
    """A heating main with four short branches, a cooling pipe beside it, the list, and the note."""
    doc = pymupdf.open()
    page = doc.new_page(width=1191, height=842)
    vs = doc.add_ocg("v50_p260|V-56512")
    kb = doc.add_ocg("v50_p260|V-55512")
    page.draw_line((100, 500), (100 + 20 * M, 500), width=PEN, color=(0, 0, 0), oc=kb)     # a cooling pipe
    for x in (130.0, 330.0, 530.0):
        _label(page, x, 450.0, "KB02-3-35", (x + 70, 500.0))
    page.draw_line((100, 300), (100 + 20 * M, 300), width=PEN, color=(0, 0, 0), oc=vs)     # the main, 20 m
    for k in range(4):                                                                     # four branches, 2 m
        x = 150 + k * 4 * M
        page.draw_line((x, 300), (x, 300 + 2 * M), width=PEN, color=(0, 0, 0), oc=vs)
    for x in (130.0, 330.0, 530.0):
        _label(page, x, 250.0, code, (x + 70, 300.0))
    page.insert_text((900, 90), "FORKLARINGAR", fontsize=11, fontname="helv")
    for i, (c, t) in enumerate(LEGEND):
        page.insert_text((900, 110 + i * 13), c, fontsize=8, fontname="helv")
        page.insert_text((960, 110 + i * 13), t, fontsize=8, fontname="helv")
    if note:
        page.insert_text((900, 230), "RADIATORER ANSLUTES MED DIM. 12 OM ANNAT EJ ANGIVES.", fontsize=7,
                         fontname="helv")
    page.insert_text((100, 800), "SKALA 1:100", fontsize=10, fontname="helv")
    doc.save(path)
    doc.close()
    return path


def _rows(path, overrides=None):
    with rules.using(overrides):
        pa = analyze_page(extract_document(path).pages[0])
    return {q["designation"]: q for q in pa.quantities}


def test_the_note_is_read_as_a_rule():
    b = _declared_branch("RADIATORER ANS?UTES NED DIM. 12 0N ANNAT E? ANGIVES.")    # as strokes read it
    assert b is not None and b.dn == 12
    assert _declared_branch("RADIATORER ANSLUTES MED DIM. 12") is None                 # no rule, no default
    assert _declared_branch("RADIATORER DIM. 12 OCH DIM. 15 OM ANNAT EJ ANGIVES") is None


def test_the_branches_take_the_mains_name_in_the_notes_size(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf")))
    assert rows["VS02-22-15"]["confirmed_horizontal_m"] > 15, rows
    branches = rows.get("VS02-22-12")
    assert branches is not None and abs(branches["confirmed_horizontal_m"] - 8.0) < 0.6, rows
    assert branches.get("declared_m", 0) > 7.0, branches


def test_without_the_note_the_branches_stay_unnamed(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf"), note=False))
    assert "VS02-22-12" not in rows, rows


def test_a_branch_longer_than_a_connection_keeps_no_name(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf")), {"pipes.ownership.BRANCH_RUN_MAX_M": 1.5})
    assert "VS02-22-12" not in rows, rows


def test_the_branches_of_a_pipe_the_list_does_not_call_heating_keep_no_name(tmp_path):
    rows = _rows(_sheet(str(tmp_path / "plan.pdf"), code="KV02-3-15"))
    assert rows.get("KV02-3-15", {}).get("confirmed_horizontal_m", 0) > 15, rows
    assert not any(k.endswith("-12") for k in rows), rows
