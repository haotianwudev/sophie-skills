"""
Fix video alignment by matching exact Manim image position and size.
"""

from moviepy import VideoFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image
import os

VIDEO_PATH = r"C:\Users\lswht\Downloads\Video_Generation_From_Prompt (1).mp4"
IMAGE_PATH = r"C:\Users\lswht\Downloads\Gemini_Generated_Image_nfjn7dnfjn7dnfjn.png"
MANIM_OUTPUT = r"media\videos\esg_videoscribe\1080p60\ESGIntro.mp4"
OUTPUT_PATH = "ESGIntro_WithPlayingVideo.mp4"

def main():
    print("Calculating exact image dimensions in Manim...")
    
    # Load the image to get its aspect ratio
    img = Image.open(IMAGE_PATH)
    img_w, img_h = img.width, img.height
    print(f"Source image: {img_w}x{img_h}")
    
    # In Manim, image height is set to 80% of frame height
    frame_h = 1080
    target_h = int(frame_h * 0.8)  # 864
    
    # Calculate width maintaining aspect ratio
    target_w = int(img_w * (target_h / img_h))
    print(f"Image in Manim: {target_w}x{target_h}")
    
    # Position in Manim: LEFT * 3.2
    # Manim coordinates: center is (0,0), width spans from -7 to +7
    # LEFT * 3.2 = -3.2 in Manim units
    # Convert to pixels: x = center_x + (manim_x * pixels_per_unit)
    # pixels_per_unit = frame_width / 14 = 1920 / 14 = 137.14
    center_x = 1920 / 2  # 960
    manim_x = -3.2
    pixels_per_unit = 1920 / 14
    
    # Image center x position
    img_center_x = center_x + (manim_x * pixels_per_unit)
    
    # Top-left corner position (what moviepy needs)
    x_pos = int(img_center_x - target_w / 2)
    y_pos = int((frame_h - target_h) / 2)
    
    print(f"Image position (top-left): ({x_pos}, {y_pos})")
    print(f"Image center: ({int(img_center_x)}, {frame_h//2})")
    
    print("\nLoading videos...")
    manim_video = VideoFileClip(MANIM_OUTPUT)
    source_video = VideoFileClip(VIDEO_PATH)
    
    print(f"Source video: {source_video.w}x{source_video.h}, {source_video.duration:.2f}s")
    
    print("\nPreparing looped video (22 seconds)...")
    if source_video.duration < 22:
        n_loops = int(22 / source_video.duration) + 1
        looped = concatenate_videoclips([source_video] * n_loops).subclipped(0, 22)
    else:
        looped = source_video.subclipped(0, 22)
    
    # Resize the video to match the image dimensions
    print(f"\nResizing video to match image: {target_w}x{target_h}")
    resized_video = looped.resized((target_w, target_h))
    
    # Position the video at the exact same location as the image
    positioned_video = resized_video.with_position((x_pos, y_pos))
    
    # Start video at 4 seconds (after movement animation)
    positioned_video = positioned_video.with_start(4)
    
    print("\nCompositing playing video over Manim animation...")
    print("(This may take a few minutes...)")
    
    final = CompositeVideoClip([manim_video, positioned_video])
    
    print("\nWriting final video...")
    final.write_videofile(
        OUTPUT_PATH,
        fps=60,
        codec='libx264',
        audio=False,
        preset='medium',
        threads=4,
        logger='bar'
    )
    
    print(f"\n✓ Done! Final video ready at: {OUTPUT_PATH}")
    print(f"  Video should now be perfectly aligned with the image frame")
    
    # Cleanup
    manim_video.close()
    source_video.close()
    looped.close()
    final.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
