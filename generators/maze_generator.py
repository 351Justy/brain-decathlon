#!/usr/bin/env python3
"""
迷路ジェネレーター (Python版)
"""

import random
import math
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

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

class Maze:
    def __init__(self, width, height, inner_width=0, inner_height=0):
        self.width = width
        self.height = height
        self.inner_width = inner_width
        self.inner_height = inner_height
        self.grid = []
        self.solution = []
        self.start = {'x': 0, 'y': 0}
        self.end = {'x': width - 1, 'y': height - 1}
        self._init_grid()
    
    def _init_grid(self):
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                has_inner_hole = (
                    self.inner_width > 0 and self.inner_height > 0 and
                    x >= (self.width - self.inner_width) // 2 and
                    x < (self.width + self.inner_width) // 2 and
                    y >= (self.height - self.inner_height) // 2 and
                    y < (self.height + self.inner_height) // 2
                )
                row.append(None if has_inner_hole else Cell(x, y))
            self.grid.append(row)
    
    def get_cell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.grid[y][x]
    
    def _get_unvisited_neighbors(self, cell):
        neighbors = []
        directions = [
            {'dx': 0, 'dy': -1, 'wall': 'top'},
            {'dx': 1, 'dy': 0, 'wall': 'right'},
            {'dx': 0, 'dy': 1, 'wall': 'bottom'},
            {'dx': -1, 'dy': 0, 'wall': 'left'},
        ]
        for d in directions:
            neighbor = self.get_cell(cell.x + d['dx'], cell.y + d['dy'])
            if neighbor and not neighbor.visited:
                neighbors.append({'cell': neighbor, 'wall': d['wall']})
        return neighbors
    
    def generate(self, entropy=0.5, roughness=1.0, start_at='leftTop'):
        if start_at == 'leftTop':
            self.start = {'x': 0, 'y': 0}
            self.end = {'x': self.width - 1, 'y': self.height - 1}
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell:
                    cell.visited = False
        
        start_cell = self.get_cell(self.start['x'], self.start['y'])
        if start_cell:
            start_cell.visited = True
        
        self._generate_maze(start_cell or self.get_cell(0, 0), entropy, roughness)
        
        if start_cell and start_at == 'leftTop':
            start_cell.walls['left'] = False
            start_cell.walls['top'] = False
        
        end_cell = self.get_cell(self.end['x'], self.end['y'])
        if end_cell and start_at == 'leftTop':
            end_cell.walls['right'] = False
            end_cell.walls['bottom'] = False
        
        self._find_solution()
    
    def _generate_maze(self, start_cell, entropy, roughness):
        if not start_cell:
            return
        
        stack = [start_cell]
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
            current_index = len(stack) - 1
            if random.random() < entropy and len(stack) > 1:
                current_index = random.randint(0, len(stack) - 1)
            
            current_cell = stack[current_index]
            neighbors = self._get_unvisited_neighbors(current_cell)
            
            if neighbors:
                def sort_key(n):
                    dir_n = {'x': n['cell'].x - current_cell.x, 'y': n['cell'].y - current_cell.y}
                    dot = dir_n['x'] * goal_direction['x'] + dir_n['y'] * goal_direction['y']
                    return dot if random.random() < 0.75 else random.random() - 0.5
                
                neighbors.sort(key=sort_key)
                chosen = neighbors[0]
                next_cell = chosen['cell']
                
                if random.random() <= roughness:
                    current_cell.walls[chosen['wall']] = False
                    next_cell.walls[opposite_wall[chosen['wall']]] = False
                
                next_cell.visited = True
                stack.append(next_cell)
            else:
                stack.pop(current_index)
    
    def _find_solution(self):
        start_cell = self.get_cell(self.start['x'], self.start['y'])
        end_cell = self.get_cell(self.end['x'], self.end['y'])
        
        if not start_cell or not end_cell:
            self.solution = []
            return
        
        def heuristic(a, b):
            return abs(a.x - b.x) + abs(a.y - b.y)
        
        open_set = [start_cell]
        came_from = {}
        g_score = {}
        f_score = {}
        
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
            open_set.sort(key=lambda c: f_score[f"{c.x},{c.y}"])
            current = open_set.pop(0)
            
            if current.x == end_cell.x and current.y == end_cell.y:
                path = []
                curr = current
                while f"{curr.x},{curr.y}" in came_from:
                    path.insert(0, curr)
                    curr = came_from[f"{curr.x},{curr.y}"]
                path.insert(0, start_cell)
                self.solution = path
                return
            
            potential_neighbors = []
            if not current.walls['top'] and self.get_cell(current.x, current.y - 1):
                potential_neighbors.append(self.get_cell(current.x, current.y - 1))
            if not current.walls['right'] and self.get_cell(current.x + 1, current.y):
                potential_neighbors.append(self.get_cell(current.x + 1, current.y))
            if not current.walls['bottom'] and self.get_cell(current.x, current.y + 1):
                potential_neighbors.append(self.get_cell(current.x, current.y + 1))
            if not current.walls['left'] and self.get_cell(current.x - 1, current.y):
                potential_neighbors.append(self.get_cell(current.x - 1, current.y))
            
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
    
    def render_svg(self, show_solution=True, cell_size=10, wall_color='gray'):
        wall_stroke_width = 1
        offset = wall_stroke_width / 2.0
        
        svg_total_width = self.width * cell_size + wall_stroke_width
        svg_total_height = self.height * cell_size + wall_stroke_width
        
        lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_total_width}" height="{svg_total_height}" viewBox="0 0 {svg_total_width} {svg_total_height}" shape-rendering="crispEdges" style="background-color: transparent;">']
        
        if show_solution and self.solution:
            solution_stroke_width = max(1, cell_size // 5)
            path_d = f'M{offset + (self.solution[0].x + 0.5) * cell_size},{offset + (self.solution[0].y + 0.5) * cell_size}'
            for i in range(1, len(self.solution)):
                path_d += f' L{offset + (self.solution[i].x + 0.5) * cell_size},{offset + (self.solution[i].y + 0.5) * cell_size}'
            lines.append(f'<path d="{path_d}" stroke="red" stroke-width="{solution_stroke_width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if not cell:
                    continue
                cell_corner_x = offset + x * cell_size
                cell_corner_y = offset + y * cell_size
                
                if cell.walls['top']:
                    lines.append(f'<line x1="{cell_corner_x}" y1="{cell_corner_y}" x2="{cell_corner_x + cell_size}" y2="{cell_corner_y}" stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>')
                if cell.walls['right']:
                    lines.append(f'<line x1="{cell_corner_x + cell_size}" y1="{cell_corner_y}" x2="{cell_corner_x + cell_size}" y2="{cell_corner_y + cell_size}" stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>')
                if cell.walls['bottom']:
                    lines.append(f'<line x1="{cell_corner_x}" y1="{cell_corner_y + cell_size}" x2="{cell_corner_x + cell_size}" y2="{cell_corner_y + cell_size}" stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>')
                if cell.walls['left']:
                    lines.append(f'<line x1="{cell_corner_x}" y1="{cell_corner_y}" x2="{cell_corner_x}" y2="{cell_corner_y + cell_size}" stroke="{wall_color}" stroke-width="{wall_stroke_width}"/>')
        
        lines.append('</svg>')
        return '\n'.join(lines)

def main():
    width, height = 75, 50
    
    print(f"迷路を生成中... ({width}x{height})")
    maze = Maze(width, height)
    maze.generate(entropy=0.5, roughness=1.0, start_at='leftTop')
    print(f"解答パス長: {len(maze.solution)} セル")
    
    date_str = get_date_prefix()
    
    filename_no_solution = f"{date_str}_maze.svg"
    with open(filename_no_solution, 'w', encoding='utf-8') as f:
        f.write(maze.render_svg(show_solution=False, cell_size=10, wall_color='gray'))
    print(f"保存: {filename_no_solution}")
    
    filename_with_solution = f"{date_str}_maze_ans.svg"
    with open(filename_with_solution, 'w', encoding='utf-8') as f:
        f.write(maze.render_svg(show_solution=True, cell_size=10, wall_color='gray'))
    print(f"保存: {filename_with_solution}")

if __name__ == '__main__':
    main()
