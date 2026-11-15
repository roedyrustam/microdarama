# Microdrama v2.1 — Modular Production Rules (AGENTS.md)
Author: Roedy Rustam

Whenever the user asks to plan, script, verify, repair, or write prompts for a live-action AI video — including vertical microdrama series, short films, single scenes, or trailers:

1. **Activate the `microdrama` Skill (`SKILL.md`) or Delegate to `microdrama-director`**:
   - Read and follow `SKILL.md` together with the gate manuals in `references/`, or delegate structured multi-gate production to `agents/microdrama-director.md`.
   - **Never generate media directly**; output verified production markdown artifacts, model-adaptive JSON bundles (`export`), and local HTML studio boards (`board.html`).
   - **Zero-Default Brief**: Never invent aspect ratio, duration, episode count, or pre-fixed shot count.

2. **Enforce the 7 Production Gates & 3 Mandatory Approval Stops**:
   - **Gate 0**: Initialize via `python assets/tools/microdrama_cli.py init <folder> --title "<Judul>"` or add an episode with `add-ep` while keeping existing `konsep.md`, `cast.md`, and `set.md` immutable.
   - **Gate 1**: Lock `brief.md` via two 4-question cards (`references/brief.md`).
   - **Gate 2 → Approval 1**: Produce `konsep.md` with logline, 3-line premise, episode arc, 3 distinct hook formulas, and 9-point rubric (`≥ 4` each, `≥ 4.3` average, Yes/Yes gates). Stop for user approval.
   - **Gate 3 → Approval 2**: Lock `cast.md` (6-attribute long form + `WARDROBE` + 1-line short form + `Nada tubuh`, Ordinary Faces Rule) and `set.md` (6 elements including all doors/entrances + plated/text-only props). Stop for user approval.
   - **Gate 4 → Approval 3**: Write `epNN/naskah.md` (numbered dialogue `s01..sNN`, shot list with no consecutive identical camera positions, 180-degree eyeline rule, Risky Shots table, and 4–30s scene split). Stop for user approval.
   - **Gate 5**: Write `epNN/prompt-aset.md` for new assets only (`Pakai ulang dari ep ...` for prior assets; 3-panel character sheets with printed name label; 24mm `absolutely no people` set plates).
   - **Gate 6**: Write `epNN/prompt-video.md` with 11 ordered blocks (`VIDEO STYLE & FORMAT` → `SHOT BREAKDOWN`) + optional `CONTINUITY`, Dual-Location Triad when >1 location plate is attached, and `microdrama_cli.py sync <folder>`.

3. **Enforce the 14 Hard Rules & Gate 7 Verification**:
   - Keep ratios (`9:16`, `16:9`, `vertical`, `horizontal`), fps, resolution, seed, model names, headers (`===`), and filenames outside prompt code blocks.
   - Spell out numbers as words in spoken dialogue, keep pacing `≤ 3.2` words/sec, forbid person/negation words in gap/glass peephole shots, avoid contrast words on missing objects, and split extras into 3 separate actions in `MOVEMENT NOTE` when `> 2` people appear.
   - Always inspect progress with `python assets/tools/microdrama_cli.py status <folder>`, verify before handover with `python assets/tools/check_prompts.py <folder> --strict` until `Semua cek lolos.`, build Studio v2.1 via `python assets/tools/microdrama_cli.py board <folder>`, and optionally package multi-model JSON via `python assets/tools/microdrama_cli.py export <folder>`.
   - Use `python assets/tools/dissect_video.py` (`diagnose`, `analyze`, `branch`, `promote`) for post-generation clip defects.
