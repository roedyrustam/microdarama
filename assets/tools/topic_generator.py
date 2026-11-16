#!/usr/bin/env python3
"""Automated Microdrama Topic & Concept Premise Generator (Python 3.10+ stdlib only).

Generates high-retention vertical microdrama topics, hooks, and 7-gate
compliant concept packages for Gerbang 1 (brief.md) and Gerbang 2 (konsep.md).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from typing import Any

GENRE_CATALOG: dict[str, list[dict[str, Any]]] = {
    "balas-dendam": [
        {
            "id": "bd-01",
            "title": "Baju Kotor Pewaris Tunggal",
            "logline": "Seorang teknisi AC pabrik diremehkan oleh direktur baru di depan ratusan karyawan, sebelum nomor seri pada cincin peraknya membuka dokumen kepemilikan saham mutlak.",
            "hook_audio": "Bising denting baki besi terlempar ke lantai ubin marmer, disusul keheningan mendadak.",
            "hook_visual": "Sepatu pantofel menginjak surat wasiat yang basah kuyup di bawah tangga pabrik.",
            "premise_lines": [
                "Premis: Rama (30) bekerja sebagai teknisi pendingin ruangan di pabrik tekstil yang sebenarnya didirikan kakeknya.",
                "Pemicu: Direktur baru memotong gaji harian buruh dan menumpahkan kopi panas ke sepatu Rama saat inspeksi.",
                "Krisis: Rama memiliki 15 detik sebelum gerbang utama disegel untuk membuktikan identitas aslinya lewat stempel cap darah kakeknya.",
            ],
            "char_protagonist": "Rama, 30 tahun, kemeja drill kelabu berdebu arang, tatapan dingin tak berkedip, jam tangan kulit retak-retak.",
            "char_antagonist": "Kevin, 34 tahun, jas pinstripe tanpa dasi, cincin giok imitasi di jempol, sering menepuk bahu orang dengan nada merendahkan.",
            "sets": ["Ruang kompresor bawah tanah pabrik yang bising uap", "Lobi marmer mengkilap dengan lampu kristal redup"],
            "rubric": {"hook": 5, "spesifik": 5, "detail_meleset": 5, "dialog": 4, "diam": 5, "tanam_bayar": 5, "akhir": 4},
        },
        {
            "id": "bd-02",
            "title": "Gadai Terakhir Sang Juara",
            "logline": "Mantan atlet tembak presisi yang kini menjadi kurir paket mengantarkan kiriman ke vila terpencil, hanya untuk mendapati paket itu berisi lencana kejuaraannya yang dicuri lima tahun lalu.",
            "hook_audio": "Ketukan tiga kali di pintu kayu tebal, disusul suara kokangan pistol angin dari balik kisi jendela.",
            "hook_visual": "Tetesan air hujan dari ujung helm ojek mengenai amplop cokelat berstempel lilin merah.",
            "premise_lines": [
                "Premis: Dani (32) mengubur masa lalunya sebagai penembak jitu nasional demi merawat adiknya yang sakit.",
                "Pemicu: Paket COD tanpa nama penerima membimbingnya ke ruang bawah tanah rumah ketua komite yang memfitnahnya.",
                "Krisis: Ia dipaksa memilih menembak target siluet dalam 5 detik atau dokumen bukti fitnah dibakar di perapian.",
            ],
            "char_protagonist": "Dani, 32 tahun, jaket parasut hijau pudar berkerah tinggi, bekas kapalan tebal di jari telunjuk kanan, ransel kurir hitam kusam.",
            "char_antagonist": "Handoko, 52 tahun, kemeja batik sutra lengan panjang digulung rapi, kacamata bingkai emas, jemari selalu mengetuk meja.",
            "sets": ["Gang sempit pemukiman padat di tengah hujan deras", "Ruang kerja kayu jati dengan brankas besi terbuka"],
            "rubric": {"hook": 5, "spesifik": 5, "detail_meleset": 5, "dialog": 5, "diam": 4, "tanam_bayar": 5, "akhir": 4},
        },
    ],
    "misteri-urban": [
        {
            "id": "mu-01",
            "title": "Lantai 13 B yang Hilang",
            "logline": "Seorang staf kebersihan apartemen tua menemukan tombol lift bertuliskan 13B yang hanya muncul saat jarum jam menyentuh pukul 03.14 dini hari.",
            "hook_audio": "Denting bel lift bersuara ganda, disusul suara gesekan logam kabel seling di lorong gelap.",
            "hook_visual": "Cermin lift memperlihatkan pantulan koridor kosong, namun sensor pintu menolak menutup seolah terhalang sesuatu.",
            "premise_lines": [
                "Premis: Sarah (26) adalah petugas shift malam di apartemen tua berlantai 20 yang sedang sengketa.",
                "Pemicu: Saat membersihkan tombol lantai, ia melihat sidik jari basah di sela dinding partisi tombol 13 dan 14.",
                "Krisis: Pintu lift terbuka di lantai tanpa ventilasi dan ponselnya menerima pesan dari nomor unit yang sudah runtuh.",
            ],
            "char_protagonist": "Sarah, 26 tahun, rompi keselamatan jingga bergaris reflektif perak, rambut diikat cepol ketat, membawa walkie-talkie berlampu LED merah.",
            "char_antagonist": "Satpam Tua Marno, 58 tahun, seragam safari cokelat dengan badge pudar, selalu memutar tasbih hitam di saku kiri.",
            "sets": ["Kabin lift apartemen tua berdinding stainless kusam", "Koridor semen telanjang dengan pipa gantung meneteskan air"],
            "rubric": {"hook": 5, "spesifik": 5, "detail_meleset": 5, "dialog": 4, "diam": 5, "tanam_bayar": 5, "akhir": 5},
        },
        {
            "id": "mu-02",
            "title": "Paket Salah Alamat",
            "logline": "Seorang fotografer jalanan menerima kardus misterius tanpa nama pengirim yang berisi 36 lembar foto polaroid rumahnya sendiri yang diambil dari dalam lemarinya.",
            "hook_audio": "Suara disobeknya selotip cokelat tebal dengan derak lambat dan renyah di kamar tidur sepi.",
            "hook_visual": "Tangan gemetar menjatuhkan foto polaroid ke lantai lantai parket, tampak punggung orang yang sedang memegang foto tersebut.",
            "premise_lines": [
                "Premis: Bima (28) tinggal sendirian di paviliun sewa gang sempit Menteng.",
                "Pemicu: Kardus bekas rokok ditaruh di depan pintunya saat ia baru saja pulang mengunci pintu dari dalam.",
                "Krisis: Foto polaroid terakhir bertuliskan tanggal hari ini dengan sudut pandang dari kisi ventilasi tepat di atas kepalanya.",
            ],
            "char_protagonist": "Bima, 28 tahun, kaos oblong hitam polos, celana kargo pudar berlutut robek halus, kamera saku analog menggantung di leher.",
            "char_antagonist": "Bayangan di balik tirai kaca buram, bertubuh jangkung mengenakan jas hujan plastik bening.",
            "sets": ["Kamar sewa sempit dengan jendela nako berdebu", "Lorong gang sempit berpagar seng berkarat"],
            "rubric": {"hook": 5, "spesifik": 5, "detail_meleset": 5, "dialog": 4, "diam": 5, "tanam_bayar": 5, "akhir": 4},
        },
    ],
    "identitas-rahasia": [
        {
            "id": "ir-01",
            "title": "Marmut di Meja Bundar",
            "logline": "Seorang akuntan magang pemalu menyelundupkan flashdisk rekaman transaksi fiktif di dalam sol sepatunya saat menghadiri jamuan makan malam direksi.",
            "hook_audio": "Berdentingnya sendok perak yang sengaja dijatuhkan ke gelas kristal, menghentikan tawa para eksekutif.",
            "hook_visual": "Tangan di bawah taplak meja putih sedang mencongkel tumit sepatu pantofel dengan jepit kertas logam.",
            "premise_lines": [
                "Premis: Aris (24) berpura-pura gugup dan ceroboh di hadapan dewan komisaris konglomerasi tambang.",
                "Pemicu: Audit eksternal tiba-tiba dimajukan malam ini dan pintu ruang perjamuan dikunci dari luar oleh satpam.",
                "Krisis: Pemeriksaan barang bawaan dimulai dari kursinya; flashdisk harus dipindahkan ke saku jas komisaris utama tanpa ketahuan.",
            ],
            "char_protagonist": "Aris, 24 tahun, kemeja putih lengan panjang agak kebesaran, kacamata minus tebal bertangkai hitam, map cokelat diapit di ketiak.",
            "char_antagonist": "Baskoro, 60 tahun, setelan jas wol abu-abu arang, arloji saku berantai emas, cerutu menyala di asbak marmer.",
            "sets": ["Ruang privat restoran lantai 42 berdinding kaca malam hari", "Dapur basah restoran dengan asap penggorengan tebal"],
            "rubric": {"hook": 5, "spesifik": 5, "detail_meleset": 5, "dialog": 5, "diam": 5, "tanam_bayar": 5, "akhir": 4},
        },
    ],
    "thriller-survival": [
        {
            "id": "ts-01",
            "title": "Sinyal Nol Menit",
            "logline": "Dua insinyur terperangkap di dalam kontainer pendingin dermaga yang sedang diangkat derek ke atas kapal kargo menuju laut lepas.",
            "hook_audio": "Derit kencang rantai derek baja yang mengencang mendadak, mengguncang dinding logam dengan bunyi menggelegar.",
            "hook_visual": "Uap napas putih pekat mengepul di kegelapan saat lampu darurat merah berkedip satu kali lalu mati.",
            "premise_lines": [
                "Premis: Rio dan Tania terkunci di kontainer muatan daging beku saat memeriksa kebocoran freon.",
                "Pemicu: Crane pelabuhan mengangkat kontainer dan menumpuknya di barisan ketiga dek kapal kargo.",
                "Krisis: Suhu turun ke minus 18 derajat dan baterai walkie-talkie hanya tersisa untuk satu panggilan transmisi.",
            ],
            "char_protagonist": "Rio, 29 tahun, parka tebal bernoda oli mesin, helm proyek kuning bergores dalam, senter kepala LED berkedip lemah.",
            "char_antagonist": "Tania, 31 tahun, coverall merah berlogo pelabuhan, sarung tangan termal tebal, tatapan waspada mencurigai Rio.",
            "sets": ["Bagian dalam kontainer berinsulasi es tebal", "Dek kapal kargo basah air asin di tengah badai"],
            "rubric": {"hook": 5, "spesifik": 5, "detail_meleset": 5, "dialog": 4, "diam": 5, "tanam_bayar": 5, "akhir": 5},
        },
    ],
    "romansa-konflik": [
        {
            "id": "rk-01",
            "title": "Tiga Belas Menit Sebelum Sah",
            "logline": "Mempelai wanita mengenali cincin kawin di jari calon suaminya sebagai cincin milik tunangannya yang hilang di laut lima tahun lalu.",
            "hook_audio": "Petikan senar biola yang putus berdering di tengah lagu pengiring masuk pengantin, memicu bisik-bisik tamu.",
            "hook_visual": "Buket bunga mawar putih jatuh ke karpet merah, menyingkap ukiran nama tergores di sisi dalam cincin emas pengantin pria.",
            "premise_lines": [
                "Premis: Clara (27) hendak mengucapkan janji nikah dengan pengusaha properti muda rekan ayahnya.",
                "Pemicu: Saat bertukar cincin, ukiran inisial tersembunyi di balik mata berlian terbaca jelas olehnya.",
                "Krisis: Ia punya 13 menit sebelum akta ditandatangani untuk membongkar siapa pria di hadapannya tanpa membuat ayahnya serangan jantung.",
            ],
            "char_protagonist": "Clara, 27 tahun, gaun pengantin satin sederhana tanpa renda berlebih, tudung transparan tipis, genggaman tangan dingin kaku.",
            "char_antagonist": "Julian, 30 tahun, tuksedo hitam pekat berkerah satin mengkilap, senyum ramah tenang yang tidak pernah sampai ke matanya.",
            "sets": ["Kamar rias pengantin berlampu hangat dengan cermin antik berkaki tiga", "Altar gereja tua bertabur kelopak bunga melati"],
            "rubric": {"hook": 5, "spesifik": 5, "detail_meleset": 5, "dialog": 5, "diam": 5, "tanam_bayar": 5, "akhir": 4},
        },
    ],
}


def list_genres() -> list[str]:
    """Return list of available genre keys."""
    return sorted(GENRE_CATALOG.keys())


def generate_topics(genre: str | None = None, count: int = 1) -> list[dict[str, Any]]:
    """Generate high-retention microdrama topics."""
    pool: list[dict[str, Any]] = []
    if genre:
        g = genre.strip().lower()
        if g not in GENRE_CATALOG:
            raise ValueError(f"Genre tidak dikenal: '{genre}'. Pilihan: {', '.join(list_genres())}")
        pool = list(GENRE_CATALOG[g])
    else:
        for items in GENRE_CATALOG.values():
            pool.extend(items)

    # If count requested is larger than pool, cycle with variations
    selected: list[dict[str, Any]] = []
    shuffled = list(pool)
    random.shuffle(shuffled)
    for i in range(count):
        base = dict(shuffled[i % len(shuffled)])
        if i >= len(shuffled):
            base["id"] = f"{base['id']}-v{i+1}"
            base["title"] = f"{base['title']} (Variasi {i+1})"
        selected.append(base)
    return selected


def format_topic_markdown(topic: dict[str, Any]) -> str:
    """Format topic as structured markdown ready for brief.md / konsep.md."""
    lines: list[str] = [
        f"### {topic['title']} (`{topic['id']}`)",
        f"**Logline:** {topic['logline']}",
        "",
        f"- **Hook Audio (0-3s):** {topic['hook_audio']}",
        f"- **Hook Visual (0-3s):** {topic['hook_visual']}",
        "- **Premis 3 Baris:**",
    ]
    for p in topic["premise_lines"]:
        lines.append(f"  - {p}")
    lines.extend([
        f"- **Tokoh Utama:** {topic['char_protagonist']}",
        f"- **Lawan / Antagonis:** {topic['char_antagonist']}",
        f"- **Set Lokasi Utama:** {', '.join(topic['sets'])}",
        f"- **Skor Rubrik Standar:** Hook {topic['rubric']['hook']}/5 · Spesifik {topic['rubric']['spesifik']}/5 · "
        f"Detail Meleset {topic['rubric']['detail_meleset']}/5 · Dialog {topic['rubric']['dialog']}/5 · "
        f"Diam {topic['rubric']['diam']}/5 · Tanam & Bayar {topic['rubric']['tanam_bayar']}/5 · Akhir {topic['rubric']['akhir']}/5",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Microdrama Automated Topic & Concept Premise Generator")
    parser.add_argument("--genre", choices=list_genres(), default=None, help="Filter genre tema microdrama")
    parser.add_argument("--count", type=int, default=1, help="Jumlah topic yang dibuat (default: 1)")
    parser.add_argument("--list-genres", action="store_true", help="Daftar genre tema yang tersedia")
    parser.add_argument("--json", dest="output_json", action="store_true", help="Output dalam format JSON")

    args = parser.parse_args(argv)

    if args.list_genres:
        if args.output_json:
            print(json.dumps({"genres": list_genres()}, indent=2))
        else:
            print("Genre tema microdrama yang tersedia:")
            for g in list_genres():
                count = len(GENRE_CATALOG[g])
                print(f"  - {g} ({count} premis dasar)")
        return 0

    try:
        topics = generate_topics(genre=args.genre, count=args.count)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.output_json:
        print(json.dumps({"count": len(topics), "topics": topics}, indent=2))
    else:
        print(f"=== {len(topics)} TOPIC MICRODRAMA OTOMATIS (Presisi 7-Gerbang) ===")
        print()
        for i, t in enumerate(topics, 1):
            print(f"[{i}] {format_topic_markdown(t)}")
            print("-" * 60)
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
