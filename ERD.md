# Entity-Relationship & Data Integrity Architecture (`ERD.md`)

Microdrama enforces consistency across disparate AI image and video generations via **strict text-to-file token bijection** and **one-way data flow** from locked bibles (`cast.md`, `set.md`) into downstream asset and video prompts.

## 1. Entity-Relationship Diagram

```mermaid
erDiagram
    PROJECT ||--|| BRIEF : defines
    PROJECT ||--|| KONSEP : establishes
    PROJECT ||--|{ CHARACTER : locks
    PROJECT ||--|{ LOCATION : locks
    PROJECT ||--|{ PROP : locks
    PROJECT ||--|{ EPISODE : contains

    BRIEF {
        string judul_proyek
        enum format "Microdrama seri | Short movie | Scene tunggal"
        string rasio "Recorded only, NEVER in prompt"
        int durasi_detik "Target per episode/film"
        int jumlah_episode "Null if non-series"
        string bahasa_dialog "Indonesia | English"
        string look "Visual & lighting direction"
        string topik_asli "Verbatim user prompt"
    }

    KONSEP {
        string logline "1 sentence with info asymmetry"
        string premis_cerita "Line 1"
        string premis_detail_meleset "Line 2 anomaly"
        string premis_aturan_tokoh "Line 3 invariant"
        table arc "Ep | Isi | Cliffhanger"
        list hooks "3 distinct formulas"
        string hook_dipilih "User selection"
        string skor_rubrik "9 metrics >= 4, avg >= 4.3"
    }

    CHARACTER {
        string nama_kapital "RAFA, ADIT, IBU"
        string token "[gambar_slug]"
        string berkas_sheet "slug_sheet.png"
        text bentuk_panjang "6 traits + WARDROBE"
        text bentuk_pendek "1-line CHARACTERS block"
        string nada_tubuh "Human-only acting rhythm"
        string tanda_wajah_cerita "Optional exception only"
    }

    LOCATION {
        string nama_kapital "TERAS, RUANG TENGAH"
        string token "[gambar_slug]"
        string berkas_plate "slug_plate.png"
        text blok_set "6 spatial elements + oddity"
        string benda_ganjil "Human note"
    }

    PROP {
        string nama_kapital "MOTOR, PAKET, FOTO"
        enum lock_mode "Berpelat | Teks saja"
        string token "Optional [gambar_slug]"
        string berkas_plate "Optional slug_plate.png"
        text blok_properti "Locked description + no text/logos"
    }

    EPISODE ||--|| NASKAH : scripted_in
    EPISODE ||--|| PROMPT_ASET : generates_new_assets_in
    EPISODE ||--|{ VIDEO_SCENE : splits_into

    NASKAH {
        int episode_num
        text dialog "Story-readable lines with sNN"
        table shot_list "Shot | Durasi | Set | Siapa | Ukuran | Posisi kamera | Dialog"
        table shot_berisiko "Shot | Faktor | Keputusan user"
        table pembagian_scene "Scene | Shot | Durasi | Lokasi (4-30s)"
    }

    PROMPT_ASET {
        list reuse_files "Pakai ulang dari ep NN"
        list new_sheets "3-panel prompts matching CHARACTER.bentuk_panjang"
        list new_plates "24mm empty plates matching LOCATION/PROP"
    }

    VIDEO_SCENE {
        int scene_num "Markdown header only"
        int durasi_s "4..30 seconds"
        list lampirkan_files "Matches [gambar_slug] tokens 1-to-1"
        text video_style_format "Block 1"
        text language "Block 2"
        text optics "Block 3"
        text camera "Block 4"
        text lighting "Block 5"
        text critical "Block 6"
        text characters "Block 7 (copies CHARACTER.bentuk_pendek)"
        text location "Block 8 (copies LOCATION + PROP + optional Ref Map)"
        text continuity "Optional Block 8b (required if >1 location plate)"
        text audio "Block 9"
        text movement_note "Block 10"
        text shot_breakdown "Block 11 (SCENE [00:00-00:NN] + SHOT 1..K)"
    }
```

---

## 2. Token Bijection & Gate Verification Data Flow

```mermaid
flowchart TD
    G1["Gate 1: brief.md<br/>(Ratio, Duration, Language, Look)"] --> G2["Gate 2: konsep.md<br/>(3-Line Premise, Arc, 3 Hooks, Rubric)"]
    G2 -->|"Approval 1"| G3["Gate 3: cast.md & set.md<br/>(Canonical Locked Text & Tokens)"]
    G3 -->|"Approval 2"| G4["Gate 4: epNN/naskah.md<br/>(Script, Shot List, Risky Shots, 4-30s Split)"]
    G4 -->|"Approval 3"| G5["Gate 5: epNN/prompt-aset.md<br/>(New Sheets & Plates Only)"]
    G3 -->|"Verbatim Long Form"| G5
    G3 -->|"Verbatim Short Form + Set/Prop"| G6["Gate 6: epNN/prompt-video.md<br/>(11-Block Scene Prompts)"]
    G4 -->|"Scene Split + Shot Breakdown"| G6
    G5 -->|"Token <-> Filename Map"| G7["Gate 7: check_prompts.py<br/>(25 Automated Checks + board.html)"]
    G6 --> G7
    G7 -->|"User Clip Defects"| R1["dissect_video.py<br/>(ffmpeg Cut Audit + Diagnose + Versioned -vN.md)"]
    R1 -->|"Promote Winner"| G6
```

---

## 3. Canonical Token & File Naming Rules
1. Every reference image asset uses a strict lowercase alphanumeric/underscore `<slug>`:
   - **Character Sheet**: Token `[gambar_<slug>]` <-> File `<slug>_sheet.png` (e.g. `[gambar_adit]` <-> `adit_sheet.png`).
   - **Wardrobe Variant Sheet**: Token `[gambar_<slug>_b]` <-> File `<slug>_b_sheet.png` (e.g. `[gambar_rafa_b]` <-> `rafa_b_sheet.png`).
   - **Location or Plated Prop**: Token `[gambar_<slug>]` <-> File `<slug>_plate.png` (e.g. `[gambar_teras]` <-> `teras_plate.png`).
2. `check_prompts.py` enforces that:
   - Every `[gambar_<slug>]` in a scene block has its exact corresponding `<slug>_sheet.png` or `<slug>_plate.png` listed in that scene's `Lampirkan:` line.
   - No file in `Lampirkan:` is unused inside the prompt block (prevents wasted or confusing model conditioning).
   - No asset already defined in `ep01..ep(N-1)` is duplicated as a new generation block in `epN/prompt-aset.md`.
