---
name: intro-manim
description: Generate a VideoScribe-style animated intro using Manim. Image fades in full-screen, slides to the left half, then title words are hand-drawn stroke by stroke on the right in vibrant colors. High quality 1080p60 output.
argument-hint: <image_path> [video_path] [scene]
allowed-tools: [Bash, Read, Glob]
---

# Intro Generation Skill (Manim)

Create a VideoScribe-style animated intro: image slides left, title words drawn stroke by stroke on the right.

**Inputs:**
- Cover image (provided by user)
- Title — auto-read from `IMAGE_PATH` env or `.social.txt` next to the image
- Scene: `IntroSceneSplit` (image left + title right, default) or `IntroScene` (title centered over image)

**Output:**
- `media/videos/intro_manim/1080p60/<SceneName>.mp4`
- Optionally merged with NotebookLM video

## Arguments

The user invoked this with: $ARGUMENTS

---

## Step 1 — Resolve inputs

Parse $ARGUMENTS:
- First arg = image path
- Second arg (optional) = NotebookLM video path to merge with
- Third arg (optional) = scene name (`IntroSceneSplit` or `IntroScene`), default `IntroSceneSplit`

If no image path provided, ask the user.

Read title from `.social.txt` next to the image:
```bash
grep -A1 "^TITLE:" "<image_base>.social.txt" | tail -1
```

If no `.social.txt` found, ask the user for the title.

---

## Step 2 — Check dependencies

```bash
manim --version 2>&1
```

If missing:
```bash
pip install manim
# Also requires MiKTeX (LaTeX) for text rendering:
# winget install MiKTeX.MiKTeX
```

---

## Step 3 — Generate intro clip

Run from the directory containing the image so output lands nearby:

```bash
cd "<image_directory>" && IMAGE_PATH="<image_path>" TITLE="<title>" SRT_PATH="<srt_path_or_empty>" manim -qh "C:/Users/lswht/intro_manim.py" <SceneName> 2>&1
```

- `IMAGE_PATH` — absolute path to the cover image
- `TITLE` — the full title string (quote it)
- `SRT_PATH` — path to `.en.srt` for auto word-pace; leave empty to use default 0.45s/word
- `-qh` — high quality 1080p60 (use `-ql` for fast 480p preview)

Output: `<image_directory>/media/videos/intro_manim/1080p60/<SceneName>.mp4`

**Quick preview first:**
```bash
cd "<image_directory>" && IMAGE_PATH="<image_path>" TITLE="<title>" manim -ql "C:/Users/lswht/intro_manim.py" <SceneName> 2>&1
```

---

## Step 4 — Merge with NotebookLM video (if video path provided)

Use FFmpeg to replace the opening of the NotebookLM video with the intro clip.

```bash
INTRO_PATH="<image_directory>/media/videos/intro_manim/1080p60/<SceneName>.mp4"

# Get intro duration
INTRO_DURATION=$(python -c "
from moviepy import VideoFileClip
c = VideoFileClip('$INTRO_PATH')
print(round(c.duration, 2))
c.close()
")

# Re-encode intro to match NotebookLM video specs (30fps, AAC audio stream)
ffmpeg -i "$INTRO_PATH" -vf "fps=30,scale=1920:1080" -c:v libx264 -crf 18 -preset fast -an intro_reenc.mp4

# Trim NotebookLM video: skip its opening equal to intro duration
ffmpeg -i "<notebooklm_video>" -ss $INTRO_DURATION -c copy notebooklm_trimmed.mp4

# Concatenate
printf "file '%s'\nfile 'notebooklm_trimmed.mp4'\n" "$(pwd)/intro_reenc.mp4" > concat_list.txt
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy "<video_base>_with_intro.mp4"

# Cleanup
rm intro_reenc.mp4 notebooklm_trimmed.mp4 concat_list.txt
```

---

## Scene descriptions

| Scene | Layout |
|---|---|
| `IntroSceneSplit` | Image fades in full-screen → slides to left half → title words hand-written on right half, word by word in alternating colors |
| `IntroScene` | Image fades in full-screen with dark overlay → all title words arranged in grid and drawn stroke by stroke, centered |

---

## Notes
- Config in `intro_manim.py`: `COLORS`, `FONT_SIZES`, `WORD_INTERVAL` env var
- MiKTeX must be installed for Manim text rendering on Windows
- First run downloads font/LaTeX cache — subsequent runs are faster
- `intro_manim.py` is at `C:/Users/lswht/intro_manim.py`
