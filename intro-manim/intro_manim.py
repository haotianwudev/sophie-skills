"""
VideoScribe-style animated intro using Manim.
Image drags from bottom-left to left side with emphasis, then styled pill banners
appear on the right, ending with a three-line final title.

Usage:
    manim -pql intro_manim.py VideoScribeIntro   # preview (low quality, fast)
    manim -pqh intro_manim.py VideoScribeIntro   # high quality 1080p60

Override paths via environment variables:
    IMAGE_PATH="path/to/image.png" manim -qh intro_manim.py VideoScribeIntro

TIMING STRUCTURE (~21 seconds):
- 0–3s:   Image drags from bottom-left to left side (smooth)
- 3–4s:   Scale pulse emphasis
- 4–5.5s: Hold
- 5.5–15.5s: 4 pill banners grow in one by one (2.5s each)
- 15.5–16s:  All pills fade out together
- 16–17s: Brief pause
- 17–19s: Final title written line by line
- 19–21s: Hold on final title
"""

import os
from manim import *

# --- Config (TODO: set these before running) ---
IMAGE_PATH = os.environ.get("IMAGE_PATH", "")   # TODO: path to your thumbnail/cover image
TITLE = os.environ.get("TITLE", "Your Title Here")


class VideoScribeIntro(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        # === IMAGE ANIMATION (0–4s) ===
        # TODO: confirm IMAGE_PATH is set above
        media = ImageMobject(IMAGE_PATH)
        media.height = config.frame_height * 0.8

        start_pos = LEFT * 5 + DOWN * 4   # off-screen bottom-left
        target_pos = LEFT * 3.2           # left panel, vertically centred
        media.move_to(start_pos)

        # Drag from bottom-left to left side (0–3s)
        self.add(media)
        self.play(media.animate.move_to(target_pos), run_time=3.0, rate_func=smooth)

        # Scale pulse for emphasis (3–4s)
        self.play(media.animate.scale(1.12), run_time=0.5, rate_func=rush_into)
        self.play(media.animate.scale(1 / 1.12), run_time=0.5, rate_func=rush_from)

        # Hold (4–5.5s)
        self.wait(1.5)

        # === PILL BANNERS (5.5–15.5s) ===
        # 4 pills × 2.5s each (1.4s grow-in + 1.1s hold) = 10s
        # TODO: replace text and hex colors with your own content
        phrases = [
            ("Key Point 1", "#C0392B"),   # deep red    — e.g. a risk or problem
            ("Key Point 2", "#1A5276"),   # dark blue   — e.g. a signal or indicator
            ("Key Point 3", "#1E8449"),   # dark green  — e.g. an action or strategy
            ("Key Point 4", "#6C3483"),   # deep purple — e.g. a takeaway or CTA
        ]

        right_x = 3.2       # horizontal centre of the right panel
        # 4 rows evenly spaced around y=0
        y_positions = [1.95, 0.65, -0.65, -1.95]

        pill_group = VGroup()

        for (phrase, hex_color), y_pos in zip(phrases, y_positions):
            font_size = 46 if len(phrase) > 11 else 54

            label = Text(phrase, color=WHITE, font_size=font_size, weight=BOLD)

            # Pill sized to fit the label with comfortable padding
            pill = RoundedRectangle(
                width=label.width + 0.7,
                height=label.height + 0.45,
                corner_radius=0.22,
                fill_color=hex_color,
                fill_opacity=1,
                stroke_width=0,
            )
            pill.move_to(RIGHT * right_x + UP * y_pos)
            label.move_to(pill.get_center())

            # Pill grows from centre while label writes simultaneously
            self.play(
                GrowFromCenter(pill),
                Write(label, run_time=1.2),
                run_time=1.4,
                rate_func=smooth,
            )
            pill_group.add(VGroup(pill, label))
            self.wait(1.1)

        # Fade all pills out together (15.5–16s)
        self.play(FadeOut(pill_group, run_time=0.5))

        # Brief pause before final title (16–17s)
        self.wait(1.0)

        # === FINAL TITLE (17–19s) ===
        # TODO: replace with your video's actual title (3 lines recommended)
        line1 = Text("Title Word",   color=GREEN,  font_size=72, weight=BOLD)
        line2 = Text("Second Line",  color=RED,    font_size=54, slant=ITALIC)
        line3 = Text("Third Line",   color=PURPLE, font_size=52, weight=BOLD)

        # Slight horizontal offsets give a dynamic, non-uniform look
        line1.move_to(RIGHT * right_x + UP * 1.4 + LEFT * 0.2)
        line2.move_to(RIGHT * right_x + UP * 0.2 + RIGHT * 0.3)
        line3.move_to(RIGHT * right_x + DOWN * 1.2 + LEFT * 0.1)

        self.play(Write(line1, run_time=0.65))
        self.play(Write(line2, run_time=0.65))
        self.play(Write(line3, run_time=0.70))

        # Hold on final title (19–21s)
        self.wait(2.0)
