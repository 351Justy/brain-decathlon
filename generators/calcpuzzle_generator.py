#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calc Puzzle SVG Generator
問題と解答のSVGファイルを生成するスクリプト

必要なモジュール: なし（Python3標準ライブラリのみ使用）
"""

import random
import sys
import os
from datetime import datetime


# ============================================================
# 日付取得関数
# ============================================================
def get_date_prefix():
    """日付プレフィックスを取得（引数 > 環境変数 > 今日）"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if len(arg) == 8 and arg.isdigit():
            return arg
    if 'PUZZLE_DATE' in os.environ:
        return os.environ['PUZZLE_DATE']
    return datetime.now().strftime('%Y%m%d')


class PuzzleGenerator:
    """パズル生成クラス（HTMLのロジックを移植）"""
    
    def __init__(self):
        self.ops = ['+', '-', '*', '/']
    
    def rand_int(self, min_val, max_val):
        return random.randint(min_val, max_val)
    
    def rand_op(self):
        return random.choice(self.ops)
    
    def rand_vals(self, k):
        return random.sample(range(1, 10), k)
    
    def shuffle(self, arr):
        result = arr.copy()
        random.shuffle(result)
        return result
    
    def calc_with_precedence(self, a, b, c, op1, op2):
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        
        if precedence[op2] > precedence[op1]:
            if op2 == '+':
                middle_result = b + c
            elif op2 == '-':
                middle_result = b - c
            elif op2 == '*':
                middle_result = b * c
            elif op2 == '/':
                if c == 0 or b % c != 0:
                    return None
                middle_result = b // c
            else:
                return None
            
            if op1 == '+':
                return a + middle_result
            elif op1 == '-':
                return a - middle_result
            elif op1 == '*':
                return a * middle_result
            elif op1 == '/':
                if middle_result == 0 or a % middle_result != 0:
                    return None
                return a // middle_result
        else:
            if op1 == '+':
                result = a + b
            elif op1 == '-':
                result = a - b
            elif op1 == '*':
                result = a * b
            elif op1 == '/':
                if b == 0 or a % b != 0:
                    return None
                result = a // b
            else:
                return None
            
            if op2 == '+':
                result = result + c
            elif op2 == '-':
                result = result - c
            elif op2 == '*':
                result = result * c
            elif op2 == '/':
                if c == 0 or result % c != 0:
                    return None
                result = result // c
            
            return result
        
        return None
    
    def make_symbol_indices(self, num_symbols):
        counts = [1] * num_symbols
        filled = num_symbols
        
        while filled < 9:
            idx = self.rand_int(0, num_symbols - 1)
            if counts[idx] < 2:
                counts[idx] += 1
                filled += 1
        
        arr = []
        for i, c in enumerate(counts):
            for _ in range(c):
                arr.append(i)
        
        return self.shuffle(arr)
    
    def has_triple(self, symbol_indices):
        for r in range(3):
            if (symbol_indices[r*3] == symbol_indices[r*3+1] and 
                symbol_indices[r*3+1] == symbol_indices[r*3+2]):
                return True
        for c in range(3):
            if (symbol_indices[c] == symbol_indices[c+3] and 
                symbol_indices[c+3] == symbol_indices[c+6]):
                return True
        return False
    
    def duplicate_equation(self, row_info):
        for i in range(len(row_info)):
            for j in range(i + 1, len(row_info)):
                if (row_info[i]['pattern'] == row_info[j]['pattern'] and 
                    row_info[i]['op'] == row_info[j]['op']):
                    return True
        return False
    
    def attempt(self):
        num_symbols = self.rand_int(5, 6)
        values = self.rand_vals(num_symbols)
        symbol_indices = self.make_symbol_indices(num_symbols)
        
        if self.has_triple(symbol_indices):
            return None
        
        row_ops = []
        row_results = []
        row_info = []
        
        for r in range(3):
            op1 = self.rand_op()
            op2 = self.rand_op()
            v = [
                values[symbol_indices[r*3]],
                values[symbol_indices[r*3+1]],
                values[symbol_indices[r*3+2]]
            ]
            res = self.calc_with_precedence(v[0], v[1], v[2], op1, op2)
            
            if res is None or res == 0 or not isinstance(res, int) or res < -999 or res > 999:
                return None
            
            row_ops.append([op1, op2])
            row_results.append(res)
            row_info.append({
                'pattern': f"{symbol_indices[r*3]},{symbol_indices[r*3+1]},{symbol_indices[r*3+2]}",
                'op': f"{op1},{op2}"
            })
        
        col_ops = []
        col_results = []
        col_info = []
        
        for c in range(3):
            op1 = self.rand_op()
            op2 = self.rand_op()
            v = [
                values[symbol_indices[c]],
                values[symbol_indices[c+3]],
                values[symbol_indices[c+6]]
            ]
            res = self.calc_with_precedence(v[0], v[1], v[2], op1, op2)
            
            if res is None or res == 0 or not isinstance(res, int) or res < -999 or res > 999:
                return None
            
            col_ops.append([op1, op2])
            col_results.append(res)
            col_info.append({
                'pattern': f"{symbol_indices[c]},{symbol_indices[c+3]},{symbol_indices[c+6]}",
                'op': f"{op1},{op2}"
            })
        
        if len(set(row_results)) != 3:
            return None
        if len(set(col_results)) != 3:
            return None
        
        if self.duplicate_equation(row_info) or self.duplicate_equation(col_info):
            return None
        
        return {
            'num_symbols': num_symbols,
            'values': values,
            'symbol_indices': symbol_indices,
            'row_ops': row_ops,
            'col_ops': col_ops,
            'row_results': row_results,
            'col_results': col_results
        }
    
    def generate(self):
        for _ in range(3000):
            puzzle = self.attempt()
            if puzzle:
                return puzzle
        return self.fallback_simple()
    
    def fallback_simple(self):
        return {
            'num_symbols': 5,
            'values': [1, 2, 3, 4, 5],
            'symbol_indices': [0, 1, 2, 1, 2, 3, 2, 3, 4],
            'row_ops': [['+', '+'], ['+', '-'], ['+', '+']],
            'col_ops': [['+', '+'], ['+', '+'], ['+', '+']],
            'row_results': [6, 2, 10],
            'col_results': [6, 6, 10]
        }


def cos_approx(angle):
    import math
    return math.cos(angle)


def sin_approx(angle):
    import math
    return math.sin(angle)


class SVGGenerator:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.width = 200
        self.height = 180
        self.symbol_size = 32
        self.font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
        self.used_symbols = list(range(puzzle['num_symbols']))
        random.shuffle(self.used_symbols)
    
    def get_x_position(self, element_type, index):
        if element_type == 'symbol':
            return 30 + index * 55
        elif element_type == 'op':
            return 57 + index * 55
        elif element_type == 'eq':
            return 165
        elif element_type == 'result':
            return 185
        return 0
    
    def get_y_position(self, element_type, index):
        y = 30 + index * 50
        if element_type == 'op':
            y = 55 + index * 50
        elif element_type == 'eq':
            y = 165
        elif element_type == 'result':
            y = 180
        return y
    
    def draw_symbol(self, symbol_type, cx, cy, size):
        stroke_color = "#B0B0B0"
        stroke_width = "2.5"
        fill = "none"
        half = size // 2
        
        if symbol_type == 0:
            return f'<circle cx="{cx}" cy="{cy}" r="{half - 2}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        elif symbol_type == 1:
            points = []
            for i in range(6):
                angle = (i * 60 - 90) * 3.14159 / 180
                px = cx + (half - 2) * 0.95 * round(cos_approx(angle), 4)
                py = cy + (half - 2) * 0.95 * round(sin_approx(angle), 4)
                points.append(f"{px},{py}")
            return f'<polygon points="{" ".join(points)}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        elif symbol_type == 2:
            p1 = f"{cx},{cy - half + 3}"
            p2 = f"{cx + half - 3},{cy + half - 5}"
            p3 = f"{cx - half + 3},{cy + half - 5}"
            return f'<polygon points="{p1} {p2} {p3}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        elif symbol_type == 3:
            points = []
            outer_r = half - 2
            inner_r = outer_r * 0.4
            for i in range(10):
                angle = (i * 36 - 90) * 3.14159 / 180
                r = outer_r if i % 2 == 0 else inner_r
                px = cx + r * round(cos_approx(angle), 4)
                py = cy + r * round(sin_approx(angle), 4)
                points.append(f"{px},{py}")
            return f'<polygon points="{" ".join(points)}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        elif symbol_type == 4:
            points = []
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                px = cx + (half - 3) * round(cos_approx(angle), 4)
                py = cy + (half - 3) * round(sin_approx(angle), 4)
                points.append(f"{px},{py}")
            return f'<polygon points="{" ".join(points)}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        elif symbol_type == 5:
            w = size - 6
            h = size * 0.55
            rx = h / 2
            return f'<rect x="{cx - w//2}" y="{cy - h//2}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        return ""
    
    def disp_op(self, op):
        if op == '*':
            return '×'
        elif op == '/':
            return '÷'
        return op
    
    def generate_svg(self, show_answer=False):
        elements = []
        elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">')
        
        symbol_y_offset = -2
        for row in range(3):
            for col in range(3):
                symbol_idx = row * 3 + col
                sym_type = self.puzzle['symbol_indices'][symbol_idx]
                actual_symbol = self.used_symbols[sym_type]
                
                cx = self.get_x_position('symbol', col)
                cy = self.get_y_position('symbol', row) + symbol_y_offset
                
                elements.append(self.draw_symbol(actual_symbol, cx, cy, self.symbol_size))
                
                if show_answer:
                    value = self.puzzle['values'][sym_type]
                    elements.append(
                        f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                        f'font-family="{self.font_family}" font-size="22" fill="black">{value}</text>'
                    )
        
        for row in range(3):
            for op_idx in range(2):
                op = self.puzzle['row_ops'][row][op_idx]
                cx = self.get_x_position('op', op_idx)
                cy = self.get_y_position('symbol', row)
                elements.append(
                    f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                    f'font-family="{self.font_family}" font-size="20" fill="black">{self.disp_op(op)}</text>'
                )
        
        for op_row in range(2):
            for col in range(3):
                op = self.puzzle['col_ops'][col][op_row]
                cx = self.get_x_position('symbol', col)
                cy = self.get_y_position('op', op_row)
                elements.append(
                    f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                    f'font-family="{self.font_family}" font-size="20" fill="black">{self.disp_op(op)}</text>'
                )
        
        for row in range(3):
            cx = self.get_x_position('eq', 0)
            cy = self.get_y_position('symbol', row)
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">=</text>'
            )
            cx = self.get_x_position('result', 0)
            result = self.puzzle['row_results'][row]
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">{result}</text>'
            )
        
        for col in range(3):
            cx = self.get_x_position('symbol', col)
            cy = self.get_y_position('eq', 0)
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">=</text>'
            )
            cy = self.get_y_position('result', 0)
            result = self.puzzle['col_results'][col]
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">{result}</text>'
            )
        
        elements.append('</svg>')
        return '\n'.join(elements)


def main():
    today = get_date_prefix()
    
    puzzle_filename = f"{today}_calcpuzzle.svg"
    answer_filename = f"{today}_calcpuzzle_ans.svg"
    
    print("=" * 50)
    print("Calc Puzzle SVG Generator")
    print("=" * 50)
    
    print("\nパズルを生成中...")
    generator = PuzzleGenerator()
    puzzle = generator.generate()
    
    print(f"  シンボル数: {puzzle['num_symbols']}")
    print(f"  値: {puzzle['values']}")
    
    print("\nSVGを生成中...")
    svg_gen = SVGGenerator(puzzle)
    
    puzzle_svg = svg_gen.generate_svg(show_answer=False)
    with open(puzzle_filename, 'w', encoding='utf-8') as f:
        f.write(puzzle_svg)
    print(f"  問題ファイル: {puzzle_filename}")
    
    answer_svg = svg_gen.generate_svg(show_answer=True)
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f"  解答ファイル: {answer_filename}")
    
    print("\n生成完了!")
    print("=" * 50)
    
    print("\n【パズル情報】")
    print(f"シンボルと値の対応:")
    for i, val in enumerate(puzzle['values']):
        print(f"  シンボル{i}: {val}")
    
    print(f"\n行の式:")
    for r in range(3):
        ops = puzzle['row_ops'][r]
        res = puzzle['row_results'][r]
        indices = [puzzle['symbol_indices'][r*3+c] for c in range(3)]
        vals = [puzzle['values'][idx] for idx in indices]
        print(f"  {vals[0]} {ops[0]} {vals[1]} {ops[1]} {vals[2]} = {res}")
    
    print(f"\n列の式:")
    for c in range(3):
        ops = puzzle['col_ops'][c]
        res = puzzle['col_results'][c]
        indices = [puzzle['symbol_indices'][c+r*3] for r in range(3)]
        vals = [puzzle['values'][idx] for idx in indices]
        print(f"  {vals[0]} {ops[0]} {vals[1]} {ops[1]} {vals[2]} = {res}")


if __name__ == "__main__":
    main()
