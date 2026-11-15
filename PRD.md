# Product Requirements Document (PRD) — Microdrama v2.1

## 1. Executive Summary
**Microdrama** is an Agent Skill, specialist subagent (`microdrama-director`), and deterministic Python 3 production toolkit for planning live-action AI video (vertical microdrama series, short films, and single scenes/trailers) and generating model-agnostic image and video prompts. Microdrama **never calls media-generation APIs**; it produces structured, cross-verified production text artifacts, model-adaptive JSON export bundles, and an interactive local HTML production studio (`board.html`) that eliminate the core failure modes of AI video generation: identity drift, chorus-line crowd synchronization, unreadable on-screen text, spatial teleportation across cuts, trailer-montage pacing, and wasted generation credits.

**Microdrama v2.1** expands the v2.0 foundation (`25-point static & semantic linter`, `microdrama_cli.py`, and `dissect_video.py`) with a dedicated `microdrama-director` subagent (`agents/microdrama-director.md`), a 7-Gate readiness inspector (`status`), a model-adaptive JSON exporter (`export`), and Production Studio v2.1 (`board.html` with WPS pacing, negative-prompt copy buttons, `@Element1..N` slot adaptation, and interactive 24-symptom diagnosis search).

---

## 2. Production Pipeline (7 Gates & 3 Mandatory Approvals)

| Gate | Name | Primary Inputs | Mandatory Output Artifacts | Human Approval Gate |
|---|---|---|---|---|
| **0** | Workspace Setup | Project path, new vs. continuation flag | Project folder copied from `assets/template/` or existing `konsep.md`/`cast.md`/`set.md` loaded | Path confirmation |
| **1** | Brief Lock | Two 4-question cards (Topic, Format, Ratio, Language, Duration, Episodes, Look) | `brief.md` | Implicit in questionnaire; conflict resolution confirmed if contradictory |
| **2** | Concept & Arc | `brief.md`, `references/konsep.md`, `references/copywriting.md` | `konsep.md` (Logline, 3-line Premise, Arc table, 3 distinct Hook formulas, Rubric ≥ 4.3 avg) | **Approval 1 (Mandatory Stop)** |
| **3** | Cast, Set & Prop Bible | Approved `konsep.md`, `references/cast.md` | `cast.md` (6-attribute long form + short form + body tone), `set.md` (6-element set + plated/text props) | **Approval 2 (Mandatory Stop)** |
| **4** | Script & Shot List | `konsep.md`, `cast.md`, `set.md`, `references/konsep.md`, `references/copywriting.md` | `epNN/naskah.md` (Dialogue, Shot list, Risky Shots table, Scene split 4–30s) | **Approval 3 (Mandatory Stop)** |
| **5** | Asset Prompts | `cast.md`, `set.md`, `epNN/naskah.md`, `references/prompt-aset.md` | `epNN/prompt-aset.md` (3-panel sheets with printed label + wide-angle set plates + prop plates) | Handover |
| **6** | Video Prompts | `epNN/naskah.md`, `cast.md`, `set.md`, `references/prompt-video.md` | `epNN/prompt-video.md` (11 ordered blocks + optional `CONTINUITY`, 1 block per 4–30s generation) | Handover |
| **7** | Verification & Repair | All project files, optional generated MP4 clips | `check_prompts.py` pass (`Semua cek lolos.`), `board.html`, versioned repairs (`-v2.md`) | **Final Quality Gate** |

---

## 3. Non-Functional Requirements (NFR) & Budgets

| Category | Metric / Invariant | Target Budget / Constraint | Enforcement Mechanism |
|---|---|---|---|
| **Runtime Dependencies** | External PyPI packages required by tooling | **0 external packages** (Python 3.10+ stdlib only) | `check_prompts.py`, `microdrama_cli.py`, `dissect_video.py` |
| **Scene Generation Bounds** | Min / Max duration per video prompt block | **4s ≤ scene ≤ 30s** | Automated regex + sum check in `check_prompts.py` |
| **Shot Timecode Integrity** | Continuity across `SHOT 1..N` in `SHOT BREAKDOWN` | Contiguous `0..NN` with zero gaps/overlaps | Automated boundary check in `check_prompts.py` |
| **Locked Block Fidelity** | Character/Set/Prop block drift between bible and prompts | **0.0% drift** (exact normalized substring match) | `microdrama_cli.py sync` + `check_prompts.py` |
| **Token Bijection** | `[gambar_<slug>]` vs `<slug>_sheet.png`/`<slug>_plate.png` vs `Lampirkan:` | **100% 1-to-1 bijection** | `check_prompts.py` token-attachment matcher |
| **Speech Pacing Budget** | Spoken words per second inside a shot | **≤ 3.2 words/sec**; raw digits = **0** | Automated acoustic pacing & digit check |
| **Camera Position Delta** | Consecutive shots from identical physical positions | **0 consecutive collisions** | `naskah.md` + `SHOT BREAKDOWN` collision detector |
| **Script Rubric Quality** | 9-point `copywriting.md` rubric | All rows **≥ 4**, average **≥ 4.3**, Yes/Yes on gates | `konsep.md` rubric parser in `check_prompts.py` |
| **Performance** | `check_prompts.py` execution latency on 6-episode project | **< 200 ms** local execution | Single-pass file parsing |

---

## 4. CLI & Tooling Contracts

### 4.1 `assets/tools/check_prompts.py`
```text
python assets/tools/check_prompts.py <project_folder> [--json] [--strict]
```
- **Exit 0**: All 25 static & semantic checks pass (`Semua cek lolos.`).
- **Exit 1**: One or more blocking errors found; lists exact file, scene/section, and violation.
- **Exit 2**: Invalid CLI arguments or missing mandatory project files.
- `--json`: Outputs machine-readable JSON `{status, summary, errors, warnings}`.
- `--strict`: Elevates soft warnings (e.g., speech rate > 3.2 wps, overly long sentences > 14 words) to exit code 1.

### 4.2 `assets/tools/microdrama_cli.py`
- `init <folder> [--title "<Title>"]`: Scaffolds `brief.md`, `konsep.md`, `cast.md`, `set.md` from `assets/template/`.
- `add-ep <folder> <ep_number> [--title "<Ep Title>"]`: Scaffolds `epNN/naskah.md`, `epNN/prompt-aset.md`, `epNN/prompt-video.md` and auto-populates `Pakai ulang dari ep ...` from prior episodes.
- `status <folder> [--json] [--strict]`: Inspects Gate 0–7 completion (`PASS` / `PENDING` / `ERROR`) and identifies the next required gate without modifying files.
- `sync <folder>`: Propagates locked long/short blocks from `cast.md` and `set.md` into `epNN/prompt-aset.md` and `epNN/prompt-video.md`, and synchronizes `Lampirkan:` filenames from `[gambar_x]` tokens.
- `board <folder> [--out <path>]`: Builds standalone dark-mode `board.html` (Studio v2.1) with live `check_prompts` diagnostics, per-shot `WPS` pacing column, 1-based `@Element1..N` slot pills, one-click Copy buttons (Video, `@Element` mode, Asset, Negative `Avoid`), and interactive 24-symptom search powered by `dissect_video.SYMPTOMS`.
- `export <folder> [--out <path>] [--stdout]`: Generates model-adaptive JSON (`microdrama.export.v1`) containing positive/negative asset splits, `@Element1..N` slot mappings, and per-shot `words`/`wps` telemetry.
- `check <folder> [--json] [--strict]`: Wrapper invoking the 25-point verifier.
- `sync-plugin [--check] [--global]`: Synchronizes `SKILL.md`, `assets/`, `references/`, `agents/`, and plugin metadata to `skills/microdrama/` and `~/.gemini/config/plugins/microdrama/` with SHA-256 parity verification.

### 4.3 `assets/tools/dissect_video.py`
- `diagnose "<symptom query>"`: Queries the 24-entry symptom matrix and prints root cause + 1–2 sentence surgical prompt fix.
- `analyze <video_file> --prompt <prompt-video.md> [--scene <N>] [--out-dir <dir>]`: Runs `ffmpeg` cut detection (`select='gt(scene,0.25)',showinfo`) & contact sheet (`fps=2,scale=240:-1,tile=7x5`) if `ffmpeg` is installed, compares cuts against expected `SHOT (a-bs)` timecodes, or prints exact copy-paste `ffmpeg`/`whisper` commands if `ffmpeg` is unavailable.
- `branch <prompt-video.md> [--note "<reason>"]`: Copies `prompt-video.md` to `prompt-video-v2.md` (or next sequential `vN`) with a version header note outside the prompt blocks.
- `promote <prompt-video-vN.md>`: Safely archives current `prompt-video.md` as backup and promotes `prompt-video-vN.md` to canonical `prompt-video.md`.

---

## 5. Non-Goals & Strict Boundaries
1. **No Direct Media Generation**: Never execute image/video/TTS generation APIs inside this skill.
2. **No Hardcoded Defaults**: Never assume `9:16`, `30s`, or episode counts in `brief.md`.
3. **No Tool-Specific Prompt Syntax**: Prompts remain 100% tool-agnostic English (dialogue in chosen language); tool-specific UI settings live strictly in `references/model-profiles.md`.
4. **No Subtitle / On-Screen Text Dependency**: Critical story beats must work purely through visuals and spoken/ambient sound.
