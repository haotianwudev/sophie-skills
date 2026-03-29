"""
Generate English + Chinese SRT subtitles from a video file.
Uses faster-whisper (large-v3, CUDA) for transcription and
deep-translator (Google) for Chinese translation.

Subtitles are re-segmented using word-level timestamps for readability:
  - Max 42 characters per line
  - Max 1 line per block
  - Max 7 seconds per block
  - Split at sentence boundaries

Usage:
    python subtitle_gen.py <video_file>
"""

import sys
import os
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator

MAX_CHARS = 42
MAX_LINES = 1
MAX_DURATION = 7.0


def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _load_model(device: str, compute_type: str):
    print(f"Loading faster-whisper large-v3 on {device.upper()} ({compute_type})...")
    return WhisperModel("large-v3", device=device, compute_type=compute_type)


def _collect_words(model, video_path: str):
    segments, info = model.transcribe(video_path, language="en", beam_size=5, word_timestamps=True)
    print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
    words = []
    for seg in segments:
        for word in seg.words:
            words.append({"start": word.start, "end": word.end, "word": word.word})
    return words


def transcribe(video_path: str):
    print(f"Transcribing: {video_path}")
    try:
        model = _load_model("cuda", "float16")
        return _collect_words(model, video_path)
    except RuntimeError as e:
        if "cublas" in str(e).lower() or "cuda" in str(e).lower():
            print(f"CUDA unavailable ({e})\nFalling back to CPU int8...")
            model = _load_model("cpu", "int8")
            return _collect_words(model, video_path)
        raise


def resegment(words: list) -> list:
    segments = []
    current_words = []
    current_lines = 1
    current_line_len = 0

    def flush():
        if not current_words:
            return
        text = "".join(w["word"] for w in current_words).strip()
        segments.append({
            "start": current_words[0]["start"],
            "end": current_words[-1]["end"],
            "text": text
        })

    for word in words:
        token = word["word"]
        token_len = len(token)
        duration = (word["end"] - current_words[0]["start"]) if current_words else 0

        new_line_len = current_line_len + token_len
        needs_new_line = new_line_len > MAX_CHARS
        exceeds_lines = needs_new_line and current_lines >= MAX_LINES
        exceeds_duration = duration > MAX_DURATION

        if exceeds_lines or exceeds_duration:
            flush()
            current_words = [word]
            current_lines = 1
            current_line_len = token_len
        elif needs_new_line:
            current_words.append(word)
            current_lines += 1
            current_line_len = token_len
        else:
            current_words.append(word)
            current_line_len = new_line_len

        if token.rstrip()[-1:] in {'.', '!', '?'} and current_words:
            flush()
            current_words = []
            current_lines = 1
            current_line_len = 0

    flush()
    print(f"  Re-segmented into {len(segments)} subtitle blocks")
    return segments


def translate_to_chinese(segments: list) -> list:
    print("\nTranslating to Chinese...")
    translator = GoogleTranslator(source="en", target="zh-CN")
    translated = []
    for i, seg in enumerate(segments):
        try:
            zh_text = translator.translate(seg["text"])
        except Exception as e:
            print(f"  Warning: translation failed for segment {i+1}: {e}")
            zh_text = seg["text"]
        translated.append({**seg, "text": zh_text})
        print(f"  [{i+1}/{len(segments)}] {zh_text}")
    return translated


def write_srt(segments: list, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
    print(f"Saved: {output_path}")


def write_bilingual_srt(en_segments: list, zh_segments: list, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        for i, (en, zh) in enumerate(zip(en_segments, zh_segments), 1):
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(en['start'])} --> {format_timestamp(en['end'])}\n")
            f.write(f"{en['text']}\n{zh['text']}\n\n")
    print(f"Saved: {output_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python subtitle_gen.py <video_file>")
        sys.exit(1)

    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Error: file not found: {video_path}")
        sys.exit(1)

    base = os.path.splitext(video_path)[0]
    en_srt = base + ".en.srt"
    zh_srt = base + ".zh.srt"
    bilingual_srt = base + ".bilingual.srt"

    words = transcribe(video_path)
    segments = resegment(words)

    write_srt(segments, en_srt)

    zh_segments = translate_to_chinese(segments)
    write_srt(zh_segments, zh_srt)

    write_bilingual_srt(segments, zh_segments, bilingual_srt)

    print(f"\nDone!")
    print(f"  English:   {en_srt}")
    print(f"  Chinese:   {zh_srt}")
    print(f"  Bilingual: {bilingual_srt}")


if __name__ == "__main__":
    main()
