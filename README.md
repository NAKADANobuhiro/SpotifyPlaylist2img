# Playlist2img

A Python script that generates a collage PNG from album cover images in a Spotify playlist.
When multiple tracks share the same album, only one cover is used. Images are arranged from the top-left in a grid layout.

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

### 1. Clone and create credentials file

```
cp spotify_credentials.bat.example spotify_credentials.bat
```

Edit `spotify_credentials.bat` and fill in your credentials (see step 2).
This file is listed in `.gitignore` and will never be committed.

### 2. Install dependencies

```
pip install spotipy Pillow requests
```

### 2. Create a Spotify API app

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and create an app
2. Under **Redirect URIs**, add the following and save:
   ```
   http://127.0.0.1:8888/callback
   ```
   > ⚠️ `http://localhost:8888/callback` does NOT work — always use `127.0.0.1`

3. Note your **Client ID** and **Client Secret**

### 3. Set environment variables

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

## Usage

```
python Playlist2img.py <playlist_url> [output_prefix]
```

| Argument | Description |
|----------|-------------|
| `playlist_url` | Spotify playlist URL (required) |
| `output_prefix` | Output filename prefix (defaults to the playlist name) |

### Examples

```
# Auto filename (PlaylistName_1.png, PlaylistName_2.png)
python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx

# Custom prefix (maburon_1.png, maburon_2.png)
python Playlist2img.py https://open.spotify.com/playlist/6qPcuHG2Z6pFTWZWCu8Mbf?si=xxx maburon
```

### Output files

One file is generated per 9 images. With ≤9 covers only `_1.png` is created; 10–18 covers produce `_1.png` + `_2.png`; and so on.

### First run

A browser window will open for Spotify login and permission approval.
After authorization, the token is cached in `.cache` — subsequent runs will not require browser sign-in.

## Requirements

- Python 3.10+
- spotipy 2.x
- Pillow 9.x+
- requests 2.x
