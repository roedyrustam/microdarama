# Cast & Set Bible — Gerbang 3

Ini gerbang yang menentukan apakah wajah, ruangan, dan properti bertahan konsisten lintas klip atau hancur berubah-ubah. Satu-satunya cara menjaga konsistensi lintas generate yang terpisah adalah memastikan **teks deskripsi identik huruf per huruf** di mana pun ia muncul, dipasangkan dengan token berkas gambar yang tepat.

## Kenapa Harus Identik Huruf per Huruf

Model gambar dan video membaca teks sebagai koordinat jangkar. `"Short cropped black hair"` dan `"short black hair"` di dua episode yang berbeda akan ditafsirkan sebagai dua orang berbeda.

Aturannya mutlak: **tulis sekali di `cast.md` dan `set.md`, lalu salin persis (atau jalankan `microdrama_cli.py sync`) — jangan ketik ulang, jangan diringkas, jangan diparafrase.**

---

## Dua Bentuk per Tokoh (`cast.md`)

### 1. Bentuk Panjang — untuk Prompt Sheet Karakter (Gerbang 5)

Wajib memuat **enam hal** ini dalam urutan yang konsisten:

1. Kebangsaan dan jenis kelamin (`Indonesian man`, `Indonesian woman`)
2. Usia dan tinggi badan (`28 years old, 172 cm`)
3. Warna kulit (`warm brown skin`, `light brown skin`)
4. Rambut: panjang, warna, dan tatanan (`short cropped black hair`, `black hair pulled into a tight low bun with no loose strands`)
5. Bentuk wajah atau rahang (`strong jaw`, `round face with a soft jaw`)
6. Bangun badan (`lean muscular build`, `wiry thin build`)

Dilanjutkan baris `WARDROBE:` per item lengkap dengan warna, potongan, dan bahan.
Di luar blok kode, catat **Nada tubuh** (dalam Bahasa Indonesia, untuk panduan manusia/sutradara dan bahan `MOVEMENT NOTE`).

```markdown
[RAFA] — bentuk panjang
```
```text
Indonesian man, 28 years old, 172 cm, warm brown skin, short cropped black hair,
strong jaw, lean muscular build.
WARDROBE: dark navy blue long-sleeve technician uniform shirt with the sleeves rolled
to the forearm, the name RAFA embroidered in small white letters on the right chest,
matching dark navy work trousers, black work boots, grey cloth gloves tucked into the
trouser pocket.
```
**Nada tubuh:** tenang, pundak turun, jarang menatap mata orang lebih dari dua detik.

### Aturan Penting: Tanpa Tanda di Wajah (*Ordinary Faces Rule*)

**Jangan menambahkan tanda khusus di wajah atau tubuh tokoh** — bekas luka (*scar*), tahi lalat (*mole*), tato (*tattoo*), tindik (*piercing*), bintik-bintik (*freckles*), atau gigi gingsul. AI gambar dan AI video selalu melebih-lebihkan tanda kecil: luka gores 1 cm berubah menjadi codet horor, tahi lalat kecil menjadi bisul, dan tanda itu sering berpindah dari pipi kiri ke pipi kanan antar potongan.

Wajah dikunci oleh **gambar sheet 3 panel**, bukan oleh tanda di wajah. Bedakan tokoh lewat hal makro yang mudah dibedakan model: usia, tinggi, bangun badan, panjang/tatanan rambut, kacamata, dan terutama **warna & siluet wardrobe**.

**Satu-satunya pengecualian: tanda yang memiliki fungsi cerita (*plant & payoff*).** Misalnya ibu dan anak sama-sama punya tahi lalat kecil di tulang pipi kiri sebagai petunjuk visual hubungan darah sebelum dialog mengungkapnya (seperti di proyek *Alamat yang Sama*). Syarat mutlak jika memakai pengecualian ini:
1. Tanda wajib dicatat di `cast.md` di bawah bagian tokoh dengan label eksplisit **`Tanda wajah karena cerita:`**.
2. Ukuran harus ditulis halus dan kecil (`a small dark mole on his/her left cheekbone`).
3. Wajib dikunci eksplisit di blok `CRITICAL` prompt video, menyebut sisi yang tepat serta menegaskan agar tidak menggabungkan dua wajah.

Tanpa label `Tanda wajah karena cerita:` di `cast.md`, `check_prompts.py` akan menolak tanda wajah apa pun di blok tokoh.

### 2. Bentuk Pendek — untuk Blok `CHARACTERS` Prompt Video (Gerbang 6)

Satu baris ringkas: Nama kapital, token gambar, usia, ringkasan wardrobe (tanpa deskripsi fisik wajah yang berisiko bentrok dengan gambar referensi), dan slot `<aksi di scene ini>`.

```text
RAFA [gambar_rafa] — 28, dark navy technician uniform, sleeves rolled to the forearm,
name patch on the right chest, <aksi di scene ini>.
```

Mengulang detail rahang atau kulit di bentuk pendek justru sering bertabrakan dengan interpretasi visual dari sheet referensi.

---

## Bijeksi Token & Nama Berkas (`[gambar_<slug>]`)

Setiap tokoh, set, dan properti berpelat memiliki tepat satu token lowercase tanpa spasi: `[gambar_<slug>]`.

| Jenis Aset | Contoh Nama | Token | Nama Berkas Wajib |
|---|---|---|---|
| Tokoh | `RAFA` | `[gambar_rafa]` | `rafa_sheet.png` |
| Tokoh | `BU DIAN` | `[gambar_bu_dian]` | `bu_dian_sheet.png` |
| Varian Wardrobe | `RAFA` (Ep 4-6) | `[gambar_rafa_b]` | `rafa_b_sheet.png` |
| Lokasi / Set | `RUANG RAPAT` | `[gambar_ruang_rapat]` | `ruang_rapat_plate.png` |
| Properti Berpelat | `MOTOR` | `[gambar_motor]` | `motor_plate.png` |

Pola wajib: `<slug>_sheet.png` untuk tokoh, `<slug>_plate.png` untuk set dan properti berpelat, di mana `<slug>` persis sama dengan bagian setelah `gambar_`. Verifier `check_prompts.py` akan menggagalkan proyek jika token dan nama berkas menyimpang.

### Wardrobe Varian

Jika tokoh berganti baju di episode selanjutnya, **jangan pernah menimpa wardrobe lama**. Tambahkan entri baru dengan sufiks `_b`, `_c`, dst., misalnya `## RAFA B` dengan token `[gambar_rafa_b]` dan berkas `rafa_b_sheet.png`. Wajah tetap disalin persis dari blok bentuk panjang pertama; hanya `WARDROBE` dan label nama sheet (`RAFA B`) yang berubah.

---

## `set.md` — Blok Lokasi (6 Elemen Wajib)

Setiap lokasi ditulis sekali dalam Bahasa Inggris, dan harus memuat **enam elemen**:

1. **Jenis ruang dan lokasi makro** (`High-floor Jakarta office meeting room.`)
2. **Satu elemen arsitektur dominan yang mengunci komposisi** (`One full-height glass wall onto layered towers.`)
3. **Furnitur utama & jumlahnya** (`Long wood table, twelve black mesh chairs.`)
4. **Material lantai** (karena lantai menentukan pantulan cahaya dan bayangan) (`Grey marble floor.`)
5. **Satu benda ganjil penanda ruangan** (`One ceiling cassette air-conditioner with its access panel hanging open.`)
6. **Semua pintu dan jalan masuk yang dipakai di sepanjang arc** (pintu depan, ambang dapur, tangga, pintu kamar belakang). Jika tokoh masuk lewat pintu yang tidak tertulis di blok set, model video akan mengarang posisi pintunya sendiri di setiap klip.

Nomor 6 sering baru disadari di Gerbang 4 saat blocking ditulis. Jika ada pintu baru yang dibutuhkan naskah, **tambahkan** ke blok set di `set.md` sebelum prompt aset/video dibuat, dan catat sebagai `Revisinya gerbang 4:` di bawah blok tersebut.

---

## Properti (`## Properti` di `set.md`)

Benda atau kendaraan yang muncul di lebih dari satu shot atau lintas klip dan berisiko berubah bentuk. Ditulis dengan heading `### <NAMA>`.

| Jenis | Kapan Dipakai | Bentuk di `set.md` & Prompt |
|---|---|---|
| **Berpelat** | Benda besar/kompleks (motor, mobil, perabot unik) | Blok teks + Token `[gambar_<slug>]` + Berkas plate `<slug>_plate.png` + dibuatkan plate di Gerbang 5 |
| **Teks saja** | Benda kecil/sederhana (kardus paket, foto berbingkai, tas tangan) | Blok teks saja, tanpa plate; disalin **identik** ke blok `LOCATION` setiap scene yang memakainya |

Untuk benda yang di dunia nyata selalu bertulisan (paket kurir, plat nomor kendaraan, kemasan produk), wajib cantumkan larangan teks eksplisit di dalam bloknya: `no labels, no printed text, no logos anywhere, licence plate blank`.

---

## Saat Melanjutkan Episode Lama

Baca `cast.md` dan `set.md` yang sudah ada. **Jangan tulis ulang entri lama.** Tokoh dan lokasi lama wajib menggunakan token serta blok yang 100% identik. Tokoh, lokasi, atau varian baju baru cukup ditambahkan di bawah entri lama, lalu jalankan `python assets/tools/microdrama_cli.py sync <folder>`.
