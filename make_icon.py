#!/usr/bin/env python3
"""Generate icon-512.png — brand system §6: eclipse motif on the navy
field (#0d1b2a), one per-product glyph. Zephyr's glyph is the west
wind: three sweeping streaks crossing the eclipse ring — movement
across an open horizon. PIL only; deterministic."""
from PIL import Image, ImageDraw

S = 512
NAVY = (13, 27, 42, 255)
STOPS = [(15, 246, 247), (0, 212, 255), (123, 44, 191)]  # cyan->blue->purple


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def grad(t):
    return lerp(STOPS[0], STOPS[1], t * 2) if t < 0.5 else \
        lerp(STOPS[1], STOPS[2], (t - 0.5) * 2)


def main():
    img = Image.new("RGBA", (S, S), NAVY)
    d = ImageDraw.Draw(img)
    # Eclipse ring, right of center — the horizon body the wind crosses.
    box = [238, 118, 438, 318]
    for i in range(72):
        t = i / 72
        d.arc(box, start=i * 5, end=i * 5 + 6, fill=grad(t), width=13)
    d.ellipse([280, 160, 396, 276], fill=NAVY)  # occluding body
    # Wind streaks: three long arcs sweeping left-to-right, tapering.
    streaks = [(150, 92, 470), (196, 58, 448), (344, 84, 474)]
    for j, (y, x0, x1) in enumerate(streaks):
        t = 0.15 + j * 0.3
        steps = 26
        for i in range(steps):
            f0, f1 = i / steps, (i + 1) / steps
            xa, xb = x0 + (x1 - x0) * f0, x0 + (x1 - x0) * f1
            ya = y + 26 * (f0 * f0)
            yb = y + 26 * (f1 * f1)
            w = max(3, int(13 * (1 - f0 * 0.75)))
            d.line([(xa, ya), (xb, yb)], fill=grad(t + f0 * 0.2), width=w)
        # curled head at the left end
        d.arc([x0 - 26, y - 14, x0 + 22, y + 30], start=300, end=110,
              fill=grad(t), width=8)
    img.save("icon-512.png")
    print("wrote icon-512.png", img.size, img.mode)


if __name__ == "__main__":
    main()
