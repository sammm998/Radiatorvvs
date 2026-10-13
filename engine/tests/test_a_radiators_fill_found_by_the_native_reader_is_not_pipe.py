"""What the reading sets aside as a drawn figure, the native reader does not bring back as pipe.

One sheet draws its radiators as a narrow box filled with six strokes of the pen its thin pipes are drawn with. The
reading sets such ink aside: it fills its box and goes nowhere. The native reader took the fill strokes for stretches
of pipe, and they were added to the reading's own geometry - the fill of twenty-two radiators measured as the heating
pipes that end at them. Its strokes are now put to the reading's test, on the whole pen, before they join.
"""
import pymupdf

from vvs_engine.pdf.extract import extract_document
from vvs_engine.source_rules.native_bridge import merge_detection

THIN = 0.72


def _drawing(path, radiator=True):
    with pymupdf.open() as doc:
        p = doc.new_page(width=400, height=300)
        p.draw_line((40, 150), (200, 150), width=1.44)                       # the heating pipe, its own pen
        if radiator:
            p.draw_rect(pymupdf.Rect(200, 148, 251, 152), width=THIN)       # the radiator: a narrow box...
            for k in range(6):                                                # ...filled with six strokes
                y = 148.6 + 0.6 * k
                p.draw_line((200, y), (251, y), width=THIN)
        p.draw_line((60, 220), (180, 220), width=THIN)                       # a thin pipe of the same pen
        doc.save(path)
    return extract_document(str(path)).pages[0]


def _native(page, strokes):
    """The native reader's view: every stroke given is a stretch of pipe."""
    paths, stretches = [], []
    for i, path in enumerate(strokes):
        s = path.segs[0]
        paths.append({"id": i, "layer": path.layer, "width": path.width, "rect": list(path.bbox),
                      "items": [["l", s.x0, s.y0, s.x1, s.y1]]})
        stretches.append({"id": i, "path_ids": [i]})
    return {"extraction": {"paths": paths}, "graph": {"stretches": stretches, "nodes": []},
            "labels": [], "association": {"leaders": []}}


def _thin(page):
    return [p for p in page.paths if abs(p.width - THIN) < 0.01 and len(p.segs) == 1]


def test_the_radiators_fill_is_not_added_and_the_thin_pipe_is(tmp_path):
    page = _drawing(tmp_path / "radiator.pdf")
    fill = [p for p in _thin(page) if 148 <= p.bbox[1] <= 152]
    pipe = [p for p in _thin(page) if p.bbox[1] > 200]
    assert len(fill) == 6 and len(pipe) == 1
    graphs = {}
    result = merge_detection(page, _native(page, fill[:2] + pipe), graphs, {}, [], {}, {})
    assert result["native_strokes_of_drawn_figures"] == 2
    added = {q.pid for g in graphs.values() for q in g.prims.values()}
    assert added == {pipe[0].pid}


def test_strokes_of_a_pen_that_draws_no_figure_are_added_as_before(tmp_path):
    page = _drawing(tmp_path / "pipes.pdf", radiator=False)
    graphs = {}
    result = merge_detection(page, _native(page, _thin(page)), graphs, {}, [], {}, {})
    assert result["native_strokes_of_drawn_figures"] == 0 and result["added_primitives"] == 1
