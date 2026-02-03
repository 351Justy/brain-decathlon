#!/usr/bin/env python3
"""
index.htmlの過去パズルリストを更新するスクリプト
"""

import os
import re
from pathlib import Path

def get_puzzle_dates(puzzles_dir):
    """puzzlesディレクトリからパズルの日付一覧を取得"""
    dates = set()
    if puzzles_dir.exists():
        for file in puzzles_dir.glob("*_puzzle.pdf"):
            match = re.match(r'(\d{8})_puzzle\.pdf', file.name)
            if match:
                dates.add(match.group(1))
    return sorted(dates, reverse=True)


def format_date(date_str):
    """YYYYMMDD → YYYY/MM/DD"""
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:8]}"


def generate_archive_html(dates):
    """アーカイブリストのHTMLを生成"""
    if not dates:
        return '<li>まだパズルがありません</li>'
    
    html_parts = []
    for date in dates[:30]:  # 最新30件まで表示
        formatted = format_date(date)
        html_parts.append(
            f'<li>'
            f'<span>{formatted}</span> - '
            f'<a href="puzzles/{date}_puzzle.pdf">問題</a> | '
            f'<a href="puzzles/{date}_answer.pdf">解答</a>'
            f'</li>'
        )
    return '\n                '.join(html_parts)


def update_index_html():
    """index.htmlを更新"""
    script_dir = Path(__file__).parent.parent
    docs_dir = script_dir / 'docs'
    puzzles_dir = docs_dir / 'puzzles'
    index_path = docs_dir / 'index.html'
    
    # パズル日付一覧を取得
    dates = get_puzzle_dates(puzzles_dir)
    
    # アーカイブHTMLを生成
    archive_html = generate_archive_html(dates)
    
    # index.htmlを読み込み
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # プレースホルダーまたは既存リストを置換
    # <!-- ARCHIVE_LIST_PLACEHOLDER --> または既存の<li>要素を置換
    pattern = r'(<ul class="archive-list" id="archive-list">)\s*.*?\s*(</ul>)'
    replacement = f'\\1\n                {archive_html}\n            \\2'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 書き込み
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated index.html with {len(dates)} puzzle dates")


if __name__ == "__main__":
    update_index_html()
