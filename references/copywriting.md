# Copywriting — Anti-Generik & Pacing Dialog

Dibaca di Gerbang 2 dan 4. Tujuannya satu: naskah tidak boleh terdengar seperti naskah sinetron yang sudah pernah didengar penonton seribu kali, dan setiap baris dialog harus dapat diucapkan alami oleh model AI video.

## 8 Hukum Anti-Generik

1. **Spesifik mengalahkan dramatis.** *"Dia marah"* lemah. *"Dia menutup laptopnya terlalu pelan"* kuat. Penonton menyimpulkan emosi sendiri, dan kesimpulan sendiri selalu lebih menghantam.
2. **Satu detail meleset per adegan.** Sesuatu yang janggal dan belum dijelaskan. Itu yang menahan penonton tidak scroll.
3. **Diam adalah alat.** Empat detik tanpa dialog di tengah konfrontasi lebih keras daripada teriakan. Tulis diamnya sebagai nomor shot tersendiri dan beri durasi pasti.
4. **Jangan jelaskan yang sudah terlihat.** Kalau wajahnya sudah menunjukkan keterkejutan, dialog tidak boleh berbunyi *"Aku kaget!"*.
5. **Tokoh punya satu aturan tetap.** Kebiasaan yang selalu atau tidak pernah dia lakukan di semua episode. Saat aturan itu akhirnya dilanggar, itulah momen klimaks emosional seri.
6. **Tanam sebelum bayar.** Benda, nama, atau kebiasaan yang jadi kunci akhir cerita harus muncul sekilas lebih awal tanpa ditunjuk-tunjuk.
7. **Akhiri pada gerakan, bukan pada pose.** Adegan berhenti tepat saat orang atau benda mulai bergerak — bukan saat semua membeku menatap kamera.
8. **Jangan bercerita lewat tulisan.** Jika penonton harus membaca label, layar HP, atau surat untuk mengerti sebuah beat, beat itu gagal di AI video. Ganti dengan gambar atau suara.

## Detektor Klise — Dipindai Otomatis oleh `check_prompts.py`

Jika salah satu pola di bawah ini muncul di `konsep.md`, `naskah.md`, atau `prompt-video.md`, tulis ulang barisnya:

**Dialog Klise Indonesia (Anti-Sinetron):**
- *"Kamu nggak akan pernah ngerti!"* / *"Kau tidak akan pernah mengerti"*
- *"Kamu siapa sih sebenarnya?!"* / *"Siapa kamu sebenarnya"*
- *"Jangan pernah kembali ke sini!"*
- *"Aku sudah muak sama kamu!"* / *"Saya sudah muak"*
- *"Lihat saja nanti."*
- *"Tunggu pembalasanku."*
- *"Kamu akan menyesal."*
- *"Asal kamu tahu ya..."*
- Tertawa jahat tertulis sebagai `"HAHAHA!"` atau `"WKWK"`
- Memanggil nama lawan bicara di hampir setiap kalimat dialog

**Deskripsi Klise:**
- *"suasana mencekam"*, *"hening mencekam"*
- *"air mata mengalir di pipinya"*
- *"tatapan tajam penuh kebencian"*
- *"senyum tipis penuh arti"*
- *"dunia seakan berhenti"*
- *"waktu terasa melambat"*

**Kata Kosong Bahasa Inggris (di dalam blok prompt video/aset):**
- `"cinematic masterpiece"`, `"breathtaking"`, `"stunning"`, `"epic"`
- `"8k"`, `"4k"`, `"ultra realistic"`, `"hyper detailed"`
- `"award winning"`, `"photorealistic masterpiece"`
- `"dramatic lighting"` tanpa menyebut sumber dan arah cahaya

Kata-kata kosong tersebut tidak memberi informasi spasial atau optis kepada model. Ganti dengan sumber cahaya konkret (`midday sun camera-left`), lensa konkret (`85mm`), dan jarak konkret.

## Menulis Dialog yang Tidak Sinetron & Ramah Lip-Sync AI

- **Orang jarang menjawab lurus.** Pertanyaan dibalas pertanyaan, dibalas diam, atau dibalas pengamatan lain. Jawaban lurus hanya dipakai saat tokoh sengaja terdengar dingin.
- **Kalimat pendek.** Di layar vertikal, kalimat lebih dari **12–14 kata** terdengar seperti pidato dan membuat bibir AI video terburu-buru.
- **Anggaran Kecepatan Bicara (Lip-Sync Budget):** Hitung rasio `jumlah kata / durasi shot (detik)`. Target alami adalah **1,5–2,8 kata/detik** (maksimal keras **3,2 kata/detik**). Contoh: 9 kata butuh minimal shot 4 detik; 16 kata harus diberi 6–7 detik atau dipecah.
- **Tidak semua tokoh bicara.** Jika ada 5–12 orang di ruangan, hanya 1–2 yang bersuara.
- **Nama jarang disebut** dalam percakapan nyata kecuali punya bobot dramatis (seperti momen pengungkapan identitas).
- **Register lisan lokal.** Gunakan Bahasa Indonesia lisan alami sesuai latar tokoh (*"nggak"*, *"kayak"*, *"udah"*, *"gue/aku"*), bukan bahasa baku pembaca berita kecuali memang karakternya kaku.
- **Angka wajib ditulis sebagai kata.** `"dua ribu sebelas"`, `"empat belas hari"`, bukan `"2011"` atau `"14"`. Ini wajib agar pelafalan AI video akurat (`check_prompts.py` menandai angka mentah di dalam kutipan dialog).

## Rubrik Penilaian 9 Aspek — Wajib Lulus Sebelum Setor

Nilai **1–5** tiap baris kuantitatif. Semua baris wajib **≥ 4**, rata-rata **≥ 4,3**. Dua baris terakhir adalah gerbang **Ya / Tidak** mutlak.

| Aspek | Pertanyaan Uji | Syarat |
|---|---|---|
| **Hook** | Apakah ada alasan konkret untuk tidak scroll dalam tiga detik pertama? | ≥ 4 |
| **Spesifik** | Adakah minimal satu detail yang tidak bisa dipindahkan ke cerita lain? | ≥ 4 |
| **Detail meleset** | Adakah satu hal janggal yang belum dijelaskan? | ≥ 4 |
| **Dialog** | Jika dibaca keras, terdengar seperti manusia bicara atau seperti naskah sinetron? | ≥ 4 |
| **Diam** | Adakah minimal satu beat tanpa dialog yang diberi durasi shot tersendiri? | ≥ 4 |
| **Tanam & bayar** | Adakah benda/kebiasaan yang ditanam lebih awal dan dibayar di akhir? | ≥ 4 |
| **Akhir** | Berhenti pada gerakan yang sedang terjadi, bukan pose beku? | ≥ 4 |
| **Konsisten** | Apakah hook, arc, set, dan motif tokoh bebas dari kontradiksi dengan premis 3 baris? | **Wajib YA** |
| **Tanpa teks** | Apakah seluruh beat penting tersampaikan lewat gambar/suara tanpa tulisan layar? | **Wajib YA** |

Tulis ringkasan skor di bagian `## Skor rubrik` di `konsep.md` dengan format yang dapat dibaca verifier:
`Hook <n> · Spesifik <n> · Detail meleset <n> · Dialog <n> · Diam <n> · Tanam & bayar <n> · Akhir <n> — rata-rata <n,n> · Konsisten Ya · Tanpa teks Ya`

Jika ada aspek bernilai 3, tulis ulang naskahnya dulu — jangan disetor dengan catatan pembenaran.

## Saat User Menolak Konsep/Naskah

Jika user merasa naskahnya kurang menggigit, jangan menambal satu-dua kalimat dialog. Kembali ke **Premis 3 Baris** di `konsep.md` dan audit baris kedua (*detail meleset*). Naskah yang terasa datar hampir selalu berasal dari premis yang semua detailnya terlalu masuk akal dan tertebak.
