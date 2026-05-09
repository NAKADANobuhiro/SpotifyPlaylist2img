# Playlist2img

A Python script that generates a collage PNG from album cover images in a Spotify playlist.
When multiple tracks share the same album, only one cover is used. Images are arranged from the top-left in a grid layout.

[日本語版 README はこちら](README.ja.md)

## Output Layout

```
_1.png (2×2 for ≤4 covers, 3×3 for ≥5 covers)

[≤4 covers]              [≥5 covers]
┌──────┬──────┐          ┌──────┬──────┬──────┐
│  1   │  2   │          │  1   │  2   │  3   │
├──────┼──────┤          ├──────┼──────┼──────┤
│  3   │  4   │          │  4   │  5   │  6   │
└──────┴──────┘          ├──────┼──────┼──────┤
                         │  7   │  8   │  9   │
                         └──────┴──────┴──────┘

_2.png (generated when there are 10+ unique covers)
  · ≤4 remaining → 2×2 grid
  · ≥5 remaining → 3×3 grid
```

## Setup

### 1. Install dependencies

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

| File | Generated when | Size |
|------|---------------|------|
| `{prefix}_1.png` | Always | 600×600px (2×2, ≤4 covers) or 900×900px (3×3, ≥5 covers) |
| `{prefix}_2.png` | 10+ unique covers | 600×600px (2×2) or 900×Npx (3×3) |

### First run

A browser window will open for Spotify login and permission approval.
After authorization, the token is cached in `.cache` — subsequent runs will not require browser sign-in.

## Requirements

- Python 3.10+
- spotipy 2.x
- Pillow 9.x+
- requests 2.x
