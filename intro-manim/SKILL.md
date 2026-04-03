---
name: intro-manim
description: Generate a VideoScribe-style animated intro using Manim. Image/video drags from bottom-left to left side with emphasis, then 4 styled pill banners pop in on the right with GrowFromCenter + Write animation, ending with a three-line final title. Supports both static images and playing videos composited via moviepy. High quality 1080p60 output.
argument-hint: <image_path> <srt_path> [video_path] [duration]
allowed-tools: [Bash, Read, Glob]
---

# Intro Generation Skill (Manim)

Create a VideoScribe-style animated explainer: image/video drags from bottom-left to left side, 4 styled pill banners grow in on the right one by one, ending with a final title written stroke by stroke.

**Inputs:**
- Cover image (required) — animated on the left panel
- Optional: Video file to play after the image reaches its position (4s mark)
- Subtitle file (.srt) — for deriving title and key phrase content
- Duration (default 21 seconds)
- Optional: NotebookLM video path to merge with

**Output:**
- `media/videos/<script_name>/1080p60/VideoScribeIntro.mp4` — static image version
- `<Name>_WithVideo.mp4` — with source video playing in the left panel from 4s onward
- Optionally merged with a NotebookLM video

## Arguments

The user invoked this with: $ARGUMENTS

---

## Step 1 — Resolve inputs

Parse $ARGUMENTS:
- First arg = image path (required)
- Second arg = subtitle file path (.srt) (required for title/phrase content)
- Third arg (optional) = source video path to composite in left panel
- Fourth arg (optional) = duration in seconds (default 21)

If no image path provided, ask the user.
If no subtitle file provided, ask the user.

Read title from `.social.txt` next to the image if available:
```bash
grep -A1 "^TITLE:" "<image_base>.social.txt" | tail -1
```
Otherwise derive title from subtitle filename.

---

## Step 2 — Check dependencies

```bash
manim --version 2>&1
python -c "import moviepy; from PIL import Image; print('OK')" 2>&1
```

If missing:
```bash
pip install manim moviepy pillow
# MiKTeX required for Manim text rendering on Windows:
# winget install MiKTeX.MiKTeX
```

---

## Step 3 — Write and run the Manim script

Base the script on `intro_manim.py` in this folder. Key things to customise:

1. **`IMAGE_PATH`** — set to the user's image
2. **`phrases`** — 4 tuples of `("Text", "#hexcolor")` derived from subtitle content:
   - Use engaging questions and key concepts from the transcript
   - Recommended colors: `#C0392B` (red), `#1A5276` (navy), `#1E8449` (green), `#6C3483` (purple)
3. **Final title** — 3 lines, derive from the video title / social.txt

**Script structure (21 seconds):**
- 0–3s: Image drags from bottom-left → left panel (smooth)
- 3–4s: Scale pulse emphasis
- 4–5.5s: Hold
- 5.5–15.5s: 4 pill banners, each 1.4s grow-in + 1.1s hold = 2.5s each
- 15.5–16s: All pills fade out
- 16–17s: Pause
- 17–19s: Final title written line by line
- 19–21s: Hold

**Pill banner animation pattern (critical — do NOT use `pill.animate.scale(1)` on a zero-scaled object):**
```python
self.play(
    GrowFromCenter(pill),       # pill grows from centre (0 → full size)
    Write(label, run_time=1.2), # text writes simultaneously
    run_time=1.4,
    rate_func=smooth,
)
```

Save the script alongside the image file (or in a working directory), then run:
```bash
cd "<image_directory>"
manim -ql <script_name>.py VideoScribeIntro 2>&1   # quick 480p preview
manim -qh <script_name>.py VideoScribeIntro 2>&1   # full 1080p60
```

Output: `media/videos/<script_name>/1080p60/VideoScribeIntro.mp4`

---

## Step 4 — Composite source video (if video path provided)

Use `fix_video_alignment.py` pattern (see `market_crash_example/` or `esg_example/`):

```python
from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image

VIDEO_PATH   = r"path/to/source.mp4"
IMAGE_PATH   = r"path/to/image.png"
MANIM_OUTPUT = r"media/videos/<script>/1080p60/VideoScribeIntro.mp4"
OUTPUT_PATH  = "Output_WithVideo.mp4"

PLAY_START    = 4                        # video starts at 4s (after movement)
TOTAL_INTRO   = 21                       # total intro duration
PLAY_DURATION = TOTAL_INTRO - PLAY_START # 17 seconds of source video

# Calculate exact Manim image position
img = Image.open(IMAGE_PATH)
frame_h, frame_w = 1080, 1920
target_h = int(frame_h * 0.8)
target_w = int(img.width * (target_h / img.height))
pixels_per_unit = frame_w / 14
img_center_x = frame_w / 2 + (-3.2 * pixels_per_unit)
x_pos = int(img_center_x - target_w / 2)
y_pos = int((frame_h - target_h) / 2)
```

Run:
```bash
PYTHONUTF8=1 python fix_video_alignment.py 2>&1
```

---

## Step 5 — Merge with NotebookLM video (optional)

```bash
INTRO="path/to/VideoScribeIntro.mp4"
NLM="path/to/notebooklm_video.mp4"
BASE="OutputName"

DURATION=$(python -c "from moviepy import VideoFileClip; c=VideoFileClip('$INTRO'); print(round(c.duration,2)); c.close()")
ffmpeg -i "$INTRO" -vf "fps=30,scale=1920:1080" -c:v libx264 -crf 18 -preset fast -an intro_reenc.mp4
ffmpeg -i "$NLM" -ss $DURATION -c copy nlm_trimmed.mp4
printf "file '%s'\nfile 'nlm_trimmed.mp4'\n" "$(pwd)/intro_reenc.mp4" > concat.txt
ffmpeg -f concat -safe 0 -i concat.txt -c copy "${BASE}_with_intro.mp4"
rm intro_reenc.mp4 nlm_trimmed.mp4 concat.txt
```

---

## Animation Design Guidelines

### Timing Structure (21 seconds default)
- 0–3s: Image drags from bottom-left to left side (smooth)
- 3–4s: Scale pulse emphasis
- 4–5.5s: Hold
- 5.5–15.5s: 4 pill banners, 2.5s each
- 15.5–16s: Pills fade out
- 16–17s: Pause
- 17–19s: Final title (3 lines written stroke by stroke)
- 19–21s: Hold

### Pill Banners
- 4 phrases maximum — gives each enough screen time to read
- Use a question + 2 content points + a closing call-to-action structure
- Colors: deep red, navy blue, forest green, deep purple (high contrast on white bg)
- White BOLD text on colored background — high contrast, clean explainer look
- Evenly centered around y=0: positions [1.95, 0.65, -0.65, -1.95]
- All pills stay visible until the fade-out at 15.5s
- **Animation**: `GrowFromCenter(pill)` + `Write(label)` simultaneously — do NOT use `pill.animate.scale()` on a zero-scaled object

### Final Title
- 3 lines derived from video title
- Colors: GREEN (bold), RED (italic), PURPLE (bold)
- Font sizes: 72 / 54 / 52 — adjust down if text is long
- Slight horizontal offsets per line for dynamic look
- Written stroke by stroke over 2 seconds, held for 2 seconds

### Visual Style
- White background
- Image on left (80% frame height, `LEFT * 3.2`)
- Text/pills on right (`right_x = 3.2`)
- Static image during movement (0–4s), source video composited after (4–21s)

---

## Example Implementations
- `esg_example/` — original ESG intro (plain colored text, 8 phrases)
- `market_crash_example/` — refined version (pill banners, 4 phrases, `GrowFromCenter` fix)

## Notes
- Always run `-ql` preview before `-qh` full render to catch errors fast
- `PYTHONUTF8=1` prefix required on Windows for moviepy to avoid GBK encoding errors
- MiKTeX must be installed for Manim text rendering on Windows
- Manim caches partial frames — if image path changes, old cache may silently be used; always verify output visually
- `pill.animate.scale(1)` on a zero-scaled object is a no-op — use `GrowFromCenter(pill)` instead
