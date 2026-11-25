# free-09 図版・アイキャッチ生成（PIL、ローカルのみ）
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

R = '/home/hatch/workspace/note-ai-automation/'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def f(path, size):
    return ImageFont.truetype(path, size)

BLUE = (47, 111, 219)        # #2F6FDB
NAVY = (30, 52, 86)          # #1E3456
CHAR = (51, 58, 64)
SLATE = (110, 119, 128)
PALE = (234, 240, 247)       # 左パネル用 淡色
BG = (251, 252, 254)
LIGHT = (226, 234, 246)

# ---------- 図1: ビフォーアフター ----------
W, H = 1280, 520
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.text((50, 28), '連絡帳1回にかかる時間', font=f(BOLD, 40), fill=CHAR)
# 以前
d.rounded_rectangle([50, 110, 1230, 250], radius=18, fill=(255, 255, 255), outline=SLATE, width=3)
d.text((84, 132), 'AIを使う前', font=f(BOLD, 32), fill=CHAR)
d.rounded_rectangle([84, 186, 84 + 830, 226], radius=20, fill=(176, 186, 200))
d.text((946, 128), '約10分', font=f(BOLD, 52), fill=CHAR)
# 今
d.rounded_rectangle([50, 280, 1230, 420], radius=18, fill=(255, 255, 255), outline=BLUE, width=3)
d.text((84, 302), '今', font=f(BOLD, 32), fill=NAVY)
d.rounded_rectangle([84, 356, 84 + 280, 396], radius=20, fill=BLUE)
d.text((940, 298), '2〜3分', font=f(BOLD, 52), fill=NAVY)
d.text((50, H - 56), '※ いずれも本人の体感です。ストップウォッチで測った数字ではありません', font=f(REG, 26), fill=SLATE)
img.save(R + 'free-09-figure-beforeafter.png')

# ---------- 図2: 手順3ステップ ----------
W, H = 1280, 470
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
d.text((50, 28), '連絡帳づくりの手順、3ステップ', font=f(BOLD, 40), fill=CHAR)
steps = [
    ('ステップ1', '事実をメモする', 'その日の事実だけを\n短いメモで書く'),
    ('ステップ2', 'AIに整えてもらう', 'メモを渡して\n文章の形に整える'),
    ('ステップ3', '自分で確認する', '読み直して確かめてから\n園のアプリに入力'),
]
bw, bh, gap, x0, y0 = 384, 250, 34, 44, 110
for i, (tag, t, s) in enumerate(steps):
    x = x0 + i * (bw + gap)
    d.rounded_rectangle([x, y0, x + bw, y0 + bh], radius=18, fill=LIGHT, outline=BLUE, width=3)
    d.rounded_rectangle([x + 24, y0 + 24, x + 168, y0 + 72], radius=24, fill=BLUE)
    d.text((x + 42, y0 + 33), tag, font=f(BOLD, 27), fill=(255, 255, 255))
    d.text((x + 24, y0 + 96), t, font=f(BOLD, 31), fill=NAVY)
    for j, line in enumerate(s.split('\n')):
        d.text((x + 24, y0 + 152 + j * 42), line, font=f(REG, 26), fill=CHAR)
    if i < 2:
        ax = x + bw + 4
        d.polygon([(ax, y0 + 112), (ax, y0 + 138), (ax + 26, y0 + 125)], fill=BLUE)
d.text((50, H - 58), 'メモには、子どもの名前など個人が分かる情報は入れません', font=f(REG, 25), fill=SLATE)
img.save(R + 'free-09-figure-steps.png')

# ---------- アイキャッチ（分割レイアウト） ----------
W, H = 1280, 670
canvas = Image.new('RGB', (W, H), PALE)
ill = Image.open(R + 'assets/free-09-illust.png').convert('RGB')
crop_w = int(ill.height * (640 / H))
left = ill.width - crop_w
ill = ill.crop((left, 0, ill.width, ill.height)).resize((640, H))
ill = ImageEnhance.Color(ill).enhance(0.95)
canvas.paste(ill, (640, 0))
d = ImageDraw.Draw(canvas)
d.rounded_rectangle([56, 64, 300, 118], radius=27, fill=BLUE)
d.text((76, 76), '家庭 × AI の実録', font=f(BOLD, 25), fill=(255, 255, 255))
d.text((56, 186), '連絡帳、', font=f(BOLD, 84), fill=NAVY)
d.text((56, 296), '10分→2〜3分', font=f(BOLD, 78), fill=NAVY)
d.rectangle([58, 424, 238, 436], fill=BLUE)
d.text((56, 466), '迷いの悪循環を止めた書き方', font=f(BOLD, 33), fill=CHAR)
d.text((56, 522), '保育園の連絡帳を、AIと書く毎朝の記録', font=f(REG, 27), fill=SLATE)
canvas.save(R + 'free-09-eyecatch-1280x670.png')
print('done')
