---
name: intro-manim
description: Generate a VideoScribe-style animated intro using Manim. Image/video drags from bottom-left to left side with emphasis, then key phrases are hand-drawn stroke by stroke on the right in vibrant colors, ending with final title. Supports both static images and playing videos. High quality 1080p60 output.
argument-hint: <image_path> <srt_path> [video_path] [duration]
allowed-tools: [Bash, Read, Glob]
---

# Intro Generation Skill (Manim)

Create a VideoScribe-style animated explainer: image/video drags from bottom-left to left side, key phrases drawn stroke by stroke following subtitle timing, ending with final title.

**Inputs:**
- Cover image (provided by user) - used for the movement animation
- Optional: Video file to play after reaching final position
- Subtitle file (.srt) for pacing and timing
- Duration (default 26 seconds)
- Title — derived from subtitle filename or `.social.txt` next to the image
- Optional: NotebookLM video path to merge with

**Output:**
- `media/videos/esg_videoscribe/1080p60/ESGIntro.mp4` (with static image)
- `ESGIntro_WithPlayingVideo.mp4` (with playing video after 4s)
- Optionally merged with NotebookLM video

## Arguments

The user invoked this with: $ARGUMENTS

---

## Step 1 — Resolve inputs

Parse $ARGUMENTS:
- First arg = image path (required)
- Second arg = subtitle file path (.srt) for timing (required)
- Third arg (optional) = NotebookLM video path to merge with
- Fourth arg (optional) = duration in seconds (default 26)

If no image path provided, ask the user.
If no subtitle file provided, ask the user.

Read title from subtitle filename or `.social.txt` next to the image:
```bash
grep -A1 "^TITLE:" "<image_base>.social.txt" | tail -1
```

If no `.social.txt` found, derive title from subtitle filename.

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

## Step 3 — Generate VideoScribe explainer

The script follows this structure:
1. Image animation (0-3s): Drag from bottom-left to left side (slower movement)
2. Emphasis (3-4s): Scale pulse for 1 second
3. Wait (4-6s): Hold for 2 seconds
4. Key phrases (6-22s): Animate meaningful words 1s ahead of subtitle timing
5. Final title (22-24s): Show complete title derived from subtitle file
6. Hold (24-26s): Stay with final title for 2 seconds

**Customize the script:**
- Edit `key_phrases` array with your content words/questions
- Edit final title lines (line1, line2, line3) with your title text
- Adjust colors, font sizes, and positions as needed

Run the generation:

```bash
manim -qh intro_manim.py VideoScribeIntro 2>&1
```

Or with environment variables:

```bash
IMAGE_PATH="path/to/image.png" SRT_PATH="path/to/subs.srt" manim -qh intro_manim.py VideoScribeIntro
```

- `-qh` — high quality 1080p60 (use `-ql` for fast 480p preview)

Output: `media/videos/intro_manim/1080p60/VideoScribeIntro.mp4`

**Quick preview first:**
```bash
manim -ql intro_manim.py VideoScribeIntro 2>&1
```

---

## Step 4 — Add playing video (optional)

If you want the actual video to play after the movement animation (starting at 4s):

**Create a video alignment script** (or use the example from `esg_example/fix_video_alignment.py`):

```python
# fix_video_alignment.py
from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image
import os

VIDEO_PATH = r"path/to/your/video.mp4"
IMAGE_PATH = r"path/to/your/image.png"
MANIM_OUTPUT = r"media/videos/intro_manim/1080p60/VideoScribeIntro.mp4"
OUTPUT_PATH = "VideoScribeIntro_WithPlayingVideo.mp4"

# ... (see esg_example/fix_video_alignment.py for full implementation)
```

Run it:

```bash
python fix_video_alignment.py
```

This script:
- Calculates exact image dimensions and position from Manim
- Loops the source video to fill 22 seconds (26s - 4s animation)
- Resizes video to match image dimensions exactly
- Composites video over the animation starting at 4 seconds
- Output: `VideoScribeIntro_WithPlayingVideo.mp4`

**Requirements:**
- moviepy installed: `pip install moviepy`
- Video file path configured in script

---

## Step 5 — Merge with NotebookLM video (if video path provided)

Use FFmpeg to replace the opening of the NotebookLM video with the intro clip.

```bash
INTRO_PATH="<image_directory>/media/videos/<script_name>/1080p60/ESGIntro.mp4"

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

## Animation Design Guidelines

### Timing Structure (26 seconds total)
- 0-3s: Image drags from bottom-left to left side (slow, smooth motion)
- 3-4s: Scale pulse emphasis (1 second)
- 4-6s: Wait/hold (2 seconds)
- 6-22s: Key phrases appear 1s ahead of subtitle timing
- 22-24s: Final title written stroke by stroke
- 24-26s: Hold final title (2 seconds)

### Key Phrases
- Use meaningful content words and engaging questions
- Include questions to create narrative tension (e.g., "A Great Guide?", "More Confusing?", "A Compass?")
- Extract from subtitle content, 1 second ahead of spoken timing
- All phrases stay visible on screen, stacked vertically
- Example: "ESG", "Environmental", "Social", "Governance", "A Great Guide?", "Investing", "More Confusing?", "A Compass?"

### Visual Style
- White background for clean VideoScribe look
- Vibrant cycling colors: YELLOW, RED, BLUE, GREEN, ORANGE, PURPLE, TEAL, PINK, GOLD
- Bold weight fonts
- Image/video on left (80% height), text on right
- Stroke-by-stroke writing animation (Write effect)
- All key phrases stay visible on screen (stacked vertically with 0.75 spacing)
- Video support: Static image during movement (0-4s), playing video after reaching position (4-26s)

### Final Title
- Derive from subtitle filename (e.g., "ESG: A Compass Without Direction")
- Three lines: "ESG:" (GREEN, bold, 68pt), "A Compass" (RED, italic, 58pt), "Without Direction" (PURPLE, bold, 52pt - smaller for longer text)
- Each line has different font size and position offset for dynamic look
- Clear all previous phrases before showing
- Write stroke by stroke over 2 seconds
- Hold for 2 seconds at end

---

## Notes
- Main script: `intro_manim.py` with scene `VideoScribeIntro`
- Config in script: `COLORS`, `key_phrases`, final title lines
- Customize phrases and title text for your content
- MiKTeX must be installed for Manim text rendering on Windows
- First run downloads font/LaTeX cache — subsequent runs are faster
- White background creates clean VideoScribe aesthetic
- Subtitle timing can be parsed to extract phrase timings
- Video alignment: Script calculates exact Manim image dimensions and position
- Video compositing uses moviepy for frame-perfect alignment
- For playing video: Image used during movement (0-4s), video plays after (4-26s)
- Example implementation available in `esg_example/` folder
