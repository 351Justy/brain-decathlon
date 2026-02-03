#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
覆面算（Cryptarithm）SVG生成スクリプト
- ミニモード専用（被乗数3桁、乗数2桁、記号3つ）
- 確定数字の総数は4個以下
- 各行に最大1つの確定数字
- 一意解を持つ問題のみ生成
"""

import random
import os
from datetime import datetime
from itertools import permutations

# 記号リスト
SYMBOLS = ['△', '□', '○', '☆', '◇', '◎']

# ミニモード設定
SETTINGS = {
    'a_digits': 3,  # 被乗数の桁数
    'b_digits': 2,  # 乗数の桁数
    'symbol_count': 3,  # 記号の数
    'max_confirmed_count': 4  # 確定数字の総数の上限
}


def generate_multiplier_without_zero(digits):
    """0を含まない乗数を生成"""
    result = ''
    for _ in range(digits):
        digit = random.randint(1, 9)
        result += str(digit)
    return int(result)


def generate_multiplicand(digits):
    """被乗数を生成（0を含んでよい）"""
    min_val = 10 ** (digits - 1)
    max_val = 10 ** digits - 1
    return random.randint(min_val, max_val)


def calculate_multiplication(a, b):
    """筆算の計算"""
    result = a * b
    b_str = str(b)
    
    partials = []
    for i in range(len(b_str) - 1, -1, -1):
        digit = int(b_str[i])
        partial = a * digit
        partials.append(partial)
    
    return {
        'multiplicand': a,
        'multiplier': b,
        'partials': partials,
        'result': result
    }


def extract_all_digits(calc):
    """筆算に登場する全数字を抽出"""
    digits = []
    
    for d in str(calc['multiplicand']):
        digits.append(d)
    for d in str(calc['multiplier']):
        digits.append(d)
    for p in calc['partials']:
        for d in str(p):
            digits.append(d)
    for d in str(calc['result']):
        digits.append(d)
    
    return digits


def count_digits(digits):
    """数字の出現回数をカウント"""
    count = {}
    for d in digits:
        count[d] = count.get(d, 0) + 1
    return count


def get_top_digits(count, n):
    """出現回数上位n個の数字を取得"""
    sorted_items = sorted(count.items(), key=lambda x: x[1], reverse=True)
    return [digit for digit, _ in sorted_items[:n]]


def replace_with_symbols(calc, digits_to_replace):
    """数字を記号に置き換え"""
    mapping = {}
    for i, digit in enumerate(digits_to_replace):
        mapping[digit] = SYMBOLS[i]
    
    masked = {
        'multiplicand': str(calc['multiplicand']),
        'multiplier': str(calc['multiplier']),
        'partials': [str(p) for p in calc['partials']],
        'result': str(calc['result'])
    }
    
    for digit, symbol in mapping.items():
        masked['multiplicand'] = masked['multiplicand'].replace(digit, symbol)
        masked['multiplier'] = masked['multiplier'].replace(digit, symbol)
        masked['partials'] = [p.replace(digit, symbol) for p in masked['partials']]
        masked['result'] = masked['result'].replace(digit, symbol)
    
    reverse_mapping = {v: k for k, v in mapping.items()}
    
    return {
        'original': calc,
        'masked': masked,
        'mapping': mapping,
        'reverse_mapping': reverse_mapping
    }


def get_confirmed_digits(calc, mapping):
    """確定数字を取得（種類のリスト）"""
    all_digits = extract_all_digits(calc)
    confirmed = set()
    for d in all_digits:
        if d not in mapping:
            confirmed.add(d)
    return list(confirmed)


def count_confirmed_digits_total(masked):
    """確定数字の総数をカウント（出現回数の合計）"""
    total = 0
    # 被乗数
    for char in masked['multiplicand']:
        if char not in SYMBOLS:
            total += 1
    # 乗数
    for char in masked['multiplier']:
        if char not in SYMBOLS:
            total += 1
    # 部分積
    for partial in masked['partials']:
        for char in partial:
            if char not in SYMBOLS:
                total += 1
    # 結果
    for char in masked['result']:
        if char not in SYMBOLS:
            total += 1
    return total


def has_at_most_one_confirmed_digit_per_row(masked):
    """各行に確定数字が最大1つかチェック"""
    def count_digits(text):
        return sum(1 for char in text if char not in SYMBOLS)
    
    # 被乗数
    if count_digits(masked['multiplicand']) > 1:
        return False
    # 乗数
    if count_digits(masked['multiplier']) > 1:
        return False
    # 部分積
    for partial in masked['partials']:
        if count_digits(partial) > 1:
            return False
    # 結果
    if count_digits(masked['result']) > 1:
        return False
    
    return True


def verify_solution(masked, assignment):
    """解が正しいかチェック"""
    multiplicand_str = masked['multiplicand']
    multiplier_str = masked['multiplier']
    partials_str = list(masked['partials'])
    result_str = masked['result']
    
    for symbol, digit in assignment.items():
        multiplicand_str = multiplicand_str.replace(symbol, digit)
        multiplier_str = multiplier_str.replace(symbol, digit)
        partials_str = [p.replace(symbol, digit) for p in partials_str]
        result_str = result_str.replace(symbol, digit)
    
    # 数字のみかチェック
    if not multiplicand_str.isdigit():
        return False
    if not multiplier_str.isdigit():
        return False
    if not all(p.isdigit() for p in partials_str):
        return False
    if not result_str.isdigit():
        return False
    
    a = int(multiplicand_str)
    b = int(multiplier_str)
    result = int(result_str)
    
    if a * b != result:
        return False
    
    b_digits = list(reversed(str(b)))
    for i, bd in enumerate(b_digits):
        digit = int(bd)
        expected_partial = a * digit
        actual_partial = int(partials_str[i])
        if expected_partial != actual_partial:
            return False
    
    return True


def has_unique_solution(problem):
    """一意解チェック"""
    masked = problem['masked']
    mapping = problem['mapping']
    symbols = list(mapping.values())
    confirmed_digits = get_confirmed_digits(problem['original'], mapping)
    available_digits = [d for d in '0123456789' if d not in confirmed_digits]
    
    solution_count = 0
    found_solution = None
    
    # 全ての組み合わせを試す
    for perm in permutations(available_digits, len(symbols)):
        assignment = {symbols[i]: perm[i] for i in range(len(symbols))}
        if verify_solution(masked, assignment):
            solution_count += 1
            if solution_count == 1:
                found_solution = assignment.copy()
            if solution_count > 1:
                break
    
    return {
        'is_unique': solution_count == 1,
        'solution': found_solution
    }


def generate_problem():
    """問題生成（条件を満たすまで繰り返す）"""
    max_attempts = 1000
    
    for attempt in range(max_attempts):
        candidates = []
        
        # 50題生成（条件が厳しいため多めに生成）
        for _ in range(50):
            a = generate_multiplicand(SETTINGS['a_digits'])
            b = generate_multiplier_without_zero(SETTINGS['b_digits'])
            
            calc = calculate_multiplication(a, b)
            all_digits = extract_all_digits(calc)
            digit_count = count_digits(all_digits)
            top_digits = get_top_digits(digit_count, SETTINGS['symbol_count'])
            
            problem = replace_with_symbols(calc, top_digits)
            confirmed_digits = get_confirmed_digits(calc, problem['mapping'])
            confirmed_total = count_confirmed_digits_total(problem['masked'])
            
            # 条件チェック：
            # 1. 確定数字の総数が4以下
            # 2. 各行に最大1つの確定数字
            if (confirmed_total <= SETTINGS['max_confirmed_count'] and 
                has_at_most_one_confirmed_digit_per_row(problem['masked'])):
                candidates.append({
                    'problem': problem,
                    'confirmed_total': confirmed_total,
                    'confirmed_digits': confirmed_digits
                })
        
        # 確定数字の総数が少ない順にソート
        candidates.sort(key=lambda x: x['confirmed_total'])
        
        # 一意解を探す
        for candidate in candidates:
            check = has_unique_solution(candidate['problem'])
            if check['is_unique']:
                return {
                    **candidate['problem'],
                    'solution': check['solution'],
                    'confirmed_digits': candidate['confirmed_digits'],
                    'confirmed_total': candidate['confirmed_total']
                }
    
    raise Exception("条件を満たす問題を生成できませんでした")


def draw_symbol_shape(symbol, cx, cy, size, stroke_color="lightgray"):
    """記号をSVG図形として描画"""
    half = size / 2
    stroke_w = 2.5  # 記号の線の太さ
    
    if symbol == '△':
        # 三角形（正三角形に近い形）
        top_y = cy - half * 0.9
        bottom_y = cy + half * 0.7
        left_x = cx - half * 0.8
        right_x = cx + half * 0.8
        return f'<polygon points="{cx},{top_y} {left_x},{bottom_y} {right_x},{bottom_y}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}"/>'
    
    elif symbol == '□':
        # 正方形
        s = size * 0.7
        return f'<rect x="{cx - s/2}" y="{cy - s/2}" width="{s}" height="{s}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}"/>'
    
    elif symbol == '○':
        # 円
        r = size * 0.35
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}"/>'
    
    elif symbol == '☆':
        # 星（5点）
        import math
        points = []
        outer_r = size * 0.4
        inner_r = size * 0.2
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            r = outer_r if i % 2 == 0 else inner_r
            px = cx + r * math.cos(angle)
            py = cy - r * math.sin(angle)
            points.append(f"{px},{py}")
        return f'<polygon points="{" ".join(points)}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}"/>'
    
    elif symbol == '◇':
        # ひし形
        s = size * 0.4
        return f'<polygon points="{cx},{cy-s} {cx+s},{cy} {cx},{cy+s} {cx-s},{cy}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}"/>'
    
    elif symbol == '◎':
        # 二重丸
        r1 = size * 0.35
        r2 = size * 0.2
        return f'<circle cx="{cx}" cy="{cy}" r="{r1}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}"/><circle cx="{cx}" cy="{cy}" r="{r2}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}"/>'
    
    return ''


def generate_svg(problem, show_answer=False):
    """SVG生成"""
    masked = problem['masked']
    solution = problem['solution']
    
    # ============================================================
    # SVGパラメータ（調整可能）
    # ============================================================
    
    # セルサイズ
    cell_width = 50          # セルの横幅（文字間隔に影響）
    cell_height = 60         # セルの高さ（行の高さのベース）
    
    # 行間
    line_height = cell_height + 5   # 行の高さ（行間を広げるにはこの値を大きく）
    line_separator_height = 20      # 横線後のスペース
    
    # 余白
    padding_left = 60        # 左余白
    padding_top = 40         # 上余白
    padding_right = 20       # 右余白（SVG幅計算用）
    padding_bottom = 20      # 下余白（SVG高さ計算用）
    
    # フォント
    font_size = 36           # 数字のフォントサイズ
    font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"  # Linux/Render対応フォント
    
    # 記号
    symbol_size = 44         # 記号図形のサイズ（大きくすると記号が大きくなる）
    symbol_stroke_color = "lightgray"  # 記号の線の色
    
    # 線
    separator_stroke_width = 3   # 横線の太さ
    separator_color = "black"    # 横線の色
    
    # 数字の色
    digit_color = "black"        # 確定数字の色
    
    # ============================================================
    
    # 最大幅を計算
    max_width = len(masked['result'])
    
    # 行数を計算
    num_lines = 2 + 1 + len(masked['partials']) + 1 + 1  # 被乗数、乗数、線、部分積、線、結果
    
    # SVGサイズ（演算子列を含めて+1）
    svg_width = padding_left + (max_width + 2) * cell_width + padding_right
    svg_height = padding_top + num_lines * line_height + padding_bottom
    
    # SVG開始
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">')
    svg_parts.append('<style>')
    svg_parts.append(f'  .digit {{ font-family: {font_family}; font-size: {font_size}px; fill: {digit_color}; }}')
    svg_parts.append(f'  .operator {{ font-family: {font_family}; font-size: {font_size}px; fill: {digit_color}; font-weight: bold; }}')
    svg_parts.append('</style>')
    
    current_y = padding_top
    
    def draw_row(text, operator='', shift=0):
        """1行を描画"""
        nonlocal current_y
        row_parts = []
        
        # 演算子（2列目 = 結果の最上位桁と同じ列に配置）
        if operator:
            x = padding_left + cell_width + cell_width / 2  # 2列目の中央
            y = current_y + cell_height * 0.65
            row_parts.append(f'<text x="{x}" y="{y}" class="operator" text-anchor="middle">{operator}</text>')
        
        # 文字列を右寄せで配置（1列目は演算子用なので+1）
        text_len = len(text)
        start_x = padding_left + (max_width + 1 - text_len - shift) * cell_width
        
        for i, char in enumerate(text):
            cx = start_x + i * cell_width + cell_width / 2
            cy = current_y + cell_height * 0.5
            
            is_symbol = char in SYMBOLS
            
            if show_answer and is_symbol:
                # 正解表示: 記号を数字に置き換え
                display_char = solution.get(char, char)
                y = current_y + cell_height * 0.65
                row_parts.append(f'<text x="{cx}" y="{y}" class="digit" text-anchor="middle">{display_char}</text>')
            elif is_symbol:
                # 記号を図形として描画
                row_parts.append(draw_symbol_shape(char, cx, cy, symbol_size, symbol_stroke_color))
            else:
                # 数字
                y = current_y + cell_height * 0.65
                row_parts.append(f'<text x="{cx}" y="{y}" class="digit" text-anchor="middle">{char}</text>')
        
        current_y += line_height
        return '\n'.join(row_parts)
    
    def draw_line():
        """横線を描画"""
        nonlocal current_y
        x1 = padding_left + cell_width  # 2列目から開始
        x2 = padding_left + (max_width + 1) * cell_width
        y = current_y + 5
        line = f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{separator_color}" stroke-width="{separator_stroke_width}"/>'
        current_y += line_separator_height
        return line
    
    # 被乗数
    svg_parts.append(draw_row(masked['multiplicand']))
    
    # 乗数
    svg_parts.append(draw_row(masked['multiplier'], operator='×'))
    
    # 横線
    svg_parts.append(draw_line())
    
    # 部分積
    for idx, partial in enumerate(masked['partials']):
        svg_parts.append(draw_row(partial, shift=idx))
    
    # 横線
    svg_parts.append(draw_line())
    
    # 結果
    svg_parts.append(draw_row(masked['result']))
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def main():
    """メイン処理"""
    # 日付を取得
    today = datetime.now().strftime('%Y%m%d')
    
    # ファイル名
    problem_filename = f'{today}_cryptarithm.svg'
    answer_filename = f'{today}_cryptarithm_ans.svg'
    
    print("覆面算（ミニモード）を生成中...")
    print(f"条件: 記号3つ、確定数字の総数4個以下、各行に最大1つの確定数字、一意解")
    
    # 問題生成
    problem = generate_problem()
    
    # 情報表示
    print(f"\n生成完了!")
    print(f"被乗数: {problem['original']['multiplicand']}")
    print(f"乗数: {problem['original']['multiplier']}")
    print(f"結果: {problem['original']['result']}")
    print(f"確定数字の種類: {problem['confirmed_digits']}")
    print(f"確定数字の総数: {problem['confirmed_total']}個")
    print(f"記号マッピング: {problem['reverse_mapping']}")
    
    # SVG生成（問題）
    svg_problem = generate_svg(problem, show_answer=False)
    with open(problem_filename, 'w', encoding='utf-8') as f:
        f.write(svg_problem)
    print(f"\n問題ファイル: {problem_filename}")
    
    # SVG生成（正解）
    svg_answer = generate_svg(problem, show_answer=True)
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(svg_answer)
    print(f"正解ファイル: {answer_filename}")


if __name__ == '__main__':
    main()
