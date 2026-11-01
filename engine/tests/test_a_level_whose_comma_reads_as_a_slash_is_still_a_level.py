"""A level whose decimal comma was read as a slash is still a level, and never a pipe.

"VG+28,46" drawn as strokes came out "VG+28/46". No longer shaped like a level, it was read as a designation of
size 28; its leader ended on the cooling and waste pipes it stood over, and those runs were "pointed at but
unnamed" - three names for one run. After a sign, a slash between two numbers is that comma.
"""
from vvs_engine.semantics.annotation import ELEV_RE


def test_a_level_read_with_a_slash_is_a_level():
    for t in ("VG+28/46", "VG+28,46", "VG+1.67", "FG+19.82", "CL+2650"):
        assert ELEV_RE.match(t), t


def test_pipe_names_are_not_levels():
    for t in ("VS02-22-12", "KV1+VV1", "S54-75", "KV01-53-/VV01-53-20", "VG28/46"):
        assert not ELEV_RE.match(t), t
