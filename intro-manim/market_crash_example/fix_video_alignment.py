"""
Composite Video_Generation_From_Prompt.mp4 over the Manim intro,
replacing the static image after the 4s movement animation.
"""

from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image
import os

VIDEO_PATH  = r"F:\Video\market crash\Video_Generation_From_Prompt.mp4"
IMAGE_PATH  = r"F:\Video\market crash\Gemini_Generated_Image_kwd1p3kwd1p3kwd1.png"
MANIM_OUTPUT = r"C:\Users\lswht\Downloads\media\videos\spotting_intro_manim\1080p60\VideoScribeIntro.mp4"
OUTPUT_PATH = r"C:\Users\lswht\Downloads\SpottingMarketCrash_WithVideo.mp4"

PLAY_START  = 4          # seconds into intro when video starts
TOTAL_INTRO = 21         # total intro duration
PLAY_DURATION = TOTAL_INTRO - PLAY_START   # 17 seconds


def main():
    print("Calculating image position in Manim frame...")
    img = Image.open(IMAGE_PATH)
    img_w, img_h = img.size
    print(f"  Source image: {img_w}x{img_h}")

    frame_h = 1080
    frame_w = 1920
    target_h = int(frame_h * 0.8)                  # 864
    target_w = int(img_w * (target_h / img_h))
    print(f"  Image in Manim: {target_w}x{target_h}")

    # LEFT * 3.2 in Manim coords → pixel x
    pixels_per_unit = frame_w / 14               # 137.14
    img_center_x    = frame_w / 2 + (-3.2 * pixels_per_unit)
    x_pos = int(img_center_x - target_w / 2)
    y_pos = int((frame_h - target_h) / 2)
    print(f"  Position (top-left): ({x_pos}, {y_pos})")

    print("\nLoading videos...")
    manim_video  = VideoFileClip(MANIM_OUTPUT)
    source_video = VideoFileClip(VIDEO_PATH)
    print(f"  Manim intro:  {manim_video.w}x{manim_video.h}, {manim_video.duration:.2f}s")
    print(f"  Source video: {source_video.w}x{source_video.h}, {source_video.duration:.2f}s")

    print(f"\nPreparing {PLAY_DURATION}s of source video...")
    if source_video.duration < PLAY_DURATION:
        n_loops = int(PLAY_DURATION / source_video.duration) + 1
        looped = concatenate_videoclips([source_video] * n_loops).subclipped(0, PLAY_DURATION)
    else:
        looped = source_video.subclipped(0, PLAY_DURATION)

    print(f"Resizing to {target_w}x{target_h}...")
    resized   = looped.resized((target_w, target_h))
    positioned = resized.with_position((x_pos, y_pos)).with_start(PLAY_START)

    print("\nCompositing...")
    final = CompositeVideoClip([manim_video, positioned])

    print(f"Writing → {OUTPUT_PATH}")
    final.write_videofile(
        OUTPUT_PATH,
        fps=60,
        codec="libx264",
        audio=False,
        preset="medium",
        threads=4,
        logger="bar",
    )

    manim_video.close()
    source_video.close()
    looped.close()
    final.close()
    print(f"\nDone! → {OUTPUT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
