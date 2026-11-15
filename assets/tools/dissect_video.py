#!/usr/bin/env python3
"""Microdrama v2.0 Post-Generation Video Dissector & Repair Loop CLI (Gerbang 7).

Zero external Python packages required. Uses ffmpeg/ffprobe on PATH if available.

Subcommands:
  diagnose "<query>" [--list]
  analyze <video_file> --prompt <prompt-video.md> [--scene 1] [--out-dir <dir>]
  branch <prompt-video.md> [--note "alasan revisi"]
  promote <prompt-video-vN.md>
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SYMPTOMS: list[dict[str, str]] = [
    {
        "id": "1",
        "gejala": "Wajah berubah antar klip / antar potongan shot",
        "penyebab": "Deskripsi tokoh diparafrase antar berkas, atau sheet salah lampir karena nama berkas tidak sejalan dengan token.",
        "perbaikan": "Jalankan `microdrama_cli.py sync` dan pastikan sheet 3-panel punya label nama tercetak di pojok kiri bawah.",
        "tags": "wajah berubah face swap morphing beda orang karakter sheet tertukar",
    },
    {
        "id": "2",
        "gejala": "Teks aneh atau simbol muncul di layar",
        "penyebab": "Header manusia (`===`) atau nama berkas ikut masuk ke dalam blok prompt, atau blok LANGUAGE lupa melarang subtitle.",
        "perbaikan": "Pindahkan header ke judul markdown di luar blok dan pastikan `No subtitles, no captions, no on-screen text` ada di LANGUAGE.",
        "tags": "teks aneh huruf simbol muncul di layar subtitle caption header",
    },
    {
        "id": "3",
        "gejala": "Huruf acak / gibberish di label paket, plat nomor, atau layar HP",
        "penyebab": "Properti tidak diberi `no printed text` / `licence plate blank`, atau layar HP menghadap kamera.",
        "perbaikan": "Tambahkan `no labels, no printed text, licence plate blank` di set/properti dan `screen always angled away from camera` di CRITICAL.",
        "tags": "huruf acak gibberish label paket plat nomor layar hp monitor tv tulisan",
    },
    {
        "id": "4",
        "gejala": "Dialog keluar dalam Bahasa Inggris padahal diminta Bahasa Indonesia",
        "penyebab": "Blok LANGUAGE tidak mengunci instruksi `Speak the lines exactly as written`.",
        "perbaikan": "Tambahkan di LANGUAGE: `Speak the lines exactly as written in the breakdown below: do not translate them, do not paraphrase them.`",
        "tags": "bahasa inggris dialog bahasa terjemahan translate english",
    },
    {
        "id": "5",
        "gejala": "Dialog diparafrase atau AI menambah kalimat sendiri",
        "penyebab": "Tidak ada larangan `do not invent extra lines` atau jumlah total kalimat belum dikunci.",
        "perbaikan": "Kunci jumlah baris di LANGUAGE (`Exactly TWO lines are spoken in the whole scene`) dan tambahkan `do not invent extra lines`.",
        "tags": "dialog diparafrase nambah kalimat extra lines bicara sendiri",
    },
    {
        "id": "6",
        "gejala": "Ada narasi atau gumaman di scene yang seharusnya hening",
        "penyebab": "Blok LANGUAGE tidak memakai bentuk `NO spoken dialogue`.",
        "perbaikan": "Ganti isi LANGUAGE menjadi: `This scene has NO spoken dialogue — no voices, no narration, no inner monologue, no whispering.`",
        "tags": "narasi gumaman suara hening bisu silent dialogue",
    },
    {
        "id": "7",
        "gejala": "Figuran bergerak atau menoleh serempak seperti paduan suara",
        "penyebab": "MOVEMENT NOTE tidak ada atau tidak memecah aksi figuran secara eksplisit.",
        "perbaikan": "Tulis tiga reaksi terpisah untuk figuran di MOVEMENT NOTE plus larangan keras `never a synchronised crowd turn`.",
        "tags": "figuran serempak paduan suara crowd gerak bareng background staff",
    },
    {
        "id": "8",
        "gejala": "Orang asing muncul lewat di lorong atau jalan yang harusnya sepi",
        "penyebab": "CRITICAL tidak mengunci jumlah tokoh secara absolut.",
        "perbaikan": "Tulis di awal CRITICAL: `ONE character only. Nobody else appears at any point.`",
        "tags": "orang asing figuran liar muncul jalan sepi lorong",
    },
    {
        "id": "9",
        "gejala": "Drama keluarga terasa seperti film horor / thriller",
        "penyebab": "VIDEO STYLE & FORMAT tidak menolak genre horor pada premis bernuansa sepi/mengintip.",
        "perbaikan": "Tambahkan di VIDEO STYLE & FORMAT: `This is a quiet family drama, NOT horror and NOT a thriller.`",
        "tags": "horor thriller tegang serem musik serem gelap drama keluarga",
    },
    {
        "id": "10",
        "gejala": "Hasil terasa seperti trailer atau montase terputus-putus",
        "penyebab": "VIDEO STYLE & FORMAT tidak menegaskan `ONE continuous ... NOT a montage`.",
        "perbaikan": "Tegaskan di baris awal VIDEO STYLE & FORMAT: `ONE continuous moment — NOT a trailer, NOT a montage — cut between MULTIPLE camera positions.`",
        "tags": "trailer montage montase terputus patah-patah",
    },
    {
        "id": "11",
        "gejala": "Potongan terasa monoton dari sudut kamera yang sama",
        "penyebab": "Dua shot berurutan memakai posisi sama atau CAMERA lupa aturan delta posisi.",
        "perbaikan": "Pindahkan salah satu shot ke posisi berbeda dan pastikan kalimat `Never two consecutive shots from the same position.` ada di CAMERA.",
        "tags": "monoton kamera sama posisi sudut tidak pindah",
    },
    {
        "id": "12",
        "gejala": "Frame terlihat datar / lighting membosankan",
        "penyebab": "LIGHTING ditulis memakai kata sifat (`dramatic lighting`) tanpa sumber dan arah cahaya.",
        "perbaikan": "Sebut sumber konkret, arah (`camera-left`), suhu Kelvin (`5600K`/`3200K`), *negative fill*, dan satu aksen warna tunggal.",
        "tags": "datar flat lighting cahaya gelap kontras",
    },
    {
        "id": "13",
        "gejala": "Panel badan di character sheet terpotong tanpa kepala",
        "penyebab": "Daftar `Avoid:` pada sheet tidak memuat `missing head`.",
        "perbaikan": "Pastikan `missing head` dan `different faces between panels` ada di baris `Avoid:` prompt sheet.",
        "tags": "kepala terpotong missing head sheet panel",
    },
    {
        "id": "14",
        "gejala": "Jumlah orang bertambah atau berkurang antar potongan",
        "penyebab": "Jumlah tokoh & figuran tidak dikunci numerik di CRITICAL.",
        "perbaikan": "Sebut jumlah eksak di kalimat pertama CRITICAL (`TWO speaking characters plus twelve silent background staff`) dan `no extra people appearing or vanishing`.",
        "tags": "orang bertambah orang hilang jumlah orang duplikat",
    },
    {
        "id": "15",
        "gejala": "Prompt ditolak tool atau klip akhir terpotong mendadak",
        "penyebab": "Durasi scene di luar 4–30 detik atau dialog melebihi kecepatan bicara alami.",
        "perbaikan": "Pecah scene mengikuti jeda alami ke rentang 4–30s dan jaga pacing dialog ≤ 3.2 kata/detik.",
        "tags": "ditolak terpotong durasi kecepatan dialog panjang",
    },
    {
        "id": "16",
        "gejala": "Pintu atau tata letak ruangan berubah antar klip",
        "penyebab": "Pintu/jalan masuk yang dipakai blocking tidak tertulis di blok `set.md`.",
        "perbaikan": "Tambahkan semua pintu dan jalan masuk yang dipakai arc ke `set.md` lalu jalankan `microdrama_cli.py sync`.",
        "tags": "pintu berubah ruangan beda tata letak set bocor",
    },
    {
        "id": "17",
        "gejala": "Tokoh tiba-tiba bocor ke sisi lain pintu (dalam vs luar rumah)",
        "penyebab": "Dua plate lokasi dipakai tanpa Triad Lokasi Ganda.",
        "perbaikan": "Pasang Peta Referensi di LOCATION, tag lokasi `— OUTSIDE/INSIDE, ... —` di tiap baris SHOT, dan kunci posisi tokoh di CONTINUITY.",
        "tags": "bocor sisi pintu salah dalam luar teras dua plate multi lokasi",
    },
    {
        "id": "18",
        "gejala": "Wajah atau kepala hantu muncul di shot intip lewat celah atau kaca",
        "penyebab": "Baris SHOT intip menyebut kata orang atau larangan seperti `no face, no head, nobody`.",
        "perbaikan": "Hapus semua kata orang/wajah/larangan orang dari baris SHOT intip; tulis hanya benda dan lantai yang terlihat.",
        "tags": "wajah muncul celah kaca intip peephole no face no head",
    },
    {
        "id": "19",
        "gejala": "Kamera di sisi salah, kaca buram jadi bening, atau pintu tertutup malah terbuka",
        "penyebab": "Sudut tidak ada di plate, atau benda ditegaskan berulang-ulang di banyak blok (`stays closed` 3x).",
        "perbaikan": "Tulis posisi kamera & latar belakang 1x saja; hapus pengulangan penegasan pintu di blok selain satu butir CONTINUITY.",
        "tags": "pintu terbuka kaca bening stays closed sudut salah",
    },
    {
        "id": "20",
        "gejala": "Tokoh berwajah aneh: luka jadi codet horor, tahi lalat jadi bisul",
        "penyebab": "Tanda kecil di wajah ditulis tanpa fungsi cerita hingga dibesar-besarkan model AI.",
        "perbaikan": "Hapus semua tanda wajah dari `cast.md` dan `prompt-aset.md` jika bukan bagian penting alur cerita.",
        "tags": "codet bisul luka tahi lalat muka aneh scar mole",
    },
    {
        "id": "21",
        "gejala": "Kendaraan/paket/benda hilang, dobel, atau pindah tempat antar cut",
        "penyebab": "Tidak ada butir spesifik untuk benda tersebut di blok CONTINUITY.",
        "perbaikan": "Tambahkan satu butir CONTINUITY: posisi eksak, sejak SHOT berapa, di SHOT mana terlihat, dan `outside the frame — never gone`.",
        "tags": "motor hilang paket hilang dobel pindah tempat continuity",
    },
    {
        "id": "22",
        "gejala": "Shot wide menyalin komposisi plate mentah-mentah dan mengabaikan teks",
        "penyebab": "Set plate digenerate dari sudut yang berlawanan dengan wide shot terpenting.",
        "perbaikan": "Generate ulang set plate dari sudut wide shot terpenting adegan (misal dari seberang gang menghadap pagar).",
        "tags": "menyalin komposisi plate wide shot sudut plate",
    },
    {
        "id": "23",
        "gejala": "Bekas kotak atau petak bersih di debu dirender jadi keset atau lempengan fisik",
        "penyebab": "Ketiadaan benda dijelaskan memakai kata kontras (`darker`, `deeper colour`).",
        "perbaikan": "Ganti kata kontras dengan deskripsi permukaan rata: `flat, level with the floor, nothing on it, not an object`.",
        "tags": "bekas kotak debu keset lempengan tambalan darker ketiadaan",
    },
    {
        "id": "24",
        "gejala": "Muncul baris dialog palsu di luar layar saat close-up benda/tangan",
        "penyebab": "Close-up tanpa wajah terlalu dekat momen dialog sehingga model mengarang ucapan off-screen.",
        "perbaikan": "Kunci jumlah tepat baris dialog di LANGUAGE atau pindahkan dialog ke shot yang memperlihatkan wajah pembicara.",
        "tags": "dialog palsu off-screen halusinasi suara close-up tangan",
    },
]


def cmd_diagnose(args: argparse.Namespace) -> int:
    if args.list or not args.query:
        for item in SYMPTOMS:
            print(f"[{item['id'].zfill(2)}] {item['gejala']}")
            print(f"     Penyebab : {item['penyebab']}")
            print(f"     Perbaikan: {item['perbaikan']}\n")
        return 0

    terms = [t.lower() for t in re.findall(r"[a-z0-9_-]+", args.query) if len(t) > 1]
    scored: list[tuple[int, dict[str, str]]] = []
    for item in SYMPTOMS:
        haystack = f"{item['gejala']} {item['penyebab']} {item['perbaikan']} {item['tags']}".lower()
        score = sum(2 if t in item["gejala"].lower() else 1 for t in terms if t in haystack)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        print(f"Tidak ada gejala yang cocok persis untuk '{args.query}'. Jalankan dengan --list untuk melihat seluruh 24 pola.")
        return 1

    print(f"Ditemukan {len(scored)} kecocokan untuk '{args.query}':\n")
    for _sc, item in scored[:5]:
        print(f"[{item['id'].zfill(2)}] GEJALA   : {item['gejala']}")
        print(f"     PENYEBAB : {item['penyebab']}")
        print(f"     PERBAIKAN: {item['perbaikan']}\n")
    return 0


def _extract_expected_shots(prompt_path: pathlib.Path, scene_num: int) -> tuple[int, list[tuple[int, int, int]]]:
    text = prompt_path.read_text(encoding="utf-8")
    sections = re.split(r"\n## ", text)[1:]
    valid_blocks = []
    for sek in sections:
        m = re.search(r"```[^\n]*\n(.*?)```", sek, re.S)
        if m:
            valid_blocks.append((sek.splitlines()[0].strip(), m.group(1)))
    if not valid_blocks or scene_num < 1 or scene_num > len(valid_blocks):
        raise ValueError(f"Scene {scene_num} tidak ditemukan di {prompt_path}")

    judul, blk = valid_blocks[scene_num - 1]
    dur_m = re.search(r"(\d+) detik", judul)
    dur = int(dur_m.group(1)) if dur_m else 0
    shots = [(int(n), int(a), int(b)) for n, a, b in re.findall(r"^SHOT (\d+) \((\d+)-(\d+)s\)", blk, re.M)]
    return dur, shots


def cmd_analyze(args: argparse.Namespace) -> int:
    prompt_path = pathlib.Path(args.prompt)
    if not prompt_path.exists():
        print(f"Berkas prompt tidak ditemukan: {prompt_path}", file=sys.stderr)
        return 2

    try:
        expected_dur, expected_shots = _extract_expected_shots(prompt_path, args.scene)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(f"=== Analisis Scene {args.scene} ({expected_dur}s) dari {prompt_path.name} ===")
    print("Timecode target di prompt:")
    for n, a, b in expected_shots:
        print(f"  SHOT {n}: {a:>2}s -> {b:>2}s (durasi {b-a}s)")

    video_path = pathlib.Path(args.video)
    ffmpeg_bin = shutil.which("ffmpeg")
    ffprobe_bin = shutil.which("ffprobe")

    if not ffmpeg_bin or not video_path.exists():
        print("\n[Mode Perintah Reproduksi] ffmpeg tidak tersedia di PATH atau berkas video belum ada.")
        print("Jalankan perintah berikut setelah video tergenerate:")
        print(f'  ffmpeg -i "{video_path}" -filter:v "select=\'gt(scene,0.25)\',showinfo" -f null -')
        print(f'  ffmpeg -i "{video_path}" -vf "fps=2,scale=240:-1,tile=7x5" kontak_%d.png')
        print(f'  whisper "{video_path}" --language id --model medium')
        return 0

    out_dir = pathlib.Path(args.out_dir) if args.out_dir else (video_path.parent / "dissect")
    out_dir.mkdir(parents=True, exist_ok=True)

    actual_dur = None
    if ffprobe_bin:
        probe = subprocess.run(
            [ffprobe_bin, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode == 0 and probe.stdout.strip():
            actual_dur = float(probe.stdout.strip())
            print(f"\nDurasi klip aktual: {actual_dur:.2f}s (target: {expected_dur}s)")

    scene_proc = subprocess.run(
        [ffmpeg_bin, "-i", str(video_path), "-filter:v", "select='gt(scene,0.25)',showinfo", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    cuts = [float(t) for t in re.findall(r"pts_time:([0-9.]+)", scene_proc.stderr)]
    print(f"\nTitik potong terdeteksi ({len(cuts)} cut):", [round(c, 2) for c in cuts])

    expected_cuts = [float(a) for _n, a, _b in expected_shots[1:]]
    print("Titik potong target di prompt:", expected_cuts)
    if len(cuts) != len(expected_cuts):
        print(f"! Peringatan: jumlah cut ({len(cuts)}) berbeda dengan target prompt ({len(expected_cuts)}).")

    contact_pattern = out_dir / "kontak_%d.png"
    subprocess.run(
        [ffmpeg_bin, "-y", "-i", str(video_path), "-vf", "fps=2,scale=240:-1,tile=7x5", str(contact_pattern)],
        capture_output=True,
        text=True,
        check=False,
    )
    generated_sheets = sorted(out_dir.glob("kontak_*.png"))
    if generated_sheets:
        print(f"Contact sheet 2fps disimpan ke: {generated_sheets[0].parent} ({len(generated_sheets)} berkas)")
    return 0


def cmd_branch(args: argparse.Namespace) -> int:
    src = pathlib.Path(args.prompt_file)
    if not src.exists():
        print(f"Berkas tidak ditemukan: {src}", file=sys.stderr)
        return 2

    parent = src.parent
    stem = src.stem  # e.g. prompt-video
    existing_nums = [1]
    for p in parent.glob(f"{stem}-v*.md"):
        m = re.match(rf"^{re.escape(stem)}-v(\d+)\.md$", p.name)
        if m:
            existing_nums.append(int(m.group(1)))
    next_v = max(existing_nums) + 1
    dst = parent / f"{stem}-v{next_v}.md"

    content = src.read_text(encoding="utf-8")
    note_header = f"<!-- Branch v{next_v} dari {src.name}"
    if args.note:
        note_header += f": {args.note}"
    note_header += " -->\n\n"
    dst.write_text(note_header + content, encoding="utf-8")
    print(f"Cabang versi baru dibuat: {dst}")
    print("Ubah hanya 1-2 kalimat yang menyasar akar penyebab, lalu uji dengan rasio & referensi yang sama.")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    ver_file = pathlib.Path(args.version_file)
    if not ver_file.exists():
        print(f"Berkas versi tidak ditemukan: {ver_file}", file=sys.stderr)
        return 2

    m = re.match(r"^(.+)-v\d+\.md$", ver_file.name)
    if not m:
        print("Nama berkas harus berpola <nama>-vN.md (mis. prompt-video-v2.md).", file=sys.stderr)
        return 2

    canonical = ver_file.parent / f"{m.group(1)}.md"
    if canonical.exists():
        backup = ver_file.parent / f"{m.group(1)}-prev-backup.md"
        shutil.copy2(canonical, backup)
        print(f"Versi lama dicadangkan ke: {backup}")

    cleaned = re.sub(r"^<!-- Branch v\d+[^>]*-->\s*\n*", "", ver_file.read_text(encoding="utf-8"))
    canonical.write_text(cleaned, encoding="utf-8")
    print(f"Dipromosikan {ver_file.name} -> {canonical.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Microdrama v2.0 Video Dissector & Repair Loop")
    sub = parser.add_subparsers(dest="command", required=True)

    p_diag = sub.add_parser("diagnose", help="Cari akar masalah & perbaikan bedah dari gejala hasil generate")
    p_diag.add_argument("query", nargs="?", default="")
    p_diag.add_argument("--list", action="store_true", help="Tampilkan seluruh 24 pola gejala")

    p_ana = sub.add_parser("analyze", help="Bedah klip MP4 dengan ffmpeg dan cocokkan dengan timecode SHOT")
    p_ana.add_argument("video", help="Path berkas video (.mp4)")
    p_ana.add_argument("--prompt", required=True, help="Path berkas prompt-video.md")
    p_ana.add_argument("--scene", type=int, default=1, help="Nomor scene (default: 1)")
    p_ana.add_argument("--out-dir", default=None, help="Folder keluaran contact sheet")

    p_br = sub.add_parser("branch", help="Buat cabang versi prompt-video-vN.md tanpa menimpa versi lama")
    p_br.add_argument("prompt_file", help="Path prompt-video.md")
    p_br.add_argument("--note", default="", help="Catatan alasan perbaikan")

    p_pro = sub.add_parser("promote", help="Promosikan prompt-video-vN.md menjadi prompt-video.md aktif")
    p_pro.add_argument("version_file", help="Path berkas versi (mis. prompt-video-v2.md)")

    args = parser.parse_args(argv)
    dispatch = {
        "diagnose": cmd_diagnose,
        "analyze": cmd_analyze,
        "branch": cmd_branch,
        "promote": cmd_promote,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
