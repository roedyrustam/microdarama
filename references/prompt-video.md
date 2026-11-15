# Prompt Video — Gerbang 6

Berkas terpenting di seluruh pipeline Microdrama. Keluarannya adalah `epNN/prompt-video.md`.

## Batas Durasi & Format Berkas

**Satu blok prompt = satu scene = satu kali generate = 4–30 detik.**

Satu judul markdown + baris `Lampirkan:` berada **di luar** blok kode (untuk manusia), dan satu blok kode prompt utuh berada di bawahnya (satu-satunya teks yang di-copy user ke AI video).

````markdown
## Scene 1 · Ruang rapat · 30 detik
Lampirkan: `rafa_sheet.png`, `bu_dian_sheet.png`, `ruang_rapat_plate.png`

```
VIDEO STYLE & FORMAT
...
```
````

**Larangan Keras:** Jangan pernah menaruh header manusia seperti `=== PROMPT VIDEO · EP01 ===`, nama berkas (`rafa_sheet.png`), rasio (`9:16`, `vertical`, `horizontal`), fps, seed, atau nama model di dalam blok kode.

---

## Sebelas Blok Wajib (+ `CONTINUITY` Opsional)

Urutan di bawah ini disengaja dan diverifikasi secara ketat oleh `check_prompts.py`: **seluruh aturan global diletakkan di atas sebagai pengunci sistem sebelum model membaca urutan adegan.**

### 1 · `VIDEO STYLE & FORMAT`
Menetapkan panjang klip, gaya penyutradaraan, penegasan kontinuitas, tempo, akting, look warna, dan larangan anti-sinetron/genre.

```text
VIDEO STYLE & FORMAT
30-second scene in the style of a modern Indonesian short drama. ONE continuous
confrontation — a single unbroken moment in one room, NOT a trailer, NOT a montage —
covered like a real film: cut between MULTIPLE camera positions, angles changing every
few seconds while the moment flows continuously. Slow, heavy pacing with real silence
between lines. Naturalistic acting, underplayed, never theatrical. Look: cold filmic
colour grading, crushed blacks, fine film grain, shallow depth of field, accurate
Indonesian skin tones. NOT sinetron, NO dramatic zooms, NO rapid cutting, dialogue
never rushed.
```
- **Wajib memuat:** `<N>-second scene` di awal baris, `ONE continuous ... NOT a trailer, NOT a montage`, dan penegasan look tanpa rasio.
- **Anti-Salah-Genre:** Jika premis bisa terbaca horor (rumah sepi, pintu tertutup, orang mengintip), tulis eksplisit: `This is a quiet family drama, NOT horror and NOT a thriller.`

### 2 · `LANGUAGE`
Blok paling menentukan agar dialog tidak berubah jadi Bahasa Inggris, tidak diparafrase, dan tidak memunculkan teks subtitle palsu.

```text
LANGUAGE
All spoken dialogue in INDONESIAN (Bahasa Indonesia), Jakarta register, casual spoken
form — not formal news-reader Indonesian. Speak the lines exactly as written in the
breakdown below: do not translate them, do not paraphrase them, do not invent extra
lines. Numbers are spoken as Indonesian words. No English words. No subtitles, no
captions, no on-screen text of any kind burned into the frame. Character names are never
spoken aloud unless they appear inside the quotation marks.
```
- Jika terdapat jumlah baris dialog sangat sedikit di tengah scene hening, tambahkan jumlah pastinya di sini: `Exactly TWO lines are spoken in the whole scene: ...`
- **Scene tanpa dialog** tetap wajib memiliki blok ini dalam bentuk:
```text
LANGUAGE
This scene has NO spoken dialogue — no voices, no narration, no inner monologue, no
whispering. No subtitles, no captions, no on-screen text of any kind burned into the
frame.
```
- Suara non-tokoh (suara aplikasi HP, radio) juga didaftarkan di sini dan ditulis di `SHOT BREAKDOWN` seperti `PHONE VOICE (off-screen, flat, synthetic): "..."`.

### 3 · `OPTICS`
Menetapkan lensa dasar, bukaan T-stop untuk kedalaman ruang, dan lensa close-up.

| Lensa | FOV | Fungsi Dramatis |
|---|---|---|
| `24mm` | ~74° | ruang terasa luas/menekan, tokoh kecil di dalam arsitektur |
| `35mm` | ~54° | perspektif natural, tulang punggung adegan dialog & wide |
| `50mm` | ~40° | netral mendekati mata manusia, detail tangan/lantai |
| `85mm` | ~24° | isolasi wajah close-up, latar belakang melembut |
| `100mm macro` | ~18° | detail mikro objek (bingkai foto, bel pintu) |
| `135mm–200mm` | 12–15° | kompresi berat, terasa mengintip dari jauh |

### 4 · `CAMERA`
Daftar posisi fisik kamera yang dipakai, jenis pergerakan rig (`locked-off tripod`, `slow dolly push`, `slow backward track`), aturan *eyeline* (sumbu 180°), dan **frasa wajib**:
`Never two consecutive shots from the same position.`

### 5 · `LIGHTING`
Dilarang memakai kata sifat kosong seperti `"dramatic lighting"`. Wajib menyebut **lima parameter teknis**:
1. **Sumber cahaya utama:** matahari siang lewat kaca, cahaya susu pintu buram, lampu meja.
2. **Arah cahaya:** `camera-left`, `almost directly overhead`, `from behind`.
3. **Suhu warna (Kelvin):** `5600K` (siang hari dingin/netral), `3200K` (lampu pijar hangat).
4. **Kontras & *negative fill*:** sisi bayangan dibiarkan jatuh dalam atau terisi pantulan lantai.
5. **Satu aksen warna tunggal:** misalnya satu lampu meja amber di ruang dingin, atau jaket hijau pudar di antara batu abu-abu.

### 6 · `CRITICAL`
Mengunci jumlah tokoh dan mencegah kemunculan orang asing, perubahan wajah, atau layar HP terbaca.
- Selalu sebut jumlah pasti: `TWO speaking characters plus twelve silent background staff.` atau `ONE character only. Nobody else appears at any point.`
- Jika ada layar (HP/laptop/TV): `His phone screen is always angled away from camera — no readable screen.`
- Jika ada tanda wajah pengecualian cerita: kunci eksplisit sisi dan persamaannya di sini (`Both have a small dark mole on the LEFT cheekbone...`).

### 7 · `CHARACTERS (from reference images)`
Salin **bentuk pendek** dari `cast.md` persis sama, satu baris per tokoh dengan token `[gambar_<slug>]`, dilengkapi aksi spesifik tokoh di scene tersebut. Tambahkan `BACKGROUND — ...` (`none` jika sepi, atau jumlah + deskripsi + `none featured` jika ada figuran).

### 8 · `LOCATION (from references)`
Salin **blok set** dan **blok properti** dari `set.md` **apa adanya, huruf per huruf**.

#### Triad Lokasi Ganda (Wajib jika > 1 plate lokasi dalam 1 generate)
Jika satu scene melampirkan lebih dari satu plate lokasi (misal `teras_plate.png` dan `ruang_tengah_plate.png` karena shot terakhir mengintip lewat celah pintu), wajib menerapkan **ketiga pengaman berikut sekaligus**:
1. **Peta Referensi di awal `LOCATION`:** menjelaskan plate mana untuk sisi mana dan dipakai di `SHOT` berapa.
2. **Tag Lokasi di setiap baris `SHOT`:** tepat setelah timecode, misal `SHOT 6 (23-26s) — OUTSIDE, terrace, seen from the lane — 35mm MEDIUM...`
3. **Blok `CONTINUITY`:** mengunci posisi setiap tokoh dan benda penting.

### `CONTINUITY` *(Opsional — Wajib jika >1 plate lokasi atau ada properti persisten)*
Ditempatkan persis di antara `LOCATION` dan `AUDIO`.
- Satu butir per tokoh atau benda (maksimal 3 benda).
- Wajib menjelaskan: **posisi persisnya, sejak `SHOT` berapa, di `SHOT` mana ia terlihat, dan bahwa di shot lain ia sekadar berada di luar frame (`outside the frame — never gone`).**
- **Jangan menumpuk penegasan** berulang-ulang di banyak blok; satu kalimat sederhana jauh lebih dipatuhi model.

### 9 · `AUDIO`
Menjelaskan *room tone* / *ambience*, efek suara foley spesifik (ketukan tongkat, derit kursi, tarikan selotip), aturan skor musik (`NO musical score at all`, atau masuk di detik terakhir saja), dan tempo dialog.

### 10 · `MOVEMENT NOTE`
**Selalu ada.** Mengatur kontras gerak:
- **1 tokoh:** ambil nada tubuh dari `cast.md` (cara berdiri, cara melangkah, pantangan gerak).
- **2 tokoh:** tegaskan **dua ritme berlawanan (`run on OPPOSITE rhythms`)**, tidak pernah bercermin.
- **> 2 orang di frame:** dua ritme tokoh utama **plus wajib memecah figuran** menjadi minimal tiga aksi terpisah dan melarang gerakan serempak (`The twelve staff NEVER react as a block ... never a synchronised crowd turn`).

### 11 · `SHOT BREAKDOWN`
Judul bagian wajib persis `SHOT BREAKDOWN`.
- Baris pembuka: `SCENE [00:00-00:<NN>] <LOKASI> — one continuous <apa>, cut between positions:` *(tanpa nomor scene di dalam blok; selalu mulai `00:00`)*.
- Format baris shot:
  `SHOT <n> (<mulai>-<selesai>s), <lensa> <UKURAN> from <posisi fisik>, <gerakan>: <aksi>.`
  *(atau dengan tag lokasi `— SISI, tempat, sudut —` untuk adegan multi-plate).*
- Timecode harus bersambung rapat tanpa celah (`0-4s`, `4-9s`, ..., berakhir tepat di `NN`).
- Dialog ditulis di baris baru: `NAMA (arahan): "Kalimat dialog."` (tanpa angka mentah, kalimat ringkas).
- Shot tanpa dialog ditulis eksplisit: `No dialogue — five seconds of dead room tone.`
- **Kalimat penutup wajib** berhenti pada gerakan: `... — no freeze frame, no fade to black.`

#### Aturan Khusus untuk Shot Rentan Plot Hole:
- **Shot lewat celah/kaca/lubang kunci:** Tulis **hanya benda/ruang yang terlihat**. Dilarang menyebut tokoh, mata, napas, `POV`, ataupun larangan seperti `no face, no head, nobody`.
- **Bekas atau ketiadaan benda (misal petak bersih di debu):** Tulis sebagai permukaan datar (`flat, level with the floor, nothing on it, not an object`). Dilarang menulis kata kontras seperti `darker` atau `deeper colour`.
- **Sudut balik (*reverse angle*):** Sebut posisi kamera dan apa yang terlihat di belakang tokoh sekali saja dengan jelas.

---

## Yang Dilarang Masuk ke Dalam Blok Prompt

| Dilarang | Alasan |
|---|---|
| Rasio (`9:16`, `16:9`, `vertical`, `horizontal`) | Diatur di UI model video sebelum generate |
| Resolusi, `fps`, `seed`, nama model | Pengaturan alat eksternal, bukan deskripsi adegan |
| Header manusia (`=== ... ===`) & nama berkas (`.png`, `.jpg`) | Sering dirender sebagai teks bocor di gambar |
| Kata `subtitle` / `caption` di luar blok `LANGUAGE` | Memicu model menggambar teks di bawah frame |
| `8k`, `4k`, `masterpiece`, `ultra realistic`, `award winning`, `dramatic lighting` | Kata kosong tanpa informasi optis/cahaya |
| `SCREENPLAY` atau `SCENE 1` bernomor di dalam prompt | Setiap prompt adalah 1 generate independen |
