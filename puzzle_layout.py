#!/usr/bin/env python3
"""
9種類のパズルSVGを生成し、PDFに配置するスクリプト
SVGファイル名は実行日付に基づいて YYYYMMDD_xxx.svg の形式

使用方法:
    パズル生成スクリプト群があるフォルダで実行してください。
    $ python puzzle_layout.py [YYYYMMDD]

出力:
    YYYYMMDD_puzzle.pdf（問題用）
    YYYYMMDD_answer.pdf（解答用）
    ※生成後、SVGファイルは自動削除されます
"""

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF
import reportlab.lib.colors as rl_colors
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import io
import sys
import subprocess
from pathlib import Path

# ============================================
# フォント登録
# ============================================
def register_fonts():
    """DejaVu Sans フォントを登録（存在する場合）"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]
    
    registered = False
    for path in font_paths:
        if os.path.exists(path):
            if "Bold" in path:
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', path))
                except:
                    pass
            else:
                try:
                    pdfmetrics.registerFont(TTFont('DejaVuSans', path))
                    registered = True
                except:
                    pass
    
    return registered


# フォント登録を試みる
DEJAVU_AVAILABLE = register_fonts()

# 使用するフォント名
FONT_REGULAR = 'DejaVuSans' if DEJAVU_AVAILABLE else 'Helvetica'
FONT_BOLD = 'DejaVuSans-Bold' if DEJAVU_AVAILABLE else 'Helvetica-Bold'


# ============================================
# svglibがサポートしていない色名を事前登録
# ============================================
def register_custom_colors():
    custom_colors = {
        'lightgray': '#D3D3D3',
        'lightgrey': '#D3D3D3',
        'darkgray': '#A9A9A9',
        'darkgrey': '#A9A9A9',
        'dimgray': '#696969',
        'dimgrey': '#696969',
        'gray': '#808080',
        'grey': '#808080',
        'lightslategray': '#778899',
        'lightslategrey': '#778899',
        'slategray': '#708090',
        'slategrey': '#708090',
    }

    for name, hex_value in custom_colors.items():
        if not hasattr(rl_colors, name):
            setattr(rl_colors, name, HexColor(hex_value))


register_custom_colors()

from svglib.svglib import svg2rlg


# ============================================
# SVG生成スクリプトの実行
# ============================================
def generate_svg_files(working_dir, date_prefix=None):
    """
    各パズル生成スクリプトを実行してSVGファイルを生成
    日付を引数と環境変数の両方で渡す
    """
    scripts = [
        "building_puzzle_svg.py",
        "calcpuzzle_generator.py",
        "countdown_generator.py",
        "cryptarithm_generator.py",
        "kenken_svg_generator.py",
        "matchstick_puzzle_generator.py",
        "maze_generator.py",
        "mininumpre_generator.py",
        "sumpuzzle_generator.py",
    ]
    
    base_dir = Path(working_dir)
    
    # 環境変数で日付を渡す（サブプログラムが対応している場合）
    env = os.environ.copy()
    if date_prefix:
        env['PUZZLE_DATE'] = date_prefix
    
    for script in scripts:
        script_path = base_dir / script
        if script_path.exists():
            print(f"=== Running {script} ===")
            try:
                # 日付を引数として渡す
                cmd = [sys.executable, str(script_path)]
                if date_prefix:
                    cmd.append(date_prefix)
                
                result = subprocess.run(
                    cmd,
                    cwd=str(base_dir),
                    env=env,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Error running {script}: {e}")
        else:
            print(f"Warning: {script} not found, skipping...")
    
    print("All SVG generation scripts finished.")


def delete_svg_files(working_dir, date_prefix):
    """
    生成したSVGファイル（18ファイル）を削除
    """
    puzzle_names = [
        'building', 'kenken', 'matchstick', 'cryptarithm',
        'countdown', 'mininumpre', 'calcpuzzle', 'sumpuzzle', 'maze'
    ]
    
    deleted_count = 0
    for name in puzzle_names:
        # 問題用SVG
        svg_path = os.path.join(working_dir, f"{date_prefix}_{name}.svg")
        if os.path.exists(svg_path):
            os.remove(svg_path)
            deleted_count += 1
        
        # 解答用SVG
        ans_svg_path = os.path.join(working_dir, f"{date_prefix}_{name}_ans.svg")
        if os.path.exists(ans_svg_path):
            os.remove(ans_svg_path)
            deleted_count += 1
    
    print(f"Deleted {deleted_count} SVG files.")


# ============================================
# ユーティリティ関数
# ============================================
def get_date_prefix():
    return datetime.now().strftime("%Y%m%d")


def get_formatted_date():
    """YYYY/MM/DD形式の日付を返す"""
    return datetime.now().strftime("%Y/%m/%d")


def generate_qr_code(url, box_size=10, border=1):
    """QRコードを生成してPIL Imageを返す"""
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


# ============================================
# Puzzle PDF用の描画関数
# ============================================
def draw_header_section(c, page_width, page_height, date_str):
    """
    ヘッダーテキストを描画（背景色なし）
    「Brain Decathlon YYYY/MM/DD   pi=    digits , Puzzle   / 9 , Time    :     」
    入力欄は4倍幅の余白
    """
    header_x = 8 * mm
    header_y = page_height - 5 * mm
    
    c.setFillColor(HexColor('#000000'))
    c.setFont(FONT_BOLD, 9)
    
    # 4倍幅の余白を表現するためにスペースを多めに入れる
    blank = "        "  # 8スペース（4倍幅相当）
    text = f"Brain Decathlon {date_str}   pi={blank}digits , Puzzle{blank}/ 9 , Time{blank}:{blank}"
    text_y = header_y - 4 * mm
    c.drawString(header_x + 2 * mm, text_y, text)


def draw_note_section(c, page_width, page_height):
    """
    4行の横罫線ノートを描画（背景色なし）
    1行目の最初に「π=」と書く
    罫線はパズル画像と被らない範囲まで
    """
    note_x = 5 * mm
    note_y = page_height - 10 * mm
    note_width = 132 * mm
    note_height = 32 * mm
    
    # 4行の横罫線（グレーの破線）を描画
    c.setStrokeColor(HexColor('#808080'))
    c.setLineWidth(0.5)
    c.setDash(3, 2)
    
    line_spacing = note_height / 4
    for i in range(4):
        line_y = note_y - (i + 1) * line_spacing
        c.line(note_x + 2 * mm, line_y, note_x + note_width - 2 * mm, line_y)
    
    c.setDash()
    
    # 1行目の最初に「π=」を書く
    c.setFillColor(HexColor('#000000'))
    c.setFont(FONT_REGULAR, 12)
    pi_y = note_y - line_spacing + 2 * mm
    c.drawString(note_x + 3 * mm, pi_y, "π=")


def draw_qr_sections(c, page_width, page_height, date_prefix):
    """
    Guide/AnswerのQRコードを描画（背景色なし）
    """
    from reportlab.lib.utils import ImageReader
    
    box_width = 26 * mm
    qr_size = 16 * mm
    
    guide_x = page_width - 60 * mm
    guide_y = page_height - 5 * mm
    
    answer_x = page_width - 32 * mm
    answer_y = page_height - 5 * mm
    
    # 「Guide」テキストを描画
    c.setFillColor(HexColor('#000000'))
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(guide_x + box_width / 2, guide_y - 4 * mm, "Guide")
    
    # 「Answer」テキストを描画
    c.drawCentredString(answer_x + box_width / 2, answer_y - 4 * mm, "Answer")
    
    # GuideのQRコードを生成・描画
    guide_url = "https://351justy.github.io/brain-decathlon/guide.pdf"
    guide_qr = generate_qr_code(guide_url, box_size=10, border=1)
    
    guide_qr_buffer = io.BytesIO()
    guide_qr.save(guide_qr_buffer, format='PNG')
    guide_qr_buffer.seek(0)
    guide_qr_image = ImageReader(guide_qr_buffer)
    
    qr_y_offset = guide_y - 5 * mm - qr_size
    qr_x_offset = guide_x + (box_width - qr_size) / 2
    c.drawImage(guide_qr_image, qr_x_offset, qr_y_offset, width=qr_size, height=qr_size)
    
    # AnswerのQRコードを生成・描画
    answer_url = f"https://351justy.github.io/brain-decathlon/puzzles/{date_prefix}_answer.pdf"
    answer_qr = generate_qr_code(answer_url, box_size=10, border=1)
    
    answer_qr_buffer = io.BytesIO()
    answer_qr.save(answer_qr_buffer, format='PNG')
    answer_qr_buffer.seek(0)
    answer_qr_image = ImageReader(answer_qr_buffer)
    
    qr_x_offset = answer_x + (box_width - qr_size) / 2
    c.drawImage(answer_qr_image, qr_x_offset, qr_y_offset, width=qr_size, height=qr_size)


# ============================================
# Answer PDF用の描画関数
# ============================================
def draw_answer_header_section(c, page_width, page_height, date_str):
    """
    Answer PDF用ヘッダー：「Brain Decathlon YYYY/MM/DD Answer」
    """
    header_x = 8 * mm
    header_y = page_height - 5 * mm
    
    c.setFillColor(HexColor('#000000'))
    c.setFont(FONT_BOLD, 11)
    
    text = f"Brain Decathlon {date_str} Answer"
    text_y = header_y - 4 * mm
    c.drawString(header_x + 2 * mm, text_y, text)


def draw_answer_pi_section(c, page_width, page_height):
    """
    Answer PDF用：円周率の数字を表示（罫線なし）
    9ptフォント、行間を詰める
    """
    note_x = 5 * mm
    note_y = page_height - 10 * mm
    
    # 円周率の6行
    pi_lines = [
        "π=3.1415926535 8979323846 2643383279 5028841971 6939937510",
        "       5820974944 5923078164 0628620899 8628034825 3421170679",
        "       8214808651 3282306647 0938446095 5058223172 5359408128",
        "       4811174502 8410270193 8521105559 6446229489 5493038196",
        "       4428810975 6659334461 2847564823 3786783165 2712019091",
        "       4564856692 3460348610 4543266482 1339360726 0249141273",
        "       7245870066 0631558817 4881520920 9628292540 9171536436",
        "       7892590360 0113305305 4882046652 1384146951 9415116094",
        "       3305727036 5759591953 0921861173 8193261179 3105118548",
        "       0744623799 6274956735 1885752724 8912279381 8301194912",
    ]
    
    c.setFillColor(HexColor('#000000'))
    c.setFont(FONT_REGULAR, 10)  # 10ptフォント
    
    line_spacing = 4 * mm  # 行間を詰める
    for i, line in enumerate(pi_lines):
        line_y = note_y - (i + 1) * line_spacing
        c.drawString(note_x + 3 * mm, line_y, line)


def draw_answer_qr_sections(c, page_width, page_height):
    """
    Answer PDF用：「more π」と「Games」のQRコード
    """
    from reportlab.lib.utils import ImageReader
    
    box_width = 26 * mm
    qr_size = 16 * mm
    
    morepi_x = page_width - 60 * mm
    morepi_y = page_height - 5 * mm
    
    games_x = page_width - 32 * mm
    games_y = page_height - 5 * mm
    
    # 「more π」テキストを描画
    c.setFillColor(HexColor('#000000'))
    c.setFont(FONT_BOLD, 9)
    c.drawCentredString(morepi_x + box_width / 2, morepi_y - 4 * mm, "more π")
    
    # 「Games」テキストを描画
    c.drawCentredString(games_x + box_width / 2, games_y - 4 * mm, "Games")
    
    # more πのQRコードを生成・描画
    morepi_url = "https://www.tstcl.jp/randd/constants/pi/"
    morepi_qr = generate_qr_code(morepi_url, box_size=10, border=1)
    
    morepi_qr_buffer = io.BytesIO()
    morepi_qr.save(morepi_qr_buffer, format='PNG')
    morepi_qr_buffer.seek(0)
    morepi_qr_image = ImageReader(morepi_qr_buffer)
    
    qr_y_offset = morepi_y - 5 * mm - qr_size
    qr_x_offset = morepi_x + (box_width - qr_size) / 2
    c.drawImage(morepi_qr_image, qr_x_offset, qr_y_offset, width=qr_size, height=qr_size)
    
    # GamesのQRコードを生成・描画
    games_url = "https://justy.co.jp/games/"
    games_qr = generate_qr_code(games_url, box_size=10, border=1)
    
    games_qr_buffer = io.BytesIO()
    games_qr.save(games_qr_buffer, format='PNG')
    games_qr_buffer.seek(0)
    games_qr_image = ImageReader(games_qr_buffer)
    
    qr_x_offset = games_x + (box_width - qr_size) / 2
    c.drawImage(games_qr_image, qr_x_offset, qr_y_offset, width=qr_size, height=qr_size)


# ============================================
# 共通レイアウト定義
# ============================================
def get_layout():
    """パズルのレイアウト情報を返す"""
    MM = 72.0 / 25.4

    base_layout = {
        'building': (
            31.5 + 140*MM,
            (574.5 - 3*MM) - 5*MM,
            124.0 * 1.16,
            122.0 * 1.16
        ),
        'kenken': (
            185.5 + 40*MM,
            609.0 - 12*MM,
            124.5 * 0.78,
            126.5 * 0.78
        ),
        'matchstick': (
            387.5 + 8*MM,
            719.5,
            142.5 * 1.2,
            40.5  * 1.2
        ),
        'cryptarithm': (
            325.0 - 60*MM,
            562.0 - 12*MM,
            125.0 * 1.15,
            165.0 * 1.15
        ),
        'countdown': (
            450.0 - 150*MM,
            (562.5 + 15*MM) - 13*MM,
            108.5 * 1.5,
            151.0 * 1.5
        ),
        'mininumpre': (
            35.0 - 5*MM,
            405.5 - 1*MM,
            159.5 * 0.87,
            159.5 * 0.87
        ),
        'calcpuzzle': (
            175.0 + 14*MM,
            (407.0 - 3*MM) - 3*MM,
            187.0,
            157.0
        ),
        'sumpuzzle': (
            390.5 + 5*MM,
            399.0,
            169.5,
            166.0
        ),
        'maze': (
            (36.5 + 522.5/2) - (522.5*1.07)/2,
            (((37.5 + 364.5/2) - (364.5*1.07)/2) - 3*MM) - 2*MM,
            522.5 * 1.07,
            364.5 * 1.07
        ),
    }

    dx_dy_mm = {
        'building': ( +4, +5),
        'kenken':   ( +4, +5),
        'matchstick': (0, -3),
        'cryptarithm': (0, -1),
        'countdown': (-5, -3),
        'mininumpre': (0, 0),
        'calcpuzzle': (0, 0),
        'sumpuzzle': (0, 0),
        'maze': (0, 0),
    }

    layout = {}
    for name, (x, y, w, h) in base_layout.items():
        dx_mm, dy_mm = dx_dy_mm.get(name, (0, 0))
        layout[name] = (
            x + dx_mm * MM,
            y + dy_mm * MM,
            w,
            h
        )
    
    return layout


# ============================================
# PDF生成関数
# ============================================
def create_puzzle_pdf(working_dir=None, date_override=None):
    """問題用PDFを生成"""
    if working_dir is None:
        working_dir = os.getcwd()

    date_prefix = date_override if date_override else get_date_prefix()
    
    if date_override:
        year = date_override[:4]
        month = date_override[4:6]
        day = date_override[6:8]
        formatted_date = f"{year}/{month}/{day}"
    else:
        formatted_date = get_formatted_date()

    output_path = os.path.join(working_dir, f"{date_prefix}_puzzle.pdf")

    svg_files = {
        'building': f'{date_prefix}_building.svg',
        'kenken': f'{date_prefix}_kenken.svg',
        'matchstick': f'{date_prefix}_matchstick.svg',
        'cryptarithm': f'{date_prefix}_cryptarithm.svg',
        'countdown': f'{date_prefix}_countdown.svg',
        'mininumpre': f'{date_prefix}_mininumpre.svg',
        'calcpuzzle': f'{date_prefix}_calcpuzzle.svg',
        'sumpuzzle': f'{date_prefix}_sumpuzzle.svg',
        'maze': f'{date_prefix}_maze.svg',
    }

    page_width, page_height = A4
    c = canvas.Canvas(output_path, pagesize=A4)

    # ヘッダー、ノート、QRコードセクションを描画
    draw_header_section(c, page_width, page_height, formatted_date)
    draw_note_section(c, page_width, page_height)
    draw_qr_sections(c, page_width, page_height, date_prefix)

    def load_svg(name):
        path = os.path.join(working_dir, svg_files[name])
        if os.path.exists(path):
            return svg2rlg(path)
        else:
            print(f"Warning: {path} not found")
            return None

    def draw_svg(drawing, x, y, target_width=None, target_height=None):
        if drawing is None:
            return
        ow, oh = drawing.width, drawing.height
        if target_width and target_height:
            scale = min(target_width / ow, target_height / oh)
        elif target_width:
            scale = target_width / ow
        elif target_height:
            scale = target_height / oh
        else:
            scale = 1.0
        drawing.scale(scale, scale)
        renderPDF.draw(drawing, c, x, y)

    layout = get_layout()

    for name in layout:
        x, y, w, h = layout[name]
        d = load_svg(name)
        draw_svg(d, x, y, target_width=w, target_height=h)

    c.save()
    print(f"PDF created: {output_path}")
    return output_path


def create_answer_pdf(working_dir=None, date_override=None):
    """解答用PDFを生成（_ans付きSVGを使用）"""
    if working_dir is None:
        working_dir = os.getcwd()

    date_prefix = date_override if date_override else get_date_prefix()
    
    if date_override:
        year = date_override[:4]
        month = date_override[4:6]
        day = date_override[6:8]
        formatted_date = f"{year}/{month}/{day}"
    else:
        formatted_date = get_formatted_date()

    output_path = os.path.join(working_dir, f"{date_prefix}_answer.pdf")

    svg_files = {
        'building': f'{date_prefix}_building_ans.svg',
        'kenken': f'{date_prefix}_kenken_ans.svg',
        'matchstick': f'{date_prefix}_matchstick_ans.svg',
        'cryptarithm': f'{date_prefix}_cryptarithm_ans.svg',
        'countdown': f'{date_prefix}_countdown_ans.svg',
        'mininumpre': f'{date_prefix}_mininumpre_ans.svg',
        'calcpuzzle': f'{date_prefix}_calcpuzzle_ans.svg',
        'sumpuzzle': f'{date_prefix}_sumpuzzle_ans.svg',
        'maze': f'{date_prefix}_maze_ans.svg',
    }

    page_width, page_height = A4
    c = canvas.Canvas(output_path, pagesize=A4)

    # Answer PDF用のヘッダー、円周率、QRコードセクションを描画
    draw_answer_header_section(c, page_width, page_height, formatted_date)
    draw_answer_pi_section(c, page_width, page_height)
    draw_answer_qr_sections(c, page_width, page_height)

    def load_svg(name):
        path = os.path.join(working_dir, svg_files[name])
        if os.path.exists(path):
            return svg2rlg(path)
        else:
            print(f"Warning: {path} not found")
            return None

    def draw_svg(drawing, x, y, target_width=None, target_height=None):
        if drawing is None:
            return
        ow, oh = drawing.width, drawing.height
        if target_width and target_height:
            scale = min(target_width / ow, target_height / oh)
        elif target_width:
            scale = target_width / ow
        elif target_height:
            scale = target_height / oh
        else:
            scale = 1.0
        drawing.scale(scale, scale)
        renderPDF.draw(drawing, c, x, y)

    layout = get_layout()

    for name in layout:
        x, y, w, h = layout[name]
        d = load_svg(name)
        draw_svg(d, x, y, target_width=w, target_height=h)

    c.save()
    print(f"PDF created: {output_path}")
    return output_path


# ============================================
# メイン処理
# ============================================
def main():
    """
    メイン処理：
    1. SVGファイルを生成（各パズル生成スクリプトを実行）
    2. Puzzle PDFを生成
    3. Answer PDFを生成
    4. SVGファイルを削除
    """
    date_override = sys.argv[1] if len(sys.argv) > 1 else None
    date_prefix = date_override if date_override else get_date_prefix()
    working_dir = os.getcwd()
    
    print("=" * 50)
    print(f"Brain Decathlon PDF Generator")
    print(f"Date: {date_prefix}")
    print("=" * 50)
    
    # Step 1: SVGファイルを生成
    print("\n[Step 1] Generating SVG files...")
    generate_svg_files(working_dir, date_prefix)
    
    # Step 2: Puzzle PDFを生成
    print("\n[Step 2] Creating Puzzle PDF...")
    create_puzzle_pdf(working_dir, date_override)
    
    # Step 3: Answer PDFを生成
    print("\n[Step 3] Creating Answer PDF...")
    create_answer_pdf(working_dir, date_override)
    
    # Step 4: SVGファイルを削除
    print("\n[Step 4] Cleaning up SVG files...")
    delete_svg_files(working_dir, date_prefix)
    
    print("\n" + "=" * 50)
    print("All done!")
    print(f"Output files:")
    print(f"  - {date_prefix}_puzzle.pdf")
    print(f"  - {date_prefix}_answer.pdf")
    print("=" * 50)


if __name__ == "__main__":
    main()
