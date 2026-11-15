# Microdrama v2.1 Rule (OpenAI Codex / ChatGPT Agents)
Author: Roedy Rustam

Trigger automatically whenever a user requests a vertical `microdrama`, short film, AI video script, shot list, character sheet prompt, set plate prompt, 11-block AI video prompt, or post-generation AI clip plot-hole repair:

1. Load `skills/microdrama/SKILL.md` (`microdrama` v2.1.0) and follow its 7 Gates + 3 Mandatory Approval Stops (`konsep.md`, `cast.md` + `set.md`, `epNN/naskah.md`).
2. Respect the Zero-Default Brief rule and all 14 Hard Rules (ratios/filenames/model names strictly outside prompt blocks, exact bible string parity enforced via `microdrama_cli.py sync`, dialogue numbers spelled as words `≤ 3.2` words/sec, peephole shots free of person/negation words).
3. Validate with `python assets/tools/check_prompts.py <folder> --strict`, inspect gates with `python assets/tools/microdrama_cli.py status <folder>`, build Studio v2.1 via `board <folder>`, package multi-model JSON via `export <folder>`, and repair generated clips with `assets/tools/dissect_video.py`.
