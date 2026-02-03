#!/usr/bin/env python3
"""
迷路ジェネレーター (Python版)
maze.html のロジックをPythonに移植

パラメータ:
- 幅: 75セル
- 高さ: 50セル
- スタート位置: 左上 (0,0) → ゴール: 右下 (74,49)
- E (entropy): 50 (0.5)
- R (roughness): 100 (1.0)
- 壁の色: グレー
- 背景: 透明
- セルサイズ: 10ピクセル

出力:
- YYYYMMDD_maze.svg (解答なし)
- YYYYMMDD_maze_ans.svg (解答あり)
"""

import random
import math
from datetime import datetime


class Cell:
    """セルクラス"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False


class Maze:
    """迷路クラス"""
    
    def __init__(self, width: int, height: int, inner_width: int = 0, inner_height: int = 0):
        self.width = width
        self.height = height
        self.inner_width = inner_width
        self.inner_height = inner_height
        self.grid: list[list[Cell | None]] = []
        self.solution: list[Cell] = []
        self.start = {'x': 0, 'y': 0}
        self.end = {'x': width - 1, 'y': height - 1}
        self._init_grid()
    
    def _init_grid(self):
        """グリッドを初期化"""
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # 内部穴のチェック
                has_inner_hole = (
                    self.inner_width > 0 and self.inner_height > 0 and
                    x >= (self.width - self.inner_width) // 2 and
                    x < (self.width + self.inner_width) // 2 and
                    y >= (self.height - self.inner_height) // 2 and
                    y < (self.height + self.inner_height) // 2
                )
                if has_inner_hole:
                    row.append(None)
                else:
                    row.append(Cell(x, y))
            self.grid.append(row)
    
    def get_cell(self, x: int, y: int) -> Cell | None:
        """指定座標のセルを取得"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.grid[y][x]
    
    def _get_unvisited_neighbors(self, cell: Cell) -> list[dict]:
        """未訪問の隣接セルを取得"""
        neighbors = []
        x, y = cell.x, cell.y
        directions = [
            {'dx': 0, 'dy': -1, 'wall': 'top'},
            {'dx': 1, 'dy': 0, 'wall': 'right'},
            {'dx': 0, 'dy': 1, 'wall': 'bottom'},
            {'dx': -1, 'dy': 0, 'wall': 'left'},
        ]
        for d in directions:
            nx, ny = x + d['dx'], y + d['dy']
            neighbor = self.get_cell(nx, ny)
            if neighbor and not neighbor.visited:
                neighbors.append({'cell': neighbor, 'wall': d['wall']})
        return neighbors
    
    def generate(self, entropy: float = 0.5, roughness: float = 1.0, start_at: str = 'leftTop'):
        """迷路を生成"""
        # スタート・ゴール位置の設定
        if start_at == 'top':
            self.start = {'x': self.width // 2, 'y': 0}
            self.end = {'x': self.width // 2, 'y': self.height - 1}
        elif start_at == 'right':
            self.start = {'x': self.width - 1, 'y': self.height // 2}
            self.end = {'x': 0, 'y': self.height // 2}
        elif start_at == 'bottom':
            self.start = {'x': self.width // 2, 'y': self.height - 1}
            self.end = {'x': self.width // 2, 'y': 0}
        elif start_at == 'left':
            self.start = {'x': 0, 'y': self.height // 2}
            self.end = {'x': self.width - 1, 'y': self.height // 2}
        elif start_at == 'leftTop':
            self.start = {'x': 0, 'y': 0}
            self.end = {'x': self.width - 1, 'y': self.height - 1}
        
        # 訪問フラグをリセット
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    cell.visited = False
        
        # 迷路生成
        start_cell = self.get_cell(self.start['x'], self.start['y'])
        if start_cell:
            start_cell.visited = True
        
        self._generate_maze(start_cell or self.get_cell(0, 0), entropy, roughness)
        
        # スタート・ゴールの壁を除去
        if start_cell:
            if start_at == 'top':
                start_cell.walls['top'] = False
            elif start_at == 'right':
                start_cell.walls['right'] = False
            elif start_at == 'bottom':
                start_cell.walls['bottom'] = False
            elif start_at == 'left':
                start_cell.walls['left'] = False
            elif start_at == 'leftTop':
                start_cell.walls['left'] = False
                start_cell.walls['top'] = False
        
        end_cell = self.get_cell(self.end['x'], self.end['y'])
        if end_cell:
            if start_at == 'top':
                end_cell.walls['bottom'] = False
            elif start_at == 'right':
                end_cell.walls['left'] = False
            elif start_at == 'bottom':
                end_cell.walls['top'] = False
            elif start_at == 'left':
                end_cell.walls['right'] = False
            elif start_at == 'leftTop':
                end_cell.walls['right'] = False
                end_cell.walls['bottom'] = False
        
        # 解答を探索
        self._find_solution()
    
    def _generate_maze(self, start_cell: Cell | None, entropy: float, roughness: float):
        """深さ優先探索で迷路を生成"""
        if not start_cell:
            return
        
        stack = [start_cell]
        
        # ゴール方向ベクトル
        goal_direction = {
            'x': self.end['x'] - self.start['x'],
            'y': self.end['y'] - self.start['y']
        }
        dir_length = math.sqrt(goal_direction['x'] ** 2 + goal_direction['y'] ** 2)
        if dir_length > 0:
            goal_direction['x'] /= dir_length
            goal_direction['y'] /= dir_length
        
        opposite_wall = {'top': 'bottom', 'right': 'left', 'bottom': 'top', 'left': 'right'}
        
        while stack:
            # エントロピーに基づいてスタックからセルを選択
            current_index = len(stack) - 1
            if random.random() < entropy and len(stack) > 1:
                current_index = random.randint(0, len(stack) - 1)
            
            current_cell = stack[current_index]
            neighbors = self._get_unvisited_neighbors(current_cell)
            
            if neighbors:
                # ゴール方向にソート（75%の確率）
                def sort_key(n):
                    dir_n = {
                        'x': n['cell'].x - current_cell.x,
                        'y': n['cell'].y - current_cell.y
                    }
                    dot = dir_n['x'] * goal_direction['x'] + dir_n['y'] * goal_direction['y']
                    if random.random() < 0.75:
                        return dot
                    else:
                        return random.random() - 0.5
                
                neighbors.sort(key=sort_key)
                
                chosen = neighbors[0]
                next_cell = chosen['cell']
                wall_to_remove = chosen['wall']
                
                # roughnessに基づいて壁を除去
                if random.random() <= roughness:
                    current_cell.walls[wall_to_remove] = False
                    next_cell.walls[opposite_wall[wall_to_remove]] = False
                
                next_cell.visited = True
                stack.append(next_cell)
            else:
                stack.pop(current_index)
    
    def _find_solution(self):
        """A*アルゴリズムで解答を探索"""
        start_cell = self.get_cell(self.start['x'], self.start['y'])
        end_cell = self.get_cell(self.end['x'], self.end['y'])
        
        if not start_cell or not end_cell:
            self.solution = []
            return
        
        def heuristic(a: Cell, b: Cell) -> int:
            return abs(a.x - b.x) + abs(a.y - b.y)
        
        open_set = [start_cell]
        came_from: dict[str, Cell] = {}
        g_score: dict[str, float] = {}
        f_score: dict[str, float] = {}
        
        # スコアを初期化
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    key = f"{x},{y}"
                    g_score[key] = float('inf')
                    f_score[key] = float('inf')
        
        start_key = f"{start_cell.x},{start_cell.y}"
        g_score[start_key] = 0
        f_score[start_key] = heuristic(start_cell, end_cell)
        
        while open_set:
            # f_scoreが最小のセルを選択
            open_set.sort(key=lambda c: f_score[f"{c.x},{c.y}"])
            current = open_set.pop(0)
            
            if current.x == end_cell.x and current.y == end_cell.y:
                # パスを再構築
                path = []
                curr = current
                while f"{curr.x},{curr.y}" in came_from:
                    path.insert(0, curr)
                    curr = came_from[f"{curr.x},{curr.y}"]
                path.insert(0, start_cell)
                self.solution = path
                return
            
            x, y = current.x, current.y
            potential_neighbors = []
            
            if not current.walls['top'] and self.get_cell(x, y - 1):
                potential_neighbors.append(self.get_cell(x, y - 1))
            if not current.walls['right'] and self.get_cell(x + 1, y):
                potential_neighbors.append(self.get_cell(x + 1, y))
            if not current.walls['bottom'] and self.get_cell(x, y + 1):
                potential_neighbors.append(self.get_cell(x, y + 1))
            if not current.walls['left'] and self.get_cell(x - 1, y):
                potential_neighbors.append(self.get_cell(x - 1, y))
            
            for neighbor in potential_neighbors:
                if not neighbor:
                    continue
                
                neighbor_key = f"{neighbor.x},{neighbor.y}"
                current_key = f"{current.x},{current.y}"
                tentative_g_score = g_score[current_key] + 1
                
                if tentative_g_score < g_score[neighbor_key]:
                    came_from[neighbor_key] = current
                    g_score[neighbor_key] = tentative_g_score
                    f_score[neighbor_key] = tentative_g_score + heuristic(neighbor, end_cell)
                    
                    if not any(n.x == neighbor.x and n.y == neighbor.y for n in open_set):
                        open_set.append(neighbor)
        
        self.solution = []
    
    def render_svg(self, show_solution: bool = True, cell_size: int = 10, wall_color: str = 'gray') -> str:
        """SVG文字列を生成"""
        wall_stroke_width = 1
        offset = wall_stroke_width / 2.0
        
        maze_pixel_width = self.width * cell_size
        maze_pixel_height = self.height * cell_size
        
        svg_total_width = maze_pixel_width + wall_stroke_width
        svg_total_height = maze_pixel_height + wall_stroke_width
        
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{svg_total_width}" height="{svg_total_height}" '
            f'viewBox="0 0 {svg_total_width} {svg_total_height}" '
            f'shape-rendering="crispEdges" '
            f'style="background-color: transparent;">'
        ]
        
        # 解答パスを描画
        if show_solution and self.solution:
            solution_stroke_width = max(1, cell_size // 5)
            path_d = f'M{offset + (self.solution[0].x + 0.5) * cell_size},{offset + (self.solution[0].y + 0.5) * cell_size}'
            for i in range(1, len(self.solution)):
                path_d += f' L{offset + (self.solution[i].x + 0.5) * cell_size},{offset + (self.solution[i].y + 0.5) * cell_size}'
            
            lines.append(
                f'<path d="{path_d}" stroke="red" stroke-width="{solution_stroke_width}" '
                f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            )
        
        # 壁を描画
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if not cell:
                    continue
                
                cell_corner_x = offset + x * cell_size
                cell_corner_y = offset + y * cell_size
                
                if cell.walls['top']:
                    lines.append(
                        f'<line x1="{cell_corner_x}" y1="{cell_corner_y}" '
                        f'x2="{cell_corner_x + cell_size}" y2="{cell_corner_y}" '
                        f'stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>'
                    )
                if cell.walls['right']:
                    lines.append(
                        f'<line x1="{cell_corner_x + cell_size}" y1="{cell_corner_y}" '
                        f'x2="{cell_corner_x + cell_size}" y2="{cell_corner_y + cell_size}" '
                        f'stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>'
                    )
                if cell.walls['bottom']:
                    lines.append(
                        f'<line x1="{cell_corner_x}" y1="{cell_corner_y + cell_size}" '
                        f'x2="{cell_corner_x + cell_size}" y2="{cell_corner_y + cell_size}" '
                        f'stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>'
                    )
                if cell.walls['left']:
                    lines.append(
                        f'<line x1="{cell_corner_x}" y1="{cell_corner_y}" '
                        f'x2="{cell_corner_x}" y2="{cell_corner_y + cell_size}" '
                        f'stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>'
                    )
        
        lines.append('</svg>')
        return '\n'.join(lines)


def main():
    # パラメータ設定
    width = 75
    height = 50
    inner_width = 0
    inner_height = 0
    entropy = 0.5       # E50
    roughness = 1.0     # R100
    start_at = 'leftTop'
    cell_size = 10
    wall_color = 'gray'
    
    # 迷路を生成
    print(f"迷路を生成中... ({width}x{height})")
    maze = Maze(width, height, inner_width, inner_height)
    maze.generate(entropy=entropy, roughness=roughness, start_at=start_at)
    print(f"解答パス長: {len(maze.solution)} セル")
    
    # ファイル名を生成
    date_str = datetime.now().strftime('%Y%m%d')
    filename_no_solution = f"{date_str}_maze.svg"
    filename_with_solution = f"{date_str}_maze_ans.svg"
    
    # SVGを保存（解答なし）
    svg_no_solution = maze.render_svg(show_solution=False, cell_size=cell_size, wall_color=wall_color)
    with open(filename_no_solution, 'w', encoding='utf-8') as f:
        f.write(svg_no_solution)
    print(f"保存: {filename_no_solution}")
    
    # SVGを保存（解答あり）
    svg_with_solution = maze.render_svg(show_solution=True, cell_size=cell_size, wall_color=wall_color)
    with open(filename_with_solution, 'w', encoding='utf-8') as f:
        f.write(svg_with_solution)
    print(f"保存: {filename_with_solution}")


if __name__ == '__main__':
    main()
