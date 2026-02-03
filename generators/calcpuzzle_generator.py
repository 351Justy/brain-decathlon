#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calc Puzzle SVG Generator
問題と解答のSVGファイルを生成するスクリプト

必要なモジュール: なし（Python3標準ライブラリのみ使用）
"""

import random
import os
from datetime import datetime


class PuzzleGenerator:
    """パズル生成クラス（HTMLのロジックを移植）"""
    
    def __init__(self):
        # 全演算子を使用
        self.ops = ['+', '-', '*', '/']
    
    def rand_int(self, min_val, max_val):
        """min_val以上max_val以下のランダムな整数を返す"""
        return random.randint(min_val, max_val)
    
    def rand_op(self):
        """ランダムな演算子を返す"""
        return random.choice(self.ops)
    
    def rand_vals(self, k):
        """1〜9の中からk個の異なる値を返す"""
        return random.sample(range(1, 10), k)
    
    def shuffle(self, arr):
        """配列をシャッフルして返す"""
        result = arr.copy()
        random.shuffle(result)
        return result
    
    def calc_with_precedence(self, a, b, c, op1, op2):
        """演算子の優先順位を考慮して a op1 b op2 c を計算"""
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        
        # op2の優先順位がop1より高い場合、先にb op2 cを計算
        if precedence[op2] > precedence[op1]:
            # 先にb op2 cを計算
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
            
            # 次にa op1 middle_resultを計算
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
            # 左から順に計算
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
        """9マスのシンボルインデックスを生成（各記号最大2回）"""
        counts = [1] * num_symbols  # まず全記号1回
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
        """行・列で同じ記号が3連続かチェック"""
        # 行チェック
        for r in range(3):
            if (symbol_indices[r*3] == symbol_indices[r*3+1] and 
                symbol_indices[r*3+1] == symbol_indices[r*3+2]):
                return True
        # 列チェック
        for c in range(3):
            if (symbol_indices[c] == symbol_indices[c+3] and 
                symbol_indices[c+3] == symbol_indices[c+6]):
                return True
        return False
    
    def duplicate_equation(self, row_info):
        """行・列の式が重複していないかチェック"""
        for i in range(len(row_info)):
            for j in range(i + 1, len(row_info)):
                if (row_info[i]['pattern'] == row_info[j]['pattern'] and 
                    row_info[i]['op'] == row_info[j]['op']):
                    return True
        return False
    
    def attempt(self):
        """パズル生成を1回試行"""
        num_symbols = self.rand_int(5, 6)  # 5〜6種
        values = self.rand_vals(num_symbols)
        symbol_indices = self.make_symbol_indices(num_symbols)
        
        # 3連続チェック
        if self.has_triple(symbol_indices):
            return None
        
        # 行式作成
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
        
        # 列式作成
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
        
        # 行・列の結果が重複していないかチェック
        if len(set(row_results)) != 3:
            return None
        if len(set(col_results)) != 3:
            return None
        
        # 式の重複チェック
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
        """パズルを生成（最大3000回試行）"""
        for _ in range(3000):
            puzzle = self.attempt()
            if puzzle:
                return puzzle
        
        # フォールバック（通常は呼ばれない）
        return self.fallback_simple()
    
    def fallback_simple(self):
        """緊急用フォールバック"""
        return {
            'num_symbols': 5,
            'values': [1, 2, 3, 4, 5],
            'symbol_indices': [0, 1, 2, 1, 2, 3, 2, 3, 4],
            'row_ops': [['+', '+'], ['+', '-'], ['+', '+']],
            'col_ops': [['+', '-'], ['+', '+'], ['-', '+']],
            'row_results': [6, 2, 7],
            'col_results': [5, 8, -1]
        }


class SVGGenerator:
    """SVG生成クラス"""
    
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
        
        # レイアウト設定（省スペース版）
        self.symbol_size = 48
        self.op_width = 28
        self.eq_width = 24
        self.result_width = 44
        self.row_gap = 4
        self.col_gap = 2
        self.margin = 12
        
        # 横幅計算: シンボル3 + 演算子2 + イコール1 + 結果1
        self.width = (self.margin * 2 + 
                      self.symbol_size * 3 + 
                      self.op_width * 2 + 
                      self.eq_width + 
                      self.result_width + 
                      self.col_gap * 6)
        
        # 縦幅計算: シンボル行3 + 演算子行2 + イコール行1 + 結果行1
        self.height = (self.margin * 2 + 
                       self.symbol_size * 3 + 
                       self.op_width * 2 + 
                       self.eq_width + 
                       self.op_width + 
                       self.row_gap * 6)
        
        # 使用するシンボルをランダムに選択
        all_symbol_types = list(range(6))
        random.shuffle(all_symbol_types)
        self.used_symbols = all_symbol_types[:puzzle['num_symbols']]
    
    def get_x_position(self, col_type, col_index):
        """X座標を取得（col_type: 'symbol','op','eq','result'）"""
        x = self.margin
        
        if col_type == 'symbol':
            # シンボル列: 0, 1, 2
            x += col_index * (self.symbol_size + self.col_gap + self.op_width + self.col_gap)
            x += self.symbol_size // 2
        elif col_type == 'op':
            # 演算子列: 0, 1
            x += self.symbol_size + self.col_gap
            x += col_index * (self.op_width + self.col_gap + self.symbol_size + self.col_gap)
            x += self.op_width // 2
        elif col_type == 'eq':
            x += (self.symbol_size + self.col_gap + self.op_width + self.col_gap) * 2 + self.symbol_size + self.col_gap
            x += self.eq_width // 2
        elif col_type == 'result':
            x += (self.symbol_size + self.col_gap + self.op_width + self.col_gap) * 2 + self.symbol_size + self.col_gap + self.eq_width + self.col_gap
            x += self.result_width // 2
        
        return x
    
    def get_y_position(self, row_type, row_index):
        """Y座標を取得（row_type: 'symbol','op','eq','result'）"""
        y = self.margin
        
        if row_type == 'symbol':
            # シンボル行: 0, 1, 2
            y += row_index * (self.symbol_size + self.row_gap + self.op_width + self.row_gap)
            y += self.symbol_size // 2
        elif row_type == 'op':
            # 演算子行: 0, 1
            y += self.symbol_size + self.row_gap
            y += row_index * (self.op_width + self.row_gap + self.symbol_size + self.row_gap)
            y += self.op_width // 2
        elif row_type == 'eq':
            y += (self.symbol_size + self.row_gap + self.op_width + self.row_gap) * 2 + self.symbol_size + self.row_gap
            y += self.eq_width // 2
        elif row_type == 'result':
            y += (self.symbol_size + self.row_gap + self.op_width + self.row_gap) * 2 + self.symbol_size + self.row_gap + self.eq_width + self.row_gap
            y += self.op_width // 2
        
        return y
    
    def draw_symbol(self, symbol_type, cx, cy, size):
        """シンボルをSVG要素として返す（ライトグレー線で中空描画）"""
        stroke_color = "#B0B0B0"  # ライトグレー
        stroke_width = "2.5"
        fill = "none"  # 中空
        half = size // 2
        
        if symbol_type == 0:
            # 円
            return f'<circle cx="{cx}" cy="{cy}" r="{half - 2}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        
        elif symbol_type == 1:
            # 六角形
            points = []
            for i in range(6):
                angle = (i * 60 - 90) * 3.14159 / 180
                px = cx + (half - 2) * 0.95 * round(cos_approx(angle), 4)
                py = cy + (half - 2) * 0.95 * round(sin_approx(angle), 4)
                points.append(f"{px},{py}")
            return f'<polygon points="{" ".join(points)}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        
        elif symbol_type == 2:
            # 三角形
            p1 = f"{cx},{cy - half + 3}"
            p2 = f"{cx + half - 3},{cy + half - 5}"
            p3 = f"{cx - half + 3},{cy + half - 5}"
            return f'<polygon points="{p1} {p2} {p3}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        
        elif symbol_type == 3:
            # 星（五芒星）
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
            # 五角形
            points = []
            for i in range(5):
                angle = (i * 72 - 90) * 3.14159 / 180
                px = cx + (half - 3) * round(cos_approx(angle), 4)
                py = cy + (half - 3) * round(sin_approx(angle), 4)
                points.append(f"{px},{py}")
            return f'<polygon points="{" ".join(points)}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        
        elif symbol_type == 5:
            # カプセル形（横長の角丸長方形）
            w = size - 6
            h = size * 0.55
            rx = h / 2
            return f'<rect x="{cx - w//2}" y="{cy - h//2}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
        
        return ""
    
    def disp_op(self, op):
        """演算子を表示用に変換"""
        if op == '*':
            return '×'
        elif op == '/':
            return '÷'
        return op
    
    def generate_svg(self, show_answer=False):
        """SVGを生成"""
        elements = []
        
        # SVGヘッダー
        elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">')
        
        # シンボル描画（3x3グリッド）
        symbol_y_offset = -2  # シンボルを少し上げる調整値
        for row in range(3):
            for col in range(3):
                symbol_idx = row * 3 + col
                sym_type = self.puzzle['symbol_indices'][symbol_idx]
                actual_symbol = self.used_symbols[sym_type]
                
                cx = self.get_x_position('symbol', col)
                cy = self.get_y_position('symbol', row) + symbol_y_offset
                
                # シンボル描画
                elements.append(self.draw_symbol(actual_symbol, cx, cy, self.symbol_size))
                
                if show_answer:
                    # 解答：数字を表示
                    value = self.puzzle['values'][sym_type]
                    elements.append(
                        f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                        f'font-family="{self.font_family}" font-size="22" fill="black">{value}</text>'
                    )
        
        # 行の演算子（シンボル間）
        for row in range(3):
            for op_idx in range(2):
                op = self.puzzle['row_ops'][row][op_idx]
                cx = self.get_x_position('op', op_idx)
                cy = self.get_y_position('symbol', row)
                elements.append(
                    f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                    f'font-family="{self.font_family}" font-size="20" fill="black">{self.disp_op(op)}</text>'
                )
        
        # 列の演算子（シンボル行の間）
        for op_row in range(2):
            for col in range(3):
                op = self.puzzle['col_ops'][col][op_row]
                cx = self.get_x_position('symbol', col)
                cy = self.get_y_position('op', op_row)
                elements.append(
                    f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                    f'font-family="{self.font_family}" font-size="20" fill="black">{self.disp_op(op)}</text>'
                )
        
        # 行のイコールと結果
        for row in range(3):
            # イコール
            cx = self.get_x_position('eq', 0)
            cy = self.get_y_position('symbol', row)
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">=</text>'
            )
            # 結果
            cx = self.get_x_position('result', 0)
            result = self.puzzle['row_results'][row]
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">{result}</text>'
            )
        
        # 列のイコールと結果
        for col in range(3):
            # イコール
            cx = self.get_x_position('symbol', col)
            cy = self.get_y_position('eq', 0)
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">=</text>'
            )
            # 結果
            cy = self.get_y_position('result', 0)
            result = self.puzzle['col_results'][col]
            elements.append(
                f'<text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
                f'font-family="{self.font_family}" font-size="20" fill="black">{result}</text>'
            )
        
        elements.append('</svg>')
        return '\n'.join(elements)


def cos_approx(angle):
    """cosの近似計算（mathモジュール不使用）"""
    import math
    return math.cos(angle)


def sin_approx(angle):
    """sinの近似計算（mathモジュール不使用）"""
    import math
    return math.sin(angle)


def main():
    """メイン処理"""
    # 日付取得
    today = datetime.now().strftime('%Y%m%d')
    
    # 出力ファイル名
    puzzle_filename = f"{today}_calcpuzzle.svg"
    answer_filename = f"{today}_calcpuzzle_ans.svg"
    
    print("=" * 50)
    print("Calc Puzzle SVG Generator")
    print("=" * 50)
    
    # パズル生成
    print("\nパズルを生成中...")
    generator = PuzzleGenerator()
    puzzle = generator.generate()
    
    print(f"  シンボル数: {puzzle['num_symbols']}")
    print(f"  値: {puzzle['values']}")
    
    # SVG生成
    print("\nSVGを生成中...")
    svg_gen = SVGGenerator(puzzle)
    
    # 問題SVG
    puzzle_svg = svg_gen.generate_svg(show_answer=False)
    with open(puzzle_filename, 'w', encoding='utf-8') as f:
        f.write(puzzle_svg)
    print(f"  問題ファイル: {puzzle_filename}")
    
    # 解答SVG
    answer_svg = svg_gen.generate_svg(show_answer=True)
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f"  解答ファイル: {answer_filename}")
    
    print("\n生成完了!")
    print("=" * 50)
    
    # パズル情報表示
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
