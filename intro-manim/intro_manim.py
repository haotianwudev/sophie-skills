"""
Manim intro scene: image background + hand-drawn colorful title words.

Each word is Written (stroke by stroke) in a different color and font weight,
timed to match subtitle pace from .en.srt.

Usage:
    manim -pql intro_manim.py IntroScene   # low quality preview
    manim -pqh intro_manim.py IntroScene   # high quality 1080p

Set IMAGE_PATH, TITLE, WORD_INTERVAL before running, or pass via env vars:
    IMAGE_PATH=cover.png TITLE="My Title" manim -pqh intro_manim.py IntroScene
"""

import os
import re
import sys
from manim import *

# --- Config (override via env vars) ---
IMAGE_PATH  = os.environ.get("IMAGE_PATH", r"C:\Users\lswht\Downloads\Gemini_Generated_Image_nfjn7dnfjn7dnfjn.png")
TITLE       = os.environ.get("TITLE", "ESG Investing: Why the Ratings Are a Mess")
SRT_PATH    = os.environ.get("SRT_PATH", r"C:\Users\lswht\Downloads\ESG_ A Compass Without Direction_.en.srt")
WORD_INTERVAL = float(os.environ.get("WORD_INTERVAL", "0"))  # 0 = auto from SRT

# Vibrant cartoon colors (cycles per word)
COLORS = [YELLOW, RED, BLUE, GREEN, ORANGE, PURPLE, WHITE, TEAL, PINK, GOLD]

# Font sizes alternating for variety
FONT_SIZES = [72, 80, 68, 76, 72, 80, 68]


def calc_word_interval(srt_path: str) -> float:
    if not srt_path or not os.path.exists(srt_path):
        return 0.45
    content = open(srt_path, encoding="utf-8").read()
    timings = re.findall(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)', content)
    texts   = re.findall(r'-->\s*[\d:,]+\s*\n(.+)', content)
    if not timings or not texts:
        return 0.45
    def to_sec(ts):
        h, m, s = ts.replace(',', '.').split(':')
        return int(h)*3600 + int(m)*60 + float(s)
    total_words = sum(len(t.split()) for t in texts[:30])
    total_time  = sum(to_sec(e) - to_sec(s) for s, e in timings[:30])
    wps = total_words / total_time if total_time > 0 else 2.0
    return max(0.35, min(0.65, 1.0 / wps * 1.2))


class IntroScene(Scene):
    def construct(self):
        interval = WORD_INTERVAL if WORD_INTERVAL > 0 else calc_word_interval(SRT_PATH)
        words    = TITLE.split()

        # --- Background image ---
        bg = ImageMobject(IMAGE_PATH)
        bg.height = config.frame_height
        bg.width  = config.frame_width

        # Dark overlay rect
        overlay = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=BLACK,
            fill_opacity=0.45,
            stroke_width=0,
        )

        self.play(FadeIn(bg, run_time=1.2), FadeIn(overlay, run_time=1.2))
        self.wait(0.2)

        # --- Build word mobjects ---
        word_mobs = []
        for i, word in enumerate(words):
            t = Text(
                word,
                color=COLORS[i % len(COLORS)],
                font_size=FONT_SIZES[i % len(FONT_SIZES)],
                weight=BOLD,
            )
            word_mobs.append(t)

        # Arrange into a VGroup, wrapped into lines
        group = VGroup(*word_mobs).arrange_in_grid(
            rows=2 if len(words) > 5 else 1,
            buff=0.25,
        )
        group.move_to(DOWN * 1.2)

        # --- Write each word stroke by stroke ---
        for i, mob in enumerate(word_mobs):
            # Position relative to group
            mob.move_to(group[i].get_center())
            write_time = max(0.3, interval * 0.8)
            self.play(Write(mob, run_time=write_time))

        self.wait(1.8)


class IntroSceneSplit(Scene):
    """Image slides to the left half; title words hand-written on the right."""

    def construct(self):
        self.camera.background_color = "#111111"
        interval = WORD_INTERVAL if WORD_INTERVAL > 0 else calc_word_interval(SRT_PATH)
        words = TITLE.split()

        # --- Background image: start full-screen ---
        bg = ImageMobject(IMAGE_PATH)
        bg.height = config.frame_height
        bg.width  = config.frame_width

        self.play(FadeIn(bg, run_time=1.0))
        self.wait(0.25)

        # --- Slide image to left half ---
        # Target scale so image height == frame height, width fills left ~47%
        left_scale = 0.52
        left_x = -config.frame_width * 0.265   # center of left panel

        self.play(
            bg.animate.scale(left_scale).move_to(LEFT * abs(left_x)),
            run_time=0.85,
            rate_func=smooth,
        )

        # Thin vertical separator line
        sep = Line(
            start=UP  * config.frame_height / 2,
            end=DOWN * config.frame_height / 2,
            stroke_color=WHITE,
            stroke_width=1.5,
            stroke_opacity=0.35,
        ).move_to(ORIGIN + LEFT * 0.05)
        self.play(Create(sep, run_time=0.3))

        # --- Build word mobjects ---
        word_mobs = []
        for i, word in enumerate(words):
            t = Text(
                word,
                color=COLORS[i % len(COLORS)],
                font_size=FONT_SIZES[i % len(FONT_SIZES)],
                weight=BOLD,
            )
            word_mobs.append(t)

        # Arrange into grid on the right panel
        n_rows = 3 if len(words) > 5 else 2
        group = VGroup(*word_mobs).arrange_in_grid(rows=n_rows, buff=0.28)

        # Fit within right half with margin
        right_panel_w = config.frame_width * 0.46
        if group.width > right_panel_w:
            group.scale(right_panel_w / group.width)

        right_center_x = config.frame_width * 0.265
        group.move_to(RIGHT * right_center_x)

        # --- Write each word stroke by stroke ---
        write_time = max(0.28, interval * 0.75)
        for mob in word_mobs:
            self.play(Write(mob, run_time=write_time))

        self.wait(2.0)
