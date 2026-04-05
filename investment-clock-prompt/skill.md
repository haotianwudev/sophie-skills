---
name: investment-clock-prompt
description: Generate a Gemini Deep Research prompt for the Investment Clock weekly analysis. Runs the prompt generator script and prints the result for copy-pasting into Gemini.
argument-hint: (no arguments)
allowed-tools: [Bash]
---

# Investment Clock Prompt

Generate a Gemini Deep Research prompt from the latest Investment Clock data.

## Instructions for Claude

Run the prompt generator script:

```bash
cd F:/workspace/sophie-pipeline && poetry run python investment-clock/generate_prompt.py
```

The script will:
1. Query `investment_clock_data` for the latest EWM Z-scores, all 9 weighted signals, and 6-month trajectory
2. Query `investment_clock_evaluation` for the last evaluation (for continuity context)
3. Save the prompt to `investment-clock/prompts/YYYY-MM-DD.md`
4. Print the full prompt

After running, tell the user:
- The file path where the prompt was saved
- The detected phase and Z-scores
- To copy the prompt into Gemini Deep Research, then run `/investment-clock-analyze` with the result
