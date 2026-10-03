"""キリン ビバ！ドリームキャンペーンの対象バーコード一覧を取得し、index.html に埋め込む。

使い方:  python update_list.py
"""
import html
import json
import re
import urllib.request
from datetime import date
from pathlib import Path

URL = "https://www.kirin.co.jp/campaign/beverage/viva/barcode/"
HERE = Path(__file__).parent
TARGET = HERE / "index.html"

req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
src = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
src = re.sub(r"<!--.*?-->", "", src, flags=re.S)  # コメントアウトされた旧一覧を除外

items = {}
for code, name in re.findall(r"<dt>\s*(\d{8,14})\s*</dt>\s*<dd>(.*?)</dd>", src, re.S):
    name = re.sub(r"<[^>]+>", "", html.unescape(name)).strip()
    items.setdefault(code, name)

if len(items) < 50:
    raise SystemExit(f"取得件数が少なすぎます（{len(items)}件）。ページ構成が変わった可能性があります。")

data = json.dumps(
    {"updated": date.today().isoformat(), "source": URL, "items": items},
    ensure_ascii=False,
    indent=0,
)
page = TARGET.read_text(encoding="utf-8")
page, n = re.subn(
    r"(/\*LIST-BEGIN\*/).*?(/\*LIST-END\*/)",
    lambda m: m.group(1) + data + m.group(2),
    page,
    flags=re.S,
)
if n != 1:
    raise SystemExit("index.html に埋め込み位置（LIST-BEGIN/END）が見つかりません。")
TARGET.write_text(page, encoding="utf-8")
print(f"{len(items)} 件を埋め込みました → {TARGET.name}")
