# Brain Decathlon 🧠

毎日の脳トレパズル「Brain Decathlon」のPDF自動生成システム

## 概要

9種類のパズルを毎日自動生成し、GitHub Pagesで配信します。

### パズルの種類
1. Building Puzzle（ビルパズル）
2. KenKen（賢賢）
3. Matchstick Puzzle（マッチ棒パズル）
4. Cryptarithm（覆面算）
5. Countdown（カウントダウン）
6. Mini Number Place（ミニナンプレ）
7. Calc Puzzle（計算パズル）
8. Sum Puzzle（合計パズル）
9. Maze（迷路）

## セットアップ

### 1. リポジトリの準備

```bash
git clone https://github.com/your-username/brain-decathlon.git
cd brain-decathlon
pip install -r requirements.txt
```

### 2. GitHub Pagesの設定

1. リポジトリの Settings → Pages
2. Source: `Deploy from a branch`
3. Branch: `main` / `docs`
4. Save

### 3. 自動実行の確認

- `.github/workflows/generate-puzzle.yml` が毎日UTC 15:00（日本時間 0:00）に実行
- Actions タブで実行状況を確認可能
- 手動実行も可能（Actions → Generate Daily Puzzle → Run workflow）

## ローカル実行

```bash
# 今日のパズルを生成
cd generators
python ../puzzle_layout.py

# 特定の日付を指定
python ../puzzle_layout.py 20260215
```

## ディレクトリ構造

```
brain-decathlon/
├── .github/workflows/    # GitHub Actions設定
├── generators/           # パズル生成スクリプト（9種類）
├── scripts/              # ユーティリティスクリプト
├── docs/                 # GitHub Pages（公開ディレクトリ）
│   ├── index.html        # トップページ
│   ├── guide.html        # 遊び方ガイド
│   └── puzzles/          # 生成されたPDF
├── puzzle_layout.py      # メイン生成スクリプト
├── requirements.txt      # Python依存関係
└── README.md
```

## URL構成

- トップページ: `https://your-username.github.io/brain-decathlon/`
- 今日の問題: `https://your-username.github.io/brain-decathlon/puzzles/YYYYMMDD_puzzle.pdf`
- 今日の解答: `https://your-username.github.io/brain-decathlon/puzzles/YYYYMMDD_answer.pdf`
- ガイド: `https://your-username.github.io/brain-decathlon/guide.html`

## カスタマイズ

### QRコードのURL変更

`puzzle_layout.py` 内の以下の変数を変更：

```python
guide_url = "https://justy.co.jp/decathlon/guide.html"
answer_url = f"https://justy.co.jp/decathlon/{date_prefix}_ans.pdf"
morepi_url = "https://justy.co.jp/pi/"
games_url = "https://justy.co.jp/games/"
```

### 実行時刻の変更

`.github/workflows/generate-puzzle.yml` の cron 設定を変更：

```yaml
schedule:
  - cron: '0 15 * * *'  # UTC 15:00 = JST 00:00
```

## ライセンス

© 2026 Justy LLC

## 問い合わせ

[Justy LLC](https://justy.co.jp)
