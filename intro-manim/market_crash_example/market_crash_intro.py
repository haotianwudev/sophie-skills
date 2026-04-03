"""
VideoScribe-style intro for "Spotting a Market Crash" — 21 seconds.
Run: manim -qh market_crash_intro.py VideoScribeIntro
"""

from manim import *

IMAGE_PATH = r"F:\Video\market crash\Gemini_Generated_Image_kwd1p3kwd1p3kwd1.png"

COLORS = [YELLOW, RED, BLUE, GREEN, ORANGE, PURPLE, TEAL, PINK, GOLD]


class VideoScribeIntro(Scene):
    def construct(self):
        self.camera.background_color = WHITE

        # === IMAGE ANIMATION (0–4s) ===
        media = ImageMobject(IMAGE_PATH)
        media.height = config.frame_height * 0.8

        start_pos = LEFT * 5 + DOWN * 4
        target_pos = LEFT * 3.2
        media.move_to(start_pos)

        # Drag from bottom-left to left side (0–3s)
        self.add(media)
        self.play(media.animate.move_to(target_pos), run_time=3.0, rate_func=smooth)

        # Scale pulse (3–4s)
        self.play(media.animate.scale(1.12), run_time=0.5, rate_func=rush_into)
        self.play(media.animate.scale(1 / 1.12), run_time=0.5, rate_func=rush_from)

        # Hold (4–5.5s)
        self.wait(1.5)

        # === KEY PHRASES (5.5–16s) — 4 styled pill banners, vertically centred ===
        # Each pill: 1.4s grow-in + 1.1s hold = 2.5s × 4 = 10s → ends at 15.5s
        phrases = [
            ("Market Crash?",  "#C0392B"),   # deep red
            ("VIX Signals",    "#1A5276"),   # dark blue
            ("Rotate & Hedge", "#1E8449"),   # dark green
            ("Be Prepared.",   "#6C3483"),   # deep purple
        ]

        right_x = 3.2   # centred in the right panel
        # 4 rows centred around y=0, spaced 1.3 apart
        y_positions = [1.95, 0.65, -0.65, -1.95]

        pill_group = VGroup()

        for i, ((phrase, hex_color), y_pos) in enumerate(zip(phrases, y_positions)):
            font_size = 46 if len(phrase) > 11 else 54

            label = Text(phrase, color=WHITE, font_size=font_size, weight=BOLD)
            # Pill sized to text + padding
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

            # Pill grows from centre, label writes on top simultaneously
            self.play(
                GrowFromCenter(pill),
                Write(label, run_time=1.2),
                run_time=1.4,
                rate_func=smooth,
            )
            card = VGroup(pill, label)
            self.wait(1.1)
            pill_group.add(card)

        # Fade all pills out together (15.5s → 16s)
        self.play(FadeOut(pill_group, run_time=0.5))

        # Wait to reach 17s mark
        self.wait(1.0)

        # === FINAL TITLE (17–19s) ===
        line1 = Text("Spotting",        color=GREEN,  font_size=72, weight=BOLD)
        line2 = Text("a Market Crash",  color=RED,    font_size=54, slant=ITALIC)
        line3 = Text("Like a Pro",      color=PURPLE, font_size=52, weight=BOLD)

        line1.move_to(RIGHT * right_x + UP * 1.4 + LEFT * 0.2)
        line2.move_to(RIGHT * right_x + UP * 0.2 + RIGHT * 0.3)
        line3.move_to(RIGHT * right_x + DOWN * 1.2 + LEFT * 0.1)

        self.play(Write(line1, run_time=0.65))
        self.play(Write(line2, run_time=0.65))
        self.play(Write(line3, run_time=0.70))

        # Hold (19–21s)
        self.wait(2.0)
