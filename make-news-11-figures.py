# news-11 図版・アイキャッチ生成（PIL、ローカルのみ）
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

R = '/home/hatch/workspace/note-ai-automation/'
BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'

def f(path, size):
    return ImageFont.truetype(path, size)

ORANGE = (201, 122, 43)      # #C97A2B
DARK = (122, 62, 14)         # 濃いオレンジshade
CHAR = (51, 58, 64)
PALE = (247, 239, 227)       # #F7EFE3

# ---------- 図1: 流れ図 ----------
W, H = 1280, 430
img = Image.new('RGB', (W, H), (255, 253, 248))
d = ImageDraw.Draw(img)
d.text((50, 28), 'Install as app までの流れ', font=f(BOLD, 40), fill=CHAR)
steps = [
    ('1. 説明する', 'Claudeに作りたい\nアプリを伝える'),
    ('2. 試す', 'artifactとして\nまず使ってみる'),
    ('3. 入れる', '「Install as app」\nをクリック'),
    ('4. 開く', '独自アイコンから\n独自ウィンドウで'),
]
bw, bh, gap, x0, y0 = 272, 240, 34, 44, 110
for i, (t, s) in enumerate(steps):
    x = x0 + i * (bw + gap)
    d.rounded_rectangle([x, y0, x + bw, y0 + bh], radius=18, fill=(255, 244, 228) if i < 3 else (252, 231, 199), outline=ORANGE, width=3)
    d.text((x + 24, y0 + 26), t, font=f(BOLD, 34), fill=DARK)
    for j, line in enumerate(s.split('\n')):
        d.text((x + 24, y0 + 92 + j * 42), line, font=f(REG, 27), fill=CHAR)
    if i < 3:
        ax = x + bw + 4
        d.polygon([(ax, y0 + bh // 2 - 14), (ax, y0 + bh // 2 + 14), (ax + 26, y0 + bh // 2)], fill=ORANGE)
d.text((50, H - 58), 'パッケージ化・署名は不要。APIキーや別のログインも要りません（公式ブログより）', font=f(REG, 25), fill=(110, 119, 128))
img.save(R + 'news-11-figure-flow.png')

# ---------- 図2: 権限3段階 ----------
W, H = 1280, 620
img = Image.new('RGB', (W, H), (255, 253, 248))
d = ImageDraw.Draw(img)
d.text((50, 28), '権限の3段階（広がるほど慎重に）', font=f(BOLD, 40), fill=CHAR)
tiers = [
    ('Default', 'ブラウザでできる範囲のみ', (233, 240, 226), (84, 120, 70), 560),
    ('App permissions', '最前面ウィンドウ／ショートカット／通知など\nClaudeが厳密に制御できる機能を要求できる', (252, 231, 199), ORANGE, 800),
    ('Full computer access', 'プログラム実行、ファイルの読み取り・変更・削除を\n都度確認なしでできる', (248, 205, 170), (166, 62, 20), 1040),
]
y = 100
for name, desc, fillc, outc, wdt in tiers:
    d.rounded_rectangle([50, y, 50 + wdt, y + 140], radius=16, fill=fillc, outline=outc, width=3)
    d.text((74, y + 18), name, font=f(BOLD, 32), fill=DARK)
    for j, line in enumerate(desc.split('\n')):
        d.text((74, y + 66 + j * 34), line, font=f(REG, 24), fill=CHAR)
    y += 158
d.text((50, H - 52), '許可は現在のバージョンのみ有効。更新のたびに再確認されます（公式ブログより）', font=f(REG, 25), fill=(110, 119, 128))
img.save(R + 'news-11-figure-permissions.png')

# ---------- アイキャッチ（分割レイアウト） ----------
W, H = 1280, 670
canvas = Image.new('RGB', (W, H), PALE)
# 右: イラストのみ（白ブレンドなし・彩度0.95）
ill = Image.open(R + 'assets/news-11-illust.png').convert('RGB')
# 右半分に人物+PCが収まるよう、イラスト右寄りを切り出し
crop_w = int(ill.height * (640 / H))
left = ill.width - crop_w
ill = ill.crop((left, 0, ill.width, ill.height)).resize((640, H))
ill = ImageEnhance.Color(ill).enhance(0.95)
canvas.paste(ill, (640, 0))
# 左: 文字だけ
d = ImageDraw.Draw(canvas)
d.rounded_rectangle([56, 64, 430, 118], radius=27, fill=ORANGE)
d.text((76, 76), 'AIニュース勉強ノート 第11回', font=f(BOLD, 25), fill=(255, 255, 255))
d.text((56, 196), 'Claudeの作り物が', font=f(BOLD, 68), fill=DARK)
d.text((56, 292), 'アプリになる', font=f(BOLD, 80), fill=DARK)
d.rectangle([58, 420, 238, 432], fill=ORANGE)
d.text((56, 462), 'Install as app の学び3つ', font=f(BOLD, 34), fill=CHAR)
d.text((56, 516), '作る敷居と、権限の線引き', font=f(REG, 28), fill=(110, 119, 128))
canvas.save(R + 'news-11-eyecatch-1280x670.png')
print('done')
