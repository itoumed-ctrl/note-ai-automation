#!/usr/bin/env python3
"""note運営ダッシュボード生成スクリプト（標準ライブラリのみ）。

台帳ディレクトリのJSONを読み取り専用で読み、単一HTMLを出力する。
数字は台帳の実測値のみ。無い値は「未記録」「—」と表示する。

使い方:
  python3 dashboard/build_dashboard.py --data-dir <台帳ディレクトリ> --out dashboard/index.html
"""
import argparse
import json
from datetime import datetime
from html import escape
from pathlib import Path

NA = "—"
UNRECORDED = "未記録"
SERIES_ORDER = ["実録", "相談室", "ニュース", "有料"]


def load(data_dir, name):
    """JSONを読む。無い・壊れている場合は {} を返し、警告を集める。"""
    p = Path(data_dir) / name
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except FileNotFoundError:
        WARNINGS.append(f"{name} が見つかりません")
    except (OSError, json.JSONDecodeError) as e:
        WARNINGS.append(f"{name} を読めません（{type(e).__name__}）")
    return {}


WARNINGS = []


def e(v):
    return escape(str(v), quote=True)


def link(url, label):
    """http(s)のURLだけリンク化。新しいタブで開く。"""
    if isinstance(url, str) and url.startswith(("http://", "https://")):
        return f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}</a>'
    return NA


def series_group(series, paid=False):
    """表記ゆれ（consult / 相談室 第9回 / 実録（有料） 等）を4分類に寄せる。"""
    s = str(series or "")
    if paid or s == "paid" or "有料" in s:
        return "有料"
    if s.startswith("consult") or "相談室" in s:
        return "相談室"
    if s.startswith("news") or "ニュース" in s:
        return "ニュース"
    if s.startswith(("free", "実録")) or "実録" in s:
        return "実録"
    return "その他"


def slot_rank(slot):
    s = str(slot or "")
    for i, k in enumerate(["朝", "昼", "午後", "夜"]):
        if k in s:
            return i
    return 9


def short(text, n=70):
    t = " ".join(str(text or "").split())
    return t if len(t) <= n else t[:n] + "…"


def card(label, value, note=""):
    n = f'<div class="note">{e(note)}</div>' if note else ""
    return f'<div class="card"><div class="label">{e(label)}</div><div class="value">{e(value)}</div>{n}</div>'


def table(headers, rows, empty="該当なし"):
    if not rows:
        return f'<p class="empty">{e(empty)}</p>'
    th = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def build(data_dir):
    stock_d = load(data_dir, "draft-stock.json")
    sched_d = load(data_dir, "publish-schedule.json")
    pend = load(data_dir, "note-morning-pending.json")
    state = load(data_dir, "note-morning-state.json")
    xs = load(data_dir, "x-public-stats.json")

    stock = [s for s in stock_d.get("stock", []) if isinstance(s, dict)]
    entries = [x for x in sched_d.get("entries", []) if isinstance(x, dict)]
    now = datetime.now().astimezone()
    today = now.strftime("%Y-%m-%d")

    published_n = stock_d.get("published")
    in_stock = [s for s in stock if s.get("status") == "stock"]
    published_entries = [x for x in entries if x.get("status") == "published"]
    upcoming = [x for x in entries if x.get("status") != "published"]

    checked = pend.get("checked_at") or state.get("last_checked") or UNRECORDED
    profile = pend.get("profile") if isinstance(pend.get("profile"), dict) else {}
    sales = next((profile[k] for k in ("sales", "revenue", "paid_sales") if k in profile), None)

    # --- KPI
    kpis = [
        card("公開本数", f"{published_n}本" if isinstance(published_n, int) else UNRECORDED, "draft-stock.json の published"),
        card("下書き在庫数", f"{len(in_stock)}本", "status=stock の件数"),
        card("有料記事の売上", f"{sales}円" if sales is not None else UNRECORDED, "台帳に売上の記録がありません" if sales is None else "pending の profile より"),
    ]
    if isinstance(profile.get("followers"), int):
        kpis.append(card("noteフォロワー", f'{profile["followers"]}人', f'pending の profile（確認 {str(pend.get("checked_at", UNRECORDED))[:10]}時点）'))
    x_fol = xs.get("followers")
    kpis.append(card("Xフォロワー", f"{x_fol}人" if isinstance(x_fol, int) else UNRECORDED,
                     f'最終取得 {str(xs.get("checked_at", UNRECORDED))[:10]}。直近の確認は403で失敗（値は更新されていません）' if xs else ""))

    # --- series summary
    summ = {g: [0, 0] for g in SERIES_ORDER}
    for s in in_stock:
        g = series_group(s.get("series"), s.get("paid") is True)
        summ.setdefault(g, [0, 0])[0] += 1
    for x in published_entries:
        g = series_group(x.get("series"))
        summ.setdefault(g, [0, 0])[1] += 1
    series_rows = [[e(g), f"{a}", f"{b}"] for g, (a, b) in summ.items() if g in SERIES_ORDER or a or b]
    series_note = (f"公開済みは publish-schedule の published 件数（{len(published_entries)}件）の集計です。"
                   f"公開本数 {published_n if isinstance(published_n, int) else UNRECORDED} とは数え方が異なります"
                   "（予定表に載らない公開があるため）。")

    # --- stock table
    stock_rows = []
    for s in stock:
        paid = s.get("paid") is True
        edit = s.get("edit_url") or s.get("draft_edit_url") or s.get("url")
        memo = s.get("notes_append") or s.get("note")
        stock_rows.append([
            e(s.get("title") or UNRECORDED),
            e(series_group(s.get("series"), paid)),
            '<span class="badge">有料</span>' if paid else NA,
            e(s.get("status") or UNRECORDED),
            link(s.get("pr"), "PR"),
            link(edit, "編集"),
            e(short(memo)) if memo else NA,
        ])

    # --- history
    published_entries.sort(key=lambda x: (str(x.get("date", "")), slot_rank(x.get("slot")), str(x.get("published_at", ""))), reverse=True)
    hist_rows = [[e(x.get("date") or NA), e(x.get("slot") or NA), e(x.get("title") or UNRECORDED),
                  link(x.get("published_url") or x.get("public_url"), "記事を開く")] for x in published_entries[:15]]

    # --- upcoming
    up_rows = []
    for x in sorted(upcoming, key=lambda x: (str(x.get("date", "")), slot_rank(x.get("slot")))):
        st = x.get("status")
        label = st if st else ("日付超過・ステータス未記録" if str(x.get("date", "")) < today else UNRECORDED)
        up_rows.append([e(x.get("date") or NA), e(x.get("slot") or NA), e(x.get("series") or NA),
                        e(x.get("title") or UNRECORDED), e(label), link(x.get("draft_edit_url"), "編集")])

    # --- carryover
    co = pend.get("carryover_next_run")
    co_items = []
    if isinstance(co, dict):
        for k, v in co.items():
            co_items.append((k, len(v) if isinstance(v, (list, dict)) else v))
    elif isinstance(co, list):
        co_items.append(("合計", len(co)))
    crd = pend.get("comment_reply_drafts")
    crd_n = len(crd) if isinstance(crd, (list, dict)) else None
    labels = {"follows": "フォロー", "likes": "スキ"}
    co_html = "".join(card(f"持ち越し: {labels.get(k, k)}", f"{n}件") for k, n in co_items) or \
        f'<p class="empty">持ち越しは{UNRECORDED}です</p>'
    co_html += card("コメント返信の下書き", f"{crd_n}件" if crd_n is not None else UNRECORDED)
    reply_rows = []
    for c in (crd if isinstance(crd, list) else []):
        if isinstance(c, dict):
            reply_rows.append([e(c.get("commenter") or NA), e(c.get("article_title") or NA),
                               e(c.get("comment_at") or NA), link(c.get("article_url"), "記事を開く")])

    warn = "".join(f'<p class="warn">⚠ {e(w)}</p>' for w in WARNINGS)
    css = """
*{box-sizing:border-box}body{margin:0;background:#f5f7fa;color:#1f2933;font:15px/1.7 -apple-system,"Hiragino Sans","Noto Sans JP","Yu Gothic",sans-serif}
header{background:#1b2a4a;color:#fff;padding:20px 16px}header h1{margin:0 0 4px;font-size:22px}header p{margin:0;font-size:13px;color:#cfd8e8}
main{max-width:1000px;margin:0 auto;padding:16px}section{background:#fff;border:1px solid #e1e6ee;border-radius:10px;padding:16px;margin-bottom:16px}
h2{margin:0 0 12px;font-size:17px;color:#1b2a4a;border-left:4px solid #1b2a4a;padding-left:8px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.card{border:1px solid #e1e6ee;border-radius:8px;padding:12px;background:#fafbfd}.label{font-size:12px;color:#5b6778}
.value{font-size:24px;font-weight:700;color:#1b2a4a}.note{font-size:11px;color:#7a8596;margin-top:2px}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:7px 8px;border-bottom:1px solid #e8ecf2;text-align:left;vertical-align:top}
th{background:#eef2f8;color:#1b2a4a;white-space:nowrap}a{color:#1b4fa0}.badge{background:#1b2a4a;color:#fff;border-radius:10px;padding:1px 8px;font-size:11px}
.empty,.small{color:#5b6778;font-size:13px}.warn{color:#9a3412;background:#fff7ed;padding:6px 10px;border-radius:6px}
@media(max-width:600px){main{padding:10px}.value{font-size:20px}}
"""
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>note運営ダッシュボード</title><style>{css}</style></head><body>
<header><h1>note運営ダッシュボード</h1>
<p>生成日時: {e(now.strftime("%Y-%m-%d %H:%M"))} ／ データの最終確認: {e(checked)}</p></header>
<main>{warn}
<section><h2>KPI</h2><div class="cards">{"".join(kpis)}</div></section>
<section><h2>シリーズ別サマリ</h2>{table(["シリーズ", "在庫件数", "公開済み件数"], series_rows)}<p class="small">{e(series_note)}</p></section>
<section><h2>下書き在庫</h2>{table(["タイトル", "シリーズ", "有料", "ステータス", "PR", "編集", "備考"], stock_rows, "在庫の記録がありません")}</section>
<section><h2>公開履歴（新しい順・最大15件）</h2>{table(["日付", "スロット", "タイトル", "公開URL"], hist_rows, "公開済みの記録がありません")}</section>
<section><h2>公開予定</h2>{table(["日付", "スロット", "シリーズ", "タイトル", "状態", "編集"], up_rows, "公開予定はありません")}</section>
<section><h2>持ち越し・要注意</h2><div class="cards">{co_html}</div>{table(["コメント者", "記事", "日時", "リンク"], reply_rows, "返信待ちのコメントはありません") if reply_rows else ""}</section>
</main></body></html>
"""


def main():
    ap = argparse.ArgumentParser(description="note運営ダッシュボードを生成する")
    ap.add_argument("--data-dir", required=True, help="台帳ディレクトリ（読み取り専用）")
    ap.add_argument("--out", default="dashboard/index.html")
    a = ap.parse_args()
    html = build(a.data_dir)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"生成しました: {out}（警告 {len(WARNINGS)} 件）")


if __name__ == "__main__":
    main()
