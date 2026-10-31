"""A pen the sheet's own labels have ticked draws pipe, whatever its strokes end at.

A pen whose every stroke starts or ends at a label box writes; it does not draw. But a sheet drew its heating pipes
up to small rings at the radiators, the lettering read each ring as the letter O, and so every stroke of the heating
pen ended "at a label": the pen four heating labels had ticked was taken for a writing pen, and none of them got a
metre. A leader leaves its tick on the pipe it points at, never on another leader - so a pen two labels have
ticked draws pipe.
"""
import os

from vvs_engine import pipeline, rules
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import analyze_page

from test_a_tick_across_two_pipes_marks_both import _sheet


def _read(path, monkeypatch, overrides=None):
    # every pen of the sheet taken for a writing pen, as the rings read as O made the heating pen look
    monkeypatch.setattr(pipeline, "_writing_pens", lambda page, families, blocks: set(families))
    page = extract_document(path).pages[0]
    with rules.using(overrides):
        pa = analyze_page(page)
    return {r["designation"]: r for r in pa.quantities}


def test_the_pen_its_labels_ticked_keeps_its_metres(tmp_path, monkeypatch):
    rows = _read(_sheet(os.path.join(tmp_path, "rör.pdf")), monkeypatch)
    for name in ("KV2-K1-35", "VS2-S13-35", "KV1-K1-28"):
        assert rows.get(name, {}).get("confirmed_horizontal_m", 0) > 0, (name, rows.get(name))


def test_without_enough_ticks_the_pen_is_still_set_aside(tmp_path, monkeypatch):
    rows = _read(_sheet(os.path.join(tmp_path, "rör.pdf")), monkeypatch,
                 {"pipeline.WRITING_PEN_TICKED_LABELS": 20})
    assert not any(r.get("confirmed_horizontal_m", 0) > 0 for r in rows.values()), rows
