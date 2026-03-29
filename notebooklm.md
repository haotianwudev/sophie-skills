---
name: notebooklm
description: Interact with Google NotebookLM via notebooklm-py. Use for creating notebooks, adding sources, asking questions, generating audio/content, and research workflows.
argument-hint: [action] [args...]
allowed-tools: [Bash, Read, Write, Glob]
---

# NotebookLM Skill

Interact with Google NotebookLM using the `notebooklm` CLI (notebooklm-py).

## Arguments

The user invoked this with: $ARGUMENTS

## Authentication Check

Before any operation, verify the user is authenticated:
```bash
PYTHONUTF8=1 notebooklm status
```
If this fails with an auth error, prompt the user to run:
```bash
notebooklm login
```
This opens a browser for Google login and saves `~/.notebooklm/storage_state.json`.

> **Windows note:** Always prefix all `notebooklm` commands with `PYTHONUTF8=1` to avoid GBK encoding errors from emoji characters in the output.

---

## Notebook Selection Rules

**IMPORTANT — always follow this order:**

1. **Search first:** Run `PYTHONUTF8=1 notebooklm list --json` to get the full list with complete (non-truncated) IDs.
2. **Match by title:** If a notebook matching the user's topic is found, use it — do NOT create a new one.
3. **Ask before creating:** If no match is found, ask the user: "No existing notebook found for '[title]' — should I create one?"
4. **Set active notebook** using the full ID from `--json` output (never use truncated IDs from plain `list`):
```bash
PYTHONUTF8=1 notebooklm list --json
# Extract full ID, then:
PYTHONUTF8=1 notebooklm use <full-notebook-id>
```

---

## Operations — Parse $ARGUMENTS and execute the matching action:

### List notebooks
**Trigger:** "list", "show notebooks", "my notebooks"
```bash
PYTHONUTF8=1 notebooklm list --json
```

### Create a notebook
**Trigger:** "create", "new notebook", "make notebook"

Always search for an existing notebook first. Only create if user confirms.
```bash
PYTHONUTF8=1 notebooklm create "<title>"
```

### Set active notebook
**Trigger:** "use", "switch to", "select notebook"

Always get the full ID from `--json` output first:
```bash
PYTHONUTF8=1 notebooklm list --json
PYTHONUTF8=1 notebooklm use <full-notebook-id>
```

### Add a source
**Trigger:** "add source", "add url", "add file", "add text"
```bash
# URL (web page or YouTube)
PYTHONUTF8=1 notebooklm source add <url>

# Local file
PYTHONUTF8=1 notebooklm source add <file-path>

# Plain text (inline, no --text flag)
PYTHONUTF8=1 notebooklm source add "<content>" --title "<title>"
```

### List sources
**Trigger:** "list sources", "show sources", "what sources"
```bash
PYTHONUTF8=1 notebooklm source list --json
```

### Ask a question
**Trigger:** "ask", "query", "question"
```bash
PYTHONUTF8=1 notebooklm ask "<question>"
```

### Generate audio overview
**Trigger:** "generate audio", "podcast", "audio overview", "deep dive"
```bash
# Formats: DEEP_DIVE (default), BRIEF, CRITIQUE, DEBATE
# Length: SHORT, DEFAULT, LONG
PYTHONUTF8=1 notebooklm generate audio --format DEEP_DIVE --length DEFAULT --no-wait
```
Then poll until complete:
```bash
PYTHONUTF8=1 notebooklm artifact list --json
```

### Generate video
**Trigger:** "generate video", "make video", "create video"

Always use these fixed defaults — never deviate:
- Format: `explainer`
- Style: `watercolor`
- Description: `The narration should be female voice. The video should begin with the line, 'Welcome to Sophie Daddy's Channel'. The video should be around 10 minutes.`

**IMPORTANT:** Never use `--wait` — video generation takes 10–20 minutes and will time out the CLI. Instead:

**Step 1 — Submit (returns instantly):**
```bash
PYTHONUTF8=1 notebooklm generate video "The narration should be female voice. The video should begin with the line, 'Welcome to Sophie Daddy's Channel'. The video should be around 10 minutes." --format explainer --style watercolor --json
```

**Step 2 — Poll until completed (run in background):**
```bash
for i in $(seq 1 40); do
  status=$(PYTHONUTF8=1 notebooklm artifact list --json 2>/dev/null | python -c "
import sys, json
data = json.load(sys.stdin)
latest = sorted(data['artifacts'], key=lambda x: x['created_at'], reverse=True)
latest_video = next((a for a in latest if a['type_id'] == 'video'), None)
if latest_video:
    print(latest_video['status'] + '|' + latest_video['id'] + '|' + latest_video['title'])
")
  echo "$(date '+%H:%M:%S') - $status"
  artifact_status=$(echo "$status" | cut -d'|' -f1)
  if [ "$artifact_status" = "completed" ] || [ "$artifact_status" = "failed" ]; then
    break
  fi
  sleep 30
done
```

**Step 3 — Download when completed:**
```bash
cd "$HOME/Downloads" && PYTHONUTF8=1 notebooklm download video -a <artifact-id>
```

### Generate study content
**Trigger:** "quiz", "flashcards", "study guide", "briefing"
```bash
PYTHONUTF8=1 notebooklm generate quiz --difficulty MEDIUM --quantity STANDARD
PYTHONUTF8=1 notebooklm generate flashcards
PYTHONUTF8=1 notebooklm generate study-guide
PYTHONUTF8=1 notebooklm generate report --format "Briefing Doc"
```

### Download generated artifact
**Trigger:** "download", "save audio", "export"
```bash
# Video
cd "$HOME/Downloads" && PYTHONUTF8=1 notebooklm download video -a <artifact-id>

# Audio
cd "$HOME/Downloads" && PYTHONUTF8=1 notebooklm download audio -a <artifact-id>

# Check available artifacts first
PYTHONUTF8=1 notebooklm artifact list --json
```

### Research (web or Drive)
**Trigger:** "research", "find sources on", "research topic"
```bash
PYTHONUTF8=1 notebooklm research start "<query>" --source web --mode deep
PYTHONUTF8=1 notebooklm research status
```

### Show current context
**Trigger:** "status", "current notebook", "which notebook"
```bash
PYTHONUTF8=1 notebooklm status
```

---

## Workflow Examples

**Video generation for existing notebook:**
1. `PYTHONUTF8=1 notebooklm list --json` → find full notebook ID by title
2. `PYTHONUTF8=1 notebooklm use <full-id>`
3. Submit video generation (no `--wait`)
4. Poll `artifact list --json` every 30s in background
5. Download when status = `completed`

**Full new-notebook workflow (only after user confirms):**
1. `PYTHONUTF8=1 notebooklm create "My Research Topic"`
2. `PYTHONUTF8=1 notebooklm use <full-id>`
3. `PYTHONUTF8=1 notebooklm source add <url-or-file>`
4. `PYTHONUTF8=1 notebooklm ask "Summarize the key findings"`
5. Generate content (audio/video) without `--wait`, then poll

**Quick Q&A on existing notebook:**
1. `PYTHONUTF8=1 notebooklm list --json` → find notebook id
2. `PYTHONUTF8=1 notebooklm use <full-id>`
3. `PYTHONUTF8=1 notebooklm ask "<question>"`

---

## Notes
- **Always use `PYTHONUTF8=1`** prefix on Windows to avoid GBK encoding errors
- **Always use `--json`** when you need IDs — plain list truncates them and causes RPC errors
- **Never use `--wait`** for video/audio generation — poll `artifact list --json` instead
- Auth state stored at `~/.notebooklm/storage_state.json`
- Uses undocumented Google APIs — best for personal/prototyping use
- Run `notebooklm --help` or `notebooklm <command> --help` for full options
