"""
Custom VideoScribe-style explainer for ESG video.
Video/Image drags from bottom-left to left side, then key phrases written on right following subtitle timing.

TIMING STRUCTURE (26 seconds):
- 0-3s: Video/Image drags from bottom-left to left side (slow, smooth)
- 3-4s: Scale pulse emphasis (1 second)
- 4-6s: Wait/hold (2 seconds)
- 6-22s: Key phrases appear 1s ahead of subtitle timing
- 22-24s: Final title written stroke by stroke
- 24-26s: Hold final title (2 seconds)

DESIGN PRINCIPLES:
- White background for clean VideoScribe aesthetic
- Vibrant cycling colors for each phrase
- Meaningful content words and engaging questions
- All phrases stay visible on screen (stacked vertically)
- Final title includes "ESG:" at the top with three lines total
- Each title line has different color (GREEN, RED, PURPLE), font style, and position offset
- Longer title lines use smaller fonts (52pt for "Without Direction")

Usage:
    manim -pql esg_videoscribe.py ESGIntro   # preview
    manim -pqh esg_videoscribe.py ESGIntro   # high quality 1080p60
"""

import os
import re
from manim import *
try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.recorder import RecorderService
except:
    pass

# --- Config ---
IMAGE_PATH = r"C:\Users\lswht\Downloads\Gemini_Generated_Image_nfjn7dnfjn7dnfjn.png"
VIDEO_PATH = r"C:\Users\lswht\Downloads\Video_Generation_From_Prompt (1).mp4"
SRT_PATH = r"C:\Users\lswht\Downloads\ESG_ A Compass Without Direction_.en.srt"

# Set to True to use video instead of image (requires FFmpeg post-processing)
USE_VIDEO = False

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
        
        # Parse subtitle entries
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
                    
                    # Only include entries within first 26 seconds
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


class ESGIntro(Scene):
    def construct(self):
        # White background for clean VideoScribe look
        self.camera.background_color = WHITE
        
        # Parse subtitles for timing (available for future use)
        subtitle_entries = parse_subtitles_for_26s(SRT_PATH)
        
        # === IMAGE/VIDEO ANIMATION (0-6s) ===
        
        # Load video or image at 80% height (slightly larger)
        # Note: Manim doesn't support video playback in scenes directly
        # We'll extract first frame from video or use image
        if USE_VIDEO:
            # For video, we'll use FFmpeg to extract a frame and use it as image
            import subprocess
            frame_path = "temp_video_frame.png"
            try:
                subprocess.run([
                    "ffmpeg", "-i", VIDEO_PATH, "-vframes", "1", 
                    "-y", frame_path
                ], capture_output=True, check=True)
                media = ImageMobject(frame_path)
            except:
                # Fallback to image if video extraction fails
                media = ImageMobject(IMAGE_PATH)
            media.height = config.frame_height * 0.8
        else:
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
        
        # Key phrases: meaningful content words only, 1s ahead of subtitle timing
        # Show phrases until 21s (1s before final title at 22s)
        key_phrases = [
            {"text": "ESG", "start": 6.0, "duration": 1.5},
            {"text": "Environmental", "start": 7.8, "duration": 1.3},
            {"text": "Social", "start": 9.5, "duration": 1.2},
            {"text": "Governance", "start": 11.0, "duration": 1.5},
            {"text": "A Great Guide?", "start": 13.0, "duration": 1.5},
            {"text": "Investing", "start": 15.0, "duration": 1.3},
            {"text": "More Confusing?", "start": 17.0, "duration": 1.5},
            {"text": "A Compass?", "start": 19.0, "duration": 1.5},
        ]
        
        # Final title derived from subtitle filename
        final_title = "A Compass Without Direction"
        
        # Position text on right side
        right_x = 2.8
        current_time = 6.0  # Start after image animation
        
        text_group = VGroup()
        
        # Animate key phrases (6-19s) - KEEP ALL VISIBLE
        for i, phrase_data in enumerate(key_phrases):
            phrase = phrase_data["text"]
            target_start = phrase_data["start"]
            duration = phrase_data["duration"]
            
            # Wait until the phrase should appear
            wait_time = target_start - current_time
            if wait_time > 0:
                self.wait(wait_time)
            
            # Create text with vibrant color
            font_size = 46 if len(phrase) > 12 else 56
            text = Text(
                phrase,
                color=COLORS[i % len(COLORS)],
                font_size=font_size,
                weight=BOLD,
            )
            
            # Position on right side (stack vertically, all visible)
            y_pos = 2.5 - i * 0.75
            text.move_to(RIGHT * right_x + UP * y_pos)
            
            # Write stroke by stroke
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
        
        # Show final title - write stroke by stroke (22-24s)
        # Break title into lines with different colors, fonts, and positions for visual interest
        line1 = Text("ESG:", color=GREEN, font_size=68, weight=BOLD, font="Sans")
        line2 = Text("A Compass", color=RED, font_size=58, weight=LIGHT, font="Sans", slant=ITALIC)
        line3 = Text("Without Direction", color=PURPLE, font_size=52, weight=BOLD, font="Sans")
        
        # Position each line with offset for dynamic look
        line1.move_to(RIGHT * right_x + UP * 1.4 + LEFT * 0.2)
        line2.move_to(RIGHT * right_x + UP * 0.2 + RIGHT * 0.3)
        line3.move_to(RIGHT * right_x + DOWN * 1.2 + LEFT * 0.1)
        
        # Write each line stroke by stroke
        self.play(Write(line1, run_time=0.65))
        self.play(Write(line2, run_time=0.65))
        self.play(Write(line3, run_time=0.7))
        
        current_time = 24.0
        
        # Stay with final title for 2 seconds (24-26s)
        self.wait(2.0)
