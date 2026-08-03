"""
generate_staff_pages.py
=======================
Excelファイルを読み込み、staff_template.html をもとに各教員のHTMLページを生成するスクリプト。

使い方:
    python generate_staff_pages.py \
        --excel   学科HP回収用_分野説明文__2_.xlsx \
        --template staff_template.html \
        --outdir  staffs/

生成ファイル名: staff_{名前(ローマ字・小文字・スペースなし)}.html
例) Sayaka Shiota → staff_shiotasayaka.html  (姓名逆順・小文字)
"""

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# ユーティリティ
# ---------------------------------------------------------------------------

def normalize_str(s: str) -> str:
    """文字列を None / NaN 安全に文字列へ変換し、前後の空白を除去する。"""
    if pd.isna(s):
        return ""
    return str(s).strip()


def make_filename(name_en: str) -> str:
    """
    英語氏名からファイル名を生成する。
    "Sayaka Shiota" → "staff_shiotasayaka.html"  (姓 + 名、小文字、スペース除去)
    姓名が判別できない場合はそのまま小文字・スペース除去。
    """
    name_en = normalize_str(name_en)
    # NFKC正規化（全角→半角など）
    name_en = unicodedata.normalize("NFKC", name_en)
    parts = name_en.split()
    if len(parts) >= 2:
        # 姓（最後のパーツ）+ 名（残り）の順に結合
        surname = parts[-1].lower()
        given   = "".join(p.lower() for p in parts[:-1])
        slug = surname + given
    else:
        slug = name_en.lower().replace(" ", "")
    # 英数字以外を除去
    slug = re.sub(r"[^a-z0-9]", "", slug)
    return f"staff_{slug}.html"


def extract_url(raw: str, prefer: str = "ja") -> str:
    """
    URL フィールドを解析して最初の有効な URL を返す。
    - 複数 URL が改行で区切られている場合、prefer="ja" なら（日）を優先
    - 「なし」「NaN」の場合は空文字を返す
    - URL っぽくない文字列（「学科パンフレット…」など）も空文字として扱う
    """
    raw = normalize_str(raw)
    if not raw or raw in ("nan", "なし", "NaN"):
        return ""
    # URLを含まない行をスキップ
    if "http" not in raw:
        return ""

    lines = [l.strip() for l in raw.splitlines() if "http" in l]
    if not lines:
        return ""

    # （日）or (日) タグ付きがあれば優先して返す（日本語ページ用）
    for line in lines:
        if "（日）" in line or "(日)" in line:
            url = re.search(r"https?://\S+", line)
            if url:
                return url.group(0).rstrip("　 ")  # 全角スペース対策
    # なければ最初の URL
    url = re.search(r"https?://\S+", lines[0])
    return url.group(0).rstrip("　 ") if url else ""


def build_url_buttons(personal_url: str, lab_url: str) -> str:
    """個人・研究室 URL のボタン HTML を組み立てる。URL がない場合はボタンを出力しない。"""
    buttons = []
    if personal_url:
        buttons.append(
            f'<li><a href="{personal_url}"><span class="btn_bg_green">個人website</span></a></li>'
        )
    if lab_url:
        buttons.append(
            f'<li><a href="{lab_url}"><span class="btn_bg_green">研究室website</span></a></li>'
        )
    if not buttons:
        return ""
    return '<ul class="list_il">\n' + "\n".join(buttons) + "\n</ul>"


def make_photo_filename(name_en: str) -> str:
    """写真ファイル名を生成する（HTMLファイル名と同じスラグを使用）。"""
    html_name = make_filename(name_en)          # staff_shiotasayaka.html
    slug = html_name[len("staff_"):-len(".html")]  # shiotasayaka
    return f"photo_{slug}.jpg"


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def load_staff_data(excel_path: str) -> pd.DataFrame:
    """
    Excel の Sheet1 を読み込み、教員行のみ抽出して返す。
    グループヘッダー行（職位が教授/准教授/助教でない行）は除外する。
    """
    df = pd.read_excel(excel_path, sheet_name="現学科メンバー", header=0)
    df.columns = [
        "職位", "氏名", "氏名_en",
        "分野名_ja", "分野名_en",
        "説明_ja", "説明_en",
        "メッセージ_ja",
        "個人URL", "研究室URL",
        "写真更新", "写真URL",
    ]
    valid_positions = {"教授", "准教授", "助教"}
    staff = df[
        df["職位"].notna() &
        df["職位"].str.strip().isin(valid_positions)
    ].copy()
    staff = staff.reset_index(drop=True)
    return staff


def generate_pages(
    excel_path: str,
    template_path: str,
    outdir: str,
) -> None:
    template = Path(template_path).read_text(encoding="utf-8")
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    staff = load_staff_data(excel_path)
    skipped = []

    for _, row in staff.iterrows():
        name_ja    = normalize_str(row["氏名"])
        name_en    = normalize_str(row["氏名_en"])
        position   = normalize_str(row["職位"])
        keywords   = normalize_str(row["分野名_ja"])
        desc_ja    = normalize_str(row["説明_ja"])
        message_ja = normalize_str(row["メッセージ_ja"])

        # 必須フィールドが空の場合はスキップ（ログに記録）
        if not name_ja or not name_en:
            skipped.append(f"[SKIP] 氏名不明: {row.to_dict()}")
            continue
        if not desc_ja:
            print(f"[WARN] 説明文(日本語)が空です: {name_ja}")
        if not message_ja:
            print(f"[WARN] メッセージが空です: {name_ja}")

        # URL 処理
        personal_url = extract_url(normalize_str(row["個人URL"]))
        lab_url      = extract_url(normalize_str(row["研究室URL"]))

        # ファイル名・写真
        filename_html = make_filename(name_en)
        filename_en   = filename_html          # 英語ページも同名と仮定
        photo_file    = make_photo_filename(name_en)

        # ボタン HTML
        url_buttons = build_url_buttons(personal_url, lab_url)

        # テンプレート置換
        html = template
        html = html.replace("{{NAME_JA}}",       name_ja)
        html = html.replace("{{POSITION}}",      position)
        html = html.replace("{{KEYWORDS_JA}}",   keywords)
        html = html.replace("{{DESCRIPTION_JA}}", desc_ja)
        html = html.replace("{{MESSAGE_JA}}",    message_ja)
        html = html.replace("{{PHOTO_FILENAME}}", photo_file)
        html = html.replace("{{FILENAME_EN}}",   filename_en)
        html = html.replace("{{URL_BUTTONS}}",   url_buttons)

        out_path = out / filename_html
        out_path.write_text(html, encoding="utf-8")
        print(f"[OK]   {name_ja} ({name_en}) → {out_path}")

    for msg in skipped:
        print(msg)

    print(f"\n完了: {len(staff) - len(skipped)} ファイル生成, {len(skipped)} 件スキップ")


# ---------------------------------------------------------------------------
# CLI エントリーポイント
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Excelから教員HTMLページを一括生成します。"
    )
    parser.add_argument(
        "--excel",
        default="学科HP回収用_分野説明文__2_.xlsx",
        help="入力 Excel ファイルのパス",
    )
    parser.add_argument(
        "--template",
        default="staff_template.html",
        help="テンプレート HTML のパス",
    )
    parser.add_argument(
        "--outdir",
        default="staffs",
        help="出力ディレクトリ（存在しない場合は作成）",
    )
    args = parser.parse_args()

    generate_pages(
        excel_path=args.excel,
        template_path=args.template,
        outdir=args.outdir,
    )


if __name__ == "__main__":
    main()
