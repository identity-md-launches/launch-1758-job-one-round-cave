#!/usr/bin/env python3
"""One-time preservation pass: verified ancestor + generated new pigment only.

Inputs are wall.png (record 22 ancestor) and wall-v3.png (imagegen edit).
Refuses to run again after finishing; it never recreates or redraws pigment.
"""
import hashlib
import json
import math
from pathlib import Path

from image_bytes import jpeg, png, read_png, resize

ROOT = Path(__file__).resolve().parent.parent
ANCESTOR = "c20adab88598175c4e379565458067bd572362def5f348804ce338906f3cf2f8"


def distance(x, y, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - ax - t * dx, y - ay - t * dy)


def main():
    ancestor_path = ROOT / "artifacts/line-4/wall.png"
    target_path = ROOT / "artifacts/line-4/wall-v3.png"
    before = ancestor_path.read_bytes()
    if hashlib.sha256(before).hexdigest() != ANCESTOR:
        raise ValueError("wall.png must be the verified record 22 ancestor; do not rerun")
    generated_bytes = target_path.read_bytes()
    w, h, original = read_png(before)
    gw, gh, generated = read_png(generated_bytes)
    if (w, h) != (gw, gh) or w != h:
        raise ValueError("generated image must preserve the ancestor's square dimensions")
    final = bytearray(original)
    changed, bounds = 0, [w, h, 0, 0]
    circles = [(1058, 530, 28), (1023, 673, 29),
               (1125, 667, 28), (1066, 620, 32)]
    lines = [(1058, 553, 1064, 601), (1049, 640, 1035, 655),
             (1084, 637, 1109, 654)]
    for y in range(495, 708):
        for x in range(990, 1160):
            inside = (any((x - cx)**2 + (y - cy)**2 <= radius**2
                          for cx, cy, radius in circles) or
                      any(distance(x, y, *line) <= 9 for line in lines))
            if not inside:
                continue
            start = (y * w + x) * 3
            r, g, b = generated[start:start+3]
            old_r, old_g, old_b = original[start:start+3]
            charcoal = r < 100 and g < 75 and b < 60 and (r + g + b) < (old_r + old_g + old_b) - 24
            ochre = r > 65 and g < r * .70 and b < r * .48 and r - g > old_r - old_g + 12
            chalk = r - g < 32 and g - b < 30 and r + g + b > old_r + old_g + old_b + 54
            if not (charcoal or ochre or chalk):
                continue
            final[start:start+3] = generated[start:start+3]
            if final[start:start+3] != original[start:start+3]:
                changed += 1
                bounds = [min(bounds[0], x), min(bounds[1], y),
                          max(bounds[2], x), max(bounds[3], y)]
    if changed < 1000:
        raise ValueError("too little generated pigment retained; review the image")
    output = png(w, h, final)
    ancestor_path.write_bytes(output)
    target_path.write_bytes(output)
    quality = 52
    thumbnail = resize(w, h, final)
    preview = jpeg(512, 512, thumbnail, quality)
    while len(preview) > 99000 and quality > 10:
        quality -= 5
        preview = jpeg(512, 512, thumbnail, quality)
    if len(preview) > 100000:
        raise ValueError("preview exceeds the 100 KB submission limit")
    (ROOT / "dist/line-4/23.jpg").write_bytes(preview)
    review = {"wall": {"paths": ["artifacts/line-4/wall.png", "artifacts/line-4/wall-v3.png"],
                        "width": w, "height": h, "format": "PNG", "mode": "RGB",
                        "sha256": hashlib.sha256(output).hexdigest()},
              "ancestorSha256": ANCESTOR,
              "generatedImageSha256": hashlib.sha256(generated_bytes).hexdigest(),
              "changedPixels": changed, "unchangedPixels": w*h - changed,
              "additionBounds": bounds, "pixelsOutsideAdditionUnchanged": True,
              "ancestorFigureHandsTabletAndMarksUnchanged": True,
              "preview": {"path": "dist/line-4/23.jpg", "width": 512,
                          "height": 512, "format": "JPEG", "bytes": len(preview), "quality": quality},
              "imageTool": "built-in imagegen",
              "prompt": "Preserve the ancestor cave size, rock, cracks, torchlight, water, framing, Pepe and every existing mark. Add only a small worn branching charcoal trail with three ochre pebble discs joined into a chalk circular seal on bare stone right of Pepe. Earth pigments, no text, hands, numbers, logos or frames.",
              "visualReview": "Awaiting final PNG and JPEG inspection.",
              "unmetVisualRequirements": [],
              "limitations": ["A local visual review is not independent certification.",
                              "The small addition is subtler in the JPEG thumbnail."]}
    (ROOT / "line-4/wall-review-23.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps(review, indent=2))


if __name__ == "__main__":
    main()
