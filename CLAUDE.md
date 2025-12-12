# CLAUDE.md - プロジェクト設定

## 実行環境

### Python
- **パス**: `/usr/local/bin/python`
- **バージョン**: 3.13
- **pip**: `/Library/Frameworks/Python.framework/Versions/3.13/bin/pip`

### Git
- **パス**: システムデフォルト

### GitHub CLI (gh)
- **パス**: `/opt/homebrew/bin/gh`

## コマンド

### アプリ起動
```bash
/usr/local/bin/python main.py
```

### 依存パッケージインストール
```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/pip install -r requirements.txt
```

### GitHub操作
```bash
/opt/homebrew/bin/gh repo view
/opt/homebrew/bin/gh pr create
```

## プロジェクト構造

```
15_srt_gen/
├── main.py              # エントリーポイント
├── requirements.txt     # 依存パッケージ
├── REQUIREMENT.md       # 要件定義書
├── CLAUDE.md            # このファイル
└── src/
    ├── transcriber.py   # Whisper音声認識
    ├── srt_generator.py # SRT生成
    └── gui/
        ├── app.py           # メインウィンドウ
        ├── file_selector.py # ファイル選択
        ├── progress_view.py # 進捗表示
        └── editor.py        # タイムスタンプ編集
```

## 依存関係

- openai-whisper
- customtkinter
- ffmpeg-python
- FFmpeg (システムインストール: `brew install ffmpeg`)

## リポジトリ

- **URL**: https://github.com/Tasogare-eng/srt_generator
- **公開設定**: Public
