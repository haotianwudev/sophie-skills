"""
Generate animated intro video: image fade-in + colorful multi-font word-by-word title.

Each word appears in a different color and font, timed to match subtitle pace.

Usage:
    python intro_gen.py <image_path> [srt_path] [output_path]
    python intro_gen.py cover.jpg
    python intro_gen.py cover.jpg subtitles.en.srt
    python intro_gen.py cover.jpg subtitles.en.srt intro.mp4

Title auto-read from .social.txt next to the image.
Pace auto-calculated from .en.srt if provided, else default 0.5s/word.
"""

import sys
import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip

# --- Config ---
VIDEO_W = 1920
VIDEO_H = 1080
FPS = 30
FADE_IN_DURATION = 1.2
WORD_HOLD = 2.0
OVERLAY_ALPHA = 0.40

# Vibrant cartoon color palette (one per word, cycles)
WORD_COLORS = [
    (255, 220, 50),   # yellow
    (255, 100, 100),  # coral red
    (100, 220, 255),  # sky blue
    (150, 255, 120),  # lime green
    (255, 160, 50),   # orange
    (220, 130, 255),  # purple
    (255, 255, 255),  # white
    (100, 255, 200),  # mint
    (255, 180, 220),  # pink
    (180, 255, 100),  # yellow-green
]

# Available Windows fonts (variety of weights/styles for cartoon feel)
FONT_CANDIDATES = [
    ("C:/Windows/Fonts/impact.ttf", 96),
    ("C:/Windows/Fonts/arialbd.ttf", 88),
    ("C:/Windows/Fonts/comic.ttf", 84),         # Comic Sans
    ("C:/Windows/Fonts/Georgia Bold.ttf", 88),
    ("C:/Windows/Fonts/georgiab.ttf", 88),
    ("C:/Windows/Fonts/verdanab.ttf", 82),
    ("C:/Windows/Fonts/trebucbd.ttf", 86),
    ("C:/Windows/Fonts/calibrib.ttf", 88),
    ("C:/Windows/Fonts/arialbi.ttf", 88),
    ("C:/Windows/Fonts/tahoma.ttf", 82),
]


def load_fonts():
    """Load available fonts from candidates."""
    fonts = []
    for path, size in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                fonts.append(ImageFont.truetype(path, size))
            except Exception:
                pass
    if not fonts:
        fonts = [ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 88)]
    return fonts


def read_title(img_path: str) -> str:
    base = os.path.splitext(img_path)[0]
    social_path = base + ".social.txt"
    if not os.path.exists(social_path):
        for f in os.listdir(os.path.dirname(img_path) or "."):
            if f.endswith(".social.txt"):
                social_path = os.path.join(os.path.dirname(img_path) or ".", f)
                break
    if os.path.exists(social_path):
        content = open(social_path, encoding="utf-8").read()
        match = re.search(r"TITLE:\s*\n(.+)", content)
        if match:
            return match.group(1).strip()
    return None


def calc_word_interval(srt_path: str) -> float:
    """Calculate average words-per-second from SRT timing."""
    if not srt_path or not os.path.exists(srt_path):
        return 0.5
    content = open(srt_path, encoding="utf-8").read()
    timings = re.findall(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)', content)
    texts = re.findall(r'-->\s*[\d:,]+\s*\n(.+)', content)
    if not timings or not texts:
        return 0.5
    def to_sec(ts):
        h, m, s = ts.replace(',', '.').split(':')
        return int(h)*3600 + int(m)*60 + float(s)
    total_words = sum(len(t.split()) for t in texts[:30])
    total_time = sum(to_sec(e) - to_sec(s) for s, e in timings[:30])
    wps = total_words / total_time if total_time > 0 else 2.0
    # Use subtitle pace but slightly slower for readability
    interval = max(0.35, min(0.65, 1.0 / wps * 1.2))
    print(f"  Subtitle pace: {wps:.1f} words/sec → word interval: {interval:.2f}s")
    return interval


def prepare_bg(img_path: str) -> np.ndarray:
    img = Image.open(img_path).convert("RGB")
    img_ratio = img.width / img.height
    target_ratio = VIDEO_W / VIDEO_H
    if img_ratio > target_ratio:
        new_h = VIDEO_H
        new_w = int(new_h * img_ratio)
    else:
        new_w = VIDEO_W
        new_h = int(new_w / img_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - VIDEO_W) // 2
    top = (new_h - VIDEO_H) // 2
    img = img.crop((left, top, left + VIDEO_W, top + VIDEO_H))
    return np.array(img)


def render_frame(t, bg, words, word_times, fonts, fade_dur):
    frame = Image.fromarray(bg.astype("uint8"))

    # Dim overlay
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, int(255 * OVERLAY_ALPHA)))
    frame = Image.alpha_composite(frame.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(frame)

    visible = [(i, w) for i, (w, wt) in enumerate(zip(words, word_times)) if t >= wt]
    if not visible:
        if t < fade_dur:
            arr = np.array(frame)
            return (arr * min(1.0, t / fade_dur)).astype("uint8")
        return np.array(frame)

    # Layout: measure each word with its font, build rows
    row_h = 110
    padding = 28
    row_items = []
    current_row = []
    current_w = 0
    max_row_w = VIDEO_W - 160

    for idx, word in visible:
        font = fonts[idx % len(fonts)]
        bbox = font.getbbox(word)
        w = bbox[2] - bbox[0] + padding
        if current_w + w > max_row_w and current_row:
            row_items.append(current_row)
            current_row = [(idx, word, font, w)]
            current_w = w
        else:
            current_row.append((idx, word, font, w))
            current_w += w
    if current_row:
        row_items.append(current_row)

    n_rows = len(row_items)
    total_h = n_rows * row_h
    y_start = VIDEO_H * 0.72 - total_h / 2

    for row_i, row in enumerate(row_items):
        row_total_w = sum(item[3] for item in row)
        x = (VIDEO_W - row_total_w) / 2
        y = y_start + row_i * row_h

        for idx, word, font, word_w in row:
            color = WORD_COLORS[idx % len(WORD_COLORS)]

            # Pop-in scale effect for newest word
            is_newest = (idx == visible[-1][0])
            if is_newest:
                age = t - word_times[idx]
                scale = min(1.0, 0.5 + age / 0.15)
                if scale < 1.0:
                    # Draw slightly larger then settle
                    pass

            # Shadow
            draw.text((x + 3, y + 3), word, font=font, fill=(0, 0, 0, 180))
            # Colored word
            draw.text((x, y), word, font=font, fill=color)
            x += word_w

    arr = np.array(frame)
    fade = min(1.0, t / fade_dur)
    if fade < 1.0:
        arr = (arr * fade).astype("uint8")
    return arr


def main():
    if len(sys.argv) < 2:
        print("Usage: python intro_gen.py <image_path> [srt_path] [output_path]")
        sys.exit(1)

    img_path = sys.argv[1]
    srt_path = None
    output = None

    for arg in sys.argv[2:]:
        if arg.endswith(".srt"):
            srt_path = arg
        elif arg.endswith(".mp4"):
            output = arg

    # Auto-find SRT next to image
    if not srt_path:
        base = os.path.splitext(img_path)[0]
        candidate = base + ".en.srt"
        if os.path.exists(candidate):
            srt_path = candidate
        else:
            for f in os.listdir(os.path.dirname(img_path) or "."):
                if f.endswith(".en.srt"):
                    srt_path = os.path.join(os.path.dirname(img_path) or ".", f)
                    break

    if not output:
        output = os.path.splitext(img_path)[0] + "_intro.mp4"

    title = read_title(img_path)
    if not title:
        print("Error: no title found. Add a .social.txt or pass title as argument.")
        sys.exit(1)

    print(f"Image:  {img_path}")
    print(f"Title:  {title}")
    print(f"SRT:    {srt_path or 'not found, using default pace'}")
    print(f"Output: {output}")

    word_interval = calc_word_interval(srt_path)
    words = title.split()
    word_times = [FADE_IN_DURATION + 0.3 + i * word_interval for i in range(len(words))]
    total_duration = word_times[-1] + WORD_HOLD

    print(f"Duration: {total_duration:.1f}s  |  Words: {len(words)}  |  Interval: {word_interval:.2f}s")

    fonts = load_fonts()
    print(f"Fonts loaded: {len(fonts)}")

    bg = prepare_bg(img_path)

    def make_frame(t):
        return render_frame(t, bg, words, word_times, fonts, FADE_IN_DURATION)

    clip = VideoClip(make_frame, duration=total_duration).with_fps(FPS)
    print("Rendering...")
    clip.write_videofile(output, fps=FPS, codec="libx264", audio=False,
                         ffmpeg_params=["-crf", "18", "-preset", "fast"])
    print(f"\nDone! Saved: {output}")


if __name__ == "__main__":
    main()
