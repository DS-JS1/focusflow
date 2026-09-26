"""Build the GitHub Pages site from focusflow.html.

focusflow.html is the single source. It has no <html>/<head> wrapper because the
claude.ai artifact host adds one. This script adds that wrapper plus the
install/offline bits (manifest, service worker, icons) and writes index.html.

Run:  python build.py
"""
import math, re, struct, zlib
from pathlib import Path

HERE = Path(__file__).parent
SRC = (HERE / "focusflow.html").read_text(encoding="utf-8")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icon-180.png">
<meta name="apple-mobile-web-app-title" content="Focus Flow">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
</head>
<body>
"""
TAIL = """
<script>
if('serviceWorker' in navigator){
  // Check for a new version on launch and whenever the app comes back to the foreground.
  let hadController=!!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener('controllerchange',()=>{if(hadController&&window.ffUpdateReady)window.ffUpdateReady();hadController=true});
  addEventListener('load',()=>navigator.serviceWorker.register('sw.js',{updateViaCache:'none'}).then(reg=>{
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)reg.update().catch(()=>{})});
  }).catch(()=>{}));
}
</script>
</body>
</html>
"""

# ---- icons: dark tile with the progress ring ----
BG = (11, 16, 38)
C1, C2 = (62, 224, 255), (139, 123, 255)
TRACK = (40, 50, 95)


def icon_pixels(n):
    cx = cy = n / 2
    r, half = n * 0.30, n * 0.055
    sweep = 300  # degrees of ring drawn, clockwise from 12 o'clock
    end = math.radians(sweep - 90)
    kx, ky, kr = cx + r * math.cos(end), cy + r * math.sin(end), n * 0.075
    rows = []
    for y in range(n):
        row = bytearray()
        for x in range(n):
            px, py = x + 0.5, y + 0.5
            col = BG
            d = math.hypot(px - cx, py - cy)
            cov = max(0.0, min(1.0, half - abs(d - r) + 0.5))
            if cov:
                ang = (math.degrees(math.atan2(py - cy, px - cx)) + 90) % 360
                if ang <= sweep:
                    t = ang / sweep
                    ring = tuple(int(a + (b - a) * t) for a, b in zip(C1, C2))
                else:
                    ring = TRACK
                col = tuple(int(c + (rc - c) * cov) for c, rc in zip(col, ring))
            kcov = max(0.0, min(1.0, kr - math.hypot(px - kx, py - ky) + 0.5))
            if kcov:
                col = tuple(int(c + (255 - c) * kcov) for c in col)
            row += bytes(col)
        rows.append(row)
    return rows


def write_png(path, n):
    rows = icon_pixels(n)
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    path.write_bytes(png)


if __name__ == "__main__":
    (HERE / "index.html").write_text(HEAD + SRC + TAIL, encoding="utf-8")
    for n in (180, 192, 512):
        p = HERE / f"icon-{n}.png"
        if not p.exists():
            write_png(p, n)
    # bump the service-worker cache name so phones pick up the new version
    sw = HERE / "sw.js"
    text = sw.read_text(encoding="utf-8")
    m = re.search(r"focusflow-v(\d+)", text)
    sw.write_text(text.replace(m.group(0), f"focusflow-v{int(m.group(1)) + 1}"), encoding="utf-8")
    print("Built index.html")
