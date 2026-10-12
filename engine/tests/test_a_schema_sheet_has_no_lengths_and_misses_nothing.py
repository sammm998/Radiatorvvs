"""A flow or principle diagram is drawn without a scale on purpose: its lines say what connects to what, not how long
anything is. Its pipes are measured on the plans. The reading says so, and asks nothing of it a plan owes:

- its verdict is SCHEMATIC, not "incomplete": no reason "no scale" and none "nothing measured", and the share of
  pipe names with metres is no question to ask of it
- none of its pipe names is listed as missed; they stand as the pipes the schema shows
- its components are counted, and in "Alla" its pipe names say where they are measured
- the same drawing without the schema's title is still a sheet without a scale, as before
"""
import pymupdf

from vvs_engine import disciplines
from vvs_engine.coverage import completion_checks, coverage_validity
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import analyze_page, reading_coverage


def _line(shape, p0, p1, w=0.7):
    shape.draw_line(p0, p1)
    shape.finish(width=w, color=(0, 0, 0), closePath=False)


def _label(page, shape, text, at, to):
    """A label written at `at`, underlined, with a leader to `to` and a tick across where it lands."""
    x, y = at
    page.insert_text((x, y), text, fontsize=10, fontname="helv")
    w = 6.2 * len(text)
    _line(shape, (x, y + 2), (x + w, y + 2))
    _line(shape, (x + w, y + 2), to)
    _line(shape, (to[0] - 2.5, to[1] + 2.5), (to[0] + 2.5, to[1] - 2.5))


def _sheet(path, title):
    """Two pipes drawn as single lines between boxes, named by their labels, a valve's tag on one of them, and no
    scale anywhere: no scale text, no bar, no pipe drawn with both its edges."""
    doc = pymupdf.open()
    page = doc.new_page(width=842, height=595)
    shape = page.new_shape()
    if title:
        page.insert_text((60, 560), title, fontsize=12, fontname="helv")
    for y, text in ((200, "KV1-X7-40"), (320, "VV1-X7-25")):
        _line(shape, (120, y), (620, y), 1.44)
        shape.draw_rect(pymupdf.Rect(620, y - 20, 680, y + 20))
        shape.finish(width=1.0, color=(0, 0, 0))
        _label(page, shape, text, (200, y - 40), (260, y))
    shape.draw_rect(pymupdf.Rect(400, 194, 412, 206))
    shape.finish(width=0.7, color=(0, 0, 0))
    _label(page, shape, "AV201-40", (430, 150), (406, 194))
    page.insert_text((140, 440), "VS1-S13-54/V3", fontsize=10, fontname="helv")     # a pipe's name, with no leader
    shape.commit()
    doc.save(path)
    doc.close()
    return str(path)


def _read(path):
    pa = analyze_page(extract_document(path).pages[0])
    cov = reading_coverage(pa)
    verdict = completion_checks(coverage_validity(cov, pa.anchors, None, pa.scale.state if pa.scale else None,
                                                  len(pa.measures)), pa.quantities)
    return pa, cov, verdict


def test_a_schema_is_judged_as_a_schema_and_none_of_its_pipe_names_is_missed(tmp_path):
    pa, cov, v = _read(_sheet(tmp_path / "principschema.pdf", "PRINCIPSCHEMA VS-INSTALLATIONER"))
    assert pa.scale.reason == "schematic_not_to_scale"
    assert v["verdict"] == "SCHEMATIC", v
    assert "SCHEMATIC_NOT_TO_SCALE" in v["reasons"]
    assert not {"NO_SCALE", "SHEET_NAMES_PIPES_BUT_NOTHING_WAS_MEASURED"} & set(v["reasons"]), v["reasons"]
    assert v["measures"]["NAMES_WITH_METRES_SHARE"] is None
    assert cov["schematic"] is True and cov["missed"] == [] and cov["without_metres"] == [] and cov["share"] is None
    assert {n["name"] for n in cov["names_on_schematic"]} == {"KV1-X7-40", "VV1-X7-25", "VS1-S13-54/V3"}
    assert [(c["name"], c["count"]) for c in cov["components"]] == [("AV201-40", 1)]


def test_in_alla_a_schemas_pipe_names_say_where_they_are_measured(tmp_path):
    path = _sheet(tmp_path / "principschema.pdf", "PRINCIPSCHEMA VS-INSTALLATIONER")
    with disciplines.using("alla"):
        pa = analyze_page(extract_document(path).pages[0])
    E = {e["name"]: e for e in pa.register["entries"]}
    assert E["KV1-X7-40"]["kind"] == "ledning" and E["KV1-X7-40"]["quantity"] == 0
    assert E["KV1-X7-40"]["reasons"] == ["schema, mängdas på planritningarna"]
    # a pipe's name the schema writes with no leader has no row in the takeoff at all, and is no run missed either
    assert (E["VS1-S13-54/V3"]["kind"], E["VS1-S13-54/V3"]["reasons"]) == ("ledning", ["schema, mängdas på planritningarna"])
    assert E["AV201-40"]["unit"] == "st"


def test_what_the_checks_say_is_listed_on_a_schema_but_does_not_make_it_a_takeoff_to_review():
    v = {"verdict": "SCHEMATIC", "reasons": ["SCHEMATIC_NOT_TO_SCALE"], "measures": {}}
    unanswered = {"model": {"result": {"assignments": [{"status": "unresolved", "reason": "unanswered"}]}}}
    out = completion_checks(v, [], unanswered)
    assert out["verdict"] == "SCHEMATIC" and out["reasons"] == ["SCHEMATIC_NOT_TO_SCALE", "MODEL_REVIEW_INCOMPLETE"]
    assert completion_checks({**v, "verdict": "VALID", "reasons": []}, [], unanswered)["verdict"] == "DEGRADED"


def test_the_same_drawing_without_the_schemas_title_is_still_a_sheet_without_a_scale(tmp_path):
    pa, cov, v = _read(_sheet(tmp_path / "plan.pdf", None))
    assert pa.scale.reason != "schematic_not_to_scale"
    assert v["verdict"] == "INVALID" and "NO_SCALE" in v["reasons"], v
    assert not cov.get("schematic") and "names_on_schematic" not in cov
