---
name: subtitle
description: Generate English and Chinese SRT subtitles from a video file using faster-whisper (large-v3, CUDA) and Google Translate. Also generates bilingual SRT and social media copy for YouTube, 小红书, and Bilibili.
argument-hint: <video_file_path>
allowed-tools: [Bash, Write, Read, Glob]
---

# Subtitle Generation Skill

Generate subtitle files and social media copy from a video.

**Outputs (all saved alongside the video file):**
- `video.en.srt` — English subtitles (1 line, max 42 chars)
- `video.zh.srt` — Chinese subtitles
- `video.bilingual.srt` — English + Chinese stacked
- `video.social.txt` — YouTube + 小红书 + Bilibili copy

## Arguments

The user invoked this with: $ARGUMENTS

---

## Step 1 — Resolve video path

If $ARGUMENTS is provided, use it as the video path. If not, ask the user for the video file path.

Common locations to check: `$HOME/Downloads/`, current directory.

---

## Step 2 — Check dependencies

```bash
python -c "import faster_whisper, deep_translator" 2>&1
where ffmpeg 2>/dev/null || ffmpeg -version 2>/dev/null
```

If any are missing:
```bash
pip install faster-whisper deep-translator
winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
```

---

## Step 3 — Run subtitle generation in background

```bash
cd "<video_directory>" && PYTHONUTF8=1 python "C:/Users/lswht/subtitle_gen.py" "<video_path>" 2>&1
```

Wait for completion. The script outputs:
- `<base>.en.srt`
- `<base>.zh.srt`
- `<base>.bilingual.srt`

---

## Step 4 — Generate social media copy from the SRT files

After subtitle generation completes, read the `.en.srt` file. Extract all subtitle text lines (skip index numbers and timestamps). Use the full transcript content to generate the social copy — do NOT use the video filename as the title.

### What to generate:

**YouTube:**
- `TITLE` — English, descriptive, concise. No "Sophie Daddy's Channel" suffix.
- `DESCRIPTION` — 3-5 sentences summarizing the video content only. No calls to action, no subscribe prompts, no disclaimer, no links.
- `HASHTAGS` — 8-12 relevant English hashtags

**中文平台 (one section, used for both 小红书 and Bilibili):**
- `TITLE` — Short, simple Chinese title (8-15 characters), derived from transcript content. Concise and natural, no brackets or fancy formatting.
- 3-5 tags total, always ending with `#SophieDaddy`. No generic tags like #投资理财 #金融知识 #深度研究.
- Tag selection rules:
  - Include from preset list **only if content fits**: `#美股` `#量化金融` `#期权策略`
  - Generate 2-3 **content-specific tags** derived from the actual transcript (e.g. for ESG video: `#ESG投资` `#可持续投资`; for options video: `#期权交易` `#波动率`; for macro video: `#宏观经济` `#美联储`)
  - Tags should be what a Chinese viewer would actually search for on 小红书/Bilibili

### Output format for `video.social.txt`:

```
============================================================
YOUTUBE
============================================================

TITLE:
[title]

DESCRIPTION:
[description]

HASHTAGS:
[hashtags]

============================================================
中文平台 (小红书 / Bilibili)
============================================================

[Chinese title]

#[topic tag] #[topic tag if applicable] #SophieDaddy
```

Save to `<base>.social.txt` (UTF-8 encoding).

---

## Notes
- **Always use `PYTHONUTF8=1`** prefix on Windows to avoid GBK encoding errors
- CUDA fallback: automatically switches to CPU int8 if CUDA Toolkit not installed
- GPU: RTX 4070 Ti + large-v3 float16 ≈ 1-2 min for a 10-min video
- large-v3 model (~3GB) downloaded on first run, cached at `~/.cache/huggingface/`
- To permanently fix GPU: `winget install --id Nvidia.CUDA -e`
