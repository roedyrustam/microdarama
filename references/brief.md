# Brief — Gerbang 1

Tujuan gerbang ini: mengunci parameter yang **tidak bisa diturunkan dari topik**. Semua angka di sini milik user. Skill tidak punya pendapat soal angka.

## Aturan Inti (Zero-Default Rule)

1. **Jangan pernah mengisi sendiri.** Tidak ada default rasio, default durasi, atau default jumlah episode. Kosongkan semua slot yang belum dijawab, biarkan user yang menentukan.
2. **Dua kartu, tidak lebih.** Alat tanya pilihan maksimal empat pertanyaan per kartu, jadi brief dibagi **persis dua kartu** (lihat tabel di bawah). Jangan mencicil sisanya di pesan teks.
3. **Jangan tanya jumlah shot.** Lihat bagian "Yang tidak ditanyakan" di bawah.
4. Topik cerita boleh diturunkan dari kalimat pertama user. Kalau user sudah bilang *"microdrama tentang teknisi AC"*, formatnya sudah terjawab — tandai sebagai terisi dan tanyakan sisanya saja.

## Daftar Pertanyaan

| Kartu | Pertanyaan | Opsi yang ditawarkan | Catatan |
|---|---|---|---|
| **1** | **Topik** | 2–3 ide konkret + isi sendiri | dilewati kalau user sudah menyebut cerita |
| **1** | **Format** | Microdrama seri · Short movie · Scene/trailer tunggal | menentukan struktur naskah di gerbang 2 & 4 |
| **1** | **Rasio** | 9:16 · 16:9 · 1:1 | dicatat untuk pengaturan AI video user, **tidak pernah masuk prompt** |
| **1** | **Bahasa dialog** | Indonesia · English | masuk blok `LANGUAGE` di prompt video |
| **2** | **Durasi** | 2–3 angka dengan konsekuensi dramaturginya + isi sendiri | per episode kalau seri, total kalau short movie |
| **2** | **Jumlah episode** | 2–3 angka + isi sendiri | hanya untuk format seri; `1` juga sah |
| **2** | **Look** | 2–3 look visual yang cocok dengan topik + jelaskan sendiri | masuk blok `VIDEO STYLE & FORMAT` dan `LIGHTING` |

Alat tanya selalu menyediakan isian bebas, jadi opsi angka di kartu 2 hanyalah tawaran — user sering mengisi angka lain, dan angka user itulah yang dipakai.

Untuk **Scene/trailer tunggal**, pertanyaan jumlah episode dilewati, dan **Look** boleh naik ke kartu 1 agar cukup dalam satu atau dua kartu ringkas.

**Durasi lebih dari 30 detik** tidak masalah — satu prompt video memang dibatasi **4–30 detik**, tapi pemecahannya dikerjakan di gerbang 4 mengikuti alur cerita. Jangan membatasi durasi episode di sini.

## Yang Tidak Ditanyakan

**Jumlah shot.** Shot muncul dari kebutuhan naskah: berapa sudut yang dibutuhkan untuk menceritakan adegan itu. Memaksakan angka shot di depan membuat naskah kaku — adegan dipotong atau dipanjangkan hanya untuk memenuhi kuota. Biarkan naskah yang menentukan, lalu AI video yang mengeksekusinya.

Jika user bertanya *"berapa shot nanti?"*, jawab apa adanya: ditentukan setelah naskah jadi, dan akan terlihat di shot list gerbang 4.

## Kalau User Menjawab "Terserah"

Jangan memaksa, tapi jangan juga diam-diam memilih sendiri lalu menuliskannya sebagai keputusan user. Tawarkan **dua kemungkinan konkret dengan konsekuensinya**, lalu biarkan user menunjuk:

> Durasi 60 detik bikin ceritanya padat, satu beat saja — cocok kalau mau penonton langsung nonton ulang. 90 detik kasih ruang buat satu hening sebelum cliffhanger. Pilih yang mana?

Kalau user tetap bilang terserah, pilih satu, **sebut jelas bahwa itu pilihanmu**, dan catat di `brief.md` sebagai `(dipilih skill, belum dikonfirmasi)` supaya mudah diubah nanti.

## Kalau Jawaban Saling Bentrok

Jawaban bisa bertabrakan satu sama lain — misalnya topik yang berbunyi *"tiap malam"* dengan look *"siang hari"*, atau durasi *15 detik* untuk *short movie tiga babak*. Jangan diam-diam memilih salah satu.

1. Sebutkan bentroknya dalam satu kalimat.
2. Tawarkan resolusi yang paling masuk akal, dengan alasannya.
3. Catat keputusan dan alasannya di `brief.md` bagian **Penyesuaian**.

Kalau resolusinya jelas dan kecil (misalnya menggeser waktu ke siang hari yang justru membuat pintu tertutup terasa lebih ganjil), boleh langsung jalan dengan menyebutkannya jelas. Kalau resolusinya mengubah inti cerita, tanyakan dulu sebelum menulis `konsep.md`.

## Mengubah Brief di Tengah Jalan

Jika user bilang *"episode 4 jadiin 2 menit"* atau *"ganti ke 16:9"*, yang diedit **hanya `brief.md`** terlebih dahulu. Lalu laporkan peta dampaknya sebelum mengeksekusi ulang:

| Yang berubah | Bagian yang perlu ditulis ulang |
|---|---|
| **Rasio** | **Tidak ada** — rasio tidak pernah masuk prompt |
| **Durasi** | `epNN/naskah.md` (shot list, pembagian scene) dan timecode `SHOT BREAKDOWN` di `epNN/prompt-video.md` |
| **Jumlah episode** | Tabel `Arc` di `konsep.md` |
| **Bahasa dialog** | Blok `LANGUAGE`, `CRITICAL` (lip-sync), dan seluruh baris dialog |
| **Look** | Blok `VIDEO STYLE & FORMAT` dan `LIGHTING` di setiap prompt video, serta keterangan cahaya di set plate baru |

Setelah memperbarui `cast.md` atau `set.md` jika ada penyesuaian, jalankan `python assets/tools/microdrama_cli.py sync <folder>` dan `python assets/tools/check_prompts.py <folder>`.

## Bentuk `brief.md`

```markdown
# Brief — <judul proyek>

| | |
|---|---|
| Format | Microdrama seri |
| Rasio | 9:16 |
| Durasi | 75 detik per episode |
| Jumlah episode | 6 |
| Bahasa dialog | Indonesia |
| Look | Jakarta modern, kantor kelas atas |

Topik: <kalimat asli user, apa adanya, jangan diparafrase>

Catatan: rasio dicatat di sini untuk pengaturan AI video. Rasio tidak ditulis di dalam prompt.
Jumlah shot tidak dipatok — ditentukan naskah.
```

Simpan kalimat asli user apa adanya. Di gerbang 2 kalimat itu menjadi bahan baku logline; detail kecil yang tersembunyi di kalimat awal sering hilang jika langsung diparafrase.
