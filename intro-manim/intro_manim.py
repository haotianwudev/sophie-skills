"""
VideoScribe-style animated intro using Manim.
Image/video drags from bottom-left to left side, then key phrases appear on right.

Usage:
    manim -pql videoscribe_intro.py VideoScribeIntro   # preview
    manim -pqh videoscribe_intro.py VideoScribeIntro   # high quality 1080p60

Set via environment variables:
    IMAGE_PATH="path/to/image.png" SRT_PATH="path/to/subs.srt" manim -qh videoscribe_intro.py VideoScribeIntro
"""

import os
import re
from manim import *

# --- Config (override via env vars) ---
IMAGE_PATH = os.environ.get("IMAGE_PATH", r"C:\Users\lswht\Downloads\Gemini_Generated_Image_nfjn7dnfjn7dnfjn.png")
SRT_PATH = os.environ.get("SRT_PATH", r"C:\Users\lswht\Downloads\ESG_ A Compass Without Direction_.en.srt")
TITLE = os.environ.get("TITLE", "Your Title Here")

# Vibrant colors cycling
COLORS = [YELLOW, RED, BLUE, GREEN, ORANGE, PURPLE, TEAL, PINK, GOLD]


def parse_subtitles_for_26s(srt_path: str):
    """Parse subtitle file and extract timed phrases for first 26 seconds."""
    if not srt_path or not os.path.exists(srt_path):
        return []
    
    try:
        content = open(srt_path, encoding="utf-8").read()
        
        def to_sec(ts):
            h, m, s = ts.replace(',', '.').split(':')
            return int(h)*3600 + int(m)*60 + float(s)
        
        entries = []
        blocks = content.strip().split('\n\n')
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                timing_line = lines[1]
                match = re.match(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)', timing_line)
                if match:
                    start_time = to_sec(match.group(1))
                    end_time = to_sec(match.group(2))
                    text = ' '.join(lines[2:]).strip()
                    
                    if start_time < 26:
                        entries.append({
                            'start': start_time,
                            'end': min(end_time, 26),
                            'text': text
                        })
        
        return entries
    except Exception as e:
        print(f"Error parsing subtitles: {e}")
        return []


class VideoScribeIntro(Scene):
    def construct(self):
        # White background for clean VideoScribe look
        self.camera.background_color = WHITE
        
        # Parse subtitles for timing (available for future use)
        subtitle_entries = parse_subtitles_for_26s(SRT_PATH)
        
        # === IMAGE ANIMATION (0-6s) ===
        
        # Load image at 80% height
        media = ImageMobject(IMAGE_PATH)
        media.height = config.frame_height * 0.8
        
        # Start position: bottom-left corner (off-screen)
        start_pos = LEFT * 5 + DOWN * 4
        media.move_to(start_pos)
        
        # Target position: left side, centered vertically
        target_pos = LEFT * 3.2
        
        # Drag from bottom-left to left side - SLOW (0-3s)
        self.add(media)
        self.play(
            media.animate.move_to(target_pos),
            run_time=3.0,
            rate_func=smooth
        )
        
        # Emphasize with scale pulse - 1 SECOND (3-4s)
        self.play(
            media.animate.scale(1.12),
            run_time=0.5,
            rate_func=rush_into
        )
        self.play(
            media.animate.scale(1/1.12),
            run_time=0.5,
            rate_func=rush_from
        )
        
        # Wait 2 seconds (4-6s)
        self.wait(2.0)
        
        # === TEXT ANIMATION (6-26s) ===
        
        # TODO: Customize these phrases based on your content
        # Extract from subtitle timing or define manually
        key_phrases = [
            {"text": "Word 1", "start": 6.0, "duration": 1.5},
            {"text": "Word 2", "start": 7.8, "duration": 1.3},
            {"text": "Word 3", "start": 9.5, "duration": 1.2},
            {"text": "Word 4", "start": 11.0, "duration": 1.5},
            {"text": "Phrase 5", "start": 13.0, "duration": 1.5},
            {"text": "Phrase 6", "start": 15.0, "duration": 1.3},
            {"text": "Phrase 7", "start": 17.0, "duration": 1.5},
            {"text": "Phrase 8", "start": 19.0, "duration": 1.5},
        ]
        
        # Position text on right side
        right_x = 2.8
        current_time = 6.0
        
        text_group = VGroup()
        
        # Animate key phrases - KEEP ALL VISIBLE
        for i, phrase_data in enumerate(key_phrases):
            phrase = phrase_data["text"]
            target_start = phrase_data["start"]
            duration = phrase_data["duration"]
            
            wait_time = target_start - current_time
            if wait_time > 0:
                self.wait(wait_time)
            
            font_size = 46 if len(phrase) > 12 else 56
            text = Text(
                phrase,
                color=COLORS[i % len(COLORS)],
                font_size=font_size,
                weight=BOLD,
            )
            
            y_pos = 2.5 - i * 0.75
            text.move_to(RIGHT * right_x + UP * y_pos)
            
            write_time = min(duration * 0.65, 1.8)
            self.play(Write(text, run_time=write_time))
            
            text_group.add(text)
            current_time = target_start + write_time
        
        # Clear all phrases before final title
        if len(text_group) > 0:
            self.play(*[FadeOut(t, run_time=0.4) for t in text_group])
            current_time += 0.4
        
        # Wait to reach 22s mark for final title
        wait_before_final = 22.0 - current_time
        if wait_before_final > 0:
            self.wait(wait_before_final)
            current_time = 22.0
        
        # Show final title - customize these lines
        line1 = Text("Your Title:", color=GREEN, font_size=68, weight=BOLD, font="Sans")
        line2 = Text("Line Two", color=RED, font_size=58, weight=LIGHT, font="Sans", slant=ITALIC)
        line3 = Text("Line Three", color=PURPLE, font_size=52, weight=BOLD, font="Sans")
        
        line1.move_to(RIGHT * right_x + UP * 1.4 + LEFT * 0.2)
        line2.move_to(RIGHT * right_x + UP * 0.2 + RIGHT * 0.3)
        line3.move_to(RIGHT * right_x + DOWN * 1.2 + LEFT * 0.1)
        
        self.play(Write(line1, run_time=0.65))
        self.play(Write(line2, run_time=0.65))
        self.play(Write(line3, run_time=0.7))
        
        # Stay with final title for 2 seconds (24-26s)
        self.wait(2.0)
