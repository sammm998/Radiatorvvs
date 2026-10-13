"""An apparatus drawn on the pipe pen is no pipe, and the pipe's name stops at its edge.

One sheet draws its air handling unit box beside box, each box with a double edge, on the pen of the heating pipe
that feeds it. The reading sets drawn figures aside by their ink: a knot of strokes that spends many times its own
extent in ink stands still. But the pipe that ends at the unit joined the unit's knot, the knot reached as far as the
pipe, and the unit was measured as the pipe, round every box - forty metres on a sixty-metre pipe. The unit's strokes
close on themselves and a run's never do, so the strokes on loops are weighed again on their own.
"""
import math

import pymupdf

from vvs_engine.geometry.core import Seg
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import analyze_page
from vvs_engine.pipes.representation import Prim, figure_pieces

PIPE, WRITE = 1.44, 0.72
M = 56.69


def _box(x0, y0, x1, y1):
    return [Seg(x0, y0, x1, y0), Seg(x1, y0, x1, y1), Seg(x1, y1, x0, y1), Seg(x0, y1, x0, y0)]


def _unit(x=300.0, y=200.0):
    """Three boxes side by side, each with a double edge 2.9 apart; the middle one divided by a double wall that lands
    on its inner edge; a fan - a box with its cross - in the last: an apparatus."""
    segs = []
    for k in range(3):
        x0 = x + 60 * k
        segs += _box(x0, y, x0 + 60, y + 50) + _box(x0 + 2.9, y + 2.9, x0 + 57.1, y + 47.1)
    segs += [Seg(x + 88.55, y + 2.9, x + 88.55, y + 47.1), Seg(x + 91.45, y + 2.9, x + 91.45, y + 47.1)]
    segs += _box(x + 130, y + 10, x + 170, y + 40)
    segs += [Seg(x + 130, y + 10, x + 170, y + 40), Seg(x + 130, y + 40, x + 170, y + 10)]
    return segs


def _pipe(x=300.0, y=200.0):
    """The pipe that feeds the unit: up to its underside, along, and away - a run, with no loop."""
    return [Seg(x + 40, y + 50, x + 40, y + 80), Seg(x + 40, y + 80, x - 200, y + 80), Seg(x - 200, y + 80, x - 200, y + 300)]


def _prims(segs):
    return [Prim(prim_id=i, pid=f"p{i}", seg_index=0, seg=s, family="f", layer="", width=PIPE) for i, s in enumerate(segs)]


def test_the_unit_stands_still_and_the_pipe_that_feeds_it_runs():
    unit, pipe = _prims(_unit()), _prims(_pipe())
    for i, q in enumerate(pipe):
        q.pid = f"pipe{i}"
    runs, figures = figure_pieces(unit + pipe)
    assert {q.pid for q in figures} == {q.pid for q in unit}
    assert {q.pid for q in runs} == {q.pid for q in pipe}


def _ring(cx, cy, radii=(4.2, 3.4, 2.6, 1.8, 1.0), n=40):
    segs = []
    for r in radii:
        pts = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
        segs += [Seg(*pts[k], *pts[k + 1]) for k in range(n)]
    return segs


def test_a_ring_the_run_passes_through_is_no_object():
    """A ring drawn in the line - rings within rings, ink many times its size - closes on itself as an object's
    strokes do, but it is a symbol of the run, smaller than any apparatus, and the run goes on through it."""
    ring = _ring(200.0, 100.0)
    pipe = [Seg(100, 100, 195.8, 100), Seg(204.2, 100, 300, 100), Seg(300, 100, 300, 250)]
    runs, figures = figure_pieces(_prims(ring + pipe))
    assert figures == [], len(figures)


def test_a_loop_of_pipe_and_a_pipe_drawn_as_its_outline_are_runs():
    ring = _prims(_box(100, 100, 220, 180))                    # a ring main round a room
    outline = _prims(_box(100, 300, 400, 306))                 # a large pipe drawn by its two edges
    for prims in (ring, outline, ring + _prims(_pipe(100, 100))):
        runs, figures = figure_pieces(prims)
        assert figures == [], len(figures)


def _sheet(path):
    doc = pymupdf.open()
    page = doc.new_page(width=842, height=595)
    sh = page.new_shape()
    for s in _unit() + _pipe():
        sh.draw_line((s.x0, s.y0), (s.x1, s.y1))
    sh.finish(width=PIPE, color=(0, 0, 0), closePath=False)
    sh.commit()
    for x, y, to in ((140, 250, (100, 330)), (140, 430, (100, 450))):
        page.insert_text((x, y), "VS3-S13-28", fontsize=10, fontname="helv")
        page.draw_line((x, y + 3), (x + 62, y + 3), width=WRITE, color=(0, 0, 0))
        page.draw_line((x, y + 3), to, width=WRITE, color=(0, 0, 0))
    page.insert_text((100, 560), "SKALA 1:50", fontsize=10, fontname="helv")
    for i in range(6):
        page.insert_text((300 + i * M, 560), str(i), fontsize=8, fontname="helv")
    page.draw_line((302, 566), (302 + 5 * M, 566), width=1.0, color=(0, 0, 0))
    doc.save(path)
    doc.close()
    return str(path)


def test_the_pipe_that_feeds_the_unit_keeps_its_whole_length(tmp_path):
    """Setting the unit aside takes nothing of the pipe: it is measured to the unit's edge, every metre of it."""
    pa = analyze_page(extract_document(_sheet(tmp_path / "aggregat.pdf")).pages[0])
    metres = sum(q["confirmed_horizontal_m"] for q in pa.quantities if q["designation"].startswith("VS3"))
    drawn = sum(s.length for s in _pipe()) * 0.3528 * 50 / 1000          # 490 pt at 1:50
    assert abs(metres - drawn) <= 0.05 * drawn, (metres, drawn)
