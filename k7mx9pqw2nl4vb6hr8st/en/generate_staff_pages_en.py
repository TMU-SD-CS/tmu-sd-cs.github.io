"""
generate_staff_pages_en.py
==========================
Excelファイルを読み込み、staff_template_en.html をもとに
各教員の英語版HTMLページを生成するスクリプト。

使い方:
    python generate_staff_pages_en.py \
        --excel   学科HP回収用_分野説明文__2_.xlsx \
        --template staff_template_en.html \
        --outdir  en/staffs/

生成ファイル名: 日本語版と同一スラグ
例) Sayaka Shiota → staff_shiotasayaka.html
    Hiroki Shibata → staff_shibatahiroki.html  (Excelの誤記を補正)
"""

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# ユーティリティ（日本語版スクリプトと共通ロジック）
# ---------------------------------------------------------------------------

POSITION_EN = {
    "教授":  "Professor",
    "准教授": "Associate Professor",
    "助教":  "Assistant Professor",
}


def normalize_str(s) -> str:
    if pd.isna(s):
        return ""
    return str(s).strip()


def make_filename(name_en: str) -> str:
    """
    英語氏名からファイル名を生成する。
    "Sayaka Shiota" → "staff_shiotasayaka.html"
    """
    name_en = unicodedata.normalize("NFKC", normalize_str(name_en))
    parts = name_en.split()
    if len(parts) >= 2:
        surname = parts[-1].lower()
        given   = "".join(p.lower() for p in parts[:-1])
        slug = surname + given
    else:
        slug = name_en.lower().replace(" ", "")
    slug = re.sub(r"[^a-z0-9]", "", slug)
    return f"staff_{slug}.html"


# Excelの氏名_en誤記・表記ゆれを正しいファイル名スラグに補正するテーブル
FILENAME_OVERRIDES = {
    # Excel氏名_en（小文字）: 正しいスラグ
    "shibata yuki": "shibatahiroki",   # 正しくは Hiroki Shibata
}


def make_filename_corrected(name_en: str) -> str:
    """誤記補正を適用したファイル名生成。"""
    key = normalize_str(name_en).lower()
    if key in FILENAME_OVERRIDES:
        return f"staff_{FILENAME_OVERRIDES[key]}.html"
    return make_filename(name_en)


def extract_url(raw: str, prefer: str = "en") -> str:
    """
    URL フィールドを解析して最初の有効な URL を返す。
    prefer="en" なら（英）タグ付きを優先する。
    """
    raw = normalize_str(raw)
    if not raw or raw in ("nan", "なし", "NaN"):
        return ""
    if "http" not in raw:
        return ""

    lines = [l.strip() for l in raw.splitlines() if "http" in l]
    if not lines:
        return ""

    # 英語版優先
    tag_en = ("（英）", "(英)", "(en)", "（en）")
    tag_ja = ("（日）", "(日)", "(ja)", "（ja）")

    prefer_tags = tag_en if prefer == "en" else tag_ja
    fallback_tags = tag_ja if prefer == "en" else tag_en

    for line in lines:
        if any(t in line for t in prefer_tags):
            url = re.search(r"https?://\S+", line)
            if url:
                return url.group(0).rstrip("　 ")

    # preferタグがなければfallback
    for line in lines:
        if any(t in line for t in fallback_tags):
            url = re.search(r"https?://\S+", line)
            if url:
                return url.group(0).rstrip("　 ")

    # タグなしなら最初のURL
    url = re.search(r"https?://\S+", lines[0])
    return url.group(0).rstrip("　 ") if url else ""


def build_url_buttons(personal_url: str, lab_url: str) -> str:
    """個人・研究室URLのボタンHTMLを組み立てる。"""
    buttons = []
    if personal_url:
        buttons.append(
            f'<li><a href="{personal_url}"><span class="btn_bg_green">Personal website</span></a></li>'
        )
    if lab_url:
        buttons.append(
            f'<li><a href="{lab_url}"><span class="btn_bg_green">Lab website</span></a></li>'
        )
    if not buttons:
        return ""
    return '<ul class="list_il">\n' + "\n".join(buttons) + "\n</ul>"


def make_photo_filename(name_en: str) -> str:
    """写真ファイル名を生成する。"""
    html_name = make_filename_corrected(name_en)
    slug = html_name[len("staff_"):-len(".html")]
    # 拡張子は.jpgをデフォルトとする（.pngは個別対応が必要な場合のみ）
    return f"photo_{slug}.jpg"


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------

def load_staff_data(excel_path: str) -> pd.DataFrame:
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
    return staff.reset_index(drop=True)


def generate_pages(excel_path: str, template_path: str, outdir: str) -> None:
    template = Path(template_path).read_text(encoding="utf-8")
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    staff = load_staff_data(excel_path)
    skipped = []

    for _, row in staff.iterrows():
        name_ja    = normalize_str(row["氏名"])
        name_en    = normalize_str(row["氏名_en"])
        position   = normalize_str(row["職位"])
        keywords   = normalize_str(row["分野名_en"])
        desc_en    = normalize_str(row["説明_en"])

        if not name_ja or not name_en:
            skipped.append(f"[SKIP] 氏名不明: {row.to_dict()}")
            continue
        if not desc_en:
            print(f"[WARN] 説明文(英語)が空です: {name_ja} / {name_en}")
        if not keywords:
            print(f"[WARN] 分野名(英語)が空です: {name_ja} / {name_en}")

        # URL処理（英語版を優先）
        personal_url = extract_url(normalize_str(row["個人URL"]),  prefer="en")
        lab_url      = extract_url(normalize_str(row["研究室URL"]), prefer="en")

        # ファイル名・写真
        filename_html = make_filename_corrected(name_en)
        filename_ja   = filename_html          # 日本語版も同名
        photo_file    = make_photo_filename(name_en)
        position_en   = POSITION_EN.get(position, position)

        # ボタンHTML
        url_buttons = build_url_buttons(personal_url, lab_url)

        # テンプレート置換
        html = template
        html = html.replace("{{NAME_EN}}",        name_en)
        html = html.replace("{{POSITION_EN}}",    position_en)
        html = html.replace("{{KEYWORDS_EN}}",    keywords)
        html = html.replace("{{DESCRIPTION_EN}}", desc_en)
        html = html.replace("{{PHOTO_FILENAME}}", photo_file)
        html = html.replace("{{FILENAME_JA}}",    filename_ja)
        html = html.replace("{{URL_BUTTONS}}",    url_buttons)

        out_path = out / filename_html
        out_path.write_text(html, encoding="utf-8")
        print(f"[OK]   {name_en} ({name_ja}) → {out_path}")

    for msg in skipped:
        print(msg)

    print(f"\n完了: {len(staff) - len(skipped)} ファイル生成, {len(skipped)} 件スキップ")


# ---------------------------------------------------------------------------
# CLI エントリーポイント
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Excelから教員英語版HTMLページを一括生成します。"
    )
    parser.add_argument(
        "--excel",
        default="学科HP回収用_分野説明文__2_.xlsx",
        help="入力 Excel ファイルのパス",
    )
    parser.add_argument(
        "--template",
        default="staff_template_en.html",
        help="英語版テンプレート HTML のパス",
    )
    parser.add_argument(
        "--outdir",
        default="en/staffs/",
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
