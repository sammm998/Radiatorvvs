"""A count written apart from its code is the code's count.

One sheet writes the bundles at a manifold both ways: "4xKV1-X32-16" and "6x VV1-X32-16". Read as two words, "6x" is
no code and the row was taken for a note, so the bundle it names went unnamed - and a row that wrote another label
beside it, "8x KV1-X32-16 2xVV1-X32-16", was lost whole. The space is spacing: the count is read as it is read where
the sheet writes it together, and two labels on one row are two labels.
"""
import pymupdf

from vvs_engine.pdf.extract import extract_document
from vvs_engine.pipeline import analyze_page


def _sheet(path, rows):
    doc = pymupdf.open()
    page = doc.new_page(width=842, height=595)
    for y, texts in rows:
        x = 100.0
        for t in texts:
            page.insert_text((x, y), t, fontsize=10, fontname="helv")
            x += pymupdf.get_text_length(t, fontname="helv", fontsize=10) + 12.0
    doc.save(path)
    doc.close()
    return str(path)


def _read(path):
    pa = analyze_page(extract_document(path).pages[0])
    return sorted((d.text, d.multiplier) for d in pa.designations)


APART = [(150, ["6x VV1-X32-16"]), (250, ["4xKV1-X32-16"]), (350, ["8x KV1-X32-16", "2xVV1-X32-16"])]
TOGETHER = [(150, ["6xVV1-X32-16"]), (250, ["4xKV1-X32-16"]), (350, ["8xKV1-X32-16", "2xVV1-X32-16"])]
NAMED = [("KV1-X32-16", 4), ("KV1-X32-16", 8), ("VV1-X32-16", 2), ("VV1-X32-16", 6)]


def test_a_count_written_apart_reads_as_the_count_written_together(tmp_path):
    assert _read(_sheet(tmp_path / "apart.pdf", APART)) == NAMED
    assert _read(_sheet(tmp_path / "together.pdf", TOGETHER)) == NAMED


def test_a_count_before_a_word_that_is_no_code_stays_a_note(tmp_path):
    names = _read(_sheet(tmp_path / "note.pdf", [(150, ["2x RADIATOR"]), (250, ["3x DUSCH-WC"])]))
    assert names == [], names
