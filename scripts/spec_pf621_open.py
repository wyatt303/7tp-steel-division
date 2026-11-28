"""Polski Fiat 621L with the open wooden cargo body (no canvas tilt).

Everything else as spec_pf621.py; build it with TK_SPEC=spec_pf621_open.
"""

import spec_pf621 as _base
from spec_pf621 import *  # noqa: F401,F403

STEM = "PF621L_OPEN"
TILT = False
# Without the tilt the panes in its sides are gone; the cab glass stays.
GLASS_BOXES = [box for box in _base.GLASS_BOXES if box[4] != _base.TILT_WINDOW_Z[0]]
is_tyre = _base.is_tyre
rivet_lines = _base.rivet_lines
cab_front = _base.cab_front
