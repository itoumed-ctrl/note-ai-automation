#!/usr/bin/env python3
"""news-05 eyecatch: Astra style — illustration full-bleed, compact white card
with green chip + headline overlaid. 1280x670. LOCAL ONLY."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 670
GREEN = (84, 150, 100)      # green for soudanshitsu
INK = (51, 58, 64)          # #333A40
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

TITLE = "職場でAIを使うと批判される。僕の3つの考え方"
CHIP_TEXT = "AI初心者の悩み相談室 第11回"
ILL = "assets/consult-11-illust.png"

# ---- full-bleed illustration (cover crop) ----
ill = Image.open(ILL).convert("RGB")
scale = max(W / ill.width, H / ill.height)
ill = ill.resize((int(ill.width * scale) + 1, int(ill.height * scale) + 1), Image.LANCZOS)
x = (ill.width - W) // 2
y = (ill.height - H) // 2
canvas = ill.crop((x, y, x + W, y + H))
d = ImageDraw.Draw(canvas)

# ---- compact white card, upper-left ----
CARD_X, CARD_Y = 48, 48
CARD_W = 660
PAD = 30
d_temp = ImageDraw.Draw(Image.new("RGB", (10, 10)))

chip_font = ImageFont.truetype(BOLD, 26, index=0)
chip_tw = int(d_temp.textlength(CHIP_TEXT, font=chip_font))
chip_w, chip_h = chip_tw + 22 * 2, 26 + 10 * 2

inner_w = CARD_W - PAD * 2

def wrap(font):
    lines, cur = [], ""
    for ch in TITLE:
        if cur == "" and ch in "。、" and lines:
            lines[-1] += ch
        elif d_temp.textlength(cur + ch, font=font) <= inner_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines

size, lines = None, None
for s in range(40, 27, -1):
    f = ImageFont.truetype(BOLD, s, index=0)
    ls = wrap(f)
    if len(ls) <= 3:
        size, lines = s, ls
        break
assert lines, "title does not fit"
font = ImageFont.truetype(BOLD, size, index=0)
lh = int(size * 1.35)
card_h = PAD + chip_h + 16 + lh * len(lines) + PAD

d.rounded_rectangle([CARD_X, CARD_Y, CARD_X + CARD_W, CARD_Y + card_h], radius=18, fill="white")
d.rounded_rectangle([CARD_X + PAD, CARD_Y + PAD, CARD_X + PAD + chip_w, CARD_Y + PAD + chip_h],
                    radius=9, fill=GREEN)
d.text((CARD_X + PAD + 22, CARD_Y + PAD + 10), CHIP_TEXT, font=chip_font, fill="white")
ty = CARD_Y + PAD + chip_h + 16
for k, line in enumerate(lines):
    d.text((CARD_X + PAD, ty + k * lh), line, font=font, fill=INK)
print(f"headline size {size}, {len(lines)} lines, card_h {card_h}")

canvas.save("consult-11-eyecatch-1280x670.png")
print("saved consult-11-eyecatch-1280x670.png", canvas.size)
