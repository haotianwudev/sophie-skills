---
name: intro-gen
description: Generate an animated intro video using MoviePy + Pillow. Image fades in, title words pop in one by one with color cycling and mixed fonts. Fast to render, no LaTeX required.
argument-hint: <image_path> [video_path]
allowed-tools: [Bash, Read, Glob]
---

# Intro Generation Skill (MoviePy)

Create an animated intro clip using MoviePy + Pillow: image fade-in + word-by-word color pop-in effect.

**Inputs:**
- Cover image (provided by user)
- Title — auto-read from `.social.txt` next to the image

**Output:**
- `<image_base>_intro.mp4` — the intro clip
- Optionally merged with NotebookLM video

## Arguments

The user invoked this with: $ARGUMENTS

---

## Step 1 — Resolve inputs

Parse $ARGUMENTS:
- First arg = image path
- Second arg (optional) = NotebookLM video path to merge with

If no image path provided, ask the user.

Check if a `.social.txt` exists alongside the image for auto title reading. If not, ask the user for the title.

---

## Step 2 — Check dependencies

```bash
python -c "import moviepy, PIL" 2>&1
```

If missing:
```bash
pip install moviepy pillow
```

---

## Step 3 — Generate intro clip

```bash
python "C:/Users/lswht/intro_gen.py" "<image_path>"
```

Title is auto-read from `.social.txt`. Output: `<image_base>_intro.mp4`

---

## Step 4 — Merge with NotebookLM video (if video path provided)

Use FFmpeg to replace the opening of the NotebookLM video with the intro clip.

```bash
# Get intro duration
INTRO_DURATION=$(python -c "
from moviepy import VideoFileClip
c = VideoFileClip('<intro_path>')
print(round(c.duration, 2))
c.close()
")

# Trim NotebookLM video from INTRO_DURATION onward
ffmpeg -i "<notebooklm_video>" -ss $INTRO_DURATION -c copy notebooklm_trimmed.mp4

# Concatenate intro + trimmed video
ffmpeg -f concat -safe 0 -i <(echo -e "file '<intro_path>'\nfile 'notebooklm_trimmed.mp4'") -c copy final_output.mp4
```

Save as `<video_base>_with_intro.mp4` alongside the original video.

---

## Notes
- Intro duration ≈ 1.5s fade + 0.45s per word + 1.5s hold
- Script config (in `intro_gen.py`): `WORD_INTERVAL`, `OVERLAY_ALPHA`, `WORD_COLORS`, `FONT_CANDIDATES`
- No audio in intro clip
- `intro_gen.py` is at `C:/Users/lswht/intro_gen.py`
