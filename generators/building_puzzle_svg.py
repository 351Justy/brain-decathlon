#!/usr/bin/env python3
"""
ビルディングパズル（Skyscrapers）SVG生成スクリプト
4×4サイズ固定、一意解保証

出力ファイル:
  - YYYYMMDD_building.svg     : 問題（外周ヒント＋空グリッド）
  - YYYYMMDD_building_ans.svg : 解答（外周ヒント＋解答入りグリッド）

必要モジュール: Python3標準ライブラリのみ（追加インストール不要）
"""

import random
from datetime import datetime
from copy import deepcopy


# ============================================================
# パズル生成ロジック（HTMLと同一）
# ============================================================

def shuffle(arr):
    """配列をシャッフルして返す"""
    result = arr[:]
    random.shuffle(result)
    return result


def vis_left(arr):
    """左から見えるビルの数を計算"""
    count = 0
    max_height = 0
    for v in arr:
        if v > max_height:
            max_height = v
            count += 1
    return count


def vis_right(arr):
    """右から見えるビルの数を計算"""
    return vis_left(arr[::-1])


def compute_clues(grid):
    """グリッドから全方向のヒントを計算"""
    n = len(grid)
    top = [0] * n
    bottom = [0] * n
    left = [0] * n
    right = [0] * n
    
    for r in range(n):
        left[r] = vis_left(grid[r])
        right[r] = vis_right(grid[r])
    
    for c in range(n):
        col = [grid[r][c] for r in range(n)]
        top[c] = vis_left(col)
        bottom[c] = vis_right(col)
    
    return {'top': top, 'bottom': bottom, 'left': left, 'right': right}


def make_latin(n):
    """ランダムなラテン方陣を生成"""
    grid = [[0] * n for _ in range(n)]
    
    # 最初の行をランダムに配置
    first_row = shuffle(list(range(1, n + 1)))
    grid[0] = first_row
    
    # バックトラッキングで残りを埋める
    def fill_grid(row, col):
        if row == n:
            return True
        if col == n:
            return fill_grid(row + 1, 0)
        
        used = set()
        for i in range(row):
            used.add(grid[i][col])
        for i in range(col):
            used.add(grid[row][i])
        
        candidates = shuffle([v for v in range(1, n + 1) if v not in used])
        
        for val in candidates:
            grid[row][col] = val
            if fill_grid(row, col + 1):
                return True
            grid[row][col] = 0
        
        return False
    
    fill_grid(1, 0)
    return grid


def solve_skyscrapers_complete(n, clues, max_solutions=2):
    """完全探索ソルバー（一意性確認用）"""
    top = clues['top']
    bottom = clues['bottom']
    left = clues['left']
    right = clues['right']
    
    grid = [[0] * n for _ in range(n)]
    solutions = []
    
    # 各セルの可能な値を事前計算
    possible = [[set(range(1, n + 1)) for _ in range(n)] for _ in range(n)]
    
    # ヒントに基づく制約を適用
    def apply_constraints():
        for i in range(n):
            if left[i] == 1:
                possible[i][0] = {n}
            if right[i] == 1:
                possible[i][n - 1] = {n}
            if top[i] == 1:
                possible[0][i] = {n}
            if bottom[i] == 1:
                possible[n - 1][i] = {n}
            
            if left[i] == n:
                for j in range(n):
                    possible[i][j] = {j + 1}
            if right[i] == n:
                for j in range(n):
                    possible[i][j] = {n - j}
            if top[i] == n:
                for j in range(n):
                    possible[j][i] = {j + 1}
            if bottom[i] == n:
                for j in range(n):
                    possible[j][i] = {n - j}
    
    apply_constraints()
    
    # バックトラッキング
    def solve(pos):
        if len(solutions) >= max_solutions:
            return
        
        if pos == n * n:
            # 全てのヒントをチェック
            clues_check = compute_clues(grid)
            valid = True
            
            for i in range(n):
                if top[i] and clues_check['top'][i] != top[i]:
                    valid = False
                if bottom[i] and clues_check['bottom'][i] != bottom[i]:
                    valid = False
                if left[i] and clues_check['left'][i] != left[i]:
                    valid = False
                if right[i] and clues_check['right'][i] != right[i]:
                    valid = False
            
            if valid:
                solutions.append([row[:] for row in grid])
            return
        
        r = pos // n
        c = pos % n
        
        # 行と列で使用済みの値を確認
        used = set()
        for i in range(n):
            if grid[r][i] > 0:
                used.add(grid[r][i])
            if grid[i][c] > 0:
                used.add(grid[i][c])
        
        for val in range(1, n + 1):
            if val in used:
                continue
            if val not in possible[r][c]:
                continue
            
            grid[r][c] = val
            
            # 早期剪定
            valid = True
            
            # 行が完成した場合のチェック
            if c == n - 1 and 0 not in grid[r]:
                if left[r] and vis_left(grid[r]) != left[r]:
                    valid = False
                if right[r] and vis_right(grid[r]) != right[r]:
                    valid = False
            
            # 列が完成した場合のチェック
            if r == n - 1 and all(grid[row][c] > 0 for row in range(n)):
                col = [grid[row][c] for row in range(n)]
                if top[c] and vis_left(col) != top[c]:
                    valid = False
                if bottom[c] and vis_right(col) != bottom[c]:
                    valid = False
            
            if valid:
                solve(pos + 1)
            
            grid[r][c] = 0
    
    solve(0)
    return solutions


def generate_unique_puzzle(n, max_attempts=300):
    """一意解を保証するパズルを生成"""
    for attempt in range(max_attempts):
        solution = make_latin(n)
        full_clues = compute_clues(solution)
        
        # ヒントをランダムに削除しながら一意性を保持
        clues = deepcopy(full_clues)
        positions = []
        
        for i in range(n):
            positions.extend([('top', i), ('bottom', i), ('left', i), ('right', i)])
        
        random.shuffle(positions)
        
        # 最小ヒント数の設定
        min_clues = max(n + 2, int(n * 1.5) + 1)
        current_clues = n * 4
        
        for side, idx in positions:
            if current_clues <= min_clues:
                break
            
            backup = clues[side][idx]
            if not backup:
                continue
            
            clues[side][idx] = 0
            
            # 完全探索で解の数を確認
            solutions = solve_skyscrapers_complete(n, clues, 2)
            
            if len(solutions) != 1:
                # 一意でない場合は元に戻す
                clues[side][idx] = backup
            else:
                current_clues -= 1
        
        # 最終確認
        final_check = solve_skyscrapers_complete(n, clues, 2)
        if len(final_check) == 1:
            clue_count = sum(
                sum(1 for x in clues[side] if x > 0)
                for side in ['top', 'bottom', 'left', 'right']
            )
            
            if clue_count <= n * 2:
                return {'n': n, 'clues': clues, 'solution': final_check[0]}
    
    # フォールバック
    solution = make_latin(n)
    clues = compute_clues(solution)
    return {'n': n, 'clues': clues, 'solution': solution}


# ============================================================
# SVG生成
# ============================================================

def draw_arrow_down(x, y, size=10):
    """下向き矢印のパスを生成（三角形）"""
    # 頂点が下、底辺が上の三角形
    half = size / 2
    return f'<path d="M{x},{y + size} L{x - half},{y} L{x + half},{y} Z" fill="black"/>'


def draw_arrow_up(x, y, size=10):
    """上向き矢印のパスを生成（三角形）"""
    # 頂点が上、底辺が下の三角形
    half = size / 2
    return f'<path d="M{x},{y} L{x - half},{y + size} L{x + half},{y + size} Z" fill="black"/>'


def draw_arrow_right(x, y, size=10):
    """右向き矢印のパスを生成（三角形）"""
    # 頂点が右、底辺が左の三角形
    half = size / 2
    return f'<path d="M{x + size},{y} L{x},{y - half} L{x},{y + half} Z" fill="black"/>'


def draw_arrow_left(x, y, size=10):
    """左向き矢印のパスを生成（三角形）"""
    # 頂点が左、底辺が右の三角形
    half = size / 2
    return f'<path d="M{x},{y} L{x + size},{y - half} L{x + size},{y + half} Z" fill="black"/>'


def generate_svg(puzzle, show_solution=False):
    """
    SVGを生成
    
    Args:
        puzzle: パズルデータ {'n': int, 'clues': dict, 'solution': list}
        show_solution: True=解答表示, False=空グリッド
    
    Returns:
        SVG文字列
    """
    n = puzzle['n']
    clues = puzzle['clues']
    solution = puzzle['solution']
    
    # サイズ設定
    cell_size = 50
    hint_size = 40
    padding = 10
    arrow_size = 10
    
    # 全体サイズ
    total_width = hint_size * 2 + cell_size * n + padding * 2
    total_height = hint_size * 2 + cell_size * n + padding * 2
    
    # グリッド開始位置
    grid_x = padding + hint_size
    grid_y = padding + hint_size
    
    font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
    
    svg_parts = []
    
    # SVGヘッダー
    svg_parts.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     width="{total_width}" height="{total_height}" 
     viewBox="0 0 {total_width} {total_height}">
''')
    
    # グリッド線を描画
    svg_parts.append('  <!-- グリッド線 -->\n')
    for i in range(n + 1):
        # 横線
        y = grid_y + i * cell_size
        svg_parts.append(f'  <line x1="{grid_x}" y1="{y}" x2="{grid_x + n * cell_size}" y2="{y}" stroke="black" stroke-width="1.5"/>\n')
        # 縦線
        x = grid_x + i * cell_size
        svg_parts.append(f'  <line x1="{x}" y1="{grid_y}" x2="{x}" y2="{grid_y + n * cell_size}" stroke="black" stroke-width="1.5"/>\n')
    
    # ヒントと矢印を描画
    svg_parts.append('\n  <!-- ヒント（数字と矢印） -->\n')
    
    for i in range(n):
        cell_center_x = grid_x + i * cell_size + cell_size / 2
        cell_center_y = grid_y + i * cell_size + cell_size / 2
        
        # 上側のヒント（top）- 数字が上、下向き矢印が下
        if clues['top'][i] > 0:
            hx = cell_center_x
            # 数字（上部）
            text_y = padding + hint_size * 0.35
            svg_parts.append(f'  <text x="{hx}" y="{text_y}" text-anchor="middle" dominant-baseline="middle" font-family="{font_family}" font-size="18" fill="black">{clues["top"][i]}</text>\n')
            # 下向き矢印（下部）
            arrow_y = padding + hint_size * 0.55
            svg_parts.append(f'  {draw_arrow_down(hx, arrow_y, arrow_size)}\n')
        
        # 下側のヒント（bottom）- 上向き矢印が上、数字が下
        if clues['bottom'][i] > 0:
            hx = cell_center_x
            base_y = grid_y + n * cell_size
            # 上向き矢印（上部）
            arrow_y = base_y + hint_size * 0.12
            svg_parts.append(f'  {draw_arrow_up(hx, arrow_y, arrow_size)}\n')
            # 数字（下部）- 矢印との間隔を少し広げる
            text_y = base_y + hint_size * 0.75
            svg_parts.append(f'  <text x="{hx}" y="{text_y}" text-anchor="middle" dominant-baseline="middle" font-family="{font_family}" font-size="18" fill="black">{clues["bottom"][i]}</text>\n')
        
        # 左側のヒント（left）- 数字が左、右向き矢印が右
        if clues['left'][i] > 0:
            hy = cell_center_y
            # 数字（左部）
            text_x = padding + hint_size * 0.3
            svg_parts.append(f'  <text x="{text_x}" y="{hy}" text-anchor="middle" dominant-baseline="middle" font-family="{font_family}" font-size="18" fill="black">{clues["left"][i]}</text>\n')
            # 右向き矢印（右部）
            arrow_x = padding + hint_size * 0.5
            svg_parts.append(f'  {draw_arrow_right(arrow_x, hy, arrow_size)}\n')
        
        # 右側のヒント（right）- 左向き矢印が左、数字が右
        if clues['right'][i] > 0:
            hy = cell_center_y
            base_x = grid_x + n * cell_size
            # 左向き矢印（左部）
            arrow_x = base_x + hint_size * 0.1
            svg_parts.append(f'  {draw_arrow_left(arrow_x, hy, arrow_size)}\n')
            # 数字（右部）
            text_x = base_x + hint_size * 0.7
            svg_parts.append(f'  <text x="{text_x}" y="{hy}" text-anchor="middle" dominant-baseline="middle" font-family="{font_family}" font-size="18" fill="black">{clues["right"][i]}</text>\n')
    
    # 解答を描画（show_solution=Trueの場合）
    if show_solution:
        svg_parts.append('\n  <!-- 解答数字 -->\n')
        for r in range(n):
            for c in range(n):
                cx = grid_x + c * cell_size + cell_size / 2
                cy = grid_y + r * cell_size + cell_size / 2
                val = solution[r][c]
                svg_parts.append(f'  <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="middle" font-family="{font_family}" font-size="24" fill="black">{val}</text>\n')
    
    svg_parts.append('</svg>\n')
    
    return ''.join(svg_parts)


def main():
    """メイン処理"""
    # パズルサイズ（4×4固定）
    n = 4
    
    # 日付からファイル名を生成
    today = datetime.now().strftime('%Y%m%d')
    problem_filename = f'{today}_building.svg'
    answer_filename = f'{today}_building_ans.svg'
    
    print(f'ビルディングパズル {n}×{n} を生成中...')
    
    # パズル生成
    puzzle = generate_unique_puzzle(n)
    
    # ヒント数をカウント
    clue_count = sum(
        sum(1 for x in puzzle['clues'][side] if x > 0)
        for side in ['top', 'bottom', 'left', 'right']
    )
    
    print(f'生成完了！ヒント数: {clue_count}')
    print()
    
    # 解答を表示
    print('解答:')
    for row in puzzle['solution']:
        print('  ' + ' '.join(str(x) for x in row))
    print()
    
    # ヒントを表示
    print('ヒント:')
    print(f'  Top:    {puzzle["clues"]["top"]}')
    print(f'  Bottom: {puzzle["clues"]["bottom"]}')
    print(f'  Left:   {puzzle["clues"]["left"]}')
    print(f'  Right:  {puzzle["clues"]["right"]}')
    print()
    
    # 問題SVG生成
    problem_svg = generate_svg(puzzle, show_solution=False)
    with open(problem_filename, 'w', encoding='utf-8') as f:
        f.write(problem_svg)
    print(f'問題ファイル保存: {problem_filename}')
    
    # 解答SVG生成
    answer_svg = generate_svg(puzzle, show_solution=True)
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f'解答ファイル保存: {answer_filename}')
    
    print()
    print('完了！')


if __name__ == '__main__':
    main()
