#!/usr/bin/env python3
"""
カウントダウン計算 問題・解答SVG生成スクリプト
"""

import random
import sys
import os
from datetime import date

def get_date_prefix():
    """日付プレフィックスを取得（引数 > 環境変数 > 今日）"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if len(arg) == 8 and arg.isdigit():
            return arg
    if 'PUZZLE_DATE' in os.environ:
        return os.environ['PUZZLE_DATE']
    return date.today().strftime('%Y%m%d')

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

OPERATORS_DISPLAY = ['+', '−', '×', '÷']
OPERATORS_EVAL = ['+', '-', '*', '/']
TARGETS = [5, 4, 3, 2, 1, 0]

def find_solution(numbers, target):
    for i in range(4):
        for j in range(4):
            for k in range(4):
                expr = f"{numbers[0]}{OPERATORS_EVAL[i]}{numbers[1]}{OPERATORS_EVAL[j]}{numbers[2]}{OPERATORS_EVAL[k]}{numbers[3]}"
                try:
                    result = eval(expr)
                    if abs(result - target) < 1e-9:
                        return [OPERATORS_DISPLAY[i], OPERATORS_DISPLAY[j], OPERATORS_DISPLAY[k]]
                except ZeroDivisionError:
                    continue
    return None

def find_all_solutions(numbers):
    solutions = {}
    for target in TARGETS:
        solutions[target] = find_solution(numbers, target)
    return solutions

def generate_svg(numbers, solutions, show_answers=False):
    row_height = 28
    padding_top = 8
    padding_bottom = 8
    height = padding_top + len(TARGETS) * row_height + padding_bottom
    
    start_x = 8
    num_width = 18
    box_size = 22
    gap = 2
    
    content_width = num_width * 4 + (box_size + gap * 2) * 3 + 20 + 18
    width = start_x * 2 + content_width
    
    font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
    
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">')
    svg_parts.append(f'''  <style>
    .number {{ font-family: {font_family}; font-size: 18px; fill: black; }}
    .operator {{ font-family: {font_family}; font-size: 16px; fill: black; }}
    .equal {{ font-family: {font_family}; font-size: 18px; fill: black; }}
    .target {{ font-family: {font_family}; font-size: 18px; fill: black; }}
    .box {{ fill: none; stroke: lightgray; stroke-width: 1; }}
  </style>''')
    
    for row_idx, target in enumerate(TARGETS):
        y = padding_top + row_idx * row_height + row_height / 2
        x = start_x
        
        for i in range(4):
            svg_parts.append(f'  <text x="{x + num_width/2}" y="{y + 6}" class="number" text-anchor="middle">{numbers[i]}</text>')
            x += num_width
            
            if i < 3:
                box_x = x + gap/2
                box_y = y - box_size/2
                svg_parts.append(f'  <rect x="{box_x}" y="{box_y}" width="{box_size}" height="{box_size}" class="box" rx="2" ry="2"/>')
                
                if show_answers and solutions[target]:
                    op = solutions[target][i]
                    svg_parts.append(f'  <text x="{box_x + box_size/2}" y="{y + 5}" class="operator" text-anchor="middle">{op}</text>')
                
                x += gap + box_size + gap
        
        x += gap
        svg_parts.append(f'  <text x="{x}" y="{y + 6}" class="equal">=</text>')
        x += 15
        svg_parts.append(f'  <text x="{x}" y="{y + 6}" class="target">{target}</text>')
    
    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)

def main():
    today = get_date_prefix()
    numbers = random.choice(PROBLEMS)
    
    print(f"選択された数字: {numbers}")
    
    solutions = find_all_solutions(numbers)
    
    print("\n解答:")
    for target in TARGETS:
        if solutions[target]:
            ops = solutions[target]
            print(f"  {numbers[0]} {ops[0]} {numbers[1]} {ops[1]} {numbers[2]} {ops[2]} {numbers[3]} = {target}")
        else:
            print(f"  目標値 {target}: 解なし")
    
    problem_svg = generate_svg(numbers, solutions, show_answers=False)
    problem_filename = f"{today}_countdown.svg"
    with open(problem_filename, 'w', encoding='utf-8') as f:
        f.write(problem_svg)
    print(f"\n問題用紙を生成しました: {problem_filename}")
    
    answer_svg = generate_svg(numbers, solutions, show_answers=True)
    answer_filename = f"{today}_countdown_ans.svg"
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f"解答用紙を生成しました: {answer_filename}")

if __name__ == '__main__':
    main()
