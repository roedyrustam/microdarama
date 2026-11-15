#!/usr/bin/env python3
"""Verifikator 25-poin proyek Microdrama v2.0 sebelum diserahkan ke user (Gerbang 7).

Pakai:
  python assets/tools/check_prompts.py <folder_proyek> [--json] [--strict]
Contoh:
  python assets/tools/check_prompts.py assets/contoh/alamat-yang-sama --strict

Cek otomatis mencakup (25 poin):
 1-2. Salinan identik blok cast.md (panjang + pendek) & set.md (lokasi + properti)
 3-4. Kelengkapan & urutan 11 blok prompt video + posisi CONTINUITY
   5. Triad Lokasi Ganda (Peta Referensi + Tag Lokasi per SHOT + CONTINUITY)
 6-8. Batas durasi 4-30 detik, konsistensi 3 titik, & total episode vs brief.md
   9. Kontinuitas timecode SHOT bersambung tanpa celah/tumpang tindih
  10. Bijeksi token [gambar_x] <-> berkas sheet/plate & baris Lampirkan/Simpan sebagai
11-12. Kata terlarang di dalam blok & larangan subtitle/caption di luar LANGUAGE
  13. Frasa pengaman wajib (kamera, subtitle, exactly as written/NO dialogue, NOT a montage, no freeze frame)
14-15. Invarian sheet karakter 3 panel & plate set/properti (no people)
  16. Detektor tabrakan posisi kamera berurutan (naskah.md & SHOT BREAKDOWN)
  17. Paritas pembagian scene naskah.md <-> prompt-video.md
  18. Detektor angka mentah di dalam kutipan dialog lisan
  19. Audit kecepatan bicara (maks 3.2 kata/detik) & panjang kalimat vertikal
  20. Pemindai klise anti-sinetron & kata kosong across konsep, naskah, prompt
  21. Detektor tanda wajah ilegal (tanpa penanda 'Tanda wajah karena cerita:')
  22. Detektor kontaminasi kata orang di shot intip celah/kaca
  23. Detektor kontras ketiadaan benda & over-repetisi penegasan state
  24. Validasi anti-sinkronisasi figuran pada MOVEMENT NOTE saat >2 orang
  25. Validasi rubrik konsep.md & pencegahan duplikasi generate aset lintas episode
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass, field
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


BLOK = [
    "VIDEO STYLE & FORMAT",
    "LANGUAGE",
    "OPTICS",
    "CAMERA",
    "LIGHTING",
    "CRITICAL",
    "CHARACTERS",
    "LOCATION",
    "AUDIO",
    "MOVEMENT NOTE",
    "SHOT BREAKDOWN",
]
OPSIONAL = {"CONTINUITY": "LOCATION"}
TERLARANG = [
    "9:16",
    "16:9",
    "4:5",
    "21:9",
    "vertical",
    "horizontal",
    "===",
    ".png",
    ".jpg",
    "SCREENPLAY",
    "resolution",
    "seed",
    "fps",
    "8k",
    "4k",
    "masterpiece",
    "award winning",
    "ultra realistic",
    "hyper detailed",
]
KLISE_ID = [
    "kamu nggak akan pernah ngerti",
    "kau tidak akan pernah mengerti",
    "kamu siapa sih sebenarnya",
    "siapa kamu sebenarnya",
    "jangan pernah kembali ke sini",
    "aku sudah muak sama kamu",
    "saya sudah muak",
    "lihat saja nanti",
    "tunggu pembalasanku",
    "kamu akan menyesal",
    "asal kamu tahu ya",
    "hahaha!",
    "suasana mencekam",
    "hening mencekam",
    "air mata mengalir di pipinya",
    "tatapan tajam penuh kebencian",
    "senyum tipis penuh arti",
    "dunia seakan berhenti",
    "waktu terasa melambat",
]
KLISE_EN = [
    "cinematic masterpiece",
    "breathtaking",
    "stunning",
    "award winning photography",
]
FACIAL_MARKS_RE = re.compile(
    r"\b(mole|scar|tattoo|piercing|birthmark|freckles|tahi lalat|bekas luka|codet|tato)\b",
    re.I,
)
PEEPHOLE_TRIGGER_RE = re.compile(
    r"(seen through the gap|looking through the gap|from the gap|through the keyhole|floor level right at the gap)",
    re.I,
)
PEEPHOLE_FORBIDDEN_RE = re.compile(
    r"\b(no face|no head|nobody|person|people|man|woman|eyes|eye|breath|breathing|POV)\b",
    re.I,
)
WORD_NUMBERS_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "fifteen": 15,
    "twenty": 20,
}

DURASI_MIN, DURASI_MAKS = 4, 30
MAX_WPS = 3.2
TOKEN = r"\[(gambar_[a-z0-9_]+)\]"


@dataclass
class AuditResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(
        default_factory=lambda: {
            "cast": 0,
            "sets": 0,
            "naskah": 0,
            "prompt aset": 0,
            "prompt video": 0,
        }
    )

    def err(self, tempat: str, pesan: str) -> None:
        self.errors.append(f"{tempat}: {pesan}")

    def warn(self, tempat: str, pesan: str) -> None:
        self.warnings.append(f"{tempat}: {pesan}")


def rata(teks: str) -> str:
    return " ".join(teks.split())


def blok_kode(teks: str) -> list[str]:
    return re.findall(r"```[^\n]*\n(.*?)```", teks, re.S)


def norm_cam(pos: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", pos.lower())
    return rata(cleaned)


def baca_cast(folder: pathlib.Path) -> dict[str, dict[str, Any]]:
    cast_file = folder / "cast.md"
    if not cast_file.exists():
        return {}
    cast: dict[str, dict[str, Any]] = {}
    for sek in re.split(r"\n#{2,3} ", cast_file.read_text(encoding="utf-8"))[1:]:
        kode = blok_kode(sek)
        token = re.search(r"Token: `" + TOKEN + "`", sek)
        if len(kode) < 2 or not token:
            continue
        berkas = re.search(r"Berkas sheet: `([^`]+)`", sek)
        has_story_mark = bool(re.search(r"Tanda wajah karena cerita:", sek, re.I))
        cast[token.group(1)] = {
            "nama": sek.splitlines()[0].strip(),
            "berkas": berkas.group(1) if berkas else None,
            "panjang": kode[0],
            "pendek": kode[1],
            "story_mark": has_story_mark,
        }
    return cast


def baca_set(folder: pathlib.Path) -> dict[str, dict[str, Any]]:
    set_file = folder / "set.md"
    if not set_file.exists():
        return {}
    sets: dict[str, dict[str, Any]] = {}
    bagian = re.split(r"\n(#{2,3}) ", set_file.read_text(encoding="utf-8"))
    for pagar, sek in zip(bagian[1::2], bagian[2::2]):
        kode = blok_kode(sek)
        if not kode:
            continue
        token = re.search(r"Token: `" + TOKEN + "`", sek)
        berkas = re.search(r"Berkas plate: `([^`]+)`", sek)
        sets[sek.splitlines()[0].strip()] = {
            "token": token.group(1) if token else None,
            "berkas": berkas.group(1) if berkas else None,
            "blok": kode[0],
            "properti": pagar == "###",
        }
    return sets


def cek_nama_berkas(res: AuditResult, tempat: str, token: str, berkas: str | None) -> None:
    if berkas and not berkas.startswith(token[len("gambar_") :] + "_"):
        res.err(tempat, f"nama berkas {berkas} tidak sejalan dengan token [{token}]")


def pecah_blok(res: AuditResult, tempat: str, blk: str) -> dict[str, str]:
    posisi: dict[str, int] = {}
    for b in BLOK + list(OPSIONAL):
        m = re.search(r"^" + re.escape(b) + r"\b", blk, re.M)
        if m:
            posisi[b] = m.start()
        elif b in BLOK:
            res.err(tempat, f"blok {b} tidak ada")
    ada = [posisi[b] for b in BLOK if b in posisi]
    if ada != sorted(ada):
        res.err(tempat, "urutan sebelas blok salah")
    for b, sebelum in OPSIONAL.items():
        if b in posisi:
            sesudah = BLOK[BLOK.index(sebelum) + 1]
            if not posisi.get(sebelum, -1) < posisi[b] < posisi.get(sesudah, -1):
                res.err(tempat, f"blok {b} harus di antara {sebelum} dan {sesudah}")
    awal = sorted(posisi.values())
    isi: dict[str, str] = {}
    for b, p in posisi.items():
        berikut = [q for q in awal if q > p]
        isi[b] = blk[p : min(berikut) if berikut else len(blk)]
    return isi


def cek_klise(res: AuditResult, tempat: str, teks: str, is_prompt: bool = False) -> None:
    low = teks.lower()
    for frasa in KLISE_ID:
        if frasa in low:
            res.err(tempat, f"klise sinetron terdeteksi: '{frasa}'")
    if is_prompt:
        for frasa in KLISE_EN:
            if frasa in low:
                res.err(tempat, f"kata kosong AI terlarang di prompt: '{frasa}'")
        if "dramatic lighting" in low:
            res.err(tempat, "'dramatic lighting' tanpa sumber cahaya konkret terdeteksi")


def cek_konsep(res: AuditResult, folder: pathlib.Path) -> None:
    konsep_file = folder / "konsep.md"
    if not konsep_file.exists():
        res.err("konsep.md", "berkas konsep.md tidak ditemukan")
        return
    teks = konsep_file.read_text(encoding="utf-8")
    cek_klise(res, "konsep.md", teks, is_prompt=False)

    # Premis 3 baris
    premis_m = re.search(r"## Premis\s*\n(.*?)(?=\n## |\Z)", teks, re.S)
    if premis_m:
        items = re.findall(r"^\s*[1-3]\.\s+\*\*[^*]+\*\*", premis_m.group(1), re.M)
        if len(items) < 3:
            res.err("konsep.md", f"Premis harus 3 baris (Cerita, Detail meleset, Aturan tokoh), ditemukan {len(items)}")

    # Hook dipilih
    dipilih = re.search(r"Dipilih user:\s*(.+)", teks)
    if not dipilih or "<diisi" in dipilih.group(1):
        res.err("konsep.md", "hook belum dipilih di baris 'Dipilih user:'")

    # Rubrik
    rubrik_m = re.search(r"## Skor rubrik\s*\n(.*?)(?=\n## |\Z)", teks, re.S)
    if not rubrik_m:
        res.warn("konsep.md", "bagian '## Skor rubrik' tidak ditemukan")
        return
    r_text = rubrik_m.group(1)
    scores = [
        int(x)
        for x in re.findall(
            r"(?:Hook|Spesifik|Detail meleset|Dialog|Diam|Tanam & bayar|Akhir)\s+(\d+)",
            r_text,
            re.I,
        )
    ]
    if scores:
        low_scores = [s for s in scores if s < 4]
        if low_scores:
            res.err("konsep.md", f"skor rubrik ada yang di bawah 4 ({scores})")
        avg = sum(scores) / len(scores)
        if avg < 4.3:
            res.err("konsep.md", f"rata-rata skor rubrik {avg:.2f} di bawah 4.3")
    if re.search(r"Konsisten\s+Tidak\b", r_text, re.I):
        res.err("konsep.md", "gerbang rubrik 'Konsisten' bernilai Tidak")
    if re.search(r"Tanpa teks\s+Tidak\b", r_text, re.I):
        res.err("konsep.md", "gerbang rubrik 'Tanpa teks' bernilai Tidak")


def cek_durasi(res: AuditResult, tempat: str, blk: str, dur_judul: int | None) -> tuple[int, list[tuple[int, int, int, str]]]:
    m = re.search(r"^(\d+)-second scene", blk, re.M)
    dur = int(m.group(1)) if m else None
    if dur is None:
        res.err(tempat, "durasi tidak disebut di awal VIDEO STYLE & FORMAT")
        return 0, []
    if not DURASI_MIN <= dur <= DURASI_MAKS:
        res.err(tempat, f"durasi {dur} s di luar {DURASI_MIN}-{DURASI_MAKS} detik per generate")
    if dur_judul is not None and dur_judul != dur:
        res.err(tempat, f"judul bilang {dur_judul} detik, prompt bilang {dur} detik")
    m = re.search(r"^SCENE \[00:00-00:(\d\d)\]", blk, re.M)
    if not m:
        res.err(tempat, "baris SCENE [00:00-00:NN] tidak ada")
    elif int(m.group(1)) != dur:
        res.err(tempat, f"timecode SCENE berakhir di {m.group(1)} s, durasi {dur} s")
    if re.search(r"^SCENE \d", blk, re.M):
        res.err(tempat, "SCENE bernomor di dalam prompt — tiap prompt satu generate, tanpa nomor")

    # Extract each SHOT block and its full text up to the next SHOT or closing line
    shot_matches = list(re.finditer(r"^SHOT (\d+) \((\d+)-(\d+)s\)", blk, re.M))
    if not shot_matches:
        res.err(tempat, "tidak ada baris SHOT")
        return dur, []

    shots_parsed: list[tuple[int, int, int, str]] = []
    harap = 0
    for idx, sm in enumerate(shot_matches):
        n, a, b = int(sm.group(1)), int(sm.group(2)), int(sm.group(3))
        if n != idx + 1:
            res.err(tempat, f"SHOT {n} seharusnya bernomor {idx + 1}")
        if a != harap:
            res.err(tempat, f"SHOT {n} mulai di {a} s, seharusnya {harap} s")
        if b <= a:
            res.err(tempat, f"SHOT {n} berdurasi nol atau mundur")
        harap = b
        end_pos = shot_matches[idx + 1].start() if idx + 1 < len(shot_matches) else len(blk)
        shots_parsed.append((n, a, b, blk[sm.start() : end_pos]))
    if harap != dur:
        res.err(tempat, f"SHOT terakhir berakhir di {harap} s, durasi scene {dur} s")
    return dur, shots_parsed


def extract_shot_camera_pos(shot_text: str) -> str | None:
    first_para = shot_text.split(":", 1)[0]
    first_para = re.sub(r"^SHOT \d+ \(\d+-\d+s\)(?: — [^—]+ —)?", "", first_para)
    m = re.search(r"\bfrom\s+([^,;\n]+)", first_para, re.I)
    if not m:
        return None
    return norm_cam(m.group(1))


def cek_shot_semantics(
    res: AuditResult,
    tempat: str,
    shots: list[tuple[int, int, int, str]],
    char_names: list[str],
) -> None:
    prev_pos: str | None = None
    prev_n: int | None = None
    for n, a, b, s_text in shots:
        shot_dur = max(1, b - a)
        header_line = s_text.split(":", 1)[0]
        # 16. Consecutive camera position inside prompt
        cam_pos = extract_shot_camera_pos(s_text)
        if cam_pos and prev_pos and cam_pos == prev_pos:
            res.err(tempat, f"SHOT {prev_n} dan SHOT {n} memakai posisi kamera sama ('{cam_pos}')")
        prev_pos, prev_n = cam_pos, n

        # 18 & 19. Spoken dialogue digits and acoustic pacing
        spoken_lines = re.findall(
            r'^[A-Z0-9_ ]+(?:\s*\([^)]*\))?:\s*"([^"]+)"',
            s_text,
            re.M,
        )
        total_words = 0
        for line in spoken_lines:
            if re.search(r"\d", line):
                res.err(tempat, f"SHOT {n} dialog mengandung angka mentah ('{line}') — tulis sebagai kata")
            words = re.findall(r"[A-Za-zÀ-ÿ'-]+", line)
            total_words += len(words)
            # Check sentence word count (> 14 words per sentence warning)
            for sent in re.split(r"[.!?]+", line):
                s_words = re.findall(r"[A-Za-zÀ-ÿ'-]+", sent)
                if len(s_words) > 14:
                    res.warn(tempat, f"SHOT {n} kalimat dialog {len(s_words)} kata (>14 kata terasa pidato di vertikal)")
        if total_words > 0:
            wps = total_words / shot_dur
            if wps > MAX_WPS:
                res.warn(
                    tempat,
                    f"SHOT {n} kecepatan bicara {wps:.1f} kata/detik ({total_words} kata/{shot_dur}s > {MAX_WPS} wps)",
                )

        # 22. Peephole / gap contamination check
        if PEEPHOLE_TRIGGER_RE.search(header_line):
            # Exclude closing line if it's the final shot
            body = re.sub(r"The shot ends .*$", "", s_text, flags=re.M)
            hit = PEEPHOLE_FORBIDDEN_RE.search(body)
            if hit:
                res.err(tempat, f"SHOT {n} (shot lewat celah/kaca) menyebut kata orang terlarang: '{hit.group(0)}'")
            for cname in char_names:
                if cname and re.search(r"\b" + re.escape(cname) + r"\b", body):
                    res.err(tempat, f"SHOT {n} (shot lewat celah/kaca) menyebut nama tokoh '{cname}'")

        # 23a. Absence contrast check
        if re.search(r"(missing|nothing on it|not an object|clean rectangle)", s_text, re.I):
            c_hit = re.search(r"\b(darker|deeper colour|deeper color)\b", s_text, re.I)
            if c_hit:
                res.err(tempat, f"SHOT {n} ketiadaan benda memakai kata kontras '{c_hit.group(0)}'")


def cek_crowd_and_continuity(res: AuditResult, tempat: str, isi: dict[str, str], blk: str) -> None:
    crit = rata(isi.get("CRITICAL", ""))
    mov = rata(isi.get("MOVEMENT NOTE", ""))

    # Estimate total people in scene from CRITICAL
    has_crowd = False
    if re.search(r"\b(background|staff|employees|guests|crowd|villagers|bystanders)\b", crit, re.I):
        if not re.search(r"background\s*—\s*none", rata(isi.get("CHARACTERS", "")), re.I):
            # Check count words or digits
            for num_word, val in WORD_NUMBERS_MAP.items():
                if val > 2 and re.search(rf"\b{num_word}\b", crit, re.I):
                    has_crowd = True
            for d_str in re.findall(r"\b(\d+)\b", crit):
                if int(d_str) > 2:
                    has_crowd = True
            if re.search(r"\b(crowd|several|group of)\b", crit, re.I):
                has_crowd = True

    if has_crowd:
        if not re.search(r"(NEVER react as a block|never a synchronised|never a synchronized)", mov, re.I):
            res.err(tempat, "CRITICAL menyebut >2 figuran/orang, tapi MOVEMENT NOTE tidak melarang gerakan serempak")

    # 23b. Over-repetition check on object/door state anchors (ignore "mouth stays closed" lip-sync guard)
    for pat in (r"(?<!mouth )stays closed", r"never opens", r"(?<!mouth )stays shut", r"remains closed"):
        occurrences = len(re.findall(pat, blk, re.I))
        if occurrences > 2:
            res.warn(tempat, f"frasa pengunci objek '{pat}' diulang {occurrences}x (>2x berisiko diubah model)")


def cek_prompt_video(
    res: AuditResult,
    f: pathlib.Path,
    cast: dict[str, dict[str, Any]],
    sets: dict[str, dict[str, Any]],
) -> tuple[int, list[tuple[int, int]]]:
    total = 0
    scene_durs: list[tuple[int, int]] = []
    peta = {t: c["berkas"] for t, c in cast.items()}
    peta.update({s["token"]: s["berkas"] for s in sets.values() if s["token"]})
    char_names = [c["nama"] for c in cast.values()]

    scene_idx = 0
    for sek in re.split(r"\n## ", f.read_text(encoding="utf-8"))[1:]:
        kode = blok_kode(sek)
        if not kode:
            continue
        scene_idx += 1
        judul = sek.splitlines()[0].strip()
        tempat = f"{f.parent.name}/{f.name} [{judul}]"
        blk = kode[0]
        blk_rata = rata(blk)
        res.counts["prompt video"] += 1

        isi = pecah_blok(res, tempat, blk)

        for kata in TERLARANG:
            if re.search(r"(?<!\w)" + re.escape(kata.lower()) + r"(?!\w)" if kata.isalnum() else re.escape(kata.lower()), blk_rata.lower()):
                res.err(tempat, f"kata terlarang di dalam prompt: {kata!r}")

        cek_klise(res, tempat, blk, is_prompt=True)

        luar_language = blk_rata.lower().replace(rata(isi.get("LANGUAGE", "")).lower(), "")
        for kata in ("subtitle", "caption"):
            if kata in luar_language:
                res.err(tempat, f"'{kata}' muncul di luar blok LANGUAGE")

        m = re.search(r"(\d+) detik", judul)
        dur, shots = cek_durasi(res, tempat, blk, int(m.group(1)) if m else None)
        total += dur
        scene_durs.append((scene_idx, dur))

        cek_shot_semantics(res, tempat, shots, char_names)
        cek_crowd_and_continuity(res, tempat, isi, blk)

        baris = next((l for l in sek.splitlines() if l.startswith("Lampirkan:")), "")
        lampiran = set(re.findall(r"`([^`]+)`", baris))
        dipakai = set(re.findall(TOKEN, blk))
        for t in sorted(dipakai):
            if t not in peta:
                res.err(tempat, f"token [{t}] tidak terdaftar di cast.md / set.md")
            elif peta[t] not in lampiran:
                res.err(tempat, f"token [{t}] dipakai tapi {peta[t]} tidak ada di baris Lampirkan")
        for b in sorted(lampiran - {peta.get(t) for t in dipakai}):
            res.err(tempat, f"{b} dilampirkan tapi tokennya tidak dipakai di prompt")

        char = rata(isi.get("CHARACTERS", ""))
        for t, c in cast.items():
            if t in dipakai and rata(c["pendek"].split("<")[0]) not in char:
                res.err(tempat, f"bentuk pendek {c['nama']} tidak identik dengan cast.md")
        lok = rata(isi.get("LOCATION", ""))
        for nama, s in sets.items():
            b = rata(s["blok"])
            if s["token"]:
                if s["token"] in dipakai and b not in lok:
                    res.err(tempat, f"blok {nama} tidak identik dengan set.md")
            elif b[:40] in blk_rata and b not in lok:
                res.err(tempat, f"properti {nama} dipakai tapi tidak tersalin identik di LOCATION")

        lokasi = [s for s in sets.values() if s["token"] in dipakai and not s["properti"]]
        if len(lokasi) > 1:
            ganda = f"{len(lokasi)} plate lokasi dalam satu generate"
            for n in re.findall(r"^SHOT (\d+) \(\d+-\d+s\)(?! — [^—]{1,100} —)", blk, re.M):
                res.err(tempat, f"SHOT {n} tanpa tag lokasi ({ganda})")
            if "SHOT" not in lok:
                res.err(tempat, f"LOCATION tidak memetakan plate ke shot ({ganda})")
            if "CONTINUITY" not in isi:
                res.err(tempat, f"blok CONTINUITY tidak ada untuk mengunci posisi tokoh ({ganda})")

        if "Never two consecutive shots from the same position" not in rata(isi.get("CAMERA", "")):
            res.err(tempat, "CAMERA tidak memuat 'Never two consecutive shots from the same position'")
        lang = rata(isi.get("LANGUAGE", ""))
        if "No subtitles" not in lang:
            res.err(tempat, "LANGUAGE tidak melarang subtitle")
        if "exactly as written" not in lang and "NO spoken dialogue" not in lang:
            res.err(tempat, "LANGUAGE tidak memuat 'exactly as written' atau 'NO spoken dialogue'")
        if "NOT a montage" not in blk_rata:
            res.err(tempat, "VIDEO STYLE & FORMAT tidak memuat 'NOT a montage'")
        if "no freeze frame" not in blk_rata:
            res.err(tempat, "penutup tidak memuat 'no freeze frame'")

    return total, scene_durs


def cek_prompt_aset(
    res: AuditResult,
    f: pathlib.Path,
    cast: dict[str, dict[str, Any]],
    sets: dict[str, dict[str, Any]],
    seen_assets: dict[str, str],
) -> None:
    teks_penuh = f.read_text(encoding="utf-8")
    ep_name = f.parent.name
    for sek in re.split(r"\n## ", teks_penuh)[1:]:
        kode = blok_kode(sek)
        if not kode:
            continue
        tempat = f"{ep_name}/{f.name} [{sek.splitlines()[0].strip()}]"
        blk = rata(kode[0])
        res.counts["prompt aset"] += 1
        simpan = re.search(r"Simpan sebagai: `([^`]+)` → token `" + TOKEN + "`", sek)
        if not simpan:
            res.err(tempat, "baris 'Simpan sebagai: `berkas` → token `[gambar_x]`' tidak ada")
            continue
        berkas, token = simpan.groups()
        cek_nama_berkas(res, tempat, token, berkas)

        # 25b. Cross-episode duplicate asset generation check
        if token in seen_assets:
            res.err(
                tempat,
                f"aset [{token}] ({berkas}) sudah dibuat di {seen_assets[token]} — seharusnya masuk baris 'Pakai ulang'",
            )
        else:
            seen_assets[token] = ep_name

        if token in cast:
            c = cast[token]
            if c["berkas"] != berkas:
                res.err(tempat, f"berkas {berkas} beda dengan cast.md ({c['berkas']})")
            orang, _, baju = c["panjang"].partition("WARDROBE:")
            if rata(orang) not in blk:
                res.err(tempat, f"bentuk panjang {c['nama']} tidak identik dengan cast.md")
            if rata("WARDROBE:" + baju) not in blk:
                res.err(tempat, f"WARDROBE {c['nama']} tidak identik dengan cast.md")
            if f"label reading {c['nama']}" not in blk:
                res.err(tempat, f"label nama {c['nama']} tidak ada")
            for wajib in ("missing head", "different faces between panels"):
                if wajib not in blk:
                    res.err(tempat, f"Avoid tidak memuat '{wajib}'")
            urut = [blk.find(p) for p in ("LEFT PANEL: tight close-up", "MIDDLE PANEL", "RIGHT PANEL")]
            if -1 in urut or urut != sorted(urut):
                res.err(tempat, "panel harus berurutan: close-up kiri, depan tengah, belakang kanan")
            if not c["story_mark"] and FACIAL_MARKS_RE.search(c["panjang"]):
                res.err(tempat, f"{c['nama']} memiliki tanda wajah tanpa label 'Tanda wajah karena cerita:' di cast.md")
        else:
            s = next((s for s in sets.values() if s["token"] == token), None)
            if not s:
                res.err(tempat, f"token [{token}] tidak terdaftar di cast.md / set.md")
                continue
            if s["berkas"] != berkas:
                res.err(tempat, f"berkas {berkas} beda dengan set.md ({s['berkas']})")
            if rata(s["blok"]) not in blk:
                res.err(tempat, "blok tidak identik dengan set.md")
            if "absolutely no people" not in blk:
                res.err(tempat, "plate tidak memuat 'absolutely no people'")


def cek_naskah(
    res: AuditResult,
    f: pathlib.Path,
    durasi_ep: int | None,
) -> list[tuple[int, int]]:
    teks = f.read_text(encoding="utf-8")
    tempat = f"{f.parent.name}/{f.name}"
    res.counts["naskah"] += 1
    cek_klise(res, tempat, teks, is_prompt=False)

    # Check shot list durations and consecutive camera positions
    shot_rows = re.findall(
        r"^\|\s*(s\d+)\s*\|\s*(\d+)\s*s\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|",
        teks,
        re.M,
    )
    total = sum(int(row[1]) for row in shot_rows)
    if durasi_ep and total != durasi_ep:
        res.err(tempat, f"shot list berjumlah {total} s, brief {durasi_ep} s")

    prev_shot: str | None = None
    prev_cam: str | None = None
    for s_id, _dur, _set, _who, _size, cam_pos, _dlg in shot_rows:
        nc = norm_cam(cam_pos)
        if nc and prev_cam and nc == prev_cam:
            res.err(tempat, f"{prev_shot} dan {s_id} memakai posisi kamera sama ('{cam_pos.strip()}')")
        prev_shot, prev_cam = s_id, nc

    # Pembagian scene rows
    scene_rows = re.findall(r"^\|\s*(\d+)\s*\|\s*s\d+[^|]*\|\s*(\d+)\s*s\s*\|", teks, re.M)
    scenes_parsed: list[tuple[int, int]] = []
    for s_num, d_str in scene_rows:
        d = int(d_str)
        scenes_parsed.append((int(s_num), d))
        if not DURASI_MIN <= d <= DURASI_MAKS:
            res.err(tempat, f"scene {s_num} ({d} s) di luar {DURASI_MIN}-{DURASI_MAKS} detik per generate")
    return scenes_parsed


def cek_cast_rules(res: AuditResult, cast: dict[str, dict[str, Any]]) -> None:
    for c in cast.values():
        m = FACIAL_MARKS_RE.search(c["panjang"])
        if m and not c["story_mark"]:
            res.err(
                "cast.md",
                f"{c['nama']} memuat tanda wajah '{m.group(0)}' tanpa pengecualian 'Tanda wajah karena cerita:'",
            )


def run_checks(folder: pathlib.Path, strict: bool = False) -> dict[str, Any]:
    res = AuditResult()
    brief_path = folder / "brief.md"
    if not brief_path.exists():
        res.err("brief.md", "berkas brief.md tidak ditemukan")
        return {
            "status": "error",
            "folder": str(folder),
            "summary": res.counts,
            "errors": res.errors,
            "warnings": res.warnings,
        }

    m = re.search(r"\| Durasi \| (\d+) detik", brief_path.read_text(encoding="utf-8"))
    durasi_ep = int(m.group(1)) if m else None
    cek_konsep(res, folder)
    cast, sets = baca_cast(folder), baca_set(folder)
    res.counts["cast"] = len(cast)
    res.counts["sets"] = len(sets)
    cek_cast_rules(res, cast)

    for t, c in cast.items():
        cek_nama_berkas(res, "cast.md", t, c["berkas"])
    for s in sets.values():
        if s["token"]:
            cek_nama_berkas(res, "set.md", s["token"], s["berkas"])

    seen_assets: dict[str, str] = {}
    for ep in sorted(p for p in folder.iterdir() if p.is_dir() and p.name.startswith("ep")):
        naskah_scenes: list[tuple[int, int]] = []
        if (ep / "naskah.md").exists():
            naskah_scenes = cek_naskah(res, ep / "naskah.md", durasi_ep)
        if (ep / "prompt-aset.md").exists():
            cek_prompt_aset(res, ep / "prompt-aset.md", cast, sets, seen_assets)
        if (ep / "prompt-video.md").exists():
            total, pv_scenes = cek_prompt_video(res, ep / "prompt-video.md", cast, sets)
            if durasi_ep and total != durasi_ep:
                res.err(f"{ep.name}/prompt-video.md", f"total {total} s, brief {durasi_ep} s")
            if naskah_scenes and pv_scenes and naskah_scenes != pv_scenes:
                res.err(
                    f"{ep.name}",
                    f"pembagian scene naskah.md {naskah_scenes} tidak cocok dengan prompt-video.md {pv_scenes}",
                )
        else:
            res.err(ep.name, "prompt-video.md belum ada")

    if strict and res.warnings:
        res.errors.extend([f"[STRICT] {w}" for w in res.warnings])
        res.warnings = []

    return {
        "status": "ok" if not res.errors else "error",
        "folder": str(folder),
        "summary": res.counts,
        "errors": res.errors,
        "warnings": res.warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifikator 25-poin proyek Microdrama v2.0 (Gerbang 7)."
    )
    parser.add_argument("folder", help="Path folder proyek Microdrama (mis. film/alamat-yang-sama)")
    parser.add_argument("--json", action="store_true", help="Keluarkan laporan dalam format JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promosikan peringatan lunak (kecepatan bicara, kalimat panjang) menjadi error",
    )
    args = parser.parse_args(argv)
    folder = pathlib.Path(args.folder)
    if not folder.exists() or not folder.is_dir():
        if args.json:
            print(json.dumps({"status": "error", "errors": [f"Folder tidak ditemukan: {folder}"]}, indent=2))
        else:
            print(f"Folder tidak ditemukan: {folder}")
        return 2

    report = run_checks(folder, strict=args.strict)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["status"] == "ok" else 1

    c = report["summary"]
    print(
        f"Dicek: {c['cast']} tokoh, {c['sets']} set & properti, {c['naskah']} naskah, "
        f"{c['prompt aset']} prompt aset, {c['prompt video']} prompt video."
    )
    if report["warnings"]:
        print(f"\n{len(report['warnings'])} peringatan:")
        for w in report["warnings"]:
            print(f"  ! {w}")
    if report["errors"]:
        print(f"\n{len(report['errors'])} masalah:")
        for e in report["errors"]:
            print(f"  - {e}")
        return 1
    print("Semua cek lolos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
