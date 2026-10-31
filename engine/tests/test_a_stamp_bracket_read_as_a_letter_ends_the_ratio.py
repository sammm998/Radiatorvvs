"""A stamp drawn as strokes reads its brackets as the letter they resemble, and its ratios are cut where they end.

`SKALA 1:50 (A1) 1:100 (A3)` drawn with stroke lettering came out "1:5O I A1" and "1:1OO I 3I": the bracket read
as an I, and an I where a number must stand is a 1. The first ratio was read as 1:501, the second as none at all,
and the sheet's own scale bar was outvoted by its own stamp. Where the run after "1:" is no scale anyone draws in,
but stops being one at a letter read as a 1, the ratio is what comes before that letter.

A stamp may also name the format before the ratio: "A3=1:100" says what "1:100 (A3)" says.
"""
import pymupdf

from vvs_engine.measure.scale import MM_PER_PT, discover_scale, ratios_in
from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import searchable_rows


def test_a_bracket_read_as_a_letter_ends_the_ratio():
    assert ratios_in("1:5OIA1") == [50]
    assert ratios_in("1:1OOI3I") == [100]
    assert ratios_in("1:5O(A1)") == [50]


def test_a_ratio_that_reads_whole_is_read_as_before():
    assert ratios_in("1:250") == [250]
    assert ratios_in("1:S0") == [50]
    assert ratios_in("1:30") == [30]              # no standard scale, but the whole run: as before
    assert ratios_in("1:10000") == []             # never four digits of a longer number


def _sheet(path, stamp, size=(1191, 842)):
    doc = pymupdf.open()
    page = doc.new_page(width=size[0], height=size[1])
    page.insert_text((900, 800), stamp, fontsize=8, fontname="helv")
    doc.save(path)
    doc.close()
    return str(path)


def test_a_format_named_before_its_ratio_is_the_sheets_scale(tmp_path):
    pg = extract_document(_sheet(tmp_path / "a3.pdf", "A3=1:100 V50-01-0001")).pages[0]
    sc = discover_scale(pg, searchable_rows(pg))
    assert sc.meters_per_pt is not None, sc.reason
    assert abs(sc.meters_per_pt - 100 * MM_PER_PT / 1000) < 1e-9
