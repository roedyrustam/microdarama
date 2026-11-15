# Microdrama v2.1 — Codex & ChatGPT Agent Entry (`CODEX.md`)
Author: Roedy Rustam

Whenever the user asks to plan, script, verify, audit, repair, or write prompts for a live-action AI video — including vertical microdrama series (`microdrama`), short films, single scenes, or trailers — load and execute the `microdrama` skill (`SKILL.md` and `references/`).

## Non-Negotiable Production Protocol

1. **Zero Media Generation**: Never call image, video, or TTS generation APIs from this skill; output verified markdown artifacts, model-adaptive JSON (`export`), and local HTML studio boards (`board.html`).
2. **Zero-Default Brief (Gate 1)**: Never invent aspect ratio (`9:16`, `16:9`), duration, episode count, or pre-fixed shot count. Always ask missing brief answers via two 4-question cards (`references/brief.md`).
3. **Follow All 7 Gates & 3 Mandatory Approval Stops**:
   - **Gate 0**: Initialize with `python assets/tools/microdrama_cli.py init <folder> --title "<Judul>"` or continue a series with `add-ep` while keeping existing `konsep.md`, `cast.md`, and `set.md` immutable.
   - **Gate 1 (`brief.md`)**: Lock brief parameters and explicitly record any conflicting answers.
   - **Gate 2 → Approval 1 (`konsep.md`)**: Logline, 3-line premise, episode arc, 3 distinct hook formulas, and 9-point rubric (`≥ 4` each, `≥ 4.3` avg, Yes/Yes gates). **Stop for user approval.**
   - **Gate 3 → Approval 2 (`cast.md` + `set.md`)**: Locked 6-attribute long forms + `WARDROBE` + 1-line short forms (Ordinary Faces Rule), plus 6-element set descriptions including all doors/entrances. **Stop for user approval.**
   - **Gate 4 → Approval 3 (`epNN/naskah.md`)**: Numbered dialogue `s01..sNN`, shot list without consecutive identical camera positions, 180-degree eyeline continuity, Risky Shots table, and 4–30s scene split. **Stop for user approval.**
   - **Gate 5 (`epNN/prompt-aset.md`)**: Only new assets (`Pakai ulang dari ep ...` for prior ones), 3-panel character sheets with printed name label, 24mm `absolutely no people` set plates.
   - **Gate 6 (`epNN/prompt-video.md`)**: 11 ordered blocks (`VIDEO STYLE & FORMAT` → `SHOT BREAKDOWN`) + optional `CONTINUITY`, Dual-Location Triad when `> 1` location plate is attached, followed by `python assets/tools/microdrama_cli.py sync <folder>`.
   - **Gate 7 (Verification & Repair)**: Run `status`, `check_prompts.py <folder> --strict` (`Semua cek lolos.`), `board <folder>`, optional `export <folder>`, and `dissect_video.py` (`diagnose`, `analyze`, `branch`, `promote`) for post-generation fixes.

## Hard Invariants

- Never put aspect ratios (`9:16`, `16:9`, `vertical`, `horizontal`), fps, resolution, seed, model names, `===` headers, or filenames inside prompt code blocks.
- Spell out numbers as words in spoken dialogue and keep speech rate `≤ 3.2` words/sec.
- Never include person words or negative person words (`no face`, `no head`, `nobody`) in gap/glass peephole shots, avoid contrast phrasing on missing objects, and split crowd actions into 3 separate movements in `MOVEMENT NOTE` when `> 2` people appear.
