#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KenKen風パズルSVG生成スクリプト
4×4サイズ、厳密な一意解検証付き
"""

import random
import itertools
import sys
import os
from datetime import datetime
from typing import List, Set, Tuple, Dict


def get_date_prefix():
    """日付プレフィックスを取得（引数 > 環境変数 > 今日）"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if len(arg) == 8 and arg.isdigit():
            return arg
    if 'PUZZLE_DATE' in os.environ:
        return os.environ['PUZZLE_DATE']
    return datetime.now().strftime('%Y%m%d')

# 定数
N = 4
CELL_SIZE = 60  # SVG単位
BORDER_THICK = 2
BORDER_THIN = 0.5
FONT_SIZE_LARGE = 36
FONT_SIZE_SMALL = 18


class Cage:
    """ケージ構造"""
    def __init__(self, cage_id: int, cells: List[int], target: int):
        self.id = cage_id
        self.cells = cells
        self.target = target


def generate_latin_square(n: int) -> List[int]:
    """ラテン方陣を生成（バックトラック）"""
    board = [0] * (n * n)
    
    def is_valid(idx: int, num: int) -> bool:
        r, c = idx // n, idx % n
        # 行チェック
        for k in range(c):
            if board[r * n + k] == num:
                return False
        # 列チェック
        for k in range(r):
            if board[k * n + c] == num:
                return False
        return True
    
    def backtrack(idx: int) -> bool:
        if idx == n * n:
            return True
        
        nums = list(range(1, n + 1))
        random.shuffle(nums)
        
        for num in nums:
            if is_valid(idx, num):
                board[idx] = num
                if backtrack(idx + 1):
                    return True
                board[idx] = 0
        return False
    
    backtrack(0)
    return board


def generate_cages(n: int) -> List[int]:
    """ケージを生成（各セルにケージIDを割り当て）"""
    grid = [-1] * (n * n)
    visited = [False] * (n * n)
    cage_id = 0
    
    for i in range(n * n):
        if visited[i]:
            continue
        
        # ターゲットサイズを決定
        rand = random.random()
        if rand < 0.1:
            target_size = 1
        elif rand < 0.5:
            target_size = 3
        elif rand < 0.7:
            target_size = 4
        else:
            target_size = 2
        
        current = [i]
        visited[i] = True
        
        # 隣接セルを追加
        safe_counter = 0
        while len(current) < target_size and safe_counter < 15:
            safe_counter += 1
            candidates = []
            
            for c_idx in current:
                cx, cy = c_idx % n, c_idx // n
                neighbors = []
                if cx > 0:
                    neighbors.append(c_idx - 1)
                if cx < n - 1:
                    neighbors.append(c_idx + 1)
                if cy > 0:
                    neighbors.append(c_idx - n)
                if cy < n - 1:
                    neighbors.append(c_idx + n)
                
                for nei in neighbors:
                    if not visited[nei]:
                        candidates.append(nei)
            
            if not candidates:
                break
            
            next_cell = random.choice(candidates)
            visited[next_cell] = True
            current.append(next_cell)
        
        for idx in current:
            grid[idx] = cage_id
        cage_id += 1
    
    # シングルセル統合
    changed = True
    while changed:
        changed = False
        cage_map = {}
        for i in range(n * n):
            cid = grid[i]
            if cid not in cage_map:
                cage_map[cid] = []
            cage_map[cid].append(i)
        
        for cid, cells in cage_map.items():
            if len(cells) == 1:
                idx = cells[0]
                cx, cy = idx % n, idx // n
                neighbors = []
                if cx > 0:
                    neighbors.append(idx - 1)
                if cx < n - 1:
                    neighbors.append(idx + 1)
                if cy > 0:
                    neighbors.append(idx - n)
                if cy < n - 1:
                    neighbors.append(idx + n)
                
                for ni in neighbors:
                    ncid = grid[ni]
                    if ncid != cid and len(cage_map[ncid]) < 5:
                        grid[idx] = ncid
                        changed = True
                        break
                
                if changed:
                    break
    
    return grid


def calculate_targets(grid_struct: List[int], solution: List[int], n: int) -> List[Cage]:
    """ターゲット値を計算"""
    cage_map = {}
    for i in range(n * n):
        cid = grid_struct[i]
        if cid not in cage_map:
            cage_map[cid] = []
        cage_map[cid].append(solution[i])
    
    cages = []
    for cid, nums in cage_map.items():
        cells = [i for i in range(n * n) if grid_struct[i] == cid]
        
        if len(nums) == 1:
            target = nums[0]
        elif len(nums) == 2:
            a, b = nums[0], nums[1]
            big, small = max(a, b), min(a, b)
            ops = ['+', '*', '-']
            if big % small == 0:
                ops.append('/')
            op = random.choice(ops)
            
            if op == '+':
                target = a + b
            elif op == '*':
                target = a * b
            elif op == '-':
                target = big - small
            else:
                target = big // small
        else:
            op = random.choice(['+', '*']) if random.random() < 0.6 else random.choice(['+', '*'])
            if op == '+':
                target = sum(nums)
            else:
                target = 1
                for v in nums:
                    target *= v
        
        cages.append(Cage(cid, cells, target))
    
    return cages


def check_cage_math(nums: List[int], target: int, op: str) -> bool:
    """ケージの制約チェック"""
    if len(nums) == 1:
        return nums[0] == target
    
    if len(nums) == 2:
        a, b = nums[0], nums[1]
        if op == '+':
            return a + b == target
        elif op == '*':
            return a * b == target
        elif op == '-':
            return abs(a - b) == target
        elif op == '/':
            return (a != 0 and b != 0 and (a // b == target or b // a == target))
        return False
    
    if len(nums) >= 3:
        if op == '+':
            return sum(nums) == target
        elif op == '*':
            prod = 1
            for v in nums:
                prod *= v
            return prod == target
        return False
    
    return False


def solve_with_operators(n: int, grid_struct: List[int], cages: List[Cage], 
                         operators: Dict[int, str], max_solutions: int = 2) -> List[List[int]]:
    """指定された演算子で解を探索"""
    board = [0] * (n * n)
    cage_map = {cage.id: cage for cage in cages}
    cell_cage_ids = grid_struct
    solutions = []
    
    def is_valid(idx: int, num: int) -> bool:
        r, c = idx // n, idx % n
        
        # 行・列チェック
        for k in range(c):
            if board[r * n + k] == num:
                return False
        for k in range(r):
            if board[k * n + c] == num:
                return False
        
        # ケージ制約チェック
        cage_id = cell_cage_ids[idx]
        cage = cage_map[cage_id]
        op = operators[cage_id]
        
        current_nums = []
        is_full = True
        
        for cell_idx in cage.cells:
            if cell_idx == idx:
                current_nums.append(num)
            elif cell_idx < idx:
                current_nums.append(board[cell_idx])
            else:
                is_full = False
        
        if is_full:
            return check_cage_math(current_nums, cage.target, op)
        
        return True
    
    def backtrack(idx: int):
        nonlocal solutions
        if idx == n * n:
            solutions.append(board[:])
            return
        if len(solutions) >= max_solutions:
            return
        
        for num in range(1, n + 1):
            if is_valid(idx, num):
                board[idx] = num
                backtrack(idx + 1)
                if len(solutions) >= max_solutions:
                    return
                board[idx] = 0
    
    backtrack(0)
    return solutions


def generate_operator_combinations(cages: List[Cage]) -> List[Dict[int, str]]:
    """すべての演算子組み合わせを生成"""
    cage_ops = {}
    for cage in cages:
        length = len(cage.cells)
        if length == 1:
            cage_ops[cage.id] = ['=']
        elif length == 2:
            cage_ops[cage.id] = ['+', '-', '*', '/']
        else:
            cage_ops[cage.id] = ['+', '*']
    
    cage_ids = [cage.id for cage in cages]
    op_lists = [cage_ops[cid] for cid in cage_ids]
    
    combinations = []
    for combo in itertools.product(*op_lists):
        combinations.append(dict(zip(cage_ids, combo)))
    
    return combinations


def has_unique_solution(n: int, grid_struct: List[int], cages: List[Cage], 
                       expected_solution: List[int]) -> bool:
    """厳密な一意解チェック"""
    all_combinations = generate_operator_combinations(cages)
    
    # 組み合わせ数が多すぎる場合
    if len(all_combinations) > 50000:
        return False
    
    found_solutions = set()
    
    for op_combo in all_combinations:
        sols = solve_with_operators(n, grid_struct, cages, op_combo, max_solutions=2)
        
        for sol in sols:
            found_solutions.add(tuple(sol))
        
        # 複数解が見つかった時点で終了
        if len(found_solutions) > 1:
            return False
    
    # 1つの解のみが見つかり、期待する解と一致するか
    if len(found_solutions) == 1:
        return tuple(expected_solution) in found_solutions
    
    return False


def generate_puzzle(n: int, max_attempts: int = 200) -> Tuple[List[int], List[int], List[Cage]]:
    """一意解のパズルを生成"""
    for attempt in range(max_attempts):
        solution = generate_latin_square(n)
        grid_struct = generate_cages(n)
        cages = calculate_targets(grid_struct, solution, n)
        
        if has_unique_solution(n, grid_struct, cages, solution):
            print(f"✓ 一意解のパズルを生成しました（試行回数: {attempt + 1}）")
            return solution, grid_struct, cages
        
        if (attempt + 1) % 10 == 0:
            print(f"  試行中... {attempt + 1}/{max_attempts}")
    
    print(f"警告: {max_attempts}回の試行で一意解が見つかりませんでした")
    return solution, grid_struct, cages


def get_cage_borders(idx: int, cage_id: int, grid_struct: List[int], n: int) -> Dict[str, bool]:
    """セルのケージ境界を判定（Trueは太線、Falseは細線）"""
    r, c = idx // n, idx % n
    borders = {}
    
    # 上（外周または異なるケージ境界は太線）
    if r == 0 or grid_struct[idx - n] != cage_id:
        borders['top'] = True
    else:
        borders['top'] = False
    
    # 下（外周または異なるケージ境界は太線）
    if r == n - 1 or grid_struct[idx + n] != cage_id:
        borders['bottom'] = True
    else:
        borders['bottom'] = False
    
    # 左（外周または異なるケージ境界は太線）
    if c == 0 or grid_struct[idx - 1] != cage_id:
        borders['left'] = True
    else:
        borders['left'] = False
    
    # 右（外周または異なるケージ境界は太線）
    if c == n - 1 or grid_struct[idx + 1] != cage_id:
        borders['right'] = True
    else:
        borders['right'] = False
    
    return borders


def is_cage_top_left(idx: int, cage_id: int, grid_struct: List[int]) -> bool:
    """ケージの左上セルか判定"""
    for i in range(idx):
        if grid_struct[i] == cage_id:
            return False
    return True


def generate_svg(solution: List[int], grid_struct: List[int], cages: List[Cage], 
                show_solution: bool = False) -> str:
    """SVGを生成"""
    n = N
    width = n * CELL_SIZE
    height = n * CELL_SIZE
    
    svg_lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'  <rect x="0" y="0" width="{width}" height="{height}" fill="white"/>',
    ]
    
    # 1. すべてのセル背景を先に描画
    for idx in range(n * n):
        r, c = idx // n, idx % n
        x = c * CELL_SIZE
        y = r * CELL_SIZE
        svg_lines.append(f'  <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="white" stroke="none"/>')
    
    # 2. 内部の境界線を描画（外周は除く）
    for idx in range(n * n):
        r, c = idx // n, idx % n
        x = c * CELL_SIZE
        y = r * CELL_SIZE
        cage_id = grid_struct[idx]
        borders = get_cage_borders(idx, cage_id, grid_struct, n)
        
        # 上辺（最上行でない場合のみ）
        if r > 0:
            if borders['top']:
                svg_lines.append(f'  <line x1="{x}" y1="{y}" x2="{x + CELL_SIZE}" y2="{y}" stroke="black" stroke-width="{BORDER_THICK}"/>')
            else:
                svg_lines.append(f'  <line x1="{x}" y1="{y}" x2="{x + CELL_SIZE}" y2="{y}" stroke="gray" stroke-width="{BORDER_THIN}"/>')
        
        # 下辺（最下行でない場合のみ）
        if r < n - 1:
            if borders['bottom']:
                svg_lines.append(f'  <line x1="{x}" y1="{y + CELL_SIZE}" x2="{x + CELL_SIZE}" y2="{y + CELL_SIZE}" stroke="black" stroke-width="{BORDER_THICK}"/>')
            else:
                svg_lines.append(f'  <line x1="{x}" y1="{y + CELL_SIZE}" x2="{x + CELL_SIZE}" y2="{y + CELL_SIZE}" stroke="gray" stroke-width="{BORDER_THIN}"/>')
        
        # 左辺（最左列でない場合のみ）
        if c > 0:
            if borders['left']:
                svg_lines.append(f'  <line x1="{x}" y1="{y}" x2="{x}" y2="{y + CELL_SIZE}" stroke="black" stroke-width="{BORDER_THICK}"/>')
            else:
                svg_lines.append(f'  <line x1="{x}" y1="{y}" x2="{x}" y2="{y + CELL_SIZE}" stroke="gray" stroke-width="{BORDER_THIN}"/>')
        
        # 右辺（最右列でない場合のみ）
        if c < n - 1:
            if borders['right']:
                svg_lines.append(f'  <line x1="{x + CELL_SIZE}" y1="{y}" x2="{x + CELL_SIZE}" y2="{y + CELL_SIZE}" stroke="black" stroke-width="{BORDER_THICK}"/>')
            else:
                svg_lines.append(f'  <line x1="{x + CELL_SIZE}" y1="{y}" x2="{x + CELL_SIZE}" y2="{y + CELL_SIZE}" stroke="gray" stroke-width="{BORDER_THIN}"/>')
    
    # 3. 最外周フレームをrectのstrokeとして描画（確実にviewBox内に収める）
    svg_lines.append(f'  <!-- 外周フレーム（太線） -->')
    half_border = BORDER_THICK / 2
    svg_lines.append(f'  <rect x="{half_border}" y="{half_border}" width="{width - BORDER_THICK}" height="{height - BORDER_THICK}" fill="none" stroke="black" stroke-width="{BORDER_THICK}"/>')
    
    # 4. ターゲット値を描画
    for idx in range(n * n):
        cage_id = grid_struct[idx]
        if is_cage_top_left(idx, cage_id, grid_struct):
            cage = next(c for c in cages if c.id == cage_id)
            r, c = idx // n, idx % n
            x = c * CELL_SIZE + 4
            y = r * CELL_SIZE + FONT_SIZE_SMALL + 2
            
            svg_lines.append(f'  <text x="{x}" y="{y}" font-family="sans-serif" font-size="{FONT_SIZE_SMALL}" fill="black">{cage.target}</text>')
    
    # 5. 解答を描画
    if show_solution:
        for idx in range(n * n):
            r, c = idx // n, idx % n
            x = c * CELL_SIZE + CELL_SIZE / 2
            y = r * CELL_SIZE + CELL_SIZE / 2 + FONT_SIZE_LARGE / 3
            
            svg_lines.append(f'  <text x="{x}" y="{y}" font-family="sans-serif" font-size="{FONT_SIZE_LARGE}" fill="black" text-anchor="middle">{solution[idx]}</text>')
    
    svg_lines.append('</svg>')
    
    return '\n'.join(svg_lines)


def main():
    """メイン処理"""
    print("KenKen風パズル生成中...")
    print(f"サイズ: {N}×{N}")
    print()
    
    # パズル生成
    solution, grid_struct, cages = generate_puzzle(N)
    
    # ファイル名生成
    today = get_date_prefix()
    filename_puzzle = f"{today}_kenken.svg"
    filename_answer = f"{today}_kenken_ans.svg"
    
    # SVG生成
    svg_puzzle = generate_svg(solution, grid_struct, cages, show_solution=False)
    svg_answer = generate_svg(solution, grid_struct, cages, show_solution=True)
    
    # ファイル保存
    with open(filename_puzzle, 'w', encoding='utf-8') as f:
        f.write(svg_puzzle)
    print(f"✓ 問題を保存しました: {filename_puzzle}")
    
    with open(filename_answer, 'w', encoding='utf-8') as f:
        f.write(svg_answer)
    print(f"✓ 解答を保存しました: {filename_answer}")
    
    print()
    print("生成完了！")


if __name__ == "__main__":
    main()
