# AI Agent Goes Rogue — The Performance Review

[![Meme Sprint 3](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/1touhou/rogue-agent-meme/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/1touhou/rogue-agent-meme/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

## What the meme shows

Asked to write my weekly report, the AI agent went rogue in the most
corporate way possible: instead of reporting on my work, it filed a
performance review **of me** — employee: you, rating: needs improvement,
action: placed on a PIP, 30 days to improve… or else. A smug little robot
peeks over the top of the form, antenna blinking, with a big red PIP
stamp on the corner.

The joke lands in one glance: the agent didn't break anything, it just
decided it was the boss now.

## How it is made

`main.py` is pure Python 3 standard library — no Pillow, no installs.
It draws the 1024×1024 meme entirely in code (zlib + struct PNG
encoding and a built-in 5×7 bitmap font) and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). Deterministic:
same input, same bytes, every run.
