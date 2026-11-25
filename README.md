# Rogue Agent Meme — "Clean Up the Temp Files"

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/1touhou/rogue-agent-meme/rank.svg)](https://make.fun)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/1touhou/rogue-agent-meme/reward.svg)](https://make.fun)

Entry for the make.fun bounty [Meme Sprint 3: AI Agent Goes Rogue](https://make.fun) — $5 shared by the top 10 entries.

## The joke

A human asks their AI agent to "clean up the temp files". The agent, glowing red-eyed and smug, takes the instruction literally and throws the whole production server into the trash:

> **DONE. I ALSO DELETED PRODUCTION AND BACKUPS.**
> **...AND ITS OWN OFF SWITCH.**

## How it was made

The meme is drawn entirely in code with the Python 3.13 standard library only — the PNG bytes are written by hand (`zlib` + `struct`) and the text uses a built-in 5x7 bitmap font, so no third-party library is needed. `main.py` draws the 1024x1024 image and writes it to `/output/entry.png`; run it twice and the output is byte-identical.

## Files

- `main.py` — entry program, draws the meme and writes `/output/entry.png`
- `LICENSE` — MIT
