# Model Profiles — Panduan Deployment Model-Agnostik

**Aturan Keras:** Jangan pernah menulis sintaks khusus model, rasio (`9:16`), durasi parameter (`--duration 10`), atau nama berkas (`.png`) di dalam blok kode prompt di `prompt-aset.md` dan `prompt-video.md`.

Gunakan tabel di bawah ini untuk memandu **user** saat men-copy-paste keluaran Microdrama ke UI atau API model AI gambar dan AI video pilihannya.

---

## 1. AI Gambar (Untuk Gerbang 5 — `prompt-aset.md`)

| Model Gambar | Pengaturan Rasio Disarankan | Cara Menggunakan Prompt Microdrama | Catatan Penting |
|---|---|---|---|
| **GPT Image 2.5 / ChatGPT Images** | `16:9` (atau `3:2`) untuk sheet 3-panel; sesuai target adegan untuk plate | Paste isi blok prompt mentah-mentah | Sangat patuh pada label teks `label reading <NAMA>` dan instruksi 3 panel terpisah |
| **Flux 2 Pro / Flux Kontext** | `16:9` untuk sheet 3-panel; `3:2` / `16:9` untuk set plate | Paste blok prompt; jika model sensitif pada kata `Avoid:`, pindahkan isi `Avoid:` ke kolom *Negative Prompt* jika UI memisahkannya | Cek kesamaan wajah kiri-tengah-kanan sebelum menyimpan sebagai `<nama>_sheet.png` |
| **Midjourney v7** | Tambahkan `--ar 16:9` **di UI / akhir bar saat generate**, bukan di berkas teks | Hapus baris `Avoid:` dan pindahkan ke `--no ...` pada bar Discord/Web UI | Pastikan `--stylize` rendah (`50–100`) agar warna tidak berlebihan dan tetap datar untuk sheet |
| **Google Imagen 4 / Gemini Image** | `16:9` untuk sheet, `16:9` atau `9:16` untuk set plate | Paste blok prompt langsung | Beri instruksi eksplisit bahwa ini *production reference sheet* bila UI menyediakan preset foto |

---

## 2. AI Video Multishot + Audio Native (Untuk Gerbang 6 — `prompt-video.md`)

| Model Video | Batas Durasi / Klip | Cara Melampirkan `[gambar_x]` | Catatan Perilaku Model & Mitigasi Microdrama |
|---|---|---|---|
| **Kling 4.0 / Kling 3.0** | 5–30 detik (optimal 10–15s / 30s multishot) | Unggah semua berkas di baris `Lampirkan:` sebagai *Elements / Reference Images*, lalu ikat masing-masing ke token `@Element` atau `[gambar_x]` sesuai UI | Sangat kuat menjaga wajah dari sheet 3 panel, tetapi sensitif terhadap dua plate lokasi dalam satu klip — **wajib memakai Triad Lokasi Ganda** |
| **Seedance 2.0** | 5–30 detik | Unggah berkas di `Lampirkan:` ke slot *Reference Subjects & Scene* sesuai urutan | Menangani perpindahan kamera cepat dengan baik; blok `MOVEMENT NOTE` sangat krusial untuk memecah sinkronisasi figuran |
| **Google Veo 3** | 4–8 detik (atau *extend* berantai hingga 30s) | Unggah berkas di baris `Lampirkan:` sebagai *Ingredients / Reference Frames* | Audio & pelafalan dialog paling akurat jika angka ditulis sebagai kata dan pacing ≤ 2,8 kata/detik; sangat peka pada `LANGUAGE` |
| **Sora 2** | 5–20 detik / *Storyboard mode* | Unggah berkas referensi ke *Asset Library* / *Storyboard frames* | Suka memperhalus bayangan jika `LIGHTING` terlalu umum — selalu sertakan suhu Kelvin dan *negative fill* |
| **Runway Gen-4** | 5–10 detik per generasi | Gunakan set plate sebagai *Frame/Scene Reference* dan sheet karakter sebagai *Character Reference* | Jika episode 30 detik memakai Runway (maks 10s), pecah di Gerbang 4 menjadi `10 + 10 + 10` detik mengikuti jeda alami |
| **Wan 2.6** | 5–15 detik | Lampirkan *Subject Sheet* & *Background Plate* pada input referensi | Wajib menjaga kalimat penutup `no freeze frame, no fade to black` agar akhir gerakan tidak melambat kaku |

---

## 3. Aturan Pemetaan Saat User Memilih Model Berdurasi Pendek (Maks 10–15s)

Meskipun secara global Microdrama mendukung **4–30 detik** per scene, apabila user di awal Gerbang 1 menyatakan akan memakai model yang batas per klipnya 10 detik atau 15 detik:
- Tetap biarkan blok prompt bersih dari nama model.
- Di Gerbang 4 (`epNN/naskah.md`), pecah episode mengikuti alur cerita dengan batas atas efektif sesuai kebutuhan user (misalnya 30 detik dipecah menjadi `10 + 10 + 10` atau `14 + 16` detik), sehingga setiap blok `prompt-video.md` langsung siap generate tanpa perlu pemotongan ulang.
