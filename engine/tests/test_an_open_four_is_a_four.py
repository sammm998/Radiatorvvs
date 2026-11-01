"""A 4 drawn open, as technical lettering draws it, is read as a 4.

The lettering on a set of plotted sheets draws its 4 open: a diagonal down to the crossbar, and a stem that
begins below the apex and never meets the diagonal. It encloses nothing. Measured only against closed 4s it
scored just outside what is accepted as a reading, became "?", and every label with a 4 in it was lost:
KB02-3-54, S54-75, RV51-40 - and the codes S54 and D54 in the sheet's own list.

The open form is built from the closed 4 of the same stroke alphabet: its stem begins between the apex and the
crossbar. The proportions drawn here are the ones measured on such a sheet, not the reference's own.
"""
import pymupdf

from vvs_engine.pdf.extract import extract_document
from vvs_engine.text import recognize
from vvs_engine.text.vector_text import vector_text_rows

from conftest import draw_hershey_text

H = 3.24
PEN = 0.24


def _open_four(sh, x, y):
    """An open 4 whose baseline is y, stroke for stroke as one was measured on a plotted sheet (points, at a text
    height of 3.24): diagonal from the apex to the crossbar, the crossbar, and a stem from below the apex down."""
    for (x0, y0), (x1, y1) in (((0.72, -3.24), (0.0, -0.72)), ((0.0, -0.72), (1.68, -0.72)),
                               ((1.20, -1.44), (1.20, 0.0))):
        sh.draw_line((x + x0, y + y0), (x + x1, y + y1))
        sh.finish(width=PEN, color=(0, 0, 0), closePath=False)
    return x + 1.68 + 0.6


# The strokes of two codes in a plotted list, "S54" above "S6", as measured (points, from the first S's baseline):
# condensed letters, an open 4. Only the codes' own lettering, nothing of the sheet they stood on.
STACKED_CODES = (
    (1.8, -3.36, 1.2, -3.6), (0.6, -3.6, 0.24, -3.48), (0.24, -3.48, 0.12, -3.36), (0.12, -3.36, 0.0, -3.0),
    (0.0, -2.76, 0.12, -2.4), (1.8, -0.84, 1.68, -1.2), (1.8, -0.72, 1.68, -0.24), (1.68, -0.24, 1.44, -0.12),
    (1.44, -0.12, 1.08, 0.0), (1.08, 0.0, 0.48, 0.0), (0.48, 0.0, 0.0, -0.24), (0.6, -3.6, 1.2, -3.6),
    (0.0, -3.0, 0.0, -2.76), (1.8, -0.84, 1.8, -0.72), (0.12, -2.4, 1.68, -1.2), (4.08, -3.6, 2.52, -3.6),
    (2.52, -3.6, 2.52, -1.8), (2.52, -1.8, 3.48, -1.8), (3.48, -1.8, 3.96, -1.68), (3.96, -1.68, 4.08, -1.32),
    (4.08, -1.32, 4.08, -0.48), (4.08, -0.48, 3.96, -0.12), (3.96, -0.12, 3.48, 0.0), (3.48, 0.0, 2.52, 0.0),
    (6.0, 0.0, 6.0, -1.8), (6.6, -1.08, 4.8, -1.08), (4.8, -1.08, 5.64, -3.6), (1.8, 2.52, 1.2, 2.28),
    (0.6, 2.28, 0.24, 2.4), (0.24, 2.4, 0.12, 2.52), (0.12, 2.52, 0.0, 2.88), (0.0, 3.0, 0.12, 3.36),
    (1.8, 5.04, 1.68, 4.68), (1.8, 5.16, 1.68, 5.52), (1.68, 5.52, 1.44, 5.64), (1.44, 5.64, 1.08, 5.76),
    (1.08, 5.76, 0.48, 5.76), (0.48, 5.76, 0.0, 5.52), (0.6, 2.28, 1.2, 2.28), (0.0, 2.88, 0.0, 3.0),
    (1.8, 5.04, 1.8, 5.16), (0.12, 3.36, 1.68, 4.68), (2.52, 5.04, 2.52, 4.08), (4.32, 5.04, 4.32, 4.56),
    (3.72, 4.08, 2.52, 4.08), (2.52, 5.04, 2.64, 5.4), (3.12, 5.76, 3.6, 5.76), (4.2, 5.4, 4.32, 5.04),
    (2.52, 4.08, 2.64, 3.48), (2.64, 3.48, 2.88, 3.0), (2.88, 3.0, 3.24, 2.64), (3.24, 2.64, 3.72, 2.28),
    (2.64, 5.4, 2.88, 5.64), (2.88, 5.64, 3.12, 5.76), (3.6, 5.76, 3.96, 5.64), (3.96, 5.64, 4.2, 5.4),
    (4.32, 4.56, 4.2, 4.2), (4.2, 4.2, 3.72, 4.08),
)


def _sheet(path, closed=False):
    doc = pymupdf.open()
    page = doc.new_page(width=420, height=297)
    sh = page.new_shape()
    # a label ending in an open 4, written along a row long enough to set the row's direction
    _, _, x, _ = draw_hershey_text(sh, "KB02-3-5", 100, 100, H, width=PEN)
    if closed:
        draw_hershey_text(sh, "4", x, 100, H, width=PEN)
    else:
        _open_four(sh, x, 100)
    draw_hershey_text(sh, "KALLVATTEN KOPPAR", 100, 140, H, width=PEN)
    # a list's codes: S54 above S6, short rows stacked, beside the long rows they explain
    for x0, y0, x1, y1 in STACKED_CODES:
        sh.draw_line((100 + x0, 200 + y0), (100 + x1, 200 + y1))
        sh.finish(width=PEN, color=(0, 0, 0), closePath=False)
    draw_hershey_text(sh, "SPILLVATTENLEDNING, PP-ROR", 125, 200, 3.6, width=PEN)
    draw_hershey_text(sh, "SPILLVATTENLEDNING, ROSTFRITT", 125, 205.76, 3.6, width=PEN)
    sh.commit()
    doc.save(path)
    doc.close()
    return str(path)


def _texts(path):
    return {r.text for r in vector_text_rows(extract_document(path).pages[0]).rows}


def test_an_open_four_in_a_label_is_read(tmp_path):
    assert "KB02-3-54" in _texts(_sheet(tmp_path / "open.pdf"))


def test_a_closed_four_is_read_as_before(tmp_path):
    assert "KB02-3-54" in _texts(_sheet(tmp_path / "closed.pdf", closed=True))


def test_two_short_codes_stacked_beside_their_rows_are_two_rows(tmp_path):
    # the 5 of this lettering reads as an S as often as not (S54 as SS4); the list compares codes through that
    # twin, so what matters here is that both rows are read, and read apart
    texts = _texts(_sheet(tmp_path / "list.pdf"))
    assert "S6" in texts and ({"S54", "SS4"} & texts), sorted(texts)


def test_without_the_open_form_the_four_is_not_read(tmp_path, monkeypatch):
    monkeypatch.setattr(recognize, "_open_four", lambda segs: [])
    recognize._ref_arrays.cache_clear()
    recognize.reference_alphabet.cache_clear()
    try:
        assert "KB02-3-54" not in _texts(_sheet(tmp_path / "open.pdf"))
    finally:
        monkeypatch.undo()
        recognize._ref_arrays.cache_clear()
        recognize.reference_alphabet.cache_clear()
