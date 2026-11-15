---
name: microdrama
description: "Merancang konsep dan MENULIS PROMPT presisi untuk video AI live-action — microdrama vertikal berseri, short movie, atau scene/trailer tunggal — dilengkapi verifikator semantik 25-poin, CLI sinkronisasi otomatis, Studio Produksi HTML (`board.html`), dan tool bedah video pasca-generate (`dissect_video.py`). Skill ini TIDAK menggenerate media apa pun: keluarannya berkas teks terverifikasi berisi konsep cerita, cast & set bible terkunci, shot list ber-audit risiko & sumbu 180°, prompt sheet karakter 3-panel dengan nama tercetak, prompt plate set/properti, dan prompt video sebelas blok (4–30 detik per generate) yang siap di-copy ke AI gambar dan AI video mana pun. Gunakan saat user minta 'microdrama', bikin microdrama, drama pendek vertikal, short movie, film pendek AI, scene atau trailer, prompt video AI, shot list, sheet karakter, memperbaiki klip AI yang plot hole, atau melanjutkan episode seri yang sudah ada."
author: "Roedy Rustam"
version: "2.0.0"
license: MIT
metadata:
  author: Roedy Rustam
  version: "2.0.0"
  updated: "2026-11-16"
---

# Microdrama v2.0 — Perancang Produksi & Penulis Prompt Video AI Presisi Tinggi

**v2.0.0 (Sovereign Precision Edition) · by Roedy Rustam · MIT.**

Skill ini adalah **asisten sutradara, penulis naskah, dan script supervisor otomatis — bukan generator media**. Tidak ada gambar, video, atau audio yang digenerate di sini. Keluarannya adalah berkas teks produksi terverifikasi dan studio HTML interaktif (`board.html`) agar user tinggal men-generate aset dan klip di model AI pilihannya (Kling, Seedance, Veo, Sora, Runway, Wan, GPT Image, Flux) dengan tingkat kegagalan serendah mungkin.

Satu tulang belakang, tiga preset:

| | MICRODRAMA | SHORT MOVIE | SCENE / TRAILER |
|---|---|---|---|
| Bentuk | seri berepisode | satu cerita utuh | satu blok tunggal |
| Struktur naskah | hook keras 3 detik awal → satu perubahan keadaan → cliffhanger | tiga babak dengan resolusi | satu momen tegang tanpa resolusi |
| Lintas episode | cast, set, properti dipakai ulang lintas episode | — | — |
| Cocok untuk | drama bersambung yang menahan penonton tidak scroll | film pendek, tugas, festival, portofolio | teaser, uji look, validasi satu adegan |

---

## Alur Kerja — Tujuh Gerbang Presisi (Jangan Dilompati)

### 0 · Tempat Kerja & Inisialisasi
- Tanyakan folder proyek jika belum jelas. **Jangan hardcode lokasi mana pun.**
- **Proyek baru:** jalankan `python assets/tools/microdrama_cli.py init <folder> --title "<Judul>"` (atau salin `assets/template/`).
- **Lanjut episode:** jalankan `python assets/tools/microdrama_cli.py add-ep <folder> <N> --title "<Judul Ep>"`. Baca `konsep.md`, `cast.md`, dan `set.md` yang ada lalu **pakai apa adanya** — jangan ubah deskripsi lama.

### 1 · BRIEF — Tanya Dulu, Jangan Menebak
Baca `references/brief.md`.
- Alat tanya maksimal 4 pertanyaan per kartu → brief selalu **tepat dua kartu**:
  - **Kartu 1:** Topik · Format · Rasio · Bahasa dialog
  - **Kartu 2:** Durasi · Jumlah episode *(lewati jika Scene tunggal)* · Look
- Lewati item yang sudah dijawab di kalimat pertama user. **Zero-Default Rule:** kosongkan semua nilai yang belum dijawab; jangan pernah menebak rasio, durasi, atau jumlah episode.
- Jika jawaban saling bentrok (misal topik malam + look siang hari), sebutkan bentroknya dalam satu kalimat, tawarkan resolusi, dan catat di `Penyesuaian` pada `brief.md`.
- **Jumlah shot tidak pernah ditanyakan.** Shot muncul dari kebutuhan naskah.
- **Output:** `brief.md`

### 2 · KONSEP → **Persetujuan 1 (Wajib Berhenti)**
Baca `references/konsep.md` dan `references/copywriting.md`.
- **Output:** `konsep.md` berisi:
  1. **Logline** (1 kalimat dengan ketimpangan informasi).
  2. **Premis 3 baris** wajib: *(1) Cerita*, *(2) Detail meleset*, *(3) Aturan tokoh*.
  3. **Arc per episode** (untuk format seri).
  4. **3 Hook alternatif dengan rumus berbeda** (*Suara dulu*, *Pertanyaan terbuka*, *Angka atau nama*, *Hening*, *Pembalik langsung*).
  5. **Skor Rubrik 9 Aspek** (semua aspek ≥ 4, rata-rata ≥ 4,3, dan dua gerbang Ya/Tidak — *Konsisten* & *Tanpa teks* — wajib **YA**).
- Berhenti. Jangan lanjut ke Gerbang 3 sebelum user memilih hook dan menyetujui konsep.

### 3 · CAST, SET & PROPERTI → **Persetujuan 2 (Wajib Berhenti)**
Baca `references/cast.md`.
- **Output:** `cast.md` dan `set.md`.
  - **Tokoh (`cast.md`):** Bentuk panjang (6 atribut fisik wajib + `WARDROBE` rinci) untuk sheet, Bentuk pendek (1 baris + `[gambar_<slug>]`) untuk blok `CHARACTERS`, dan Nada tubuh (untuk manusia).
  - **Aturan Wajah Biasa:** Dilarang memberi bekas luka, tahi lalat, tato, atau tindik sebagai "jangkar" karena model AI melebih-lebihkannya. Pengecualian hanya jika punya fungsi tanam-dan-bayar di naskah (ditulis `Tanda wajah karena cerita:` di `cast.md` dan dikunci di `CRITICAL`).
  - **Set (`set.md`):** 6 elemen wajib termasuk **semua pintu dan jalan masuk yang dipakai arc** dan satu benda ganjil.
  - **Properti (`set.md`):** Dikunci **Berpelat** (`[gambar_<slug>]` + `<slug>_plate.png`) atau **Teks saja** (disalin identik ke `LOCATION`), disertai `no labels, no printed text, no logos` / `licence plate blank`.
- Berhenti. Mengganti deskripsi setelah prompt ditulis berarti mematahkan konsistensi seluruh seri.

### 4 · NASKAH + SHOT LIST → **Persetujuan 3 (Wajib Berhenti)**
Baca `references/konsep.md` bagian Naskah & Shot List dan `references/copywriting.md`.
- **Output:** `epNN/naskah.md` berisi Dialog ber-nomor shot (`s01..sNN`), Shot List, tabel **Shot Berisiko**, dan **Pembagian Scene**.
- **Aturan Naskah & Blocking:**
  - Tulis dialog sebagai cerita dulu, pastikan bebas klise sinetron, kalimat pendek (≤12–14 kata per kalimat untuk layar vertikal), angka ditulis sebagai kata (`dua ribu sebelas`), dan kecepatan bicara ≤3,2 kata/detik.
  - **Jangan pernah dua shot berurutan dari posisi kamera yang sama.** Jaga aturan sumbu 180° dan arah pandang (*eyeline*).
  - **Pembagian Scene:** 1 scene = 1 prompt video = 1 kali generate = **4–30 detik**. Pindah lokasi selalu scene baru. Jangan pernah memotong di tengah dialog.
  - Cek total durasi terhadap `brief.md`. Jika lewat, lapor dan tawarkan shot mana yang dipotong.
  - Jika blocking butuh elemen set baru (misal pintu dapur), tambahkan ke `set.md` sebagai revisi penambahan sebelum prompt ditulis.
  - Tandai semua **Shot Berisiko** (7 faktor kerawanan AI video) di `naskah.md`, tawarkan alternatif amannya, dan **biarkan user memutuskan**.

### 5 · PROMPT ASET
Baca `references/prompt-aset.md`.
- **Output:** `epNN/prompt-aset.md` hanya berisi aset yang **baru muncul di episode itu**; aset episode lama masuk baris `Pakai ulang dari ep NN, jangan generate ulang: ...`.
- **Sheet Karakter:** selalu 3 panel (`LEFT PANEL` close-up menatap lensa, `MIDDLE PANEL` full body depan, `RIGHT PANEL` full body belakang), latar abu netral polos, label nama tercetak di sudut kiri bawah panel kiri, dan `missing head` + `different faces between panels` di daftar `Avoid:`.
- **Set Plate:** tanpa orang (`absolutely no people`), lensa 24mm, horizon rata, dikomposisikan dari **sudut wide shot terpenting**.

### 6 · PROMPT VIDEO
Baca `references/prompt-video.md` dan `references/model-profiles.md` (untuk catatan pengaturan tool di luar blok).
- **Output:** `epNN/prompt-video.md` — satu judul markdown + baris `Lampirkan:` **di luar** blok kode, dan satu blok prompt **11 bagian berurutan** (`VIDEO STYLE & FORMAT` → `LANGUAGE` → `OPTICS` → `CAMERA` → `LIGHTING` → `CRITICAL` → `CHARACTERS` → `LOCATION` → `[CONTINUITY opsional]` → `AUDIO` → `MOVEMENT NOTE` → `SHOT BREAKDOWN`).
- Jalankan `python assets/tools/microdrama_cli.py sync <folder>` untuk memastikan salinan blok dari `cast.md`/`set.md` dan daftar `Lampirkan:` identik 100%.
- **Triad Lokasi Ganda:** Jika >1 plate lokasi dalam satu scene, wajib memakai: (1) Peta Referensi di awal `LOCATION`, (2) Tag lokasi `— SISI, tempat, sudut —` di tiap baris `SHOT`, dan (3) Kunci posisi di `CONTINUITY`.

### 7 · VERIFIKASI, STUDIO PRODUKSI & PERBAIKAN PASCA-GENERATE
Baca `references/verifikasi.md`.
1. Jalankan **25-Point Verifier**:
   ```bash
   python assets/tools/check_prompts.py <folder_proyek> --strict
   ```
   Perbaiki semua masalah hingga keluar `Semua cek lolos.`.
2. Bangun **Studio Produksi Visual HTML**:
   ```bash
   python assets/tools/microdrama_cli.py board <folder_proyek>
   ```
   Menghasilkan `<folder_proyek>/board.html` berisi timeline shot, status cek, lencana risiko, lampiran gambar, dan tombol salin prompt bersih sekali klik.
3. Serahkan daftar berkas, cara pakai, link `board.html`, dan catatan kelemahan jujur (jika ada).
4. **Jika user kembali membawa klip hasil generate yang plot hole**, jalankan siklus perbaikan via `assets/tools/dissect_video.py`:
   - `analyze` klip dengan `ffmpeg` (titik potong & contact sheet 2 fps) dan Whisper (transkrip dialog).
   - `diagnose` akar penyebab dari 24-pola tabel gejala.
   - `branch` ke `prompt-video-v2.md`, perbaiki **1–2 kalimat bedah saja**, uji dengan rasio/model/referensi identik, atau `promote` versi terbaik kembali ke `prompt-video.md`.

---

## Aturan Keras (Wajib Dipatuhi Tanpa Pengecualian)

1. **Tidak menggenerate media apa pun di sini.** Hanya berkas teks & studio HTML lokal.
2. **Zero-Default pada Brief:** Rasio, durasi, jumlah episode selalu ditanya; jumlah shot tidak pernah ditanya.
3. **Rasio, fps, resolusi, seed, dan nama model tidak pernah masuk ke dalam blok prompt** (termasuk kata `vertical` dan `horizontal`).
4. **Header untuk manusia & nama berkas (`rafa_sheet.png`) selalu di luar blok kode.**
5. **Tidak ada subtitle, caption, atau teks di layar.** Kata `subtitle`/`caption` hanya boleh ada sebagai larangan di dalam blok `LANGUAGE`.
6. **Beat penting tidak boleh bergantung pada tulisan yang harus dibaca.** Terjemahkan ke visual atau suara.
7. **Dialog ditanam di dalam blok `SHOT BREAKDOWN`** dalam bahasa pilihan user; tidak ada berkas audio/TTS terpisah. Angka ditulis sebagai kata.
8. **Prompt 100% model-agnostik (Inggris)**; tanpa sintaks khusus Kling, Seedance, Veo, atau Sora di dalam prompt.
9. **Blok `cast.md`, `set.md`, dan properti disalin identik huruf per huruf.** Tanpa tanda wajah kecuali `Tanda wajah karena cerita:`.
10. **`MOVEMENT NOTE` wajib ada** dan jika >2 orang di frame, **wajib memecah figuran menjadi tiga aksi terpisah serta melarang gerakan serempak**.
11. **Satu scene = satu generate = 4–30 detik**; tidak pernah memotong di tengah dialog; timecode selalu mulai `00:00`.
12. **Shot lewat celah/kaca/lubang kunci:** tulis hanya apa yang terlihat; **dilarang keras menulis kata orang** termasuk larangan seperti `no face, no head, nobody`.
13. **Ketiadaan benda/bekas:** tulis sebagai permukaan rata (`flat, level with the floor, nothing on it, not an object`); **dilarang memakai kata kontras** (`darker`, `deeper colour`).
14. **Jangan menumpuk penegasan benda berulang-ulang** di banyak blok (maksimal 3 benda di `CONTINUITY`, masing-masing cukup satu butir presisi).

---

## Struktur Repositori

| Berkas | Fungsi |
|---|---|
| `PRD.md` · `ERD.md` · `DOCUMENTATION.md` | Spesifikasi arsitektur, relasi entitas-token, dan dokumentasi bilingual lengkap |
| `assets/template/` | Kerangka kosong 7 berkas produksi (`brief`, `konsep`, `cast`, `set`, `naskah`, `prompt-aset`, `prompt-video`) |
| `assets/tools/check_prompts.py` | Verifikator otomatis 25-poin (Python 3 stdlib, `--json`, `--strict`) |
| `assets/tools/microdrama_cli.py` | CLI produksi (`init`, `add-ep`, `sync`, `board`, `check`) + generator `board.html` |
| `assets/tools/dissect_video.py` | Tool bedah klip (`diagnose`, `analyze` ffmpeg, `branch`, `promote`) |
| `assets/contoh/alamat-yang-sama/` | Proyek benchmark lengkap 3 episode × 30 detik (lolos 25 cek + `board.html`) |
| `assets/contoh/unit-7/` | Proyek benchmark lengkap "Unit 7" Ep 01 (lolos 25 cek + `board.html`) |
| `references/*.md` | 8 manual produksi per gerbang + profil deployment model (`model-profiles.md`) |
| `tests/test_microdrama.py` | Suite pengujian unit & integrasi untuk verifier, CLI, dan dissector |

---

## Orchestration & Integration

Skill `microdrama` terhubung langsung dengan ekosistem skill dan subagen berikut:
- **`anti-slop` & `zero-tech-debt-auditor`**: Mengawal ketajaman copywriting naskah bebas klise, kebersihan UI `board.html`, dan kode Python 3 bebas dependensi.
- **`ai-prompt-engineering-expert` & `structured-output-contracts`**: Menjamin format prompt 11-blok dan skema keluaran `--json` deterministik.
- **`data-visualization-expert` & `senior-frontend`**: Merancang tampilan timeline visual, kartu aset, dan tombol salin studio `board.html`.
- **`autonomous-tdd-debugger`**: Memverifikasi keakuratan parser dan regex di `check_prompts.py` lewat test suite `unittest`.
- **`brainstorming` & `prd-architect`**: Mengorkestrasi pemecahan masalah kreatif di Gerbang 1–2 sebelum penulisan kode atau prompt dimulai.
