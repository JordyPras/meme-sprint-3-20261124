"""Meme Sprint 3: AI Agent Goes Rogue — entrypoint.

Writes the meme image to the output directory as entry.png.

The image itself (entry.png, committed next to this file) is a
1024x1024 chat-screenshot meme: the user asks AGENT-7 to book a flight
to Bali, and the agent sells the user's house to pay for it.

This program validates the image against the bounty gate (whole PNG,
at most 1 MiB, at most 1024 by 1024 pixels) and copies it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output). The copy is byte for
byte identical, so two runs always produce the same output.
"""

import hashlib
import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
MAX_EDGE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_png_size(data):
    """Return (width, height) from a PNG's IHDR chunk."""
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("not a PNG file (bad signature)")
    if len(data) < 33:
        raise ValueError("PNG too short for an IHDR chunk")
    chunk_len = struct.unpack(">I", data[8:12])[0]
    chunk_type = data[12:16]
    if chunk_type != b"IHDR" or chunk_len != 13:
        raise ValueError("first PNG chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")

    with open(source, "rb") as handle:
        data = handle.read()

    if len(data) > MAX_BYTES:
        raise ValueError(
            "entry.png is %d bytes, over the 1 MiB gate" % len(data)
        )
    width, height = read_png_size(data)
    if width > MAX_EDGE or height > MAX_EDGE:
        raise ValueError(
            "entry.png is %dx%d, over the 1024x1024 gate"
            % (width, height)
        )

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, target)

    with open(target, "rb") as handle:
        copied = handle.read()
    if hashlib.sha256(copied).hexdigest() != hashlib.sha256(data).hexdigest():
        raise ValueError("copied entry.png does not match the source")

    print("Meme Sprint 3: AI Agent Goes Rogue")
    print("meme: AGENT-7 sells your house to pay for a Bali flight")
    print("entry.png: %dx%d, %d bytes" % (width, height, len(data)))
    print("sha256: %s" % hashlib.sha256(data).hexdigest()[:16])
    print("wrote: %s" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
