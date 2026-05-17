# Playlist2img

A Python tool that generates a collage PNG from the album cover images in a Spotify playlist.
When multiple tracks share the same album, only one cover is used. Images are arranged from the top-left in a grid layout.

A command-line script and a Windows GUI launcher are both provided.

[日本語版 README はこちら](README.ja.md)

## Layout Rules

Up to 9 images per page. The number of columns is determined by the image count on each page.

| Images on page | Layout |
|---------------|--------|
| 1 | 1×1 |
| 2–6 | 2 columns (rows auto) |
| 7–9 | 3×3 |

### Examples by total count

| Total covers | Output files |
|-------------|-------------|
| 1 | `_1.png` (1×1) |
| 4 | `_1.png` (2×2) |
| 9 | `_1.png` (3×3) |
| 10 | `_1.png` (3×3) + `_2.png` (1×1) |
| 15 | `_1.png` (3×3) + `_2.png` (2 col × 3 rows) |
| 18 | `_1.png` (3×3) + `_2.png` (3×3) |
| 27 | `_1.png` + `_2.png` + `_3.png` (3×3 each) |
| 36 | `_1.png`–`_4.png` (3×3 each) |

## Setup

### 1. Clone and create the credentials file

```
cp spotify_credentials.bat.example spotify_credentials.bat
```

Edit `spotify_credentials.bat` and fill in your credentials (see step 3).
This file is listed in `.gitignore` and will never be committed.

### 2. Install dependencies

```
pip install spotipy Pillow requests
```

`tkinter` (used by the GUI launcher) ships with the standard CPython installer — no extra install needed.

### 3. Create a Spotify API app

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app
2. Under **Redirect URIs**, add the following and save:
   ```
   http://127.0.0.1:8888/callback
   ```
   > ⚠️ `http://localhost:8888/callback` does NOT work — always use `127.0.0.1`
3. Note your **Client ID** and **Client Secret**

### 4. Set environment variables

**Windows (Command Prompt):**
```
set SPOTIFY_CLIENT_ID=your_client_id
set SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Windows (PowerShell):**
```
$env:SPOTIFY_CLIENT_ID="your_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret"
```

**Mac / Linux:**
```
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

> The `Playlist2img_gui.bat` launcher loads these automatically from `spotify_credentials.bat`,
> so GUI users only need to fill in that file (step 1).

## Usage

### Command line

```
python Playlist2img.py <playlist_url> [output_prefix]
```

| Argument | Description |
|----------|-------------|
| `playlist_url` | Spotify playlist URL (required) |
| `output_prefix` | Output filename prefix (defaults to the sanitized playlist name) |

#### Examples

```
# Auto filename (PlaylistName_1.png, PlaylistName_2.png)
python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx

# Custom prefix (maburon_1.png, maburon_2.png)
python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx maburon
```

Leading/trailing whitespace and invisible format characters (zero-width space, BOM, …)
in the playlist name are trimmed automatically, so output filenames never start with a blank.

### GUI Launcher (Windows only)

`Playlist2img_gui.bat` and `Playlist2img_gui.py` provide a graphical interface.
Double-click `Playlist2img_gui.bat` to launch — it loads credentials, checks Python,
auto-installs missing dependencies, then opens the window where you paste the playlist URL
and choose an output folder.

> ⚠️ The `.bat` launcher and GUI are **Windows only**. On Mac/Linux, use the command-line script directly.

### Output files

One file is generated per 9 images. With ≤9 covers only `_1.png` is created; 10–18 covers produce `_1.png` + `_2.png`; and so on with no upper page limit.

### First run

A browser window opens for Spotify login and permission approval.
After authorization, the token is cached in `.cache` — subsequent runs do not require browser sign-in.

## Architecture

```
                ┌──────────────────────┐      ┌──────────────────────────┐
  CLI:          │  Playlist2img.py     │      │  Playlist2img_gui.py     │  :GUI
  python ...    │  (main / argv)       │      │  (tkinter App, threads)  │  bat → py
                └──────────┬───────────┘      └────────────┬─────────────┘
                           │   imports core functions ◄────┘
                           ▼
          ┌────────────────────────────────────────────────────┐
          │  Core functions (single source of truth)            │
          │                                                     │
          │  extract_playlist_id(url)   → playlist ID (regex)   │
          │  trim_filename(name)        → strip ws/format chars │
          │  get_spotify_client()       → SpotifyOAuth client   │
          │  fetch_cover_urls(sp, id)   → dedup cover URLs       │
          │  download_image(url)        → PIL.Image (RGB)        │
          │  grid_cols(n)               → column count           │
          │  make_collage(imgs, cols)   → composited PIL.Image  │
          └────────────────────────────────────────────────────┘
                           │
                           ▼  Spotify Web API (Authorization Code Flow)
            GET /playlists/{id}, GET /playlists/{id}/items  +  i.scdn.co CDN
```

- **Single-source core**: all logic lives in `Playlist2img.py`. The GUI imports those
  functions instead of duplicating them, so a fix in the core applies to both front-ends.
- **Pipeline**: extract ID → authenticate → page through playlist items (dedup by
  `album["id"]`, skip non-tracks) → download covers → split into pages of 9 →
  compose each page with Pillow → save `{prefix}_{n}.png`.
- **Resilience**: a failed image download is logged and skipped; the collage continues
  with the remaining covers.
- **Tunable constants** (top of `Playlist2img.py`): `THUMB_SIZE` (per-cover px),
  `BG_COLOR` (collage background), plus `PAGE_SIZE` inside `main` (covers per page).

See [spec.md](spec.md) for the full function-level specification and
[Runbook.md](Runbook.md) for operational troubleshooting.

## Requirements

- Python 3.10+ (developed/tested on 3.13)
- spotipy 2.x
- Pillow 9.x+
- requests 2.x
- tkinter (bundled with standard CPython; GUI only)
