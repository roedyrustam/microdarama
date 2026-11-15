# Dokumentasi Lengkap — Microdrama v2.0 (Sovereign Precision Edition)

> **Bilingual Guide (Bahasa Indonesia & English)**: Panduan lengkap untuk AI Agent, Sutradara, dan Kreator Video AI menggunakan **Microdrama v2.0**.

---

## 1. Filosofi Inti / Core Philosophy

AI video tidak gagal secara acak; ia gagal secara **prediktif**:
1. Wajah tokoh berubah antar klip → dicegah lewat **blok teks terkunci huruf-per-huruf** (`cast.md`) dan **sheet karakter 3 panel berlabel nama**.
2. Adegan terasa seperti montase trailer → dicegah lewat **penegasan `ONE continuous moment, NOT a montage`** dan **perpindahan posisi kamera di setiap potongan** (`Never two consecutive shots from the same position`).
3. Figuran bergerak serempak seperti paduan suara → dicegah lewat blok wajib **`MOVEMENT NOTE`** yang memecah reaksi figuran menjadi tiga aksi terpisah.
4. Teks/label/layar HP menjadi huruf acak → dicegah lewat **Beat Tanpa Teks**, `no labels, no printed text`, dan `screen always angled away from camera`.
5. Tokoh bocor ke sisi pintu yang salah saat memakai dua plate lokasi → dicegah lewat **Triad Lokasi Ganda**: Peta Referensi di `LOCATION` + Tag Lokasi di setiap `SHOT` + Kunci Posisi di `CONTINUITY`.
6. Prompt gagal setelah membuang kredit → dicegah sebelum generate lewat **25-Point Automated Checker** (`check_prompts.py`) dan diperbaiki setelah generate secara bedah-terukur lewat **`dissect_video.py`**.

---

## 2. Peningkatan Utama v2.0 dibanding v1.3.0 / Key Upgrades in v2.0

| Area | v1.3.0 (Asli) | v2.0 (Sovereign Precision Edition) |
|---|---|---|
| **Static Verification** | 12 cek dasar di `check_prompts.py` + 14 item checklist manual yang sering terlewat | **25 cek otomatis** di `check_prompts.py`: mendeteksi tabrakan posisi kamera berurutan, paritas `naskah.md` ↔ `prompt-video.md`, angka mentah di dialog, pacing bicara (kata/detik), detektor klise Indonesia/Inggris, tanda wajah tanpa fungsi cerita, kontaminasi kata orang di shot celah pintu, sinkronisasi figuran, skor rubrik, dan duplikasi aset lintas episode. |
| **Workflow Automation** | Salin-tempel manual antar 7 berkas yang rawan human-error | **`microdrama_cli.py`**: `init`, `add-ep`, `sync` (sinkronisasi otomatis blok `cast.md`/`set.md` ke semua episode), dan `board` (membuat `board.html` interaktif). |
| **Production Studio UI** | Hanya file markdown mentah | **`board.html`**: Studio Produksi lokal mode gelap dengan ringkasan Brief/Konsep/Rubrik, Kartu Cast/Set, Timeline Shot visual berdurasi proporsional, Lencana Risiko, Status Verifikasi Langsung, dan tombol **Copy Clean Prompt** satu klik. |
| **Post-Gen Repair Loop** | Perintah `ffmpeg` manual dan tabel teks pasif | **`dissect_video.py`**: `diagnose` (pencarian cepat 24 gejala → penyebab → perbaikan 1-2 kalimat), `analyze` (ekstraksi cut `ffmpeg` & perbandingan dengan timecode `SHOT`), `branch` & `promote` (manajemen versi `-v2.md`, `-v3.md`). |
| **Model Deployment** | Tidak ada panduan parameter per model | **`references/model-profiles.md`**: Matriks penerapan untuk Kling, Seedance, Veo, Sora, Runway, Wan, GPT Image, Flux, dan Midjourney tanpa mengotori isi blok prompt. |
| **Benchmark Lengkap** | 1 proyek utuh (`alamat-yang-sama`) + potongan `unit-7` | **2 proyek utuh terverifikasi penuh** (`alamat-yang-sama` 3 ep + `unit-7` 1 ep) sekaligus mempertahankan potongan lepas untuk kompatibilitas. |

---

## 3. Alur Kerja 7 Gerbang / 7-Gate Production Workflow

### Gerbang 0 · Tempat Kerja / Workspace
- Proyek baru disalin dari `assets/template/` (atau lewat `python assets/tools/microdrama_cli.py init <folder>`).
- Proyek lanjutan episode membaca `konsep.md`, `cast.md`, dan `set.md` yang sudah ada **tanpa mengubah deskripsi tokoh/set lama**.

### Gerbang 1 · Brief (`references/brief.md`)
- Selalu **2 kartu tanya** (maksimal 4 pertanyaan per kartu).
- **Zero-Default Rule**: Jangan pernah mengisi sendiri Rasio, Durasi, atau Jumlah Episode. Jumlah Shot **tidak pernah ditanya** di depan.
- Benturan logika (misalnya topik malam + look siang hari) dijelaskan transparan dan dicatat di bagian `Penyesuaian` di `brief.md`.

### Gerbang 2 · Konsep (`references/konsep.md` + `references/copywriting.md`) → **Persetujuan 1**
- Logline 1 kalimat dengan ketimpangan informasi (penonton tahu sesuatu yang tokoh belum tahu).
- Premis 3 baris wajib: `(1) Cerita`, `(2) Detail meleset`, `(3) Aturan tokoh`.
- Arc per episode (untuk format seri) + **3 alternatif Hook dari rumus berbeda** (`Suara dulu`, `Pertanyaan terbuka`, `Angka atau nama`, `Hening`, `Pembalik langsung`).
- Dinilai dengan **Rubrik 9 Aspek** (semua ≥ 4, rata-rata ≥ 4,3, dan dua baris gerbang `Konsisten` & `Tanpa teks` wajib YA).

### Gerbang 3 · Cast, Set & Properti (`references/cast.md`) → **Persetujuan 2**
- **Bentuk Panjang** (6 atribut fisik + `WARDROBE`) untuk sheet karakter 3 panel.
- **Bentuk Pendek** (1 baris + `[gambar_slug]`) untuk blok `CHARACTERS` prompt video.
- **Aturan Wajah Biasa**: Tanpa bekas luka, tahi lalat, atau tato kecuali berfungsi sebagai penanaman plot (`Tanda wajah karena cerita:`) dan dikunci di `CRITICAL`.
- **Set (6 elemen wajib)** + **Properti** (`Berpelat` untuk kendaraan/objek kompleks, `Teks saja` untuk kardus/foto).

### Gerbang 4 · Naskah + Shot List (`references/konsep.md`) → **Persetujuan 3**
- Tulis dialog sebagai cerita dulu (`s01..sNN`), lalu pecah menjadi tabel Shot List.
- **Aturan Emas Blocking**: Jangan pernah dua shot berurutan dari posisi kamera yang sama; pertahankan aturan sumbu 180° untuk arah pandang (*eyeline*).
- Tandai semua **Shot Berisiko** (7 faktor kerawanan AI video) di tabel khusus dan laporkan ke user untuk diputuskan.
- Pecah menjadi **Scene 4–30 detik** (pindah lokasi = scene baru; tidak pernah memotong di tengah dialog).

### Gerbang 5 · Prompt Aset (`references/prompt-aset.md`)
- Hanya buat aset baru di episode berjalan; aset lama masuk daftar `Pakai ulang dari ep ...`.
- **Sheet Karakter 3 Panel**: `LEFT PANEL` (close-up, mata ke lensa), `MIDDLE PANEL` (full body depan), `RIGHT PANEL` (full body belakang) + label nama tercetak di sudut kiri bawah panel kiri.
- **Set Plate**: 24mm, tanpa orang (`absolutely no people`), diambil dari sudut wide shot terpenting.

### Gerbang 6 · Prompt Video (`references/prompt-video.md`)
- Satu blok prompt = satu scene = 4–30 detik, dengan **11 blok tetap berurutan**:
  1. `VIDEO STYLE & FORMAT`
  2. `LANGUAGE`
  3. `OPTICS`
  4. `CAMERA`
  5. `LIGHTING`
  6. `CRITICAL`
  7. `CHARACTERS`
  8. `LOCATION` *(+ `CONTINUITY` opsional di sini jika ada multi-plate atau properti persisten)*
  9. `AUDIO`
  10. `MOVEMENT NOTE`
  11. `SHOT BREAKDOWN`
- **Triad Lokasi Ganda**: Jika >1 plate lokasi dalam satu generate, wajib ada (1) Peta Referensi di `LOCATION`, (2) Tag lokasi `— SISI, tempat, sudut —` di tiap baris `SHOT`, dan (3) Kunci posisi di `CONTINUITY`.

### Gerbang 7 · Verifikasi, Studio Visual & Perbaikan (`references/verifikasi.md`)
```bash
# 1. Jalankan 25-point verifier
python assets/tools/check_prompts.py film/alamat-yang-sama --strict

# 2. Sinkronkan blok terkunci (jika ada revisi di cast.md / set.md)
python assets/tools/microdrama_cli.py sync film/alamat-yang-sama

# 3. Bangun Studio Produksi HTML
python assets/tools/microdrama_cli.py board film/alamat-yang-sama

# 4. Diagnosis & bedah video pasca-generate
python assets/tools/dissect_video.py diagnose "tokoh bocor ke sisi lain pintu"
python assets/tools/dissect_video.py analyze hasil_scene1.mp4 --prompt film/alamat-yang-sama/ep01/prompt-video.md
```

---

## 4. Referensi Cepat Perintah CLI / CLI Quick Reference

| Perintah | Fungsi |
|---|---|
| `python assets/tools/check_prompts.py <folder> [--json] [--strict]` | Validasi 25 poin integritas proyek |
| `python assets/tools/microdrama_cli.py init <folder> --title "Judul"` | Membuat proyek baru dari template |
| `python assets/tools/microdrama_cli.py add-ep <folder> 2 --title "Judul Ep"` | Menambah episode baru + daftar reuse otomatis |
| `python assets/tools/microdrama_cli.py sync <folder>` | Menyelaraskan blok cast/set terkunci & lampiran ke seluruh prompt |
| `python assets/tools/microdrama_cli.py board <folder>` | Menghasilkan `board.html` interaktif |
| `python assets/tools/dissect_video.py diagnose "<gejala>"` | Mencari akar masalah & perbaikan bedah 1-2 kalimat |
| `python assets/tools/dissect_video.py analyze <mp4> --prompt <md>` | Membedah cut video via `ffmpeg` dan membandingkannya dengan timecode shot |
| `python assets/tools/dissect_video.py branch <prompt-video.md>` | Membuat cabang perbaikan `-v2.md`, `-v3.md` tanpa menimpa versi lama |
| `python assets/tools/dissect_video.py promote <prompt-video-v2.md>` | Mengembalikan versi terbaik menjadi `prompt-video.md` aktif |
