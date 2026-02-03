#!/usr/bin/env python3
"""
カウントダウン計算 問題・解答SVG生成スクリプト

4つの数字の間に+, -, ×, ÷の演算子を入れて、
目標値（5, 4, 3, 2, 1, 0）を作る問題を生成します。

使用方法:
    python3 countdown_generator.py

出力ファイル:
    YYYYMMDD_countdown.svg     - 問題用紙
    YYYYMMDD_countdown_ans.svg - 解答用紙

必要なモジュール:
    Python標準ライブラリのみ（追加インストール不要）
"""

import random
from datetime import date

# プリセットされた数字の組（100組）
# 条件：この4数の順序のまま、3つの演算子（+−×÷）を入れるだけで、5〜0のすべてが作れる
PROBLEMS = [
    [1, 1, 1, 2], [1, 1, 2, 1], [1, 1, 2, 2], [1, 2, 1, 1], [1, 2, 1, 2], [1, 2, 1, 3],
    [1, 2, 2, 1], [1, 2, 2, 3], [1, 2, 3, 1], [1, 2, 3, 2], [1, 2, 3, 3], [1, 2, 4, 1],
    [1, 2, 4, 3], [1, 2, 4, 4], [1, 2, 4, 6], [1, 2, 4, 8], [1, 2, 5, 5], [1, 2, 5, 6],
    [1, 2, 6, 4], [1, 2, 6, 7], [1, 2, 8, 4], [1, 3, 1, 1], [1, 3, 1, 2], [1, 3, 2, 1],
    [1, 3, 2, 4], [1, 4, 1, 2], [1, 4, 2, 1], [1, 4, 2, 2], [1, 6, 2, 4], [1, 6, 3, 1],
    [1, 8, 2, 4], [1, 8, 4, 1], [1, 8, 4, 2], [1, 9, 2, 6], [1, 9, 3, 2], [1, 9, 6, 2],
    [2, 1, 1, 1], [2, 1, 1, 2], [2, 1, 2, 1], [2, 1, 2, 2], [2, 1, 4, 3], [2, 1, 4, 6],
    [2, 1, 5, 5], [2, 1, 6, 7], [2, 2, 1, 1], [2, 2, 1, 2], [2, 2, 2, 2], [2, 3, 1, 2],
    [2, 3, 2, 1], [2, 3, 2, 2], [2, 3, 6, 1], [2, 4, 2, 1], [2, 4, 2, 3], [2, 4, 3, 1],
    [2, 4, 3, 2], [2, 4, 4, 2], [2, 4, 6, 2], [2, 4, 8, 1], [2, 5, 4, 1], [2, 5, 6, 1],
    [2, 5, 6, 2], [2, 6, 3, 1], [2, 6, 7, 1], [2, 8, 4, 1], [3, 1, 1, 2], [3, 1, 2, 1],
    [3, 1, 2, 2], [3, 2, 1, 1], [3, 2, 1, 2], [3, 2, 2, 1], [3, 2, 3, 2], [3, 2, 4, 1],
    [3, 4, 2, 3], [3, 5, 6, 2], [3, 6, 2, 4], [3, 6, 8, 1], [4, 2, 2, 4], [4, 2, 3, 2],
    [4, 2, 4, 2], [4, 2, 4, 4], [4, 3, 2, 2], [4, 4, 2, 2], [6, 2, 3, 1], [6, 2, 4, 1],
    [6, 2, 4, 3], [6, 3, 1, 1], [6, 3, 1, 2], [6, 3, 2, 1], [6, 6, 3, 3], [8, 1, 2, 4],
    [8, 1, 4, 2], [8, 2, 1, 4], [8, 2, 4, 1], [9, 1, 2, 6], [9, 1, 6, 2], [9, 2, 1, 6],
    [9, 2, 6, 1], [9, 3, 1, 2], [9, 3, 2, 1], [9, 3, 2, 4],
]

# 演算子（表示用と計算用）
OPERATORS_DISPLAY = ['+', '−', '×', '÷']  # 表示用（全角マイナス、乗算、除算記号）
OPERATORS_EVAL = ['+', '-', '*', '/']      # 計算用

# 目標値
TARGETS = [5, 4, 3, 2, 1, 0]


def find_solution(numbers, target):
    """
    4つの数字と3つの演算子で目標値を作る解を探す
    64通り（4^3）の組み合わせを探索
    
    Args:
        numbers: 4つの数字のリスト
        target: 目標値
    
    Returns:
        解が見つかった場合は演算子のリスト（表示用）、見つからない場合はNone
    """
    for i in range(4):
        for j in range(4):
            for k in range(4):
                # 計算式を構築
                expr = f"{numbers[0]}{OPERATORS_EVAL[i]}{numbers[1]}{OPERATORS_EVAL[j]}{numbers[2]}{OPERATORS_EVAL[k]}{numbers[3]}"
                try:
                    result = eval(expr)
                    # 浮動小数点の誤差を考慮して比較
                    if abs(result - target) < 1e-9:
                        return [OPERATORS_DISPLAY[i], OPERATORS_DISPLAY[j], OPERATORS_DISPLAY[k]]
                except ZeroDivisionError:
                    continue
    return None


def find_all_solutions(numbers):
    """
    全ての目標値（5, 4, 3, 2, 1, 0）に対する解を探す
    
    Args:
        numbers: 4つの数字のリスト
    
    Returns:
        目標値をキー、演算子リストを値とする辞書
    """
    solutions = {}
    for target in TARGETS:
        solution = find_solution(numbers, target)
        solutions[target] = solution
    return solutions


def generate_svg(numbers, solutions, show_answers=False):
    """
    SVGを生成する
    
    Args:
        numbers: 4つの数字のリスト
        solutions: 解答の辞書
        show_answers: True=解答用紙、False=問題用紙
    
    Returns:
        SVG文字列
    """
    # SVGの設定（省スペース化）
    row_height = 28
    padding_top = 8
    padding_bottom = 8
    height = padding_top + len(TARGETS) * row_height + padding_bottom
    
    # 要素の位置設定（余白を詰める）
    start_x = 8
    num_width = 18      # 数字の幅
    box_size = 22       # 演算子ボックスのサイズ
    gap = 2             # 要素間の隙間
    
    # 幅を計算
    content_width = num_width * 4 + (box_size + gap * 2) * 3 + 20 + 18  # 数字4つ + ボックス3つ + = + 目標値
    width = start_x * 2 + content_width
    
    # フォント設定
    font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
    
    svg_parts = []
    
    # SVGヘッダー
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">')
    
    # スタイル定義
    svg_parts.append(f'''  <style>
    .number {{ font-family: {font_family}; font-size: 18px; fill: black; }}
    .operator {{ font-family: {font_family}; font-size: 16px; fill: black; }}
    .equal {{ font-family: {font_family}; font-size: 18px; fill: black; }}
    .target {{ font-family: {font_family}; font-size: 18px; fill: black; }}
    .box {{ fill: none; stroke: lightgray; stroke-width: 1; }}
  </style>''')
    
    # 各行を生成
    for row_idx, target in enumerate(TARGETS):
        y = padding_top + row_idx * row_height + row_height / 2
        x = start_x
        
        # 数字と演算子ボックスを交互に配置
        for i in range(4):
            # 数字
            svg_parts.append(f'  <text x="{x + num_width/2}" y="{y + 6}" class="number" text-anchor="middle">{numbers[i]}</text>')
            x += num_width
            
            if i < 3:
                # 演算子ボックス
                box_x = x + gap/2
                box_y = y - box_size/2
                svg_parts.append(f'  <rect x="{box_x}" y="{box_y}" width="{box_size}" height="{box_size}" class="box" rx="2" ry="2"/>')
                
                # 解答の場合は演算子を表示
                if show_answers and solutions[target]:
                    op = solutions[target][i]
                    svg_parts.append(f'  <text x="{box_x + box_size/2}" y="{y + 5}" class="operator" text-anchor="middle">{op}</text>')
                
                x += gap + box_size + gap
        
        # イコール記号
        x += gap
        svg_parts.append(f'  <text x="{x}" y="{y + 6}" class="equal">=</text>')
        
        # 目標値
        x += 15
        svg_parts.append(f'  <text x="{x}" y="{y + 6}" class="target">{target}</text>')
    
    # SVGフッター
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def main():
    """メイン関数"""
    # 今日の日付を取得
    today = date.today().strftime('%Y%m%d')
    
    # ランダムに問題を選択
    numbers = random.choice(PROBLEMS)
    
    print(f"選択された数字: {numbers}")
    
    # 全ての目標値に対する解を探す
    solutions = find_all_solutions(numbers)
    
    # 解答を表示
    print("\n解答:")
    for target in TARGETS:
        if solutions[target]:
            ops = solutions[target]
            print(f"  {numbers[0]} {ops[0]} {numbers[1]} {ops[1]} {numbers[2]} {ops[2]} {numbers[3]} = {target}")
        else:
            print(f"  目標値 {target}: 解なし")
    
    # 問題用SVGを生成
    problem_svg = generate_svg(numbers, solutions, show_answers=False)
    problem_filename = f"{today}_countdown.svg"
    with open(problem_filename, 'w', encoding='utf-8') as f:
        f.write(problem_svg)
    print(f"\n問題用紙を生成しました: {problem_filename}")
    
    # 解答用SVGを生成
    answer_svg = generate_svg(numbers, solutions, show_answers=True)
    answer_filename = f"{today}_countdown_ans.svg"
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f"解答用紙を生成しました: {answer_filename}")


if __name__ == '__main__':
    main()
