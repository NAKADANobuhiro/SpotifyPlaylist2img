#!/usr/bin/env python3
"""
Playlist2img.py
Spotify のプレイリスト URL からアルバムカバー画像をコラージュした PNG を作成するスクリプト。

使い方:
    python Playlist2img.py <playlist_url> [output_prefix]

例:
    python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx
    python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx myplaylist

出力仕様:
    - アルバム単位で重複をスキップ
    - 1枚目: 3x3 グリッド（最大 9 枚）
    - 10 枚以上ある場合は 2 枚目を生成
      - 2 枚目が 4 枚以下なら 2x2 レイアウト
      - 2 枚目が 5 枚以上なら 3x3 レイアウト

事前準備:
    pip install spotipy Pillow requests

    環境変数:
        set SPOTIFY_CLIENT_ID=your_client_id
        set SPOTIFY_CLIENT_SECRET=your_client_secret
"""

import sys
import os
import re
import requests
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    print("エラー: Pillow がインストールされていません。")
    print("  pip install Pillow")
    sys.exit(1)

import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPES = "playlist-read-private playlist-read-collaborative"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
THUMB_SIZE = 300   # 各カバー画像のサイズ（ピクセル）
BG_COLOR = (20, 20, 20)  # コラージュ背景色（黒に近いグレー）


def extract_playlist_id(url: str) -> str:
    match = re.search(r"playlist/([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError(f"有効な Spotify プレイリスト URL ではありません: {url}")
    return match.group(1)


def get_spotify_client() -> spotipy.Spotify:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("エラー: 環境変数 SPOTIFY_CLIENT_ID と SPOTIFY_CLIENT_SECRET を設定してください。")
        print()
        print("  Windows の場合:")
        print("    set SPOTIFY_CLIENT_ID=your_client_id")
        print("    set SPOTIFY_CLIENT_SECRET=your_client_secret")
        sys.exit(1)
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES,
        open_browser=True,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def fetch_cover_urls(sp: spotipy.Spotify, playlist_id: str) -> list[str]:
    """アルバム単位で重複を除いたカバー画像 URL リストを返す。"""
    seen_album_ids: set[str] = set()
    cover_urls: list[str] = []
    results = sp.playlist_items(playlist_id)

    while results:
        for item in results.get("items", []):
            track = item.get("item") or item.get("track")
            if not track or track.get("type") != "track":
                continue
            album = track.get("album", {})
            album_id = album.get("id")
            if not album_id or album_id in seen_album_ids:
                continue
            seen_album_ids.add(album_id)
            images = album.get("images", [])
            if images:
                # images は大きい順に並んでいるので最初の要素（最大解像度）を使用
                cover_urls.append(images[0]["url"])

        results = sp.next(results) if results.get("next") else None

    return cover_urls


def download_image(url: str) -> Image.Image:
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")


def grid_cols(n: int) -> int:
    """ページ内の画像枚数からグリッドの列数を決定する。
    1枚      → 1列 (1x1)
    2〜6枚   → 2列 (2xN)
    7〜9枚   → 3列 (3xN)
    """
    if n == 1:
        return 1
    elif n <= 6:
        return 2
    else:
        return 3


def make_collage(images: list[Image.Image], cols: int, thumb: int) -> Image.Image:
    """images リストを cols 列で並べたコラージュ画像を返す。"""
    rows = (len(images) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * thumb, rows * thumb), BG_COLOR)
    for idx, img in enumerate(images):
        resized = img.resize((thumb, thumb), Image.LANCZOS)
        x = (idx % cols) * thumb
        y = (idx // cols) * thumb
        canvas.paste(resized, (x, y))
    return canvas


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print("使い方: python Playlist2img.py <playlist_url> [output_prefix]")
        print()
        print("例:")
        print("  python Playlist2img.py https://open.spotify.com/playlist/xxxxx")
        print("  python Playlist2img.py https://open.spotify.com/playlist/xxxxx myplaylist")
        sys.exit(0)

    playlist_url = args[0]
    output_prefix = args[1] if len(args) >= 2 else None

    try:
        playlist_id = extract_playlist_id(playlist_url)
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)

    print(f"プレイリスト ID: {playlist_id}")
    print("Spotify API に接続中...")
    print("※ 初回はブラウザが開きます。Spotify にログインして承認してください。")

    sp = get_spotify_client()

    playlist_info = sp.playlist(playlist_id, fields="name")
    playlist_name = playlist_info.get("name", playlist_id)
    print(f"プレイリスト名: {playlist_name}")

    # 出力ファイル名のベースを決定
    if output_prefix is None:
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", playlist_name)
        output_prefix = safe_name

    print("カバー画像 URL を取得中（アルバム重複除外）...")
    cover_urls = fetch_cover_urls(sp, playlist_id)
    print(f"ユニークなカバー: {len(cover_urls)} 枚")

    if not cover_urls:
        print("カバー画像が見つかりませんでした。")
        sys.exit(0)

    # 画像をダウンロード
    print("画像をダウンロード中...")
    images: list[Image.Image] = []
    for i, url in enumerate(cover_urls, 1):
        print(f"  [{i:>2}/{len(cover_urls)}] {url}")
        try:
            img = download_image(url)
            images.append(img)
        except Exception as e:
            print(f"  ⚠ ダウンロード失敗: {e}")

    total = len(images)
    print(f"{total} 枚ダウンロード完了。コラージュを作成中...")

    # ページごとに最大 9 枚ずつ分割してコラージュを生成
    PAGE_SIZE = 9
    pages = [images[i:i + PAGE_SIZE] for i in range(0, total, PAGE_SIZE)]

    for page_num, page in enumerate(pages, start=1):
        cols = grid_cols(len(page))
        rows = (len(page) + cols - 1) // cols
        collage = make_collage(page, cols=cols, thumb=THUMB_SIZE)
        out = f"{output_prefix}_{page_num}.png"
        collage.save(out, "PNG")
        print(f"保存しました: {out}  ({collage.width}x{collage.height}px, {len(page)} 枚, {cols}x{rows} グリッド)")

    print("\n完了！")


if __name__ == "__main__":
    main()
