"""Génère assets/img/og-image.png (1200x630) : dégradé camel → ocre veiné de bois.

Bibliothèque standard uniquement. Usage : python3 tools/og_image.py
"""
import math
import struct
import zlib
from pathlib import Path

W, H = 1200, 630
CAMEL = (0xC1, 0x9A, 0x6B)
OCRE = (0xCC, 0x77, 0x22)
CHENE = (0x2A, 0x1D, 0x14)
OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "og-image.png"


def melange(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def pixel(x, y):
    couleur = melange(CAMEL, OCRE, (x / W + y / H) / 2)
    veine = math.sin(y / 9 + 3 * math.sin(x / 140) + 1.5 * math.sin(x / 37 + y / 80))
    if veine > 0.93:
        couleur = melange(couleur, CHENE, 0.12)
    return bytes(round(c) for c in couleur)


def chunk(kind, data):
    crc = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def main():
    lignes = (b"\x00" + b"".join(pixel(x, y) for x in range(W)) for y in range(H))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"".join(lignes), 9))
        + chunk(b"IEND", b"")
    )
    OUT.write_bytes(png)
    print(f"{OUT} ({len(png)} octets)")


if __name__ == "__main__":
    main()
