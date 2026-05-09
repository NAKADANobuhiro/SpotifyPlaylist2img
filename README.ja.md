# Playlist2img

Spotify のプレイリスト URL からアルバムカバー画像をコラージュした PNG を生成するスクリプトです。
同じアルバムの曲が複数ある場合はカバーを 1 枚に絞り、左上から順に 3×3 で並べます。

## 出力イメージ

```
_1.png（4 枚以下 → 2×2、5 枚以上 → 3×3）

【4 枚以下の場合】        【5 枚以上の場合】
┌──────┬──────┐          ┌──────┬──────┬──────┐
│  1   │  2   │          │  1   │  2   │  3   │
├──────┼──────┤          ├──────┼──────┼──────┤
│  3   │  4   │          │  4   │  5   │  6   │
└──────┴──────┘          ├──────┼──────┼──────┤
                         │  7   │  8   │  9   │
                         └──────┴──────┴──────┘

_2.png（10 枚以上のとき）
  ・2 枚目が 4 枚以下 → 2×2 グリッド
  ・2 枚目が 5 枚以上 → 3×3 グリッド
```

## セットアップ

### 1. ライブラリのインストール

```
pip install spotipy Pillow requests
```

### 2. Spotify API アプリの作成

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) でアプリを作成
2. 「Redirect URIs」に以下を登録して保存:
   ```
   http://127.0.0.1:8888/callback
   ```
   > ⚠️ `http://localhost:8888/callback` は登録できないため必ず `127.0.0.1` を使うこと

3. **Client ID** と **Client Secret** を確認

### 3. 環境変数の設定

**Windows（コマンドプロンプト）:**
```
set SPOTIFY_CLIENT_ID=your_client_id
set SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Windows（PowerShell）:**
```
$env:SPOTIFY_CLIENT_ID="your_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret"
```

**Mac / Linux:**
```
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

## 使い方

```
python Playlist2img.py <playlist_url> [output_prefix]
```

| 引数 | 説明 |
|------|------|
| `playlist_url` | Spotify プレイリストの URL（必須） |
| `output_prefix` | 出力ファイル名のプレフィックス（省略時はプレイリスト名を自動使用） |

### 実行例

```
# ファイル名自動（プレイリスト名_1.png, プレイリスト名_2.png）
python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx

# ファイル名指定（maburon_1.png, maburon_2.png）
python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx maburon
```

### 出力ファイル

| ファイル | 条件 | サイズ |
|----------|------|--------|
| `{prefix}_1.png` | 常に生成 | 600×600px（2×2、4枚以下）または 900×900px（3×3、5枚以上）|
| `{prefix}_2.png` | 10 枚以上のとき生成 | 600×600px（2×2）or 900×Npx（3×3）|

### 初回実行時

ブラウザが開き Spotify のログインと権限承認が求められます。
承認後はトークンが `.cache` に保存され、2 回目以降はブラウザ不要です。

## 動作環境

- Python 3.10 以上
- spotipy 2.x
- Pillow 9.x 以上
- requests 2.x
