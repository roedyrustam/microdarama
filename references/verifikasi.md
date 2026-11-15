# Verifikasi & Perbaikan Pasca-Generate — Gerbang 7

Hampir semua kegagalan pada video AI adalah kesalahan teks atau logika ruang yang sebenarnya bisa dicegah sebelum satu kredit pun terbakar. Gerbang 7 memadukan **25-Point Static & Semantic Verifier**, **HTML Production Board**, dan **Loop Bedah Klip**.

---

## Langkah 1 · Jalankan Verifikator Otomatis 25-Poin

```bash
python assets/tools/check_prompts.py <folder_proyek> --strict
```

Untuk integrasi agen/otomatisasi, tambahkan `--json` untuk keluaran terstruktur. Di Windows, skrip otomatis mengonfigurasi UTF-8 pada stdout.

### Ringkasan 25 Cek yang Dijalankan Mesin:
1. **Salinan identik `cast.md`:** bentuk panjang + `WARDROBE` di `prompt-aset.md` dan bentuk pendek di `CHARACTERS` pada `prompt-video.md`.
2. **Salinan identik `set.md`:** blok lokasi & properti (berpelat dan teks saja) di `prompt-aset.md` dan `LOCATION`.
3. **Urutan 11 blok tetap** (`VIDEO STYLE & FORMAT` → ... → `SHOT BREAKDOWN`).
4. **Posisi blok opsional `CONTINUITY`** tepat di antara `LOCATION` dan `AUDIO`.
5. **Triad Lokasi Ganda:** jika >1 plate lokasi dilampirkan, mesin memastikan ada peta referensi di `LOCATION`, tag lokasi di **setiap** baris `SHOT`, dan blok `CONTINUITY`.
6. **Batas durasi 4–30 detik** per scene baik di `naskah.md` maupun `prompt-video.md`.
7. **Konsistensi durasi 3 titik:** judul markdown (`N detik`), baris pertama `VIDEO STYLE & FORMAT` (`N-second scene`), dan header `SCENE [00:00-00:NN]`.
8. **Total durasi episode** pada shot list `naskah.md` dan total semua scene `prompt-video.md` cocok dengan target di `brief.md`.
9. **Kontinuitas timecode `SHOT`:** penomoran berurutan `1..K`, bersambung tanpa celah/overlap dari `0` sampai tepat `NN`.
10. **Bijeksi `[gambar_x]` ↔ berkas:** setiap token di prompt tercantum di `Lampirkan:`, tidak ada lampiran yatim, dan pola `<slug>_sheet.png` / `<slug>_plate.png` konsisten.
11. **Detektor kata terlarang:** rasio, `vertical`, `horizontal`, `===`, `.png`/`.jpg`, `SCREENPLAY`, `resolution`, `seed`, `fps`, `8k`, `4k`, `masterpiece`, `award winning`, `ultra realistic`, `hyper detailed`, `dramatic lighting`.
12. **Larangan `subtitle` / `caption`** di luar blok `LANGUAGE`.
13. **Frasa pengaman wajib:** `Never two consecutive shots from the same position`, `NOT a montage`, `no freeze frame`, `No subtitles`, serta `exactly as written` atau `NO spoken dialogue`.
14. **Validasi Sheet Karakter:** label nama tercetak, `missing head`, `different faces between panels`, dan urutan panel kiri-tengah-kanan.
15. **Validasi Plate Set/Properti:** mengandung `absolutely no people`.
16. **Detektor Tabrakan Posisi Kamera Berurutan (Baru v2.0):** memindai kolom `Posisi kamera` di `naskah.md` maupun frasa posisi `from ...` di `SHOT BREAKDOWN` untuk memastikan tidak ada dua shot berurutan di posisi yang sama.
17. **Paritas `naskah.md` ↔ `prompt-video.md` (Baru v2.0):** memastikan jumlah scene dan durasi di tabel `Pembagian scene` pada `naskah.md` identik dengan `prompt-video.md`.
18. **Detektor Angka Mentah di Dialog (Baru v2.0):** memastikan tidak ada angka digit (`2011`, `14`) di dalam kutipan dialog lisan.
19. **Audit Kecepatan Bicara / Lip-Sync Pacing (Baru v2.0):** memperingatkan/menggagalkan jika jumlah kata di dalam sebuah shot melebihi `3,2 kata/detik` atau >14 kata per kalimat di microdrama vertikal.
20. **Pemindai Klise Anti-Sinetron (Baru v2.0):** memindai `konsep.md`, `naskah.md`, dan `prompt-video.md` dari kalimat sinetron dan deskripsi klise.
21. **Detektor Tanda Wajah Ilegal (Baru v2.0):** memblokir `mole`/`scar`/`tattoo`/`tahi lalat`/`bekas luka` di `cast.md` dan sheet kecuali ada penanda `Tanda wajah karena cerita:` di `cast.md`.
22. **Detektor Kontaminasi Shot Celah/Kaca (Baru v2.0):** melarang kata orang/`no face`/`no head`/`nobody`/`POV` di baris `SHOT` yang melihat lewat celah/kaca (`through the gap`, `keyhole`).
23. **Detektor Kontras Ketiadaan Benda & Over-Repetition (Baru v2.0):** melarang `darker`/`deeper colour` pada ketiadaan objek dan mendeteksi pengulangan berlebihan frasa pengunci benda.
24. **Validasi Anti-Sinkronisasi Figuran (Baru v2.0):** jika `CRITICAL` menyebut >2 orang total, `MOVEMENT NOTE` wajib memiliki pemecahan gerak figuran (`NEVER react as a block` / `never a synchronised`).
25. **Validasi Rubrik `konsep.md` & Reuse Aset Lintas Episode (Baru v2.0):** mengecek skor rubrik (≥4 semua, rata-rata ≥4,3) dan memastikan aset episode lama tidak digenerate ulang di episode baru.

Perbaiki proyek sampai keluar `Semua cek lolos.` sebelum diserahkan.

---

## Langkah 2 · Bangun Studio Produksi & Checklist Final

Jalankan:
```bash
python assets/tools/microdrama_cli.py board <folder_proyek>
```
Buka `<folder_proyek>/board.html` di browser dan pastikan seluruh kartu status berwarna hijau, daftar lampiran sesuai, serta:
- Teks bebas di dalam narasi `SHOT BREAKDOWN` tidak bertentangan dengan wardrobe atau tatanan rambut di blok terkunci `cast.md`.
- Setiap shot berisiko di `naskah.md` sudah disetujui oleh user.
- Beat penting benar-benar terbaca lewat visual/audio tanpa bergantung pada teks layar.

---

## Langkah 3 · Matriks 24 Gejala → Penyebab → Perbaikan Bedah

Bisa dikueri cepat kapan saja melalui:
`python assets/tools/dissect_video.py diagnose "<kata kunci gejala>"`

| # | Gejala di Video Hasil Generate | Akar Penyebab di Teks | Perbaikan Bedah (1–2 Kalimat) |
|---|---|---|---|
| 1 | Wajah berubah antar potongan klip | Deskripsi tokoh diparafrase, atau salah lampir sheet | Jalankan `microdrama_cli.py sync` dan pastikan sheet punya label nama tercetak |
| 2 | Teks aneh/simbol muncul di layar | Header `===` atau nama berkas masuk blok, atau `LANGUAGE` lupa melarang subtitle | Pindahkan header ke luar blok; pastikan `No subtitles, no captions, no on-screen text` ada |
| 3 | Huruf alien di label paket, plat nomor, atau layar HP | Properti tidak diberi `no printed text` / `licence plate blank`, atau HP menghadap kamera | Tambahkan `no labels, no printed text, licence plate blank` dan `screen always angled away from camera` |
| 4 | Dialog diucapkan dalam Bahasa Inggris | Blok `LANGUAGE` tidak mengunci `Speak the lines exactly as written` | Wajib tulis: `do not translate them, do not paraphrase them, do not invent extra lines` |
| 5 | Dialog diparafrase atau AI mengarang baris baru | Tidak ada `do not invent extra lines` atau jumlah baris tidak dikunci | Tambahkan `Exactly TWO lines are spoken in the whole scene` dan `do not invent extra lines` |
| 6 | Narasi atau gumaman muncul di scene hening | Blok `LANGUAGE` tidak memakai format `NO spoken dialogue` | Ganti isi `LANGUAGE` menjadi `This scene has NO spoken dialogue — no voices, no narration...` |
| 7 | Figuran bergerak atau menoleh serempak | `MOVEMENT NOTE` lupa memecah aksi figuran | Tulis 3 reaksi berbeda dan larangan keras `never a synchronised crowd turn` |
| 8 | Orang asing lewat di lorong/jalan yang mestinya sepi | `CRITICAL` tidak mengunci jumlah tokoh secara absolut | Tulis `ONE character only. Nobody else appears at any point` |
| 9 | Drama keluarga terasa seperti film horor | Tidak ada penolakan genre di `VIDEO STYLE & FORMAT` | Tambahkan `This is a quiet family drama, NOT horror and NOT a thriller` |
| 10 | Video terasa seperti trailer/montase terputus | `VIDEO STYLE & FORMAT` tidak menegaskan kontinuitas momen | Wajib tulis `ONE continuous ... — NOT a trailer, NOT a montage — cut between MULTIPLE camera positions` |
| 11 | Potongan kamera terasa monoton dari satu sudut | Dua shot berturut-turut dari posisi sama, atau `CAMERA` lupa aturan delta posisi | Pindahkan sudut salah satu shot; pastikan ada `Never two consecutive shots from the same position` |
| 12 | Gambar datar seperti lampu kantor rata | `LIGHTING` ditulis dengan kata sifat kosong (`dramatic lighting`) | Ganti dengan sumber cahaya konkret, arah, suhu Kelvin (3200K/5600K), negative fill, dan 1 aksen warna |
| 13 | Panel badan di sheet terpotong tanpa kepala | Daftar `Avoid:` pada sheet lupa menyertakan `missing head` | Tambahkan `missing head` dan `different faces between panels` di baris `Avoid:` |
| 14 | Jumlah orang bertambah/berkurang antar cut | Jumlah tokoh & figuran tidak dikunci numerik di `CRITICAL` | Buka `CRITICAL` dengan angka pasti: `TWO speaking characters plus twelve silent background staff` |
| 15 | Klip ditolak model atau bagian akhir terpotong | Durasi prompt di luar batas `4–30 detik` atau dialog terlalu padat (>3,2 kata/s) | Pecah scene di jeda alami agar 4–30 detik; kurangi kata atau perpanjang durasi shot |
| 16 | Pintu atau tata letak ruangan berubah antar klip | Pintu masuk tokoh tidak terdaftar di `set.md` | Tambahkan seluruh pintu masuk yang dipakai arc ke `set.md` lalu `sync` |
| 17 | Tokoh bocor ke sisi pintu yang salah (dalam vs luar) | Dua plate lokasi tanpa Triad Lokasi Ganda | Pasang Peta Referensi di `LOCATION` + Tag Lokasi di tiap `SHOT` + kunci posisi di `CONTINUITY` |
| 18 | Wajah atau kepala muncul di shot intip lewat celah/kaca | Shot itu menyebut tokoh atau larangan seperti `no face, no head` | Hapus semua kata orang/wajah dari baris `SHOT` tersebut; tulis benda/lantai yang terlihat saja |
| 19 | Kamera di sisi salah, kaca buram jadi bening, pintu terbuka | Sudut tidak ada di plate, atau benda ditegaskan berulang (`stays closed` di 3 blok) | Sebut posisi kamera & latar belakang 1×; hapus pengulangan penegasan pintu di blok lain |
| 20 | Tokoh berwajah aneh: codet besar, bisul di pipi | Tanda wajah kecil ditulis tanpa fungsi cerita hingga dibesar-besarkan AI | Hapus bekas luka/tahi lalat dari `cast.md`; biarkan sheet 3 panel yang mengunci wajah |
| 21 | Motor/paket hilang, dobel, atau pindah tempat antar cut | Tidak ada butir spesifik di blok `CONTINUITY` | Tambahkan 1 butir per benda: lokasi eksak, sejak `SHOT` berapa, dan `outside the frame — never gone` |
| 22 | Shot wide menyalin komposisi plate mentah-mentah | Sudut wide terpenting berlawanan dengan komposisi set plate | Generate ulang plate dari sudut wide shot terpenting adegan |
| 23 | Bekas kotak / petak bersih di debu berubah jadi keset/lempengan | Ketiadaan ditulis dengan kata kontras (`darker`, `deeper colour`) | Ganti menjadi deskripsi permukaan rata: `flat, level with the floor, nothing on it, not an object` |
| 24 | Muncul baris dialog tambahan di luar layar (*off-screen hallucination*) | Close-up tanpa wajah terlalu dekat momen dialog | Kunci jumlah total kalimat di `LANGUAGE`, atau pindahkan dialog ke shot yang menampilkan wajah pembicara |

---

## Langkah 4 · Loop Perbaikan Pasca-Generate (`dissect_video.py`)

Jika klip yang digenerate user memiliki plot hole, ikuti disiplin bedah berikut — jangan menebak dan jangan menumpuk kalimat:

1. **Bedah Video Terlebih Dahulu:**
   ```bash
   python assets/tools/dissect_video.py analyze <video.mp4> --prompt <epNN/prompt-video.md> --scene 1
   ```
   Perintah ini mengekstrak timestamp potongan adegan (`select='gt(scene,0.25)'`), membuat *contact sheet* 2 fps, membandingkan titik potong aktual terhadap timecode `SHOT`, dan menyiapkan perintah transkrip Whisper jika tersedia.
2. **Pisahkan Plot Hole dari Penyimpangan Kosmetik:** Sudut kamera sedikit bergeser tapi cerita tetap utuh bukanlah plot hole. Pintu terbuka pada cerita rumah terkunci adalah plot hole.
3. **Buat Cabang Versi Baru (`branch`) — Jangan Timpa yang Lama:**
   ```bash
   python assets/tools/dissect_video.py branch ep01/prompt-video.md --note "Fix shot 7 peephole contamination"
   ```
   Ini membuat `ep01/prompt-video-v2.md`. Ubah **hanya 1–2 kalimat** yang langsung menyasar akar penyebab.
4. **Uji dengan Variabel Kontrol Identik:** Model video, rasio, durasi, dan gambar referensi harus persis sama agar perbandingan adil.
5. **Rollback Jika Memburuk:** Prompt yang semakin panjang dan penuh larangan berulang justru sering memperburuk kepatuhan model. Jika `-v2.md` memburuk, kembali ke versi sebelumnya (`promote`) dan ganti pendekatan (misal memecah shot berisiko menjadi dua scene).
6. **Batas Model vs Batas Teks:** Jika plot hole yang sama bertahan setelah 2 putaran bedah pada prompt yang bersih, itu adalah batas kemampuan *multishot* model tersebut — tawarkan alternatif aman dari tabel Shot Berisiko atau sarankan menguji model lain.
