#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マッチ棒パズル SVG生成スクリプト

必要なモジュール: Python標準ライブラリのみ（追加インストール不要）
- random, datetime, os

使用方法:
    python3 matchstick_puzzle_generator.py

出力:
    YYYYMMDD_matchstick.svg     - 問題画像
    YYYYMMDD_matchstick_ans.svg - 正解例画像
"""

import random
import os
import sys
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

# ==========================
# 7セグメント定義
# ==========================
#   aaa
#  f   b
#  f   b
#   ggg
#  e   c
#  e   c
#   ddd

SEG = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6}

def bits(segs):
    """セグメントリストからビットマスクを作成"""
    mask = 0
    for s in segs:
        mask |= (1 << SEG[s])
    return mask

# 数字のセグメントマスク
DIGIT_MASKS = {
    0: bits(['a','b','c','d','e','f']),
    1: bits(['b','c']),
    2: bits(['a','b','d','e','g']),
    3: bits(['a','b','c','d','g']),
    4: bits(['b','c','f','g']),
    5: bits(['a','c','d','f','g']),
    6: bits(['a','c','d','e','f','g']),
    7: bits(['a','b','c']),
    8: bits(['a','b','c','d','e','f','g']),
    9: bits(['a','b','c','d','f','g']),
}

# マスクから数字への逆引き
MASK_TO_DIGIT = {v: k for k, v in DIGIT_MASKS.items()}

# 演算子のマスク（h=横棒, v=縦棒, fs=前スラッシュ, bs=後スラッシュ）
OP_MASKS = {
    '+': {'h': 1, 'v': 1, 'fs': 0, 'bs': 0},
    '-': {'h': 1, 'v': 0, 'fs': 0, 'bs': 0},
    '×': {'h': 0, 'v': 0, 'fs': 1, 'bs': 1},
    '÷': {'h': 0, 'v': 0, 'fs': 1, 'bs': 0},
}

# ==========================
# 変換テーブル（セグメント差分入り）
# ==========================
DECREASE = {
    1: {
        'op': {'+': {'to': '-', 'remove': ['v']}, '×': {'to': '÷', 'remove': ['bs']}},
        'digits': {
            6: [{'to': 5, 'remove': ['e']}],
            7: [{'to': 1, 'remove': ['a']}],
            8: [{'to': 0, 'remove': ['g']}, {'to': 6, 'remove': ['b']}, {'to': 9, 'remove': ['e']}],
            9: [{'to': 3, 'remove': ['f']}, {'to': 5, 'remove': ['b']}],
        }
    },
    2: {
        'op': {},
        'digits': {
            3: [{'to': 7, 'remove': ['d', 'g']}],
            4: [{'to': 1, 'remove': ['f', 'g']}],
            8: [{'to': 2, 'remove': ['c', 'f']}, {'to': 3, 'remove': ['e', 'f']}, {'to': 5, 'remove': ['b', 'e']}],
            9: [{'to': 4, 'remove': ['a', 'd']}],
        }
    },
    3: {
        'op': {},
        'digits': {
            0: [{'to': 7, 'remove': ['d', 'e', 'f']}],
            3: [{'to': 1, 'remove': ['a', 'd', 'g']}],
            8: [{'to': 4, 'remove': ['a', 'd', 'e']}],
            9: [{'to': 7, 'remove': ['d', 'f', 'g']}],
        }
    }
}

INCREASE = {
    1: {
        'op': {'-': {'to': '+', 'add': ['v']}, '÷': {'to': '×', 'add': ['bs']}},
        'digits': {
            0: [{'to': 8, 'add': ['g']}],
            1: [{'to': 7, 'add': ['a']}],
            3: [{'to': 9, 'add': ['f']}],
            5: [{'to': 6, 'add': ['e']}, {'to': 9, 'add': ['b']}],
            6: [{'to': 8, 'add': ['b']}],
            9: [{'to': 8, 'add': ['e']}],
        }
    },
    2: {
        'op': {},
        'digits': {
            1: [{'to': 4, 'add': ['f', 'g']}],
            2: [{'to': 8, 'add': ['c', 'f']}],
            3: [{'to': 8, 'add': ['e', 'f']}],
            4: [{'to': 9, 'add': ['a', 'd']}],
            5: [{'to': 8, 'add': ['b', 'e']}],
            7: [{'to': 3, 'add': ['d', 'g']}],
        }
    },
    3: {
        'op': {},
        'digits': {
            1: [{'to': 3, 'add': ['a', 'd', 'g']}],
            4: [{'to': 8, 'add': ['a', 'd', 'e']}],
            7: [{'to': 0, 'add': ['d', 'e', 'f']}, {'to': 9, 'add': ['d', 'f', 'g']}],
        }
    }
}

# ==========================
# 盤面状態管理クラス
# ==========================
class BoardState:
    def __init__(self):
        self.slots = {}  # slot_id -> {'present': bool, 'original': bool}
        self.moves_required = 2  # 2本（ふつう）
    
    def set_slot(self, slot_id, present, as_original=False):
        if slot_id not in self.slots:
            self.slots[slot_id] = {'present': False, 'original': False}
        self.slots[slot_id]['present'] = present
        if as_original:
            self.slots[slot_id]['original'] = present
    
    def get_slot(self, slot_id):
        return self.slots.get(slot_id, {'present': False, 'original': False})
    
    def reset(self):
        self.slots = {}

# ==========================
# 問題生成ロジック
# ==========================
def gen_valid_equation():
    """有効な式（A op B = C）を生成"""
    ops = ['+', '-', '×', '÷']
    
    for _ in range(12000):
        op = random.choice(ops)
        
        if op == '+':
            A = random.randint(1, 98)
            B = random.randint(1, min(99, 99 - A))
            C = A + B
            if C < 1 or C > 99:
                continue
        elif op == '-':
            C = random.randint(1, 99)
            A = random.randint(C + 1, 99)
            B = A - C
            if B < 1 or B > 99:
                continue
        elif op == '×':
            A = random.randint(1, 99)
            max_b = 99 // A
            if max_b < 1:
                continue
            B = random.randint(1, max_b)
            C = A * B
            if C < 1 or C > 99:
                continue
        else:  # ÷
            B = random.randint(1, 99)
            r_max = 99 // B
            if r_max < 1:
                continue
            R = random.randint(1, r_max)
            A = B * R
            C = R
            if A < 1 or A > 99 or C < 1 or C > 99:
                continue
        
        if 1 <= A <= 99 and 1 <= B <= 99 and 1 <= C <= 99:
            return {'A': A, 'B': B, 'op': op, 'C': C}
    
    return {'A': 12, 'B': 34, 'op': '+', 'C': 46}

def equation_to_chars(eq):
    """式を文字配列に変換"""
    left = str(eq['A']).rjust(2)
    right = str(eq['B']).rjust(2)
    res = str(eq['C']).rjust(2)
    return {'L': list(left), 'R': list(right), 'Z': list(res), 'OP': eq['op']}

def set_digit_in_state(state, cell_id, digit):
    """セル内に数字を設定"""
    mask = DIGIT_MASKS.get(digit, 0) if digit is not None else 0
    for seg in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
        slot_id = f"{cell_id}:{seg}"
        present = bool(mask & (1 << SEG[seg])) if digit is not None else False
        state.set_slot(slot_id, present, as_original=True)

def set_operator_in_state(state, op):
    """演算子を設定"""
    m = OP_MASKS.get(op, {'h': 0, 'v': 0, 'fs': 0, 'bs': 0})
    for seg in ['h', 'v', 'fs', 'bs']:
        slot_id = f"OP:{seg}"
        present = bool(m[seg])
        state.set_slot(slot_id, present, as_original=True)

def draw_equation_chars(state, chars):
    """式を盤面に描画"""
    cells = {
        'L': ['L0', 'L1'],
        'R': ['R0', 'R1'],
        'Z': ['Z0', 'Z1']
    }
    
    for group_key, cell_ids in cells.items():
        group_chars = chars[group_key]
        for i, ch in enumerate(group_chars):
            cell_id = cell_ids[i]
            if ch == ' ':
                set_digit_in_state(state, cell_id, None)
            else:
                set_digit_in_state(state, cell_id, int(ch))
    
    set_operator_in_state(state, chars['OP'])

def read_number_from_state(state, cell_ids):
    """盤面から数値を読み取る"""
    digits = []
    begun = False
    invalid = False
    
    for cell_id in cell_ids:
        mask = 0
        has_any = False
        for seg in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            slot_id = f"{cell_id}:{seg}"
            if state.get_slot(slot_id)['present']:
                mask |= (1 << SEG[seg])
                has_any = True
        
        if not begun:
            if not has_any:
                continue
            begun = True
        
        if not has_any:
            invalid = True
            break
        
        d = MASK_TO_DIGIT.get(mask)
        if d is None:
            invalid = True
            break
        digits.append(d)
    
    if invalid or len(digits) == 0:
        return {'ok': False}
    
    return {'ok': True, 'value': int(''.join(map(str, digits)))}

def read_operator_from_state(state):
    """盤面から演算子を読み取る"""
    h = state.get_slot('OP:h')['present']
    v = state.get_slot('OP:v')['present']
    fs = state.get_slot('OP:fs')['present']
    bs = state.get_slot('OP:bs')['present']
    
    if h and v and not fs and not bs:
        return '+'
    if h and not v and not fs and not bs:
        return '-'
    if fs and bs and not h and not v:
        return '×'
    if fs and not bs and not h and not v:
        return '÷'
    return None

def is_board_equation_correct(state):
    """盤面の式が正しいか確認"""
    L = read_number_from_state(state, ['L0', 'L1'])
    R = read_number_from_state(state, ['R0', 'R1'])
    Z = read_number_from_state(state, ['Z0', 'Z1'])
    op = read_operator_from_state(state)
    
    if not L['ok'] or not R['ok'] or not Z['ok'] or op is None:
        return {'ok': False}
    
    a, b, c = L['value'], R['value'], Z['value']
    
    if op == '÷' and b == 0:
        return {'ok': False}
    
    if op == '+':
        lhs = a + b
    elif op == '-':
        lhs = a - b
    elif op == '×':
        lhs = a * b
    elif op == '÷':
        if a % b != 0:
            return {'ok': False}
        lhs = a // b
    else:
        return {'ok': False}
    
    return {'ok': lhs == c, 'a': a, 'b': b, 'c': c, 'op': op}

def partitions(n):
    """nを1,2,3の組み合わせに分割"""
    result = []
    
    def dfs(rest, path):
        if rest == 0:
            result.append(path[:])
            return
        for k in range(min(3, rest), 0, -1):
            path.append(k)
            dfs(rest - k, path)
            path.pop()
    
    dfs(n, [])
    return result

def pick_decrease(symbol, k):
    """DECREASEから変換を選択"""
    if symbol['type'] == 'op':
        ent = DECREASE[k]['op'].get(symbol['op'])
        if not ent:
            return None
        return {'type': 'op', 'from': symbol['op'], 'to': ent['to'], 'remove': ent['remove']}
    else:
        cand = DECREASE[k]['digits'].get(symbol['value'])
        if not cand:
            return None
        pick = random.choice(cand)
        return {'type': 'digit', 'cell': symbol['cell'], 'from': symbol['value'], 'to': pick['to'], 'remove': pick['remove']}

def pick_increase(symbol, k):
    """INCREASEから変換を選択"""
    if symbol['type'] == 'op':
        ent = INCREASE[k]['op'].get(symbol['op'])
        if not ent:
            return None
        return {'type': 'op', 'from': symbol['op'], 'to': ent['to'], 'add': ent['add']}
    else:
        cand = INCREASE[k]['digits'].get(symbol['value'])
        if not cand:
            return None
        pick = random.choice(cand)
        return {'type': 'digit', 'cell': symbol['cell'], 'from': symbol['value'], 'to': pick['to'], 'add': pick['add']}

def apply_delta(state, change):
    """変更を盤面に適用"""
    if change['type'] == 'op':
        if 'remove' in change:
            for s in change['remove']:
                state.set_slot(f"OP:{s}", False)
        if 'add' in change:
            for s in change['add']:
                state.set_slot(f"OP:{s}", True)
    else:
        cell_id = change['cell']
        if 'remove' in change:
            for s in change['remove']:
                state.set_slot(f"{cell_id}:{s}", False)
        if 'add' in change:
            for s in change['add']:
                state.set_slot(f"{cell_id}:{s}", True)

def disturb_equation_once(state, chars, N):
    """式を壊す（マッチ棒をN本動かす）"""
    state.reset()
    draw_equation_chars(state, chars)
    
    split_dec = random.choice(partitions(N))
    split_inc = random.choice(partitions(N))
    
    used_cells = set()
    used_op = False
    
    # 現在の盤面からシンボルを取得
    symbols = []
    for cell_id in ['L0', 'L1', 'R0', 'R1', 'Z0', 'Z1']:
        mask = 0
        has_any = False
        for seg in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            slot_id = f"{cell_id}:{seg}"
            if state.get_slot(slot_id)['present']:
                mask |= (1 << SEG[seg])
                has_any = True
        if has_any:
            d = MASK_TO_DIGIT.get(mask)
            if d is not None:
                symbols.append({'type': 'digit', 'cell': cell_id, 'value': d})
    
    cur_op = read_operator_from_state(state)
    if cur_op:
        symbols.append({'type': 'op', 'value': cur_op, 'op': cur_op})
    
    # DECREASE適用
    for k in split_dec:
        tries = 0
        ok = False
        while tries < 100 and not ok:
            tries += 1
            cand = [s for s in symbols if (
                (s['type'] == 'op' and not used_op and s['op'] in DECREASE[k]['op']) or
                (s['type'] == 'digit' and s['cell'] not in used_cells and s['value'] in DECREASE[k]['digits'])
            )]
            if not cand:
                break
            sym = random.choice(cand)
            ch = pick_decrease(sym, k)
            if not ch:
                continue
            
            # 全てのセグメントが存在するか確認
            if ch['type'] == 'op':
                all_present = all(state.get_slot(f"OP:{s}")['present'] for s in ch['remove'])
            else:
                all_present = all(state.get_slot(f"{ch['cell']}:{s}")['present'] for s in ch['remove'])
            
            if not all_present:
                continue
            
            apply_delta(state, ch)
            ok = True
            if sym['type'] == 'digit':
                used_cells.add(sym['cell'])
            else:
                used_op = True
        
        if not ok:
            return False
    
    # INCREASE適用
    for k in split_inc:
        tries = 0
        ok = False
        while tries < 100 and not ok:
            tries += 1
            cand = [s for s in symbols if (
                (s['type'] == 'op' and not used_op and s['op'] in INCREASE[k]['op']) or
                (s['type'] == 'digit' and s['cell'] not in used_cells and s['value'] in INCREASE[k]['digits'])
            )]
            if not cand:
                break
            sym = random.choice(cand)
            ch = pick_increase(sym, k)
            if not ch:
                continue
            
            # 全てのスロットが空か確認
            if ch['type'] == 'op':
                all_empty = all(not state.get_slot(f"OP:{s}")['present'] for s in ch['add'])
            else:
                all_empty = all(not state.get_slot(f"{ch['cell']}:{s}")['present'] for s in ch['add'])
            
            if not all_empty:
                continue
            
            apply_delta(state, ch)
            ok = True
            if sym['type'] == 'digit':
                used_cells.add(sym['cell'])
            else:
                used_op = True
        
        if not ok:
            return False
    
    # 結果を確認
    L = read_number_from_state(state, ['L0', 'L1'])
    R = read_number_from_state(state, ['R0', 'R1'])
    Z = read_number_from_state(state, ['Z0', 'Z1'])
    op = read_operator_from_state(state)
    
    if not L['ok'] or not R['ok'] or not Z['ok'] or op is None:
        return False
    
    return True

def generate_puzzle(moves_required=2):
    """パズルを生成"""
    state = BoardState()
    state.moves_required = moves_required
    
    for attempts in range(400):
        eq = gen_valid_equation()
        chars = equation_to_chars(eq)
        ok = disturb_equation_once(state, chars, min(3, max(1, moves_required)))
        
        if not ok:
            continue
        
        judge = is_board_equation_correct(state)
        if judge['ok']:
            continue
        
        # オリジナル状態を記録
        for slot_id in state.slots:
            state.slots[slot_id]['original'] = state.slots[slot_id]['present']
        
        return {
            'state': state,
            'answer': eq,
            'moves_required': moves_required
        }
    
    return None

# ==========================
# SVG生成
# ==========================
def generate_svg(state, show_answer=False, answer_eq=None):
    """SVG画像を生成"""
    
    # サイズ設定（HTMLと同じ比率）
    digit_w = 110
    digit_h = 200
    seg_t = 16
    gap = 14
    digit_gap = 8  # 同じグループ内の桁間隔
    
    # 色定義
    ghost_color = "#e8e8e8"      # 空きセグメントの色
    ghost_op_color = "#ededed"   # 演算子の空きセグメントの色
    stick_color = "black"        # マッチ棒の色（黒指定）
    
    # 角丸の半径（セグメント幅の半分程度）
    rx = seg_t // 2
    
    # 各セルの位置を計算
    positions = {}
    x = 20
    
    # 左辺の2桁
    positions['L0'] = {'x': x, 'y': 20}
    x += digit_w + digit_gap
    positions['L1'] = {'x': x, 'y': 20}
    x += digit_w + gap * 2
    
    # 演算子
    positions['OP'] = {'x': x, 'y': 20}
    x += digit_w + gap * 2
    
    # 右辺の2桁
    positions['R0'] = {'x': x, 'y': 20}
    x += digit_w + digit_gap
    positions['R1'] = {'x': x, 'y': 20}
    x += digit_w + gap * 2
    
    # 等号
    eq_x = x
    eq_w = 60
    x += eq_w + gap * 2
    
    # 結果の2桁
    positions['Z0'] = {'x': x, 'y': 20}
    x += digit_w + digit_gap
    positions['Z1'] = {'x': x, 'y': 20}
    x += digit_w + 20
    
    total_width = x
    total_height = 20 + digit_h + 20
    
    # SVG開始
    svg_parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {total_height}">']
    
    # 7セグメントの座標定義
    def get_segment_rect(cell_x, cell_y, seg):
        """セグメントの矩形座標を取得"""
        half_h = digit_h // 2
        if seg == 'a':  # 上の横棒
            return (cell_x + seg_t, cell_y, digit_w - seg_t * 2, seg_t)
        elif seg == 'b':  # 右上の縦棒
            return (cell_x + digit_w - seg_t, cell_y + seg_t, seg_t, half_h - seg_t)
        elif seg == 'c':  # 右下の縦棒
            return (cell_x + digit_w - seg_t, cell_y + half_h, seg_t, half_h - seg_t)
        elif seg == 'd':  # 下の横棒
            return (cell_x + seg_t, cell_y + digit_h - seg_t, digit_w - seg_t * 2, seg_t)
        elif seg == 'e':  # 左下の縦棒
            return (cell_x, cell_y + half_h, seg_t, half_h - seg_t)
        elif seg == 'f':  # 左上の縦棒
            return (cell_x, cell_y + seg_t, seg_t, half_h - seg_t)
        elif seg == 'g':  # 真ん中の横棒
            return (cell_x + seg_t, cell_y + half_h - seg_t // 2, digit_w - seg_t * 2, seg_t)
        return None
    
    def draw_rect(x, y, w, h, fill, radius=None, transform=None):
        """矩形を描画"""
        r = radius if radius is not None else rx
        t = f' transform="{transform}"' if transform else ''
        return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" rx="{r}"{t}/>'
    
    # ==============================
    # 1. まずゴースト（空きセグメント）をすべて描画
    # ==============================
    
    # 数字セグメントのゴースト
    for cell_id in ['L0', 'L1', 'R0', 'R1', 'Z0', 'Z1']:
        pos = positions[cell_id]
        for seg in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            rect = get_segment_rect(pos['x'], pos['y'], seg)
            if rect:
                svg_parts.append(draw_rect(rect[0], rect[1], rect[2], rect[3], ghost_color))
    
    # 演算子セグメントのゴースト（h, v, fs, bs の4つ）
    op_pos = positions['OP']
    op_x, op_y = op_pos['x'], op_pos['y']
    op_center_y = op_y + digit_h // 2
    v_len = digit_h // 2 - seg_t
    
    # 横棒ゴースト
    svg_parts.append(draw_rect(op_x + seg_t, op_center_y - seg_t // 2, 
                               digit_w - seg_t * 2, seg_t, ghost_op_color))
    # 縦棒ゴースト
    svg_parts.append(draw_rect(op_x + digit_w // 2 - seg_t // 2, op_center_y - v_len // 2,
                               seg_t, v_len, ghost_op_color))
    # 前スラッシュゴースト
    cx = op_x + digit_w // 2
    cy = op_center_y
    svg_parts.append(draw_rect(op_x + seg_t, op_center_y - seg_t // 2,
                               digit_w - seg_t * 2, seg_t, ghost_op_color,
                               transform=f"rotate(-45 {cx} {cy})"))
    # 後スラッシュゴースト
    svg_parts.append(draw_rect(op_x + seg_t, op_center_y - seg_t // 2,
                               digit_w - seg_t * 2, seg_t, ghost_op_color,
                               transform=f"rotate(45 {cx} {cy})"))
    
    # ==============================
    # 2. 存在するセグメント（マッチ棒）を描画
    # ==============================
    
    # 数字セグメントを描画
    for cell_id in ['L0', 'L1', 'R0', 'R1', 'Z0', 'Z1']:
        pos = positions[cell_id]
        for seg in ['a', 'b', 'c', 'd', 'e', 'f', 'g']:
            slot_id = f"{cell_id}:{seg}"
            
            if show_answer and answer_eq:
                # 正解表示の場合は正解の状態を表示
                target_chars = equation_to_chars(answer_eq)
                if cell_id.startswith('L'):
                    idx = int(cell_id[1])
                    ch = target_chars['L'][idx]
                elif cell_id.startswith('R'):
                    idx = int(cell_id[1])
                    ch = target_chars['R'][idx]
                else:  # Z
                    idx = int(cell_id[1])
                    ch = target_chars['Z'][idx]
                
                if ch != ' ':
                    digit = int(ch)
                    mask = DIGIT_MASKS[digit]
                    present = bool(mask & (1 << SEG[seg]))
                else:
                    present = False
            else:
                slot = state.get_slot(slot_id)
                present = slot['present']
            
            if present:
                rect = get_segment_rect(pos['x'], pos['y'], seg)
                if rect:
                    svg_parts.append(draw_rect(rect[0], rect[1], rect[2], rect[3], stick_color))
    
    # 演算子を描画
    if show_answer and answer_eq:
        op = answer_eq['op']
        op_mask = OP_MASKS[op]
        h_present = bool(op_mask['h'])
        v_present = bool(op_mask['v'])
        fs_present = bool(op_mask['fs'])
        bs_present = bool(op_mask['bs'])
    else:
        h_present = state.get_slot('OP:h')['present']
        v_present = state.get_slot('OP:v')['present']
        fs_present = state.get_slot('OP:fs')['present']
        bs_present = state.get_slot('OP:bs')['present']
    
    # 横棒
    if h_present:
        svg_parts.append(draw_rect(op_x + seg_t, op_center_y - seg_t // 2,
                                   digit_w - seg_t * 2, seg_t, stick_color))
    
    # 縦棒
    if v_present:
        svg_parts.append(draw_rect(op_x + digit_w // 2 - seg_t // 2, op_center_y - v_len // 2,
                                   seg_t, v_len, stick_color))
    
    # 前スラッシュ（÷や×）
    if fs_present:
        svg_parts.append(draw_rect(op_x + seg_t, op_center_y - seg_t // 2,
                                   digit_w - seg_t * 2, seg_t, stick_color,
                                   transform=f"rotate(-45 {cx} {cy})"))
    
    # 後スラッシュ（×のみ）
    if bs_present:
        svg_parts.append(draw_rect(op_x + seg_t, op_center_y - seg_t // 2,
                                   digit_w - seg_t * 2, seg_t, stick_color,
                                   transform=f"rotate(45 {cx} {cy})"))
    
    # 等号を描画
    eq_y = 20 + digit_h // 2
    eq_gap = 24  # 等号の2本の線の中心間距離
    svg_parts.append(draw_rect(eq_x, eq_y - eq_gap - seg_t // 2, eq_w, seg_t, stick_color))
    svg_parts.append(draw_rect(eq_x, eq_y + eq_gap - seg_t // 2, eq_w, seg_t, stick_color))
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

# ==========================
# メイン処理
# ==========================
def main():
    # 日付文字列を取得
    today = get_date_prefix()
    
    # 出力ファイル名
    problem_file = f"{today}_matchstick.svg"
    answer_file = f"{today}_matchstick_ans.svg"
    
    print("マッチ棒パズル SVG生成スクリプト")
    print("=" * 40)
    print(f"難易度: 2本（ふつう）")
    print(f"出力ファイル:")
    print(f"  問題: {problem_file}")
    print(f"  正解: {answer_file}")
    print()
    
    # パズル生成
    print("パズルを生成中...")
    puzzle = generate_puzzle(moves_required=2)
    
    if puzzle is None:
        print("エラー: パズルの生成に失敗しました")
        return 1
    
    state = puzzle['state']
    answer = puzzle['answer']
    
    # 演算子の表示用変換
    op_display = answer['op']
    if op_display == '-':
        op_display = '−'
    
    print(f"正解の式: {answer['A']} {op_display} {answer['B']} = {answer['C']}")
    print()
    
    # SVG生成
    print("SVGファイルを生成中...")
    
    # 問題SVG
    problem_svg = generate_svg(state, show_answer=False)
    with open(problem_file, 'w', encoding='utf-8') as f:
        f.write(problem_svg)
    print(f"  ✓ {problem_file} を生成しました")
    
    # 正解SVG
    answer_svg = generate_svg(state, show_answer=True, answer_eq=answer)
    with open(answer_file, 'w', encoding='utf-8') as f:
        f.write(answer_svg)
    print(f"  ✓ {answer_file} を生成しました")
    
    print()
    print("完了しました！")
    
    return 0

if __name__ == '__main__':
    exit(main())
