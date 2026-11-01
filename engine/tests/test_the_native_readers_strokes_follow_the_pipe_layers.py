"""On a sheet with layer names, the native reader's strokes join only the pens named like the pipes.

The native reader takes every long stroke for a stretch of pipe. On a set of cooling plans the plan's own xref,
`pr1_0200A|P-------O-`, came back as forty-five metres of pipe nobody named on every sheet, and each sheet
reported forty-five metres it had missed. Its strokes now join a pen the reading took as pipe, a pen whose layer
is named the way those are, or a pen one of the native reader's own labels lands on.
"""
import pymupdf

from vvs_engine import rules
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipes.representation import collect_prims, describe_family, build_graph, stroke_family
from vvs_engine.source_rules.native_bridge import merge_detection

PEN = 0.72


def _drawing(path):
    with pymupdf.open() as doc:
        p = doc.new_page(width=600, height=400)
        kb = doc.add_ocg("v50_p260|V-55512")
        vs = doc.add_ocg("v50_p260|V-56512")
        plan = doc.add_ocg("pr1_0200A|P-------O-")
        p.draw_line((40, 100), (400, 100), width=PEN, oc=kb)        # the pipe the reading took
        p.draw_line((40, 200), (400, 200), width=PEN, oc=vs)        # a pipe on a layer named like it
        p.draw_line((40, 300), (400, 300), width=PEN, oc=plan)      # the plan's background
        doc.save(path)
    return extract_document(str(path)).pages[0]


def _native(page):
    paths, stretches = [], []
    for i, path in enumerate(q for q in page.paths if q.segs):
        s = path.segs[0]
        paths.append({"id": i, "layer": path.layer, "width": path.width, "rect": list(path.bbox),
                      "items": [["l", s.x0, s.y0, s.x1, s.y1]]})
        stretches.append({"id": i, "path_ids": [i]})
    return {"extraction": {"paths": paths}, "graph": {"stretches": stretches, "nodes": []},
            "labels": [], "association": {"leaders": []}}


def _merge(page, overrides=None):
    kb = next(q for q in page.paths if q.layer.endswith("V-55512"))
    fk = stroke_family(kb.layer, kb.width, kb.color)
    prims = collect_prims(page, {fk})[fk]
    g = build_graph(prims, fk)
    graphs, families = {fk: g}, {fk: describe_family(fk, prims, g)}
    with rules.using(overrides):
        result = merge_detection(page, _native(page), graphs, families, [], {}, {})
    return result, {f.split("|s|")[0].rsplit("|", 1)[-1] for f in graphs}


def test_the_background_is_not_added_and_a_pipe_layer_is(tmp_path):
    result, layers = _merge(_drawing(tmp_path / "plan.pdf"))
    assert "V-56512" in layers and "P-------O-" not in layers, layers
    assert result["native_strokes_on_layers_no_pipe_is_named_like"] == 1


def test_without_the_rule_the_background_becomes_pipe(tmp_path):
    _, layers = _merge(_drawing(tmp_path / "plan.pdf"), {"source_rules.native_bridge.NATIVE_JOINS_THE_PIPE_LAYERS": False})
    assert "P-------O-" in layers, layers
