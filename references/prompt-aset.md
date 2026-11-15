# Prompt Aset — Gerbang 5

Keluaran gerbang ini adalah `epNN/prompt-aset.md`, berisi prompt siap salin untuk AI gambar mana pun. Setiap aset terdiri dari **satu judul markdown (`## ...`) + baris `Simpan sebagai:`** di luar blok kode, dan **satu blok kode** prompt. Judul dan nama berkas tidak boleh ikut masuk ke dalam blok prompt.

## Aturan Inkremental Lintas Episode

Tiap aset digenerate **sekali per seri** (kecuali varian wardrobe baru). Karena itu, `epNN/prompt-aset.md` **hanya** menulis prompt untuk aset yang baru muncul pertama kali di episode tersebut. Aset yang sudah dibuat di episode terdahulu dicantumkan di baris atas:

```markdown
Pakai ulang dari ep 01, jangan generate ulang: `adit_sheet.png`, `ruang_tengah_plate.png`.

Aset baru di episode ini: LORONG SAMPING.
```

> **Catatan penting:** Set yang hanya terlihat sekilas (misalnya ruang tamu yang diintip lewat celah pintu di shot terakhir Ep 1) **tetap dibuatkan plate-nya di episode tempat ia pertama kali muncul**, bukan ditunda ke episode berikutnya. Verifier `check_prompts.py` mengecek agar tidak terjadi duplikasi generate lintas episode.

---

## 1. Sheet Karakter — Tiga Panel

Susunan tiga panel sudah dikunci permanen: **close-up di kiri (`LEFT PANEL`), badan depan di tengah (`MIDDLE PANEL`), badan belakang di kanan (`RIGHT PANEL`), dengan nama tokoh tercetak di gambar.**

````markdown
## Sheet karakter · RAFA
Simpan sebagai: `rafa_sheet.png` → token `[gambar_rafa]`

```
Character reference sheet for film production. Three panels side by side, separated by
thin subtle vertical gaps. One continuous neutral dark grey seamless studio backdrop
across all three panels. Soft even studio lighting, photorealistic cinematic
photography, 35mm film look, fine grain, muted desaturated colour.

LEFT PANEL: tight close-up portrait, head and shoulders only, neutral expression, mouth
closed, eyes looking straight into the lens, sharp focus on the eyes.

MIDDLE PANEL: the SAME person, full body head to feet, standing straight facing the
camera, head and face fully visible, arms relaxed at the sides, feet together, neutral
expression.

RIGHT PANEL: the SAME person, full body head to feet, standing straight seen from
directly behind, head fully visible, arms relaxed at the sides, showing the back of the
clothing.

THE PERSON: <bentuk panjang fisik dari cast.md, disalin apa adanya>

WARDROBE: <baris WARDROBE dari cast.md, disalin apa adanya>

A clean white sans-serif label reading RAFA printed in the lower left corner of the left
panel.

The same person, the same face, the same clothing in all three panels. Photorealistic,
not illustration.

Avoid: more than one person per panel, different faces between panels, missing head,
patterned or gradient background, hard shadows, dramatic camera angles, extra text,
watermark, logo.
```
````

### Invarian Wajib pada Sheet Karakter
- **Urutan panel:** `LEFT PANEL: tight close-up` → `MIDDLE PANEL` → `RIGHT PANEL`. Dicek otomatis oleh `check_prompts.py`.
- **Label nama tercetak:** `A clean white sans-serif label reading <NAMA> printed in the lower left corner of the left panel.` Tanpa label nama tercetak, sheet rentan tertukar saat user melampirkan 2–3 berkas gambar sekaligus di AI video.
- **`missing head` & `different faces between panels`:** Wajib ada di daftar `Avoid:`. Model AI gambar sering memotong kepala pada panel badan saat deskripsi wardrobe mendominasi.
- **Latar abu-abu gelap netral polos (`neutral dark grey seamless studio backdrop`):** Mencegah model video meniru pola ruangan studio ke dalam adegan film.

### Yang Boleh Disesuaikan pada Sheet
- Ekspresi wajah di `LEFT PANEL` boleh sedikit disesuaikan jika karakter memiliki ekspresi khas, namun mulut tetap tertutup rapat.
- **Properti identitas di tangan:** Jika tokoh selalu membawa properti khas (seperti tongkat Ibu di `alamat-yang-sama`), sesuaikan frasa `arms relaxed at the sides` pada `MIDDLE PANEL` dan `RIGHT PANEL`, misalnya: `left arm relaxed at her side, right hand resting on the walking cane`.
- **Rasio gambar saat generate:** Gunakan `16:9` (atau `3:2`) di UI AI gambar agar ketiga panel punya ruang horizontal lega dan resolusi wajah tetap tajam.

---

## 2. Set Plate (Lokasi)

Satu plate per lokasi. **Wajib tanpa orang sama sekali (`absolutely no people in frame`).**

````markdown
## Set plate · Ruang rapat
Simpan sebagai: `ruang_rapat_plate.png` → token `[gambar_ruang_rapat]`

```
Photorealistic interior photograph, absolutely no people in frame.

<blok set dari set.md, disalin apa adanya>

Midday, hard daylight entering from the left. 24mm lens, eye height, level horizon,
straight-on composition.

Avoid: people, text, signage, extra furniture, coloured practical lights, lens flare,
watermark.
```
````

### Aturan Komposisi Set Plate
1. **Lensa 24mm & Horizon Rata:** Tugas plate adalah memberi peta spasial ruangan ke model video, bukan berakrobat gaya sinematik.
2. **Pilih Sudut Plate dari Shot Wide Terpenting:** Pengujian membuktikan bahwa sebagian model video memperlakukan set plate sebagai *camera anchor* dan menarik komposisi *wide shot* kembali ke sudut plate walau teks meminta sudut lain. Jika *wide shot* terpenting di `naskah.md` diambil dari seberang gang menghadap pagar, buat plate dari seberang gang juga (`straight-on composition from the lane looking at the door`).
3. **Eksterior vs Interior:** Gunakan `Photorealistic exterior photograph, absolutely no people in frame.` untuk lokasi luar ruang.
4. **Daftar `Avoid:` Kondisional:** Tambahkan benda yang *tidak boleh ada di keadaan dasar set* walaupun nanti dibawa masuk oleh tokoh — misalnya `packages, footprints in the dust` untuk teras berdebu yang mula-mula kosong.

---

## 3. Plate Properti

Khusus untuk properti **berpelat** (`MOTOR`, mobil, mesin spesifik). Properti teks saja (`PAKET`, `FOTO`) tidak dibuatkan prompt di sini.

````markdown
## Plate properti · Motor
Simpan sebagai: `motor_plate.png` → token `[gambar_motor]`

```
Photorealistic reference photograph of a single vehicle, absolutely no people.

<blok properti dari set.md, disalin apa adanya>

Plain neutral grey seamless studio backdrop, soft even studio lighting. Three-quarter
front view from the right side so the scuffed panel is visible, 35mm lens, eye height,
the whole scooter in frame with space around it.

Avoid: people, rider, helmet on the seat, text, logos, brand names, licence plate
numbers, extra accessories, watermark.
```
````

Gunakan latar abu polos seperti sheet karakter dan sudut 3/4 yang memperlihatkan ciri uniknya (goresan, penyok, warna pudar).

---

## 4. Sheet Varian Wardrobe

Jika tokoh berganti pakaian di episode lanjutan (misalnya `RAFA B`), buat sheet baru dengan token `[gambar_rafa_b]` dan berkas `rafa_b_sheet.png`. Deskripsi `THE PERSON` disalin **100% identik** dari `cast.md`, hanya baris `WARDROBE` dan label nama (`label reading RAFA B`) yang berubah.

---

## Catatan Penyerahan Gerbang 5

Cantumkan baris pengantar ini di bagian atas berkas `epNN/prompt-aset.md`:
> Generate aset ini dulu di AI gambar mana pun. Simpan dengan nama berkas yang tertulis di tiap judul, karena nama itu yang dipakai sebagai token di `prompt-video.md`.
