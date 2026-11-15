# Changelog

## 2.0.0 — 2026-11-16 (Sovereign Precision Edition)

**Rekonstruksi presisi penuh dengan verifikasi otomatis 25 poin, sinkronisasi lintas berkas, studio produksi HTML interaktif, dan tool bedah video pasca-generate.**

- **`assets/tools/check_prompts.py` (Upgrade 12 → 25 Cek)**:
  - Menambahkan detektor otomatis **tabrakan posisi kamera berurutan** di `naskah.md` maupun `SHOT BREAKDOWN` `prompt-video.md`.
  - Menambahkan verifikasi **paritas `naskah.md` ↔ `prompt-video.md`** (jumlah scene, durasi per scene, dan penomoran shot).
  - Menambahkan **detektor angka mentah & pacing bicara** di baris dialog (maks. 3,2 kata/detik untuk menjaga lip-sync tetap alami).
  - Menambahkan **pemindai klise otomatis** (dialog sinetron Indonesia, deskripsi klise, dan kata kosong bahasa Inggris) lintas `konsep.md`, `naskah.md`, dan `prompt-video.md`.
  - Menambahkan **detektor tanda wajah tanpa fungsi cerita** (mencegah luka/tahi lalat/tato lolos ke prompt kecuali ada bagian `Tanda wajah karena cerita:` di `cast.md`).
  - Menambahkan **detektor kontaminasi kata orang di shot celah/kaca**, **detektor kontras ketiadaan benda**, **validasi anti-sinkronisasi figuran** di `MOVEMENT NOTE`, **validasi rubrik `konsep.md`**, dan **audit reuse aset lintas episode**.
  - Menambahkan opsi `--json` dan `--strict` dengan dukungan UTF-8 native di Windows.
- **`assets/tools/microdrama_cli.py` (Baru)**:
  - Subperintah `init`, `add-ep`, `sync` (sinkronisasi otomatis blok `cast.md`/`set.md` dan baris `Lampirkan:`), `check`, dan `board`.
  - `board` menghasilkan **`board.html`**: Studio Produksi lokal mode gelap dengan visualisasi timeline shot, penanda risiko, lencana lampiran gambar referensi, status checker langsung, dan tombol salin prompt bersih sekali klik.
- **`assets/tools/dissect_video.py` (Baru)**:
  - Subperintah `diagnose` (kueri matriks 24 gejala → penyebab → perbaikan 1–2 kalimat), `analyze` (analisis titik potong `ffmpeg` & pembanding timecode `SHOT`), `branch`, dan `promote` untuk siklus perbaikan `-v2.md`, `-v3.md`.
- **`references/model-profiles.md` (Baru)**:
  - Panduan penerapan model-agnostik untuk Kling 3.0/4.0, Seedance 2.0, Veo 3, Sora 2, Runway Gen-4, Wan 2.6, GPT Image 2.5, dan Flux 2 tanpa mengotori isi blok prompt.
- **`references/konsep.md` & `references/copywriting.md` (Diperkaya)**:
  - Menambahkan hukum **sumbu 180 derajat & vektor eyeline** serta anggaran kata per detik untuk akurasi lip-sync AI video.
- **`assets/contoh/unit-7/` (Baru)**:
  - Melengkapi contoh "Unit 7" menjadi satu proyek utuh yang lolos penuh `check_prompts.py`, sembari tetap mempertahankan berkas lepas di `assets/contoh/`.
- **Dokumentasi Arsitektur**: Menambahkan `PRD.md`, `ERD.md`, `DOCUMENTATION.md`, dan suite pengujian otomatis `tests/test_microdrama.py`.

## 1.3.0 — 2026-11-12

**Tokoh tanpa tanda di wajah.** Bentuk panjang tokoh tidak lagi wajib memuat "satu ciri unik".
- `references/cast.md`: daftar wajib tinggal enam hal; bagian baru "Tanpa tanda di wajah".
- Template `cast.md`: slot ciri unik dihapus.
- Contoh `Unit 7`: luka Rafa dan tahi lalat Bu Dian dihapus; contoh `alamat-yang-sama`: tahi lalat Adit dan Ibu tetap sebagai pengecualian cerita.

## 1.2.0 — 2026-10-31

**Pelajaran dari empat uji generate sungguhan.**
- Blok opsional `CONTINUITY` di antara `LOCATION` dan `AUDIO`.
- Peta referensi di awal `LOCATION` dan tag lokasi di tiap baris `SHOT` untuk scene multi-plate.
- Shot lewat celah/kaca tanpa kata orang; ketiadaan benda sebagai permukaan rata.
- Tabel shot berisiko di gerbang 4 dan loop perbaikan pasca-generate di `references/verifikasi.md`.

## 1.1.0 — 2026-10-31

**Hasil uji jalan dengan proyek "Alamat yang Sama"** — microdrama 3 episode × 30 detik.
- Brief menjadi dua kartu tanya; beat tanpa teks; properti berulang; `assets/tools/check_prompts.py`.

## 1.0.0 — 2026-10-31

Rilis pertama. Tujuh gerbang dengan tiga persetujuan, tiga preset, cast bible panjang & pendek, sheet 3 panel, prompt 11 blok, template, dan contoh "Unit 7".
