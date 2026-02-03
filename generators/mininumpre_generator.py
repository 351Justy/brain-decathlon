#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミニナンプレ 6×6 SVG生成スクリプト
- 論理的解法のみで解けるパズルを生成
- ヒント数: 10〜12
- 対称性: 実行日付に基づいて6種類から自動選択
- 出力: YYYYMMDD_mininumpre.svg, YYYYMMDD_mininumpre_ans.svg
"""

import random
import copy
from datetime import date


class MiniNumpreSolver:
    """論理的解法のみでナンプレを解くソルバー"""
    
    def __init__(self):
        self.N = 6
        self.BLOCK_ROWS = 2
        self.BLOCK_COLS = 3
    
    def get_candidates(self, grid):
        """各セルの候補を計算"""
        candidates = [[set() for _ in range(self.N)] for _ in range(self.N)]
        for r in range(self.N):
            for c in range(self.N):
                if grid[r][c] == 0:
                    candidates[r][c] = self._get_cell_candidates(grid, r, c)
        return candidates
    
    def _get_cell_candidates(self, grid, r, c):
        """特定セルの候補を取得"""
        if grid[r][c] != 0:
            return set()
        
        used = set()
        # 行
        for cc in range(self.N):
            if grid[r][cc] != 0:
                used.add(grid[r][cc])
        # 列
        for rr in range(self.N):
            if grid[rr][c] != 0:
                used.add(grid[rr][c])
        # ブロック
        br = (r // self.BLOCK_ROWS) * self.BLOCK_ROWS
        bc = (c // self.BLOCK_COLS) * self.BLOCK_COLS
        for rr in range(br, br + self.BLOCK_ROWS):
            for cc in range(bc, bc + self.BLOCK_COLS):
                if grid[rr][cc] != 0:
                    used.add(grid[rr][cc])
        
        return set(range(1, self.N + 1)) - used
    
    def solve_logically(self, grid):
        """
        論理的技法のみでパズルを解く
        戻り値: (解けたか, 解いたグリッド, 使用した技法のリスト)
        """
        grid = copy.deepcopy(grid)
        candidates = self.get_candidates(grid)
        techniques_used = []
        
        while True:
            progress = False
            
            # 1. Naked Single（裸の単一候補）
            result = self._naked_single(grid, candidates)
            if result:
                progress = True
                if 'Naked Single' not in techniques_used:
                    techniques_used.append('Naked Single')
                continue
            
            # 2. Hidden Single（隠れた単一候補）
            result = self._hidden_single(grid, candidates)
            if result:
                progress = True
                if 'Hidden Single' not in techniques_used:
                    techniques_used.append('Hidden Single')
                continue
            
            # 3. Naked Pair
            result = self._naked_pair(candidates)
            if result:
                progress = True
                if 'Naked Pair' not in techniques_used:
                    techniques_used.append('Naked Pair')
                continue
            
            # 4. Naked Triple
            result = self._naked_triple(candidates)
            if result:
                progress = True
                if 'Naked Triple' not in techniques_used:
                    techniques_used.append('Naked Triple')
                continue
            
            # 5. Pointing Pair/Triple
            result = self._pointing(candidates)
            if result:
                progress = True
                if 'Pointing' not in techniques_used:
                    techniques_used.append('Pointing')
                continue
            
            # 6. Box/Line Reduction
            result = self._box_line_reduction(candidates)
            if result:
                progress = True
                if 'Box/Line Reduction' not in techniques_used:
                    techniques_used.append('Box/Line Reduction')
                continue
            
            if not progress:
                break
        
        # 解けたかチェック
        solved = all(grid[r][c] != 0 for r in range(self.N) for c in range(self.N))
        return solved, grid, techniques_used
    
    def _set_cell(self, grid, candidates, r, c, val):
        """セルに値を設定し、候補を更新"""
        grid[r][c] = val
        candidates[r][c] = set()
        
        # 関連セルから候補を除去
        # 行
        for cc in range(self.N):
            candidates[r][cc].discard(val)
        # 列
        for rr in range(self.N):
            candidates[rr][c].discard(val)
        # ブロック
        br = (r // self.BLOCK_ROWS) * self.BLOCK_ROWS
        bc = (c // self.BLOCK_COLS) * self.BLOCK_COLS
        for rr in range(br, br + self.BLOCK_ROWS):
            for cc in range(bc, bc + self.BLOCK_COLS):
                candidates[rr][cc].discard(val)
    
    def _naked_single(self, grid, candidates):
        """候補が1つだけのセルを埋める"""
        for r in range(self.N):
            for c in range(self.N):
                if grid[r][c] == 0 and len(candidates[r][c]) == 1:
                    val = list(candidates[r][c])[0]
                    self._set_cell(grid, candidates, r, c, val)
                    return True
        return False
    
    def _hidden_single(self, grid, candidates):
        """行/列/ブロックで1箇所にしか入らない数字を見つける"""
        # 行チェック
        for r in range(self.N):
            for num in range(1, self.N + 1):
                positions = [c for c in range(self.N) if num in candidates[r][c]]
                if len(positions) == 1:
                    c = positions[0]
                    self._set_cell(grid, candidates, r, c, num)
                    return True
        
        # 列チェック
        for c in range(self.N):
            for num in range(1, self.N + 1):
                positions = [r for r in range(self.N) if num in candidates[r][c]]
                if len(positions) == 1:
                    r = positions[0]
                    self._set_cell(grid, candidates, r, c, num)
                    return True
        
        # ブロックチェック
        for br in range(0, self.N, self.BLOCK_ROWS):
            for bc in range(0, self.N, self.BLOCK_COLS):
                for num in range(1, self.N + 1):
                    positions = []
                    for rr in range(br, br + self.BLOCK_ROWS):
                        for cc in range(bc, bc + self.BLOCK_COLS):
                            if num in candidates[rr][cc]:
                                positions.append((rr, cc))
                    if len(positions) == 1:
                        r, c = positions[0]
                        self._set_cell(grid, candidates, r, c, num)
                        return True
        
        return False
    
    def _naked_pair(self, candidates):
        """Naked Pair技法"""
        # 行
        for r in range(self.N):
            cells = [(c, candidates[r][c]) for c in range(self.N) if len(candidates[r][c]) == 2]
            for i in range(len(cells)):
                for j in range(i + 1, len(cells)):
                    if cells[i][1] == cells[j][1]:
                        pair = cells[i][1]
                        c1, c2 = cells[i][0], cells[j][0]
                        changed = False
                        for c in range(self.N):
                            if c != c1 and c != c2:
                                for val in pair:
                                    if val in candidates[r][c]:
                                        candidates[r][c].discard(val)
                                        changed = True
                        if changed:
                            return True
        
        # 列
        for c in range(self.N):
            cells = [(r, candidates[r][c]) for r in range(self.N) if len(candidates[r][c]) == 2]
            for i in range(len(cells)):
                for j in range(i + 1, len(cells)):
                    if cells[i][1] == cells[j][1]:
                        pair = cells[i][1]
                        r1, r2 = cells[i][0], cells[j][0]
                        changed = False
                        for r in range(self.N):
                            if r != r1 and r != r2:
                                for val in pair:
                                    if val in candidates[r][c]:
                                        candidates[r][c].discard(val)
                                        changed = True
                        if changed:
                            return True
        
        # ブロック
        for br in range(0, self.N, self.BLOCK_ROWS):
            for bc in range(0, self.N, self.BLOCK_COLS):
                cells = []
                for rr in range(br, br + self.BLOCK_ROWS):
                    for cc in range(bc, bc + self.BLOCK_COLS):
                        if len(candidates[rr][cc]) == 2:
                            cells.append(((rr, cc), candidates[rr][cc]))
                for i in range(len(cells)):
                    for j in range(i + 1, len(cells)):
                        if cells[i][1] == cells[j][1]:
                            pair = cells[i][1]
                            pos1, pos2 = cells[i][0], cells[j][0]
                            changed = False
                            for rr in range(br, br + self.BLOCK_ROWS):
                                for cc in range(bc, bc + self.BLOCK_COLS):
                                    if (rr, cc) != pos1 and (rr, cc) != pos2:
                                        for val in pair:
                                            if val in candidates[rr][cc]:
                                                candidates[rr][cc].discard(val)
                                                changed = True
                            if changed:
                                return True
        
        return False
    
    def _naked_triple(self, candidates):
        """Naked Triple技法"""
        from itertools import combinations
        
        # 行
        for r in range(self.N):
            cells = [(c, candidates[r][c]) for c in range(self.N) 
                     if 0 < len(candidates[r][c]) <= 3]
            if len(cells) >= 3:
                for combo in combinations(range(len(cells)), 3):
                    union = set()
                    for idx in combo:
                        union |= cells[idx][1]
                    if len(union) == 3:
                        cols = {cells[idx][0] for idx in combo}
                        changed = False
                        for c in range(self.N):
                            if c not in cols:
                                for val in union:
                                    if val in candidates[r][c]:
                                        candidates[r][c].discard(val)
                                        changed = True
                        if changed:
                            return True
        
        # 列
        for c in range(self.N):
            cells = [(r, candidates[r][c]) for r in range(self.N) 
                     if 0 < len(candidates[r][c]) <= 3]
            if len(cells) >= 3:
                for combo in combinations(range(len(cells)), 3):
                    union = set()
                    for idx in combo:
                        union |= cells[idx][1]
                    if len(union) == 3:
                        rows = {cells[idx][0] for idx in combo}
                        changed = False
                        for r in range(self.N):
                            if r not in rows:
                                for val in union:
                                    if val in candidates[r][c]:
                                        candidates[r][c].discard(val)
                                        changed = True
                        if changed:
                            return True
        
        # ブロック
        for br in range(0, self.N, self.BLOCK_ROWS):
            for bc in range(0, self.N, self.BLOCK_COLS):
                cells = []
                for rr in range(br, br + self.BLOCK_ROWS):
                    for cc in range(bc, bc + self.BLOCK_COLS):
                        if 0 < len(candidates[rr][cc]) <= 3:
                            cells.append(((rr, cc), candidates[rr][cc]))
                if len(cells) >= 3:
                    for combo in combinations(range(len(cells)), 3):
                        union = set()
                        for idx in combo:
                            union |= cells[idx][1]
                        if len(union) == 3:
                            positions = {cells[idx][0] for idx in combo}
                            changed = False
                            for rr in range(br, br + self.BLOCK_ROWS):
                                for cc in range(bc, bc + self.BLOCK_COLS):
                                    if (rr, cc) not in positions:
                                        for val in union:
                                            if val in candidates[rr][cc]:
                                                candidates[rr][cc].discard(val)
                                                changed = True
                            if changed:
                                return True
        
        return False
    
    def _pointing(self, candidates):
        """Pointing Pair/Triple - ブロック内の候補が1行/列に限定される場合"""
        for br in range(0, self.N, self.BLOCK_ROWS):
            for bc in range(0, self.N, self.BLOCK_COLS):
                for num in range(1, self.N + 1):
                    positions = []
                    for rr in range(br, br + self.BLOCK_ROWS):
                        for cc in range(bc, bc + self.BLOCK_COLS):
                            if num in candidates[rr][cc]:
                                positions.append((rr, cc))
                    
                    if len(positions) < 2:
                        continue
                    
                    # 同じ行にあるか
                    rows = {p[0] for p in positions}
                    if len(rows) == 1:
                        r = list(rows)[0]
                        changed = False
                        for c in range(self.N):
                            if c < bc or c >= bc + self.BLOCK_COLS:
                                if num in candidates[r][c]:
                                    candidates[r][c].discard(num)
                                    changed = True
                        if changed:
                            return True
                    
                    # 同じ列にあるか
                    cols = {p[1] for p in positions}
                    if len(cols) == 1:
                        c = list(cols)[0]
                        changed = False
                        for r in range(self.N):
                            if r < br or r >= br + self.BLOCK_ROWS:
                                if num in candidates[r][c]:
                                    candidates[r][c].discard(num)
                                    changed = True
                        if changed:
                            return True
        
        return False
    
    def _box_line_reduction(self, candidates):
        """Box/Line Reduction - 行/列内の候補が1ブロックに限定される場合"""
        # 行からブロックへの削減
        for r in range(self.N):
            for num in range(1, self.N + 1):
                positions = [c for c in range(self.N) if num in candidates[r][c]]
                if len(positions) < 2:
                    continue
                
                # 全て同じブロック列にあるか
                block_cols = {c // self.BLOCK_COLS for c in positions}
                if len(block_cols) == 1:
                    bc = list(block_cols)[0] * self.BLOCK_COLS
                    br = (r // self.BLOCK_ROWS) * self.BLOCK_ROWS
                    changed = False
                    for rr in range(br, br + self.BLOCK_ROWS):
                        if rr != r:
                            for cc in range(bc, bc + self.BLOCK_COLS):
                                if num in candidates[rr][cc]:
                                    candidates[rr][cc].discard(num)
                                    changed = True
                    if changed:
                        return True
        
        # 列からブロックへの削減
        for c in range(self.N):
            for num in range(1, self.N + 1):
                positions = [r for r in range(self.N) if num in candidates[r][c]]
                if len(positions) < 2:
                    continue
                
                # 全て同じブロック行にあるか
                block_rows = {r // self.BLOCK_ROWS for r in positions}
                if len(block_rows) == 1:
                    br = list(block_rows)[0] * self.BLOCK_ROWS
                    bc = (c // self.BLOCK_COLS) * self.BLOCK_COLS
                    changed = False
                    for cc in range(bc, bc + self.BLOCK_COLS):
                        if cc != c:
                            for rr in range(br, br + self.BLOCK_ROWS):
                                if num in candidates[rr][cc]:
                                    candidates[rr][cc].discard(num)
                                    changed = True
                    if changed:
                        return True
        
        return False


class MiniNumpreGenerator:
    """ミニナンプレ問題生成クラス"""
    
    SYMMETRY_TYPES = ['none', 'horizontal', 'vertical', 'diagonal', 'rotational', 'central']
    
    def __init__(self):
        self.N = 6
        self.BLOCK_ROWS = 2
        self.BLOCK_COLS = 3
        self.solver = MiniNumpreSolver()
        self.solution = [[0] * self.N for _ in range(self.N)]
        self.puzzle = [[0] * self.N for _ in range(self.N)]
    
    def generate(self, target_hints, symmetry_type='none'):
        """
        論理的に解けるパズルを生成
        target_hints: 目標ヒント数（10〜12）
        symmetry_type: 対称性タイプ
        """
        max_attempts = 100
        
        for attempt in range(max_attempts):
            # 解答生成
            self._generate_solution()
            
            # パズル作成
            puzzle = self._create_puzzle(target_hints, symmetry_type)
            
            if puzzle:
                self.puzzle = puzzle
                return True
        
        return False
    
    def _generate_solution(self):
        """有効な解答グリッドを生成"""
        # 初期パターン
        for r in range(self.N):
            for c in range(self.N):
                self.solution[r][c] = ((r * self.BLOCK_COLS + r // self.BLOCK_ROWS + c) % self.N) + 1
        
        self._randomize_solution()
    
    def _randomize_solution(self):
        """解答をランダム化"""
        # 数字のマッピングをシャッフル
        digits = list(range(1, self.N + 1))
        mapping = digits[:]
        random.shuffle(mapping)
        for r in range(self.N):
            for c in range(self.N):
                self.solution[r][c] = mapping[self.solution[r][c] - 1]
        
        # ブロック内の行をシャッフル
        for br in range(self.N // self.BLOCK_ROWS):
            base = br * self.BLOCK_ROWS
            rows = [self.solution[base + i][:] for i in range(self.BLOCK_ROWS)]
            random.shuffle(rows)
            for i in range(self.BLOCK_ROWS):
                self.solution[base + i] = rows[i]
        
        # ブロック内の列をシャッフル
        for bc in range(self.N // self.BLOCK_COLS):
            base = bc * self.BLOCK_COLS
            cols_idx = list(range(base, base + self.BLOCK_COLS))
            random.shuffle(cols_idx)
            temp_cols = [[self.solution[r][ci] for r in range(self.N)] for ci in cols_idx]
            for i, ci in enumerate(range(base, base + self.BLOCK_COLS)):
                for r in range(self.N):
                    self.solution[r][ci] = temp_cols[i][r]
        
        # ブロック行をシャッフル
        block_row_groups = list(range(self.N // self.BLOCK_ROWS))
        random.shuffle(block_row_groups)
        copy_sol = [row[:] for row in self.solution]
        for tb, sb in enumerate(block_row_groups):
            for i in range(self.BLOCK_ROWS):
                self.solution[tb * self.BLOCK_ROWS + i] = copy_sol[sb * self.BLOCK_ROWS + i][:]
        
        # ブロック列をシャッフル
        block_col_groups = list(range(self.N // self.BLOCK_COLS))
        random.shuffle(block_col_groups)
        copy_sol = [row[:] for row in self.solution]
        for r in range(self.N):
            for tb, sb in enumerate(block_col_groups):
                for i in range(self.BLOCK_COLS):
                    self.solution[r][tb * self.BLOCK_COLS + i] = copy_sol[r][sb * self.BLOCK_COLS + i]
    
    def _get_symmetry_partners(self, r, c, symmetry_type):
        """対称位置のセルを取得"""
        N = self.N
        partners = []
        
        if symmetry_type == 'horizontal':
            if c != N - 1 - c:
                partners.append((r, N - 1 - c))
        elif symmetry_type == 'vertical':
            if r != N - 1 - r:
                partners.append((N - 1 - r, c))
        elif symmetry_type == 'diagonal':
            if r != c:
                partners.append((c, r))
        elif symmetry_type in ('rotational', 'central'):
            if r != N - 1 - r or c != N - 1 - c:
                partners.append((N - 1 - r, N - 1 - c))
        
        return partners
    
    def _create_puzzle(self, target_hints, symmetry_type):
        """
        論理的に解けるパズルを作成
        """
        temp_grid = [row[:] for row in self.solution]
        filled = self.N * self.N
        
        # セルリストをシャッフル
        cells = [(r, c) for r in range(self.N) for c in range(self.N)]
        random.shuffle(cells)
        
        for r, c in cells:
            if filled <= target_hints:
                break
            if temp_grid[r][c] == 0:
                continue
            
            # 対称パートナーを取得
            partners = self._get_symmetry_partners(r, c, symmetry_type)
            group = [(r, c)] + [(rr, cc) for rr, cc in partners if temp_grid[rr][cc] != 0]
            
            # 重複除去
            seen = set()
            unique_group = []
            for rr, cc in group:
                key = (rr, cc)
                if key not in seen:
                    seen.add(key)
                    unique_group.append((rr, cc))
            
            # ヒント数チェック
            if filled - len(unique_group) < target_hints:
                continue
            
            # 一時的に削除
            saved = [(rr, cc, temp_grid[rr][cc]) for rr, cc in unique_group]
            for rr, cc in unique_group:
                temp_grid[rr][cc] = 0
            
            # 論理的に解けるかチェック
            solved, _, _ = self.solver.solve_logically(temp_grid)
            
            if solved:
                filled -= len(unique_group)
            else:
                # 元に戻す
                for rr, cc, v in saved:
                    temp_grid[rr][cc] = v
        
        # 目標ヒント数に達しているかチェック
        actual_hints = sum(1 for r in range(self.N) for c in range(self.N) if temp_grid[r][c] != 0)
        
        if actual_hints <= target_hints + 2 and actual_hints >= target_hints - 2:
            return temp_grid
        
        return None
    
    def get_hint_count(self):
        """現在のパズルのヒント数を取得"""
        return sum(1 for r in range(self.N) for c in range(self.N) if self.puzzle[r][c] != 0)


def generate_svg(grid, solution, show_answer=False, cell_size=50):
    """
    SVG文字列を生成
    - 背景色なし
    - 太い罫線（ブロック境界・外枠）はBlack
    - 細い罫線（セル境界）はグレー
    - 数字はBlack
    - フォント設定はcryptarithm_generator.pyと統一
    """
    N = 6
    BLOCK_ROWS = 2
    BLOCK_COLS = 3
    W = cell_size * N
    H = cell_size * N
    
    # フォント設定（cryptarithm_generator.pyと統一）
    font_family = "DejaVu Sans, Liberation Sans, Noto Sans, sans-serif"
    font_size = 36  # cryptarithm_generator.pyと同じ固定値
    
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    
    # CSSスタイル（cryptarithm_generator.pyと同じ方式）
    svg_parts.append('<style>')
    svg_parts.append(f'  .digit {{ font-family: {font_family}; font-size: {font_size}px; fill: black; }}')
    svg_parts.append(f'  .digit-answer {{ font-family: {font_family}; font-size: {font_size}px; fill: #666666; }}')
    svg_parts.append('</style>')
    
    # グリッド線
    svg_parts.append('<g>')
    
    for i in range(N + 1):
        # 横線
        is_thick = (i == 0 or i == N or i % BLOCK_ROWS == 0)
        stroke_width = 3 if is_thick else 1
        stroke_color = "black" if is_thick else "#999999"
        svg_parts.append(f'<line x1="0" y1="{i * cell_size}" x2="{W}" y2="{i * cell_size}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>')
        
        # 縦線
        is_thick = (i == 0 or i == N or i % BLOCK_COLS == 0)
        stroke_width = 3 if is_thick else 1
        stroke_color = "black" if is_thick else "#999999"
        svg_parts.append(f'<line x1="{i * cell_size}" y1="0" x2="{i * cell_size}" y2="{H}" stroke="{stroke_color}" stroke-width="{stroke_width}"/>')
    
    svg_parts.append('</g>')
    
    # 数字
    svg_parts.append('<g>')
    
    for r in range(N):
        for c in range(N):
            val = grid[r][c]
            sol_val = solution[r][c]
            
            x = c * cell_size + cell_size // 2
            # y座標を調整（dominant-baselineではなく位置で調整、覆面算と同じ方式）
            y = r * cell_size + cell_size * 0.65
            
            if val != 0:
                # ヒント数字
                svg_parts.append(
                    f'<text x="{x}" y="{y}" class="digit" text-anchor="middle">{val}</text>'
                )
            elif show_answer and sol_val != 0:
                # 解答数字（グレーで表示して区別）
                svg_parts.append(
                    f'<text x="{x}" y="{y}" class="digit-answer" text-anchor="middle">{sol_val}</text>'
                )
    
    svg_parts.append('</g>')
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)


def get_symmetry_by_date(d=None):
    """日付に基づいて対称性タイプを選択"""
    if d is None:
        d = date.today()
    
    # 日付のシリアル値（toordinal）を6で割った余り
    serial = d.toordinal()
    index = serial % 6
    
    symmetry_types = ['none', 'horizontal', 'vertical', 'diagonal', 'rotational', 'central']
    return symmetry_types[index]


def main():
    """メイン処理"""
    today = date.today()
    date_str = today.strftime('%Y%m%d')
    
    # 対称性を日付から決定
    symmetry = get_symmetry_by_date(today)
    
    # ヒント数を10〜12の範囲でランダムに選択
    target_hints = random.randint(10, 12)
    
    print(f"日付: {date_str}")
    print(f"対称性: {symmetry}")
    print(f"目標ヒント数: {target_hints}")
    print("パズル生成中...")
    
    # パズル生成
    generator = MiniNumpreGenerator()
    success = generator.generate(target_hints, symmetry)
    
    if not success:
        print("エラー: パズル生成に失敗しました。再度実行してください。")
        return
    
    actual_hints = generator.get_hint_count()
    print(f"実際のヒント数: {actual_hints}")
    
    # 論理的に解けることを最終確認
    solver = MiniNumpreSolver()
    solved, _, techniques = solver.solve_logically(generator.puzzle)
    
    if not solved:
        print("エラー: 生成されたパズルが論理的に解けません。再度実行してください。")
        return
    
    print(f"使用される解法技法: {', '.join(techniques)}")
    
    # SVG生成
    puzzle_svg = generate_svg(generator.puzzle, generator.solution, show_answer=False)
    answer_svg = generate_svg(generator.puzzle, generator.solution, show_answer=True)
    
    # ファイル出力
    puzzle_filename = f"{date_str}_mininumpre.svg"
    answer_filename = f"{date_str}_mininumpre_ans.svg"
    
    with open(puzzle_filename, 'w', encoding='utf-8') as f:
        f.write(puzzle_svg)
    print(f"問題ファイル生成: {puzzle_filename}")
    
    with open(answer_filename, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f"解答ファイル生成: {answer_filename}")
    
    # パズルのテキスト表示
    print("\n--- 生成されたパズル ---")
    for r in range(6):
        row_str = ""
        for c in range(6):
            val = generator.puzzle[r][c]
            row_str += str(val) if val != 0 else "."
            if c == 2:
                row_str += "|"
        print(row_str)
        if r == 1 or r == 3:
            print("---+---")
    
    print("\n--- 解答 ---")
    for r in range(6):
        row_str = ""
        for c in range(6):
            row_str += str(generator.solution[r][c])
            if c == 2:
                row_str += "|"
        print(row_str)
        if r == 1 or r == 3:
            print("---+---")


if __name__ == '__main__':
    main()
