# Playlist2img

Spotify のプレイリスト URL からアルバムカバー画像をコラージュした PNG を生成するスクリプトです。
同じアルバムの曲が複数ある場合はカバーを 1 枚に絞り、左上から順に 3×3 で並べます。

## レイアウトルール

1ページあたり最大 9 枚。ページ内の枚数に応じてグリッドの列数が変わります。

| ページ内の枚数 | レイアウト |
|---------------|-----------|
| 1 枚 | 1×1 |
| 2〜6 枚 | 2列（行数は自動） |
| 7〜9 枚 | 3×3 |

### 枚数別の出力例

| 総枚数 | 出力ファイル |
|--------|------------|
| 1 | `_1.png` (1×1) |
| 4 | `_1.png` (2×2) |
| 9 | `_1.png` (3×3) |
| 10 | `_1.png` (3×3) + `_2.png` (1×1) |
| 15 | `_1.png` (3×3) + `_2.png` (2列×3行) |
| 18 | `_1.png` (3×3) + `_2.png` (3×3) |
| 27 | `_1.png` + `_2.png` + `_3.png` (各 3×3) |
| 36 | `_1.png`〜`_4.png` (各 3×3) |

## セットアップ

### 1. 認証情報ファイルを作成する

```
copy spotify_credentials.bat.example spotify_credentials.bat
```

`spotify_credentials.bat` を開いて、手順 3 で取得した認証情報を記入してください。
このファイルは `.gitignore` で除外されており、Git にコミットされることはありません。

### 2. ライブラリのインストール

```
pip install spotipy Pillow requests
```

### 3. Spotify API アプリの作成

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) でアプリを作成
2. 「Redirect URIs」に以下を登録して保存:
   ```
   http://127.0.0.1:8888/callback
   ```
   > ⚠️ `http://localhost:8888/callback` は登録できないため必ず `127.0.0.1` を使うこと
3. **Client ID** と **Client Secret** を確認

### 4. 環境変数の設定

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

9 枚ごとに 1 ファイルを生成します。9 枚以下なら `_1.png` のみ、10〜18 枚なら `_1.png` + `_2.png`、以降同様です。

### 初回実行時

ブラウザが開き Spotify のログインと権限承認が求められます。
承認後はトークンが `.cache` に保存され、2 回目以降はブラウザ不要です。

## GUI ランチャー（Windows 専用）

`Playlist2img_gui.bat` と `Playlist2img_gui.py` は Windows 向けの GUI を提供します。
`Playlist2img_gui.bat` をダブルクリックするだけで起動できます。

> ⚠️ `.bat` ランチャーおよび GUI は **Windows 専用**です。Mac/Linux ではコマンドラインスクリプトを直接使用してください。

## 動作環境

- Python 3.10 以上
- spotipy 2.x
- Pillow 9.x 以上
- requests 2.x
