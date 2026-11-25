# consult-14 図版・アイキャッチ生成（PIL、ローカルのみ）
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

R = '/home/hatch/workspace/note-ai-automation/'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def f(path, size):
    return ImageFont.truetype(path, size)

GREEN = (84, 150, 100)       # #549664
DARK = (43, 94, 58)          # 濃緑shade
CHAR = (51, 58, 64)
SLATE = (110, 119, 128)
PALE = (238, 242, 239)       # #EEF2EF
BG = (252, 253, 250)

# ---------- 図1: 頼み方の例（例文カード） ----------
W, H = 1280, 560
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.text((50, 28), 'Claudeへの頼み方の例（汎用の形）', font=f(BOLD, 40), fill=CHAR)
d.rounded_rectangle([50, 96, 1230, 420], radius=18, fill=(255, 255, 255), outline=GREEN, width=3)
lines = [
    '○歳向けに、宇宙旅行の話を短く作ってください。',
    '・読んで2〜3分くらいの長さで',
    '・怖くなくて、びっくりさせる場面は入れないで',
    '・最後は静かに眠る、穏やかな終わり方で',
]
y = 126
for i, line in enumerate(lines):
    d.text((84, y), line, font=f(BOLD if i == 0 else REG, 33 if i == 0 else 31), fill=DARK if i == 0 else CHAR)
    y += 62 if i == 0 else 56
d.text((84, y + 6), '※ テーマの部分だけ差し替えれば、ほかの話にも使えます', font=f(REG, 26), fill=SLATE)
d.text((50, H - 62), 'ポイントは「長さ」と「終わり方」を先に指定すること。避けたい展開も添えます', font=f(REG, 25), fill=SLATE)
img.save(R + 'consult-14-figure-prompt.png')

# ---------- 図2: 工夫3つ ----------
W, H = 1280, 470
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.text((50, 28), '寝かしつけの話づくり、工夫3つ', font=f(BOLD, 40), fill=CHAR)
points = [
    ('工夫1', 'テーマは今の興味から', '昼間の様子から拾う\n（例：宇宙旅行）'),
    ('工夫2', '頼み方は短く具体的に', '長さと終わり方を指定\n怖い展開は避ける'),
    ('工夫3', '読むのは親の声', 'AIは話づくりだけ\n読み聞かせは親の時間'),
]
bw, bh, gap, x0, y0 = 384, 250, 34, 44, 110
for i, (tag, t, s) in enumerate(points):
    x = x0 + i * (bw + gap)
    d.rounded_rectangle([x, y0, x + bw, y0 + bh], radius=18, fill=(240, 246, 240), outline=GREEN, width=3)
    d.rounded_rectangle([x + 24, y0 + 24, x + 130, y0 + 72], radius=24, fill=GREEN)
    d.text((x + 42, y0 + 33), tag, font=f(BOLD, 27), fill=(255, 255, 255))
    d.text((x + 24, y0 + 96), t, font=f(BOLD, 31), fill=DARK)
    for j, line in enumerate(s.split('\n')):
        d.text((x + 24, y0 + 152 + j * 42), line, font=f(REG, 26), fill=CHAR)
d.text((50, H - 58), '話は作ってもらう。読むのは自分。線引きは相談室第9回と同じです', font=f(REG, 25), fill=SLATE)
img.save(R + 'consult-14-figure-points.png')

# ---------- アイキャッチ（分割レイアウト） ----------
W, H = 1280, 670
canvas = Image.new('RGB', (W, H), PALE)
ill = Image.open(R + 'assets/consult-14-illust.png').convert('RGB')
crop_w = int(ill.height * (640 / H))
left = ill.width - crop_w
ill = ill.crop((left, 0, ill.width, ill.height)).resize((640, H))
ill = ImageEnhance.Color(ill).enhance(0.95)
canvas.paste(ill, (640, 0))
d = ImageDraw.Draw(canvas)
d.rounded_rectangle([56, 64, 452, 118], radius=27, fill=GREEN)
d.text((76, 76), 'AI初心者の悩み相談室 第14回', font=f(BOLD, 25), fill=(255, 255, 255))
d.text((56, 196), '寝かしつけの話、', font=f(BOLD, 72), fill=DARK)
d.text((56, 292), 'Claudeと作る', font=f(BOLD, 80), fill=DARK)
d.rectangle([58, 420, 238, 432], fill=GREEN)
d.text((56, 462), 'パパの工夫3つ', font=f(BOLD, 34), fill=CHAR)
d.text((56, 516), 'テーマは今の興味から、読むのは親の声', font=f(REG, 28), fill=SLATE)
canvas.save(R + 'consult-14-eyecatch-1280x670.png')
print('done')
