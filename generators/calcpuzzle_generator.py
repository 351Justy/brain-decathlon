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
    
    # DejaVu Sans グリフデータ（Units per Em: 2048）
    # 元データはTTF座標系（Y軸上向き）
    GLYPH_DATA = {
        '0': {
            'path': 'M651 1360Q495 1360 416.5 1206.5Q338 1053 338 745Q338 438 416.5 284.5Q495 131 651 131Q808 131 886.5 284.5Q965 438 965 745Q965 1053 886.5 1206.5Q808 1360 651 1360ZM651 1520Q902 1520 1034.5 1321.5Q1167 1123 1167 745Q1167 368 1034.5 169.5Q902 -29 651 -29Q400 -29 267.5 169.5Q135 368 135 745Q135 1123 267.5 1321.5Q400 1520 651 1520Z',
            'width': 1303,
            'bounds': (135, -29, 1167, 1520),
        },
        '1': {
            'path': 'M254 170H584V1309L225 1237V1421L582 1493H784V170H1114V0H254Z',
            'width': 1303,
            'bounds': (225, 0, 1114, 1493),
        },
        '2': {
            'path': 'M393 170H1098V0H150V170Q265 289 463.5 489.5Q662 690 713 748Q810 857 848.5 932.5Q887 1008 887 1081Q887 1200 803.5 1275.0Q720 1350 586 1350Q491 1350 385.5 1317.0Q280 1284 160 1217V1421Q282 1470 388.0 1495.0Q494 1520 582 1520Q814 1520 952.0 1404.0Q1090 1288 1090 1094Q1090 1002 1055.5 919.5Q1021 837 930 725Q905 696 771.0 557.5Q637 419 393 170Z',
            'width': 1303,
            'bounds': (150, 0, 1098, 1520),
        },
        '3': {
            'path': 'M831 805Q976 774 1057.5 676.0Q1139 578 1139 434Q1139 213 987.0 92.0Q835 -29 555 -29Q461 -29 361.5 -10.5Q262 8 156 45V240Q240 191 340.0 166.0Q440 141 549 141Q739 141 838.5 216.0Q938 291 938 434Q938 566 845.5 640.5Q753 715 588 715H414V881H596Q745 881 824.0 940.5Q903 1000 903 1112Q903 1227 821.5 1288.5Q740 1350 588 1350Q505 1350 410.0 1332.0Q315 1314 201 1276V1456Q316 1488 416.5 1504.0Q517 1520 606 1520Q836 1520 970.0 1415.5Q1104 1311 1104 1133Q1104 1009 1033.0 923.5Q962 838 831 805Z',
            'width': 1303,
            'bounds': (156, -29, 1139, 1520),
        },
        '4': {
            'path': 'M774 1317 264 520H774ZM721 1493H975V520H1188V352H975V0H774V352H100V547Z',
            'width': 1303,
            'bounds': (100, 0, 1188, 1493),
        },
        '5': {
            'path': 'M221 1493H1014V1323H406V957Q450 972 494.0 979.5Q538 987 582 987Q832 987 978.0 850.0Q1124 713 1124 479Q1124 238 974.0 104.5Q824 -29 551 -29Q457 -29 359.5 -13.0Q262 3 158 35V238Q248 189 344.0 165.0Q440 141 547 141Q720 141 821.0 232.0Q922 323 922 479Q922 635 821.0 726.0Q720 817 547 817Q466 817 385.5 799.0Q305 781 221 743Z',
            'width': 1303,
            'bounds': (158, -29, 1124, 1493),
        },
        '6': {
            'path': 'M676 827Q540 827 460.5 734.0Q381 641 381 479Q381 318 460.5 224.5Q540 131 676 131Q812 131 891.5 224.5Q971 318 971 479Q971 641 891.5 734.0Q812 827 676 827ZM1077 1460V1276Q1001 1312 923.5 1331.0Q846 1350 770 1350Q570 1350 464.5 1215.0Q359 1080 344 807Q403 894 492.0 940.5Q581 987 688 987Q913 987 1043.5 850.5Q1174 714 1174 479Q1174 249 1038.0 110.0Q902 -29 676 -29Q417 -29 280.0 169.5Q143 368 143 745Q143 1099 311.0 1309.5Q479 1520 762 1520Q838 1520 915.5 1505.0Q993 1490 1077 1460Z',
            'width': 1303,
            'bounds': (143, -29, 1174, 1520),
        },
        '7': {
            'path': 'M168 1493H1128V1407L586 0H375L885 1323H168Z',
            'width': 1303,
            'bounds': (168, 0, 1128, 1493),
        },
        '8': {
            'path': 'M651 709Q507 709 424.5 632.0Q342 555 342 420Q342 285 424.5 208.0Q507 131 651 131Q795 131 878.0 208.5Q961 286 961 420Q961 555 878.5 632.0Q796 709 651 709ZM449 795Q319 827 246.5 916.0Q174 1005 174 1133Q174 1312 301.5 1416.0Q429 1520 651 1520Q874 1520 1001.0 1416.0Q1128 1312 1128 1133Q1128 1005 1055.5 916.0Q983 827 854 795Q1000 761 1081.5 662.0Q1163 563 1163 420Q1163 203 1030.5 87.0Q898 -29 651 -29Q404 -29 271.5 87.0Q139 203 139 420Q139 563 221.0 662.0Q303 761 449 795ZM375 1114Q375 998 447.5 933.0Q520 868 651 868Q781 868 854.5 933.0Q928 998 928 1114Q928 1230 854.5 1295.0Q781 1360 651 1360Q520 1360 447.5 1295.0Q375 1230 375 1114Z',
            'width': 1303,
            'bounds': (139, -29, 1163, 1520),
        },
        '9': {
            'path': 'M225 31V215Q301 179 379.0 160.0Q457 141 532 141Q732 141 837.5 275.5Q943 410 958 684Q900 598 811.0 552.0Q722 506 614 506Q390 506 259.5 641.5Q129 777 129 1012Q129 1242 265.0 1381.0Q401 1520 627 1520Q886 1520 1022.5 1321.5Q1159 1123 1159 745Q1159 392 991.5 181.5Q824 -29 541 -29Q465 -29 387.0 -14.0Q309 1 225 31ZM627 664Q763 664 842.5 757.0Q922 850 922 1012Q922 1173 842.5 1266.5Q763 1360 627 1360Q491 1360 411.5 1266.5Q332 1173 332 1012Q332 850 411.5 757.0Q491 664 627 664Z',
            'width': 1303,
            'bounds': (129, -29, 1159, 1520),
        },
        '-': {
            'path': 'M100 643H639V479H100Z',
            'width': 739,
            'bounds': (100, 479, 639, 643),
        },
        '+': {
            'path': 'M942 1284V727H1499V557H942V0H774V557H217V727H774V1284Z',
            'width': 1716,
            'bounds': (217, 0, 1499, 1284),
        },
        '=': {
            'path': 'M217 930H1499V762H217ZM217 522H1499V352H217Z',
            'width': 1716,
            'bounds': (217, 352, 1499, 930),
        },
        '×': {
            'path': 'M1436 1100 979 641 1436 184 1317 63 858 522 399 63 281 184 737 641 281 1100 399 1221 858 762 1317 1221Z',
            'width': 1716,
            'bounds': (281, 63, 1436, 1221),
        },
        '÷': {
            'path': 'M735 1135H981V889H735ZM735 395H981V150H735ZM217 727H1499V557H217Z',
            'width': 1716,
            'bounds': (217, 150, 1499, 1135),
        },
    }
    
    UNITS_PER_EM = 2048
    
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
    
    def draw_glyph(self, char, cx, cy, font_size):
        """DejaVu Sansのグリフをパスとして描画（フォントサイズベース）"""
        if char not in self.GLYPH_DATA:
            return ''
        
        data = self.GLYPH_DATA[char]
        bounds = data['bounds']
        width = data['width']
        xMin, yMin, xMax, yMax = bounds
        
        # フォントサイズベースのスケール計算
        # Units per Em (2048) を基準にスケーリング
        scale = font_size / self.UNITS_PER_EM
        
        # グリフの中心を計算（幅はadvance widthを使用）
        glyph_cx = width / 2
        # 高さは数字のベースライン基準（0がベースライン、上がプラス）
        # 数字の典型的な高さは0〜1493程度なので、中央を約746とする
        glyph_cy = 746  # 数字の視覚的中央
        
        # 変換：TTF座標系からSVG座標系へ
        transform = f"translate({cx},{cy}) scale({scale},-{scale}) translate({-glyph_cx},{-glyph_cy})"
        
        return f'<path d="{data["path"]}" transform="{transform}" fill="black"/>'
    
    def draw_number(self, number, cx, cy, font_size=18):
        """数字をパスとして描画（複数桁対応）"""
        num_str = str(number)
        elements = []
        
        # フォントサイズベースのスケール
        scale = font_size / self.UNITS_PER_EM
        
        # 各桁の幅を計算
        char_widths = []
        for char in num_str:
            if char in self.GLYPH_DATA:
                char_widths.append(self.GLYPH_DATA[char]['width'] * scale)
            else:
                char_widths.append(font_size * 0.6)
        
        total_width = sum(char_widths)
        current_x = cx - total_width / 2
        
        for i, char in enumerate(num_str):
            char_cx = current_x + char_widths[i] / 2
            elements.append(self.draw_glyph(char, char_cx, cy, font_size))
            current_x += char_widths[i]
        
        return '\n'.join(elements)
    
    def draw_operator(self, op, cx, cy, font_size=20):
        """演算子をパスとして描画"""
        op_char = self.disp_op(op)
        return self.draw_glyph(op_char, cx, cy, font_size)
    
    def draw_equals(self, cx, cy, font_size=20):
        """イコールをパスとして描画"""
        return self.draw_glyph('=', cx, cy, font_size)
    
    def generate_svg(self, show_answer=False):
        """SVGを生成"""
        elements = []
        
        # SVGヘッダー
        elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">')
        
        # シンボル描画（3x3グリッド）
        symbol_y_offset = -3  # シンボルを少し上げる調整値
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
                    # 解答：数字を表示（パスで描画）
                    value = self.puzzle['values'][sym_type]
                    elements.append(self.draw_number(value, cx, cy, font_size=28))
        
        # 行の演算子（シンボル間）
        for row in range(3):
            for op_idx in range(2):
                op = self.puzzle['row_ops'][row][op_idx]
                cx = self.get_x_position('op', op_idx)
                cy = self.get_y_position('symbol', row) + symbol_y_offset
                elements.append(self.draw_operator(op, cx, cy, font_size=20))
        
        # 列の演算子（シンボル行の間）
        for op_row in range(2):
            for col in range(3):
                op = self.puzzle['col_ops'][col][op_row]
                cx = self.get_x_position('symbol', col)
                cy = self.get_y_position('op', op_row)
                elements.append(self.draw_operator(op, cx, cy, font_size=20))
        
        # 行のイコールと結果
        for row in range(3):
            # イコール
            cx = self.get_x_position('eq', 0)
            cy = self.get_y_position('symbol', row) + symbol_y_offset
            elements.append(self.draw_equals(cx, cy, font_size=18))
            
            # 結果
            cx = self.get_x_position('result', 0)
            result = self.puzzle['row_results'][row]
            elements.append(self.draw_number(result, cx, cy, font_size=20))
        
        # 列のイコールと結果
        for col in range(3):
            # イコール
            cx = self.get_x_position('symbol', col)
            cy = self.get_y_position('eq', 0)
            elements.append(self.draw_equals(cx, cy, font_size=18))
            
            # 結果
            cy = self.get_y_position('result', 0)
            result = self.puzzle['col_results'][col]
            elements.append(self.draw_number(result, cx, cy, font_size=20))
        
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
