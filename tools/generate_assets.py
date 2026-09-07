#!/usr/bin/env python3
"""Generate the PNG assets for the Rosé Pine Afterglow Chrome theme.

The renderer uses only Python's standard library so contributors can rebuild the
artwork without installing image tooling.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"

BASE = (25, 23, 36)
DEEP = (18, 16, 26)
SURFACE = (31, 29, 46)
OVERLAY = (38, 35, 58)
TEXT = (224, 222, 244)
LOVE = (235, 111, 146)
GOLD = (246, 193, 119)
ROSE = (235, 188, 186)
PINE = (49, 116, 143)
FOAM = (156, 207, 216)
IRIS = (196, 167, 231)


def png(path: Path, width: int, height: int, pixels: bytearray) -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    rows = bytearray()
    stride = width * 4
    for y in range(height):
        rows.append(0)
        rows.extend(pixels[y * stride : (y + 1) * stride])
    payload = b"\x89PNG\r\n\x1a\n"
    payload += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    payload += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    payload += chunk(b"IEND", b"")
    path.write_bytes(payload)


def canvas(width: int, height: int, color: tuple[int, int, int]) -> bytearray:
    return bytearray((*color, 255)) * (width * height)


def blend(buf: bytearray, width: int, height: int, x: int, y: int,
          color: tuple[int, int, int], alpha: float) -> None:
    if x < 0 or y < 0 or x >= width or y >= height or alpha <= 0:
        return
    i = (y * width + x) * 4
    a = max(0.0, min(1.0, alpha))
    ia = 1.0 - a
    buf[i] = round(buf[i] * ia + color[0] * a)
    buf[i + 1] = round(buf[i + 1] * ia + color[1] * a)
    buf[i + 2] = round(buf[i + 2] * ia + color[2] * a)


def soft_dot(buf: bytearray, width: int, height: int, cx: float, cy: float,
             radius: float, color: tuple[int, int, int], opacity: float) -> None:
    x0, x1 = max(0, int(cx - radius - 1)), min(width, int(cx + radius + 2))
    y0, y1 = max(0, int(cy - radius - 1)), min(height, int(cy + radius + 2))
    for y in range(y0, y1):
        for x in range(x0, x1):
            d = math.hypot(x - cx, y - cy)
            coverage = min(1.0, max(0.0, radius + 0.8 - d))
            blend(buf, width, height, x, y, color, opacity * coverage)


def stroke(buf: bytearray, width: int, height: int, points: list[tuple[float, float]],
           color: tuple[int, int, int], opacity: float, thickness: float) -> None:
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        distance = math.hypot(x1 - x0, y1 - y0)
        steps = max(1, int(distance / max(0.7, thickness * 0.35)))
        for step in range(steps + 1):
            t = step / steps
            soft_dot(buf, width, height, x0 + (x1 - x0) * t,
                     y0 + (y1 - y0) * t, thickness / 2, color, opacity)


def ellipse_points(cx: float, cy: float, rx: float, ry: float,
                   rotation: float = 0.0, start: float = 0.0,
                   end: float = math.tau, count: int = 220) -> list[tuple[float, float]]:
    cos_r, sin_r = math.cos(rotation), math.sin(rotation)
    result = []
    for i in range(count + 1):
        t = start + (end - start) * i / count
        x, y = rx * math.cos(t), ry * math.sin(t)
        result.append((cx + x * cos_r - y * sin_r, cy + x * sin_r + y * cos_r))
    return result


def bezier(p0: tuple[float, float], p1: tuple[float, float],
           p2: tuple[float, float], p3: tuple[float, float],
           count: int = 100) -> list[tuple[float, float]]:
    points = []
    for i in range(count + 1):
        t = i / count
        u = 1 - t
        points.append((
            u ** 3 * p0[0] + 3 * u * u * t * p1[0]
            + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1]
            + 3 * u * t * t * p2[1] + t ** 3 * p3[1],
        ))
    return points


def curve_chain(segments: list[tuple[tuple[float, float], ...]]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for segment in segments:
        part = bezier(*segment)
        points.extend(part if not points else part[1:])
    return points


def filled_ellipse(buf: bytearray, width: int, height: int, cx: float, cy: float,
                   rx: float, ry: float, rotation: float,
                   color: tuple[int, int, int], opacity: float = 1.0) -> None:
    bound = math.ceil(max(rx, ry)) + 2
    cos_r, sin_r = math.cos(rotation), math.sin(rotation)
    for y in range(max(0, int(cy - bound)), min(height, int(cy + bound + 1))):
        for x in range(max(0, int(cx - bound)), min(width, int(cx + bound + 1))):
            dx, dy = x - cx, y - cy
            local_x = dx * cos_r + dy * sin_r
            local_y = -dx * sin_r + dy * cos_r
            distance = (local_x / rx) ** 2 + (local_y / ry) ** 2
            coverage = max(0.0, min(1.0, (1.04 - distance) * 12))
            blend(buf, width, height, x, y, color, opacity * coverage)


def make_background() -> None:
    """Render flat, seam-safe editorial linework around a quiet center."""
    width, height = 1586, 992
    buf = canvas(width, height, DEEP)

    # Top-right iris ribbon.
    top_ribbon = curve_chain([
        ((1030, 48), (1050, 145), (1165, 78), (1250, 88)),
        ((1250, 88), (1335, 98), (1300, 184), (1390, 157)),
        ((1390, 157), (1460, 136), (1492, 72), (1540, 110)),
    ])
    stroke(buf, width, height, top_ribbon, IRIS, 1.0, 11)

    # Right-side triangle and ring pairing.
    stroke(buf, width, height,
           ellipse_points(1390, 348, 78, 78, count=180), GOLD, 1.0, 9)
    triangle = [(1400, 238), (1532, 328), (1398, 410), (1400, 238)]
    stroke(buf, width, height, triangle, LOVE, 1.0, 9)

    # Lower-left pine loop and small foam cross.
    pine_loop = curve_chain([
        ((42, 610), (120, 700), (250, 678), (292, 622)),
        ((292, 622), (338, 560), (184, 548), (205, 672)),
        ((205, 672), (222, 772), (385, 790), (400, 910)),
    ])
    stroke(buf, width, height, pine_loop, PINE, 1.0, 10)
    stroke(buf, width, height, [(92, 786), (180, 914)], FOAM, 1.0, 10)
    stroke(buf, width, height, [(64, 894), (203, 822)], FOAM, 1.0, 10)

    # Lower-right rose ribbon.
    lower_ribbon = curve_chain([
        ((1160, 922), (1120, 820), (1205, 770), (1305, 794)),
        ((1305, 794), (1410, 820), (1390, 690), (1460, 708)),
        ((1460, 708), (1515, 722), (1510, 792), (1542, 826)),
    ])
    stroke(buf, width, height, lower_ribbon, ROSE, 1.0, 11)

    # A small iris echo balances the lower composition without entering the UI.
    echo = curve_chain([
        ((1032, 850), (1000, 902), (1092, 918), (1108, 874)),
        ((1108, 874), (1128, 824), (1164, 900), (1212, 914)),
    ])
    stroke(buf, width, height, echo, IRIS, 0.78, 7)

    # Assert a pristine border so larger windows blend into ntp_background.
    border = 24
    for y in range(height):
        for x in range(width):
            if x < border or x >= width - border or y < border or y >= height - border:
                i = (y * width + x) * 4
                buf[i:i + 4] = bytes((*DEEP, 255))

    png(OUT / "new-tab-background.png", width, height, buf)


def make_icon(size: int) -> None:
    """A two-petal mark that remains legible at Chrome's smallest icon size."""
    buf = canvas(size, size, BASE)
    cx, cy = size / 2, size / 2
    soft_dot(buf, size, size, cx, cy, size * .43, OVERLAY, 1.0)
    filled_ellipse(buf, size, size, cx - size * .09, cy - size * .03,
                   size * .15, size * .28, -0.52, LOVE)
    filled_ellipse(buf, size, size, cx + size * .09, cy - size * .03,
                   size * .15, size * .28, 0.52, IRIS)
    soft_dot(buf, size, size, cx, cy + size * .12, max(1.2, size * .055), GOLD, 1.0)
    png(OUT / f"icon-{size}.png", size, size, buf)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    make_background()
    for size in (16, 32, 48, 128):
        make_icon(size)
    print(f"Generated seam-safe background and icon assets in {OUT}")


if __name__ == "__main__":
    main()
