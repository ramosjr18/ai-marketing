#!/usr/bin/env python3
"""One UUID v7 per line.

v7 carries the time inside it: sorting files by name sorts them by when they were created,
which is what `clients/<case>/transcripts/` needs. And it does not collide when two
conversations on the same day would otherwise share a name.

    .venv/bin/python tools/id7.py          one id
    .venv/bin/python tools/id7.py 3        three
"""

from __future__ import annotations

import os
import sys
import time
import uuid


def uuid7() -> uuid.UUID:
    """uuid.uuid7() en Python 3.14+. En versiones anteriores, el mismo formato a mano."""
    if hasattr(uuid, "uuid7"):
        return uuid.uuid7()
    ms = int(time.time() * 1000) & ((1 << 48) - 1)
    rand = int.from_bytes(os.urandom(10), "big")
    rand_a = (rand >> 62) & 0x0FFF
    rand_b = rand & ((1 << 62) - 1)
    value = (ms << 80) | (0x7 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    return uuid.UUID(int=value)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for _ in range(n):
        print(uuid7())
