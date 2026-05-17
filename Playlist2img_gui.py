#!/usr/bin/env python3
"""
Playlist2img_gui.py
Playlist2img の GUI 起動ランチャー。
URL 入力ポップアップを表示し、コラージュ PNG を生成する。

使い方:
    python Playlist2img_gui.py
    （コマンドライン引数は不要）
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

# Playlist2img.py と同じディレクトリを検索パスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from Playlist2img import (
        extract_playlist_id,
        trim_filename,
        get_spotify_client,
        fetch_cover_urls,
        download_image,
        grid_cols,
        make_collage,
        THUMB_SIZE,
    )
except ImportError as e:
    print(f"エラー: Playlist2img.py の読み込みに失敗しました: {e}")
    sys.exit(1)

import re


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Playlist2img")
        self.resizable(False, False)
        self._build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        # --- URL 入力 ---
        tk.Label(self, text="Spotify プレイリスト URL:", anchor="w").grid(
            row=0, column=0, columnspan=2, sticky="w", **pad
        )
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(self, textvariable=self.url_var, width=60)
        url_entry.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 6), sticky="ew")
        url_entry.bind("<Return>", lambda e: self.run())

        # --- 出力フォルダ ---
        tk.Label(self, text="出力フォルダ（空欄でスクリプトと同じフォルダ）:", anchor="w").grid(
            row=2, column=0, columnspan=2, sticky="w", **pad
        )
        self.outdir_var = tk.StringVar(value=os.path.dirname(os.path.abspath(__file__)))
        tk.Entry(self, textvariable=self.outdir_var, width=60).grid(
            row=3, column=0, columnspan=2, padx=12, pady=(0, 6), sticky="ew"
        )

        # --- 実行ボタン ---
        self.run_btn = tk.Button(
            self, text="生成", width=12, command=self.run, bg="#1DB954", fg="white",
            font=("", 10, "bold"), relief="flat", cursor="hand2"
        )
        self.run_btn.grid(row=4, column=0, padx=12, pady=8, sticky="w")

        self.status_var = tk.StringVar(value="URL を入力して「生成」を押してください。")
        tk.Label(self, textvariable=self.status_var, fg="gray", anchor="w").grid(
            row=4, column=1, padx=4, pady=8, sticky="w"
        )

        # --- ログ表示 ---
        self.log = scrolledtext.ScrolledText(
            self, width=70, height=16, state="disabled",
            font=("Courier", 9), bg="#1a1a1a", fg="#d0d0d0",
            insertbackground="white"
        )
        self.log.grid(row=5, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="nsew")

    # ── ログ出力 ──────────────────────────────────────────────

    def log_write(self, msg: str):
        """スレッドセーフなログ追記。"""
        def _write():
            self.log.config(state="normal")
            self.log.insert("end", msg + "\n")
            self.log.see("end")
            self.log.config(state="disabled")
        self.after(0, _write)

    def set_status(self, msg: str, color: str = "gray"):
        self.after(0, lambda: self.status_var.set(msg))
        self.after(0, lambda: self.nametowidget(self.status_var).config(fg=color)
                   if False else None)  # ラベル色変更は下で対応

    # ── 実行 ─────────────────────────────────────────────────

    def run(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("入力エラー", "URL を入力してください。")
            return

        outdir = self.outdir_var.get().strip()
        if outdir and not os.path.isdir(outdir):
            messagebox.showerror("エラー", f"出力フォルダが存在しません:\n{outdir}")
            return

        # ボタンを無効化して多重実行を防止
        self.run_btn.config(state="disabled", text="処理中…")
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

        thread = threading.Thread(target=self._worker, args=(url, outdir), daemon=True)
        thread.start()

    def _worker(self, url: str, outdir: str):
        try:
            self._generate(url, outdir)
        except Exception as e:
            self.log_write(f"\n❌ エラー: {e}")
            self.after(0, lambda: messagebox.showerror("エラー", str(e)))
        finally:
            self.after(0, lambda: self.run_btn.config(state="normal", text="生成"))

    def _generate(self, url: str, outdir: str):
        self.log_write(f"URL: {url}")

        # プレイリスト ID 取得
        try:
            playlist_id = extract_playlist_id(url)
        except ValueError as e:
            raise ValueError(f"有効な Spotify プレイリスト URL ではありません: {url}") from e

        self.log_write(f"プレイリスト ID: {playlist_id}")
        self.log_write("Spotify API に接続中…")

        sp = get_spotify_client()

        playlist_info = sp.playlist(playlist_id, fields="name")
        playlist_name = trim_filename(playlist_info.get("name", playlist_id))
        if not playlist_name:
            playlist_name = playlist_id
        self.log_write(f"プレイリスト名: {playlist_name}")

        # 出力ファイル名のベース（前後の空白・書式文字を切り詰める）
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", playlist_name)
        safe_name = trim_filename(safe_name)
        if not safe_name:
            safe_name = playlist_id
        prefix = os.path.join(outdir, safe_name) if outdir else safe_name

        self.log_write("カバー画像 URL を取得中（アルバム重複除外）…")
        cover_urls = fetch_cover_urls(sp, playlist_id)
        self.log_write(f"ユニークなカバー: {len(cover_urls)} 枚")

        if not cover_urls:
            self.log_write("カバー画像が見つかりませんでした。")
            self.after(0, lambda: messagebox.showinfo("完了", "カバー画像が見つかりませんでした。"))
            return

        self.log_write("画像をダウンロード中…")
        images = []
        for i, img_url in enumerate(cover_urls, 1):
            self.log_write(f"  [{i:>2}/{len(cover_urls)}] ダウンロード中…")
            try:
                img = download_image(img_url)
                images.append(img)
            except Exception as e:
                self.log_write(f"  ⚠ ダウンロード失敗: {e}")

        self.log_write(f"{len(images)} 枚完了。コラージュを作成中…")

        PAGE_SIZE = 9
        pages = [images[i:i + PAGE_SIZE] for i in range(0, len(images), PAGE_SIZE)]
        saved_files = []

        for page_num, page in enumerate(pages, start=1):
            cols = grid_cols(len(page))
            rows = (len(page) + cols - 1) // cols
            collage = make_collage(page, cols=cols, thumb=THUMB_SIZE)
            out = f"{prefix}_{page_num}.png"
            collage.save(out, "PNG")
            saved_files.append(out)
            self.log_write(
                f"保存しました: {os.path.basename(out)}"
                f"  ({collage.width}x{collage.height}px, {len(page)} 枚, {cols}x{rows} グリッド)"
            )

        self.log_write("\n✅ 完了！")

        # 完了ダイアログ
        files_str = "\n".join(os.path.basename(f) for f in saved_files)
        msg = f"{len(saved_files)} ファイルを生成しました:\n\n{files_str}\n\n出力先: {outdir or '（スクリプトと同じフォルダ）'}"
        self.after(0, lambda: messagebox.showinfo("完了", msg))


def main():
    # 環境変数チェック
    if not os.environ.get("SPOTIFY_CLIENT_ID") or not os.environ.get("SPOTIFY_CLIENT_SECRET"):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "環境変数が未設定",
            "以下の環境変数を設定してからスクリプトを起動してください。\n\n"
            "  SPOTIFY_CLIENT_ID\n"
            "  SPOTIFY_CLIENT_SECRET\n\n"
            "設定方法（コマンドプロンプト）:\n"
            "  set SPOTIFY_CLIENT_ID=your_client_id\n"
            "  set SPOTIFY_CLIENT_SECRET=your_client_secret"
        )
        root.destroy()
        sys.exit(1)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
