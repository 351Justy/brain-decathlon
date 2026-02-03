#!/usr/bin/env python3
"""
Sum Puzzle Generator - 6×6のサムパズル
"""

import random
import sys
import os
from datetime import datetime

def get_date_prefix():
    """日付プレフィックスを取得（引数 > 環境変数 > 今日）"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if len(arg) == 8 and arg.isdigit():
            return arg
    if 'PUZZLE_DATE' in os.environ:
        return os.environ['PUZZLE_DATE']
    return datetime.now().strftime('%Y%m%d')

class PuzzleSolver:
    def __init__(self, grid, row_targets, col_targets):
        self.grid = grid
        self.size = len(grid)
        self.row_targets = row_targets
        self.col_targets = col_targets
        self.solution_count = 0
        self.max_solutions = 2
    
    def solve(self):
        self.solution_count = 0
        selected = [[False] * self.size for _ in range(self.size)]
        row_sums = [0] * self.size
        col_sums = [0] * self.size
        self._backtrack(0, 0, selected, row_sums, col_sums)
        return self.solution_count
    
    def _backtrack(self, row, col, selected, row_sums, col_sums):
        if self.solution_count >= self.max_solutions:
            return
        if row == self.size:
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
        
        if row_sums[row] <= self.row_targets[row] and col_sums[col] <= self.col_targets[col]:
            remaining_in_row = self.size - col - 1
            max_possible_row = row_sums[row] + remaining_in_row * 9
            remaining_in_col = self.size - row - 1
            max_possible_col = col_sums[col] + remaining_in_col * 9
            if max_possible_row >= self.row_targets[row] and max_possible_col >= self.col_targets[col]:
                self._backtrack(next_row, next_col, selected, row_sums, col_sums)
                if self.solution_count >= self.max_solutions:
                    return
        
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
    def __init__(self, size=6):
        self.size = size
        self.min_per_line = 2
        self.max_per_line = 4
    
    def generate(self):
        max_attempts = 100
        for attempt in range(max_attempts):
            solution = self._create_valid_solution_greedy()
            if solution is None:
                continue
            result = self._generate_grid_for_solution(solution)
            if result is not None:
                return result
        raise Exception("一意解を持つパズルを生成できませんでした")
    
    def _create_valid_solution_greedy(self):
        solution = [[False] * self.size for _ in range(self.size)]
        row_targets = [random.randint(self.min_per_line, self.max_per_line) for _ in range(self.size)]
        total_to_select = sum(row_targets)
        
        col_targets = []
        remaining = total_to_select
        for j in range(self.size - 1):
            min_possible = max(self.min_per_line, remaining - (self.size - j - 1) * self.max_per_line)
            max_possible = min(self.max_per_line, remaining - (self.size - j - 1) * self.min_per_line)
            if min_possible > max_possible:
                return None
            count = random.randint(min_possible, max_possible)
            col_targets.append(count)
            remaining -= count
        col_targets.append(remaining)
        
        if col_targets[-1] < self.min_per_line or col_targets[-1] > self.max_per_line:
            return None
        
        col_counts = [0] * self.size
        for i in range(self.size):
            needed = row_targets[i]
            available = [j for j in range(self.size) if col_counts[j] < col_targets[j]]
            if len(available) < needed:
                return None
            random.shuffle(available)
            for k in range(needed):
                col = available[k]
                solution[i][col] = True
                col_counts[col] += 1
        
        for j in range(self.size):
            if col_counts[j] != col_targets[j]:
                return None
        return solution
    
    def _generate_grid_for_solution(self, solution):
        for attempt in range(30):
            grid = [[random.randint(1, 9) for _ in range(self.size)] for _ in range(self.size)]
            row_targets = [sum(grid[i][j] for j in range(self.size) if solution[i][j]) for i in range(self.size)]
            col_targets = [sum(grid[i][j] for i in range(self.size) if solution[i][j]) for j in range(self.size)]
            
            solver = PuzzleSolver(grid, row_targets, col_targets)
            if solver.solve() == 1:
                return {'grid': grid, 'row_targets': row_targets, 'col_targets': col_targets, 'solution': solution}
        return None

class SVGGenerator:
    def __init__(self, puzzle_data, size=6):
        self.grid = puzzle_data['grid']
        self.row_targets = puzzle_data['row_targets']
        self.col_targets = puzzle_data['col_targets']
        self.solution = puzzle_data['solution']
        self.size = size
        self.cell_size = 40
        self.target_cell_width = 36
        self.target_cell_height = 30
        self.gap = 2
        self.font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
    
    def generate_puzzle_svg(self):
        return self._generate_svg(show_answer=False)
    
    def generate_answer_svg(self):
        return self._generate_svg(show_answer=True)
    
    def _generate_svg(self, show_answer=False):
        grid_width = self.size * self.cell_size + (self.size - 1) * self.gap
        grid_height = grid_width
        spacing = 5
        total_width = self.target_cell_width + spacing + grid_width
        total_height = self.target_cell_height + spacing + grid_height
        
        svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}">']
        
        col_start_x = self.target_cell_width + spacing
        for j in range(self.size):
            x = col_start_x + j * (self.cell_size + self.gap)
            text_x = x + self.cell_size / 2
            text_y = self.target_cell_height / 2
            svg_parts.append(f'<text x="{text_x}" y="{text_y}" font-family="{self.font_family}" font-size="14" fill="black" text-anchor="middle" dy="0.35em">{self.col_targets[j]}</text>')
        
        row_start_y = self.target_cell_height + spacing
        for i in range(self.size):
            y = row_start_y + i * (self.cell_size + self.gap)
            text_x = self.target_cell_width / 2
            text_y = y + self.cell_size / 2
            svg_parts.append(f'<text x="{text_x}" y="{text_y}" font-family="{self.font_family}" font-size="14" fill="black" text-anchor="middle" dy="0.35em">{self.row_targets[i]}</text>')
        
        grid_start_x = self.target_cell_width + spacing
        grid_start_y = self.target_cell_height + spacing
        
        for i in range(self.size):
            for j in range(self.size):
                x = grid_start_x + j * (self.cell_size + self.gap)
                y = grid_start_y + i * (self.cell_size + self.gap)
                svg_parts.append(f'<rect x="{x}" y="{y}" width="{self.cell_size}" height="{self.cell_size}" fill="none" stroke="lightgray" stroke-width="1"/>')
                
                text_x = x + self.cell_size / 2
                text_y = y + self.cell_size / 2
                svg_parts.append(f'<text x="{text_x}" y="{text_y}" font-family="{self.font_family}" font-size="18" fill="gray" text-anchor="middle" dy="0.35em">{self.grid[i][j]}</text>')
                
                if show_answer and self.solution[i][j]:
                    circle_r = self.cell_size / 2 - 4
                    svg_parts.append(f'<circle cx="{text_x}" cy="{text_y}" r="{circle_r}" fill="none" stroke="black" stroke-width="1"/>')
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)

def main():
    today = get_date_prefix()
    
    print("Sum Puzzle Generator (6×6)")
    print("=" * 40)
    print("パズルを生成中...")
    
    generator = PuzzleGenerator(size=6)
    puzzle_data = generator.generate()
    
    print("パズル生成完了!")
    print()
    print("グリッド:")
    for row in puzzle_data['grid']:
        print("  " + " ".join(str(n) for n in row))
    print()
    print(f"行ターゲット: {puzzle_data['row_targets']}")
    print(f"列ターゲット: {puzzle_data['col_targets']}")
    print()
    print("解答 (○=選択):")
    for row in puzzle_data['solution']:
        print("  " + " ".join("○" if cell else "・" for cell in row))
    print()
    
    svg_gen = SVGGenerator(puzzle_data, size=6)
    
    puzzle_filename = f"{today}_sumpuzzle.svg"
    with open(puzzle_filename, 'w', encoding='utf-8') as f:
        f.write(svg_gen.generate_puzzle_svg())
    print(f"問題SVGを保存しました: {puzzle_filename}")
    
    answer_filename = f"{today}_sumpuzzle_ans.svg"
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(svg_gen.generate_answer_svg())
    print(f"解答SVGを保存しました: {answer_filename}")
    
    print("\n完了!")

if __name__ == "__main__":
    main()
