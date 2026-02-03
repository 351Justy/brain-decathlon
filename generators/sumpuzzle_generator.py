#!/usr/bin/env python3
"""
Sum Puzzle Generator
6×6のサムパズル問題と解答のSVGファイルを生成するスクリプト

必要なモジュール: なし（Python標準ライブラリのみ使用）
- random: 乱数生成
- datetime: 日付取得
- os: ファイル操作
"""

import random
from datetime import datetime
import os


class PuzzleSolver:
    """パズルの解の一意性を検証するソルバー"""
    
    def __init__(self, grid, row_targets, col_targets):
        self.grid = grid
        self.size = len(grid)
        self.row_targets = row_targets
        self.col_targets = col_targets
        self.solution_count = 0
        self.max_solutions = 2  # 2つ見つかったら中断（一意性チェック用）
    
    def solve(self):
        """解の数をカウント（最大2まで）"""
        self.solution_count = 0
        selected = [[False] * self.size for _ in range(self.size)]
        row_sums = [0] * self.size
        col_sums = [0] * self.size
        
        self._backtrack(0, 0, selected, row_sums, col_sums)
        
        return self.solution_count
    
    def _backtrack(self, row, col, selected, row_sums, col_sums):
        """バックトラッキングで解を探索"""
        if self.solution_count >= self.max_solutions:
            return
        
        if row == self.size:
            # 全てのターゲットが満たされているかチェック
            valid = True
            for i in range(self.size):
                if row_sums[i] != self.row_targets[i] or col_sums[i] != self.col_targets[i]:
                    valid = False
                    break
            if valid:
                self.solution_count += 1
            return
        
        next_row = row + 1 if col == self.size - 1 else row
        next_col = 0 if col == self.size - 1 else col + 1
        value = self.grid[row][col]
        
        # このセルを選択しない場合
        if row_sums[row] <= self.row_targets[row] and col_sums[col] <= self.col_targets[col]:
            remaining_in_row = self.size - col - 1
            max_possible_row = row_sums[row] + remaining_in_row * 9
            remaining_in_col = self.size - row - 1
            max_possible_col = col_sums[col] + remaining_in_col * 9
            
            if max_possible_row >= self.row_targets[row] and max_possible_col >= self.col_targets[col]:
                self._backtrack(next_row, next_col, selected, row_sums, col_sums)
                if self.solution_count >= self.max_solutions:
                    return
        
        # このセルを選択する場合
        if (row_sums[row] + value <= self.row_targets[row] and 
            col_sums[col] + value <= self.col_targets[col]):
            
            selected[row][col] = True
            row_sums[row] += value
            col_sums[col] += value
            
            self._backtrack(next_row, next_col, selected, row_sums, col_sums)
            
            selected[row][col] = False
            row_sums[row] -= value
            col_sums[col] -= value


class PuzzleGenerator:
    """パズル問題を生成するジェネレーター"""
    
    def __init__(self, size=6):
        self.size = size
        # 6×6の場合: 各行・列に2〜4個のセルを選択
        if size == 5:
            self.min_per_line = 2
            self.max_per_line = 3
        elif size == 6:
            self.min_per_line = 2
            self.max_per_line = 4
        else:  # 7×7
            self.min_per_line = 2
            self.max_per_line = 5
    
    def generate(self):
        """一意解を持つパズルを生成"""
        max_attempts = 100
        
        for attempt in range(max_attempts):
            # 有効な解答パターンを生成
            solution = self._create_valid_solution_greedy()
            if solution is None:
                continue
            
            # その解答に対してグリッドを生成し、一意性を検証
            result = self._generate_grid_for_solution(solution)
            if result is not None:
                return result
        
        raise Exception("一意解を持つパズルを生成できませんでした")
    
    def _create_valid_solution_greedy(self):
        """貪欲法で有効な解答パターンを生成"""
        solution = [[False] * self.size for _ in range(self.size)]
        
        # 各行で選択するセル数を決定
        row_targets = []
        for i in range(self.size):
            count = random.randint(self.min_per_line, self.max_per_line)
            row_targets.append(count)
        
        total_to_select = sum(row_targets)
        
        # 各列で選択するセル数を決定
        col_targets = []
        remaining = total_to_select
        for j in range(self.size - 1):
            min_possible = max(self.min_per_line, 
                             remaining - (self.size - j - 1) * self.max_per_line)
            max_possible = min(self.max_per_line, 
                             remaining - (self.size - j - 1) * self.min_per_line)
            
            if min_possible > max_possible:
                return None
            
            count = random.randint(min_possible, max_possible)
            col_targets.append(count)
            remaining -= count
        
        col_targets.append(remaining)
        
        if col_targets[-1] < self.min_per_line or col_targets[-1] > self.max_per_line:
            return None
        
        # 解答パターンを構築
        col_counts = [0] * self.size
        
        for i in range(self.size):
            needed = row_targets[i]
            
            # 選択可能な列を取得
            available = [j for j in range(self.size) if col_counts[j] < col_targets[j]]
            
            if len(available) < needed:
                return None
            
            # シャッフルして選択
            random.shuffle(available)
            for k in range(needed):
                col = available[k]
                solution[i][col] = True
                col_counts[col] += 1
        
        # 検証
        for j in range(self.size):
            if col_counts[j] != col_targets[j]:
                return None
        
        return solution
    
    def _generate_grid_for_solution(self, solution):
        """解答に対してグリッドを生成し、一意性を検証"""
        max_grid_attempts = 30
        
        for attempt in range(max_grid_attempts):
            grid = self._generate_diverse_grid()
            row_targets = self._calculate_row_targets(grid, solution)
            col_targets = self._calculate_col_targets(grid, solution)
            
            # 一意性をチェック
            solver = PuzzleSolver(grid, row_targets, col_targets)
            solution_count = solver.solve()
            
            if solution_count == 1:
                return {
                    'grid': grid,
                    'row_targets': row_targets,
                    'col_targets': col_targets,
                    'solution': solution
                }
        
        return None
    
    def _generate_diverse_grid(self):
        """1-9のランダムな数字でグリッドを生成"""
        grid = []
        for i in range(self.size):
            row = [random.randint(1, 9) for _ in range(self.size)]
            grid.append(row)
        return grid
    
    def _calculate_row_targets(self, grid, solution):
        """各行のターゲット合計を計算"""
        targets = []
        for i in range(self.size):
            total = sum(grid[i][j] for j in range(self.size) if solution[i][j])
            targets.append(total)
        return targets
    
    def _calculate_col_targets(self, grid, solution):
        """各列のターゲット合計を計算"""
        targets = []
        for j in range(self.size):
            total = sum(grid[i][j] for i in range(self.size) if solution[i][j])
            targets.append(total)
        return targets


class SVGGenerator:
    """SVGファイルを生成するクラス"""
    
    def __init__(self, puzzle_data, size=6):
        self.grid = puzzle_data['grid']
        self.row_targets = puzzle_data['row_targets']
        self.col_targets = puzzle_data['col_targets']
        self.solution = puzzle_data['solution']
        self.size = size
        
        # レイアウト設定
        self.cell_size = 40
        self.target_cell_width = 36
        self.target_cell_height = 30
        self.gap = 2
        self.font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
        
        # 色設定
        self.target_text_color = "black"       # 合計欄の数字：黒
        self.grid_stroke_color = "lightgray"   # グリッド罫線：ライトグレー
        self.grid_text_color = "gray"          # グリッド数字：グレー
        self.answer_circle_color = "black"     # 解答の丸：黒
        self.stroke_width = 1
    
    def generate_puzzle_svg(self):
        """問題用SVGを生成"""
        return self._generate_svg(show_answer=False)
    
    def generate_answer_svg(self):
        """解答用SVGを生成"""
        return self._generate_svg(show_answer=True)
    
    def _generate_svg(self, show_answer=False):
        """SVGを生成"""
        # 全体サイズを計算
        grid_width = self.size * self.cell_size + (self.size - 1) * self.gap
        grid_height = self.size * self.cell_size + (self.size - 1) * self.gap
        
        # ターゲットセル領域
        col_targets_height = self.target_cell_height
        row_targets_width = self.target_cell_width
        
        # 間隔
        spacing = 5
        
        total_width = row_targets_width + spacing + grid_width
        total_height = col_targets_height + spacing + grid_height
        
        svg_parts = []
        
        # SVGヘッダー
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                        f'width="{total_width}" height="{total_height}" '
                        f'viewBox="0 0 {total_width} {total_height}">')
        
        # 列ターゲット（上側）- 枠なし
        col_start_x = row_targets_width + spacing
        for j in range(self.size):
            x = col_start_x + j * (self.cell_size + self.gap)
            y = 0
            
            # 数字（枠なし、黒）
            text_x = x + self.cell_size / 2
            text_y = y + col_targets_height / 2
            svg_parts.append(f'<text x="{text_x}" y="{text_y}" '
                           f'font-family="{self.font_family}" '
                           f'font-size="14" fill="{self.target_text_color}" '
                           f'text-anchor="middle" dy="0.35em">'
                           f'{self.col_targets[j]}</text>')
        
        # 行ターゲット（左側）- 枠なし
        row_start_y = col_targets_height + spacing
        for i in range(self.size):
            x = 0
            y = row_start_y + i * (self.cell_size + self.gap)
            
            # 数字（枠なし、黒）
            text_x = x + row_targets_width / 2
            text_y = y + self.cell_size / 2
            svg_parts.append(f'<text x="{text_x}" y="{text_y}" '
                           f'font-family="{self.font_family}" '
                           f'font-size="14" fill="{self.target_text_color}" '
                           f'text-anchor="middle" dy="0.35em">'
                           f'{self.row_targets[i]}</text>')
        
        # メイングリッド
        grid_start_x = row_targets_width + spacing
        grid_start_y = col_targets_height + spacing
        
        for i in range(self.size):
            for j in range(self.size):
                x = grid_start_x + j * (self.cell_size + self.gap)
                y = grid_start_y + i * (self.cell_size + self.gap)
                
                # セル枠（ライトグレー）
                svg_parts.append(f'<rect x="{x}" y="{y}" '
                               f'width="{self.cell_size}" height="{self.cell_size}" '
                               f'fill="none" stroke="{self.grid_stroke_color}" '
                               f'stroke-width="{self.stroke_width}"/>')
                
                # 数字（グレー、垂直位置調整）
                text_x = x + self.cell_size / 2
                text_y = y + self.cell_size / 2
                svg_parts.append(f'<text x="{text_x}" y="{text_y}" '
                               f'font-family="{self.font_family}" '
                               f'font-size="18" fill="{self.grid_text_color}" '
                               f'text-anchor="middle" dy="0.35em">'
                               f'{self.grid[i][j]}</text>')
                
                # 解答の場合、選択されたセルに丸を描く（黒）
                if show_answer and self.solution[i][j]:
                    circle_x = text_x
                    circle_y = text_y
                    circle_r = self.cell_size / 2 - 4
                    svg_parts.append(f'<circle cx="{circle_x}" cy="{circle_y}" '
                                   f'r="{circle_r}" fill="none" '
                                   f'stroke="{self.answer_circle_color}" '
                                   f'stroke-width="{self.stroke_width}"/>')
        
        svg_parts.append('</svg>')
        
        return '\n'.join(svg_parts)


def main():
    """メイン処理"""
    # 日付を取得
    today = datetime.now().strftime('%Y%m%d')
    
    # ファイル名
    puzzle_filename = f"{today}_sumpuzzle.svg"
    answer_filename = f"{today}_sumpuzzle_ans.svg"
    
    print("Sum Puzzle Generator (6×6)")
    print("=" * 40)
    print("パズルを生成中...")
    
    # パズル生成
    generator = PuzzleGenerator(size=6)
    puzzle_data = generator.generate()
    
    print("パズル生成完了!")
    print()
    
    # グリッド表示
    print("グリッド:")
    for row in puzzle_data['grid']:
        print("  " + " ".join(str(n) for n in row))
    print()
    print(f"行ターゲット: {puzzle_data['row_targets']}")
    print(f"列ターゲット: {puzzle_data['col_targets']}")
    print()
    
    # 解答表示
    print("解答 (○=選択):")
    for i, row in enumerate(puzzle_data['solution']):
        marks = ["○" if cell else "・" for cell in row]
        print("  " + " ".join(marks))
    print()
    
    # SVG生成
    svg_gen = SVGGenerator(puzzle_data, size=6)
    
    puzzle_svg = svg_gen.generate_puzzle_svg()
    answer_svg = svg_gen.generate_answer_svg()
    
    # ファイル保存
    with open(puzzle_filename, 'w', encoding='utf-8') as f:
        f.write(puzzle_svg)
    print(f"問題SVGを保存しました: {puzzle_filename}")
    
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f"解答SVGを保存しました: {answer_filename}")
    
    print()
    print("完了!")


if __name__ == "__main__":
    main()
