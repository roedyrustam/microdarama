#!/usr/bin/env python3
"""Microdrama v2.0 Production CLI: init, add-ep, sync, board, check.

Zero external dependencies (Python 3.10+ stdlib only).

Usage:
  python assets/tools/bang_film_cli.py init <folder> [--title "Judul"] [--force]
  python assets/tools/bang_film_cli.py add-ep <folder> <ep_num> [--title "Judul Ep"]
  python assets/tools/bang_film_cli.py sync <folder>
  python assets/tools/bang_film_cli.py board <folder> [--out <path>]
  python assets/tools/bang_film_cli.py check <folder> [--json] [--strict]
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import shutil
import sys
import textwrap
from typing import Any


TOOLS_DIR = pathlib.Path(__file__).resolve().parent
TEMPLATE_DIR = TOOLS_DIR.parent / "template"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import check_prompts as verifier  # noqa: E402


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _wrap_text(text: str, width: int = 88) -> str:
    lines: list[str] = []
    for para in text.strip().splitlines():
        if not para.strip():
            lines.append("")
        else:
            lines.append(textwrap.fill(para.strip(), width=width, break_long_words=False, break_on_hyphens=False))
    return "\n".join(lines)


def cmd_init(args: argparse.Namespace) -> int:
    target = pathlib.Path(args.folder)
    if (target / "brief.md").exists() and not args.force:
        print(f"Proyek sudah ada di {target}. Gunakan --force untuk menimpa.", file=sys.stderr)
        return 1

    target.mkdir(parents=True, exist_ok=True)
    ep01 = target / "ep01"
    ep01.mkdir(parents=True, exist_ok=True)
    title = args.title or target.name.replace("-", " ").replace("_", " ").title()

    root_files = ["brief.md", "konsep.md", "cast.md", "set.md"]
    ep_files = ["naskah.md", "prompt-aset.md", "prompt-video.md"]

    for fname in root_files:
        content = (TEMPLATE_DIR / fname).read_text(encoding="utf-8")
        content = content.replace("<judul proyek>", title).replace("<judul>", title)
        (target / fname).write_text(content, encoding="utf-8")

    for fname in ep_files:
        content = (TEMPLATE_DIR / fname).read_text(encoding="utf-8")
        content = (
            content.replace("<judul>", title)
            .replace("<judul episode>", "Episode 1")
            .replace("<NN>", "01")
        )
        if fname == "prompt-aset.md":
            content = re.sub(r"^Pakai ulang dari ep <NN>.*\n\n", "", content, flags=re.M)
        (ep01 / fname).write_text(content, encoding="utf-8")

    print(f"Proyek Microdrama diinisialisasi di: {target}")
    print("Langkah berikutnya: isi brief.md (Gerbang 1) lalu konsep.md (Gerbang 2).")
    return 0


def cmd_add_ep(args: argparse.Namespace) -> int:
    target = pathlib.Path(args.folder)
    if not (target / "brief.md").exists():
        print(f"Folder bukan proyek Microdrama yang valid (brief.md tidak ditemukan): {target}", file=sys.stderr)
        return 1

    ep_num = int(args.ep_num)
    nn = f"{ep_num:02d}"
    ep_dir = target / f"ep{nn}"
    if ep_dir.exists() and not args.force:
        print(f"Episode ep{nn} sudah ada di {target}. Gunakan --force untuk menimpa.", file=sys.stderr)
        return 1
    ep_dir.mkdir(parents=True, exist_ok=True)

    # Extract project title from brief.md
    brief_text = (target / "brief.md").read_text(encoding="utf-8")
    m_title = re.search(r"^# Brief — (.+)$", brief_text, re.M)
    proj_title = m_title.group(1).strip() if m_title else target.name
    ep_title = args.title or f"Episode {ep_num}"

    # Collect existing assets from prior episodes
    prior_assets: list[str] = []
    for prev_ep in sorted(p for p in target.iterdir() if p.is_dir() and p.name.startswith("ep") and p.name < f"ep{nn}"):
        aset_file = prev_ep / "prompt-aset.md"
        if aset_file.exists():
            for match in re.findall(r"Simpan sebagai: `([^`]+)`", aset_file.read_text(encoding="utf-8")):
                if match not in prior_assets:
                    prior_assets.append(match)

    for fname in ("naskah.md", "prompt-aset.md", "prompt-video.md"):
        content = (TEMPLATE_DIR / fname).read_text(encoding="utf-8")
        content = (
            content.replace("<judul>", f"{proj_title} · Ep {nn}")
            .replace("<judul episode>", ep_title)
            .replace("<NN>", nn)
        )
        if fname == "prompt-aset.md":
            if prior_assets:
                reuse_line = "Pakai ulang dari ep sebelumnya, jangan generate ulang: " + ", ".join(
                    f"`{a}`" for a in prior_assets
                ) + "."
                content = re.sub(r"^Pakai ulang dari ep .*$", reuse_line, content, flags=re.M)
            else:
                content = re.sub(r"^Pakai ulang dari ep .*\n\n", "", content, flags=re.M)
        (ep_dir / fname).write_text(content, encoding="utf-8")

    print(f"Episode ep{nn} ditambahkan ke {target}.")
    if prior_assets:
        print("Aset yang otomatis masuk daftar pakai ulang:", ", ".join(prior_assets))
    return 0


def _sync_prompt_aset(ep_dir: pathlib.Path, cast: dict[str, Any], sets: dict[str, Any]) -> int:
    aset_path = ep_dir / "prompt-aset.md"
    if not aset_path.exists():
        return 0
    raw = aset_path.read_text(encoding="utf-8")
    sections = re.split(r"(\n## )", raw)
    if len(sections) <= 1:
        return 0

    changed = 0
    out_parts = [sections[0]]
    for i in range(1, len(sections), 2):
        delim = sections[i]
        sek = sections[i + 1]
        simpan = re.search(r"Simpan sebagai: `([^`]+)` → token `\[(gambar_[a-z0-9_]+)\]`", sek)
        kode_m = re.search(r"(```[^\n]*\n)(.*?)(```)", sek, re.S)
        if simpan and kode_m:
            _berkas, token = simpan.groups()
            body = kode_m.group(2)
            new_body = body
            if token in cast:
                c = cast[token]
                orang, _, baju = c["panjang"].partition("WARDROBE:")
                new_body = re.sub(
                    r"THE PERSON:.*?(?=\n\s*\nWARDROBE:)",
                    "THE PERSON: " + orang.strip(),
                    new_body,
                    flags=re.S,
                )
                new_body = re.sub(
                    r"WARDROBE:.*?(?=\n\s*\nA clean white sans-serif label)",
                    "WARDROBE:" + baju.rstrip(),
                    new_body,
                    flags=re.S,
                )
            else:
                s = next((v for v in sets.values() if v["token"] == token), None)
                if s:
                    paras = new_body.strip().split("\n\n")
                    if len(paras) >= 3:
                        paras[1] = s["blok"].strip()
                        new_body = "\n\n".join(paras) + "\n"
            if new_body != body:
                sek = sek[: kode_m.start(2)] + new_body + sek[kode_m.end(2) :]
                changed += 1
        out_parts.extend([delim, sek])

    if changed:
        aset_path.write_text("".join(out_parts), encoding="utf-8")
    return changed


def _sync_characters_block(char_block: str, cast: dict[str, Any]) -> str:
    lines = char_block.splitlines()
    header = lines[0]
    entries: list[str] = []
    cur: list[str] = []
    for ln in lines[1:]:
        if re.match(r"^[A-Z0-9_ ]+\s+(?:\[gambar_|—)", ln.strip()):
            if cur:
                entries.append(" ".join(cur))
            cur = [ln.strip()]
        elif ln.strip():
            cur.append(ln.strip())
    if cur:
        entries.append(" ".join(cur))

    updated: list[str] = []
    for entry in entries:
        tok_m = re.search(r"\[(gambar_[a-z0-9_]+)\]", entry)
        if tok_m and tok_m.group(1) in cast:
            c = cast[tok_m.group(1)]
            has_placeholder = "<" in c["pendek"]
            locked_prefix = verifier.rata(c["pendek"].split("<")[0])
            entry_norm = verifier.rata(entry)
            if locked_prefix not in entry_norm:
                if not has_placeholder:
                    entry = _wrap_text(locked_prefix)
                else:
                    # Preserve the action tail after the comma count of the locked prefix
                    comma_count = locked_prefix.rstrip(", ").count(",") + 1
                    parts = entry_norm.split(",")
                    if len(parts) > comma_count:
                        tail = ", ".join(parts[comma_count:]).strip()
                        entry = _wrap_text(f"{locked_prefix} {tail}")
                    else:
                        entry = _wrap_text(locked_prefix.rstrip(", ") + ".")
            else:
                entry = _wrap_text(entry_norm)
        updated.append(entry)
    return header + "\n" + "\n".join(updated) + "\n\n"


def _sync_location_block(loc_block: str, sets: dict[str, Any]) -> str:
    new_block = loc_block
    for _nama, s in sets.items():
        tok = s["token"]
        if not tok:
            continue
        pattern = re.compile(
            rf"(^[^\n]*\[{re.escape(tok)}\]\s*—\s*)(.*?)(?=\n(?:[^\n]*\[gambar_|The\s+[a-z]+\s+—|\s*$))",
            re.M | re.S,
        )
        m = pattern.search(new_block)
        if m:
            existing_desc = verifier.rata(m.group(2))
            locked_desc = verifier.rata(s["blok"])
            if existing_desc != locked_desc:
                replacement = _wrap_text(m.group(1) + s["blok"].strip())
                # Keep label prefix on same line as start of wrapped text
                replacement_single = m.group(1) + s["blok"].strip()
                wrapped = _wrap_text(replacement_single)
                new_block = new_block[: m.start()] + wrapped + new_block[m.end() :]
    return new_block


def _sync_prompt_video(ep_dir: pathlib.Path, cast: dict[str, Any], sets: dict[str, Any]) -> int:
    pv_path = ep_dir / "prompt-video.md"
    if not pv_path.exists():
        return 0
    raw = pv_path.read_text(encoding="utf-8")
    peta: dict[str, str] = {t: c["berkas"] for t, c in cast.items() if c["berkas"]}
    peta.update({s["token"]: s["berkas"] for s in sets.values() if s["token"] and s["berkas"]})

    sections = re.split(r"(\n## )", raw)
    if len(sections) <= 1:
        return 0

    changed = 0
    out_parts = [sections[0]]
    for i in range(1, len(sections), 2):
        delim = sections[i]
        sek = sections[i + 1]
        kode_m = re.search(r"(```[^\n]*\n)(.*?)(```)", sek, re.S)
        if kode_m:
            blk = kode_m.group(2)
            new_blk = blk
            # 1. Sync Lampirkan line from [gambar_x] tokens in order of appearance
            seen_toks: list[str] = []
            for tok in re.findall(r"\[(gambar_[a-z0-9_]+)\]", new_blk):
                if tok not in seen_toks:
                    seen_toks.append(tok)
            desired_files = [peta[t] for t in seen_toks if t in peta]
            if desired_files:
                desired_line = "Lampirkan: " + ", ".join(f"`{fn}`" for fn in desired_files)
                if re.search(r"^Lampirkan:.*$", sek, re.M):
                    sek_updated = re.sub(r"^Lampirkan:.*$", desired_line, sek, count=1, flags=re.M)
                    if sek_updated != sek:
                        sek = sek_updated
                        changed += 1

            # Re-find code match inside updated sek
            kode_m = re.search(r"(```[^\n]*\n)(.*?)(```)", sek, re.S)
            assert kode_m is not None
            blk = kode_m.group(2)
            new_blk = blk

            # 2. Sync CHARACTERS block
            char_m = re.search(r"(CHARACTERS \(from reference images\)\n.*?)(?=\nLOCATION\b)", new_blk, re.S)
            if char_m:
                synced_char = _sync_characters_block(char_m.group(1), cast).rstrip() + "\n"
                if synced_char != char_m.group(1):
                    new_blk = new_blk[: char_m.start(1)] + synced_char + new_blk[char_m.end(1) :]

            # 3. Sync LOCATION block
            loc_m = re.search(r"(LOCATION \(from references\)\n.*?)(?=\n(?:CONTINUITY|AUDIO)\b)", new_blk, re.S)
            if loc_m:
                synced_loc = _sync_location_block(loc_m.group(1), sets)
                if synced_loc != loc_m.group(1):
                    new_blk = new_blk[: loc_m.start(1)] + synced_loc + new_blk[loc_m.end(1) :]

            if new_blk != blk:
                sek = sek[: kode_m.start(2)] + new_blk + sek[kode_m.end(2) :]
                changed += 1

        out_parts.extend([delim, sek])

    if changed:
        pv_path.write_text("".join(out_parts), encoding="utf-8")
    return changed


def cmd_sync(args: argparse.Namespace) -> int:
    folder = pathlib.Path(args.folder)
    if not (folder / "cast.md").exists() or not (folder / "set.md").exists():
        print("cast.md atau set.md tidak ditemukan.", file=sys.stderr)
        return 1

    cast = verifier.baca_cast(folder)
    sets = verifier.baca_set(folder)
    total_changes = 0

    for ep in sorted(p for p in folder.iterdir() if p.is_dir() and p.name.startswith("ep")):
        c_aset = _sync_prompt_aset(ep, cast, sets)
        c_vid = _sync_prompt_video(ep, cast, sets)
        if c_aset or c_vid:
            print(f"Disinkronkan {ep.name}: {c_aset} aset, {c_vid} scene/lampiran.")
        total_changes += c_aset + c_vid

    if total_changes == 0:
        print("Semua blok terkunci dan lampiran sudah 100% sinkron.")
    return 0


def _parse_brief(folder: pathlib.Path) -> dict[str, str]:
    p = folder / "brief.md"
    data: dict[str, str] = {"Title": folder.name}
    if not p.exists():
        return data
    text = p.read_text(encoding="utf-8")
    m = re.search(r"^# Brief — (.+)$", text, re.M)
    if m:
        data["Title"] = m.group(1).strip()
    for k, v in re.findall(r"^\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|$", text, re.M):
        k_s, v_s = k.strip(), v.strip()
        if k_s and v_s and not set(k_s) <= {"-"}:
            data[k_s] = v_s
    t_m = re.search(r"^Topik:\s*(.+)$", text, re.M)
    if t_m:
        data["Topik"] = t_m.group(1).strip()
    return data


def _parse_konsep(folder: pathlib.Path) -> dict[str, Any]:
    p = folder / "konsep.md"
    out: dict[str, Any] = {"logline": "", "premis": [], "rubrik": "", "hook": ""}
    if not p.exists():
        return out
    text = p.read_text(encoding="utf-8")
    m_log = re.search(r"## Logline\s*\n(.*?)(?=\n## |\Z)", text, re.S)
    if m_log:
        out["logline"] = verifier.rata(m_log.group(1))
    m_prem = re.search(r"## Premis\s*\n(.*?)(?=\n## |\Z)", text, re.S)
    if m_prem:
        out["premis"] = [ln.strip() for ln in m_prem.group(1).splitlines() if re.match(r"^\s*\d+\.", ln)]
    m_hook = re.search(r"Dipilih user:\s*(.+)", text)
    if m_hook:
        out["hook"] = m_hook.group(1).strip()
    m_rub = re.search(r"## Skor rubrik\s*\n(.*?)(?=\n## |\Z)", text, re.S)
    if m_rub:
        out["rubrik"] = m_rub.group(1).strip().splitlines()[0]
    return out


def _parse_episode_scenes(ep_dir: pathlib.Path) -> dict[str, Any]:
    ep_data: dict[str, Any] = {
        "name": ep_dir.name,
        "title": ep_dir.name.upper(),
        "shots": [],
        "risks": {},
        "assets": [],
        "reuse": "",
        "scenes": [],
    }
    naskah_p = ep_dir / "naskah.md"
    if naskah_p.exists():
        ntext = naskah_p.read_text(encoding="utf-8")
        m_t = re.search(r"^# Naskah — (.+)$", ntext, re.M)
        if m_t:
            ep_data["title"] = m_t.group(1).strip()
        for row in re.findall(
            r"^\|\s*(s\d+)\s*\|\s*(\d+)\s*s\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|",
            ntext,
            re.M,
        ):
            ep_data["shots"].append(
                {
                    "id": row[0].strip(),
                    "dur": int(row[1]),
                    "set": row[2].strip(),
                    "who": row[3].strip(),
                    "size": row[4].strip(),
                    "cam": row[5].strip(),
                    "dlg": row[6].strip(),
                }
            )
        for s_ids, faktor, dec in re.findall(r"^\|\s*(s[\d,\s]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|$", ntext, re.M):
            for sid in re.findall(r"s\d+", s_ids):
                ep_data["risks"][sid] = f"{faktor.strip()} ({dec.strip()})"

    aset_p = ep_dir / "prompt-aset.md"
    if aset_p.exists():
        atext = aset_p.read_text(encoding="utf-8")
        r_m = re.search(r"^Pakai ulang.*$", atext, re.M)
        if r_m:
            ep_data["reuse"] = r_m.group(0)
        for sek in re.split(r"\n## ", atext)[1:]:
            kode = verifier.blok_kode(sek)
            if not kode:
                continue
            judul = sek.splitlines()[0].strip()
            simpan_m = re.search(r"Simpan sebagai: `([^`]+)` → token `\[(gambar_[a-z0-9_]+)\]`", sek)
            ep_data["assets"].append(
                {
                    "title": judul,
                    "file": simpan_m.group(1) if simpan_m else "",
                    "token": simpan_m.group(2) if simpan_m else "",
                    "prompt": kode[0].strip(),
                }
            )

    pv_p = ep_dir / "prompt-video.md"
    if pv_p.exists():
        pvtext = pv_p.read_text(encoding="utf-8")
        for sek in re.split(r"\n## ", pvtext)[1:]:
            kode = verifier.blok_kode(sek)
            if not kode:
                continue
            judul = sek.splitlines()[0].strip()
            lamp_m = re.search(r"^Lampirkan:\s*(.+)$", sek, re.M)
            attachments = re.findall(r"`([^`]+)`", lamp_m.group(1)) if lamp_m else []
            dur_m = re.search(r"(\d+) detik", judul)
            dur = int(dur_m.group(1)) if dur_m else 0
            blk = kode[0].strip()
            shot_bars = []
            for sm in re.finditer(r"^SHOT (\d+) \((\d+)-(\d+)s\)(?: — ([^—]+) —)?([^\n:]*)", blk, re.M):
                sn, a, b = int(sm.group(1)), int(sm.group(2)), int(sm.group(3))
                tag = sm.group(4).strip() if sm.group(4) else ""
                meta = sm.group(5).strip()
                shot_bars.append({"n": sn, "start": a, "end": b, "dur": b - a, "tag": tag, "meta": meta})
            ep_data["scenes"].append(
                {
                    "title": judul,
                    "dur": dur,
                    "attachments": attachments,
                    "shot_bars": shot_bars,
                    "prompt": blk,
                }
            )
    return ep_data


def cmd_board(args: argparse.Namespace) -> int:
    folder = pathlib.Path(args.folder)
    if not (folder / "brief.md").exists():
        print(f"Folder bukan proyek Microdrama yang valid: {folder}", file=sys.stderr)
        return 1

    out_path = pathlib.Path(args.out) if args.out else (folder / "board.html")
    report = verifier.run_checks(folder, strict=False)
    brief = _parse_brief(folder)
    konsep = _parse_konsep(folder)
    cast = verifier.baca_cast(folder)
    sets = verifier.baca_set(folder)
    episodes = [_parse_episode_scenes(ep) for ep in sorted(p for p in folder.iterdir() if p.is_dir() and p.name.startswith("ep"))]

    is_ok = report["status"] == "ok" and not report["warnings"]
    badge_cls = "badge-ok" if report["status"] == "ok" else "badge-err"
    badge_txt = (
        f"25-Point Verifier: LOLOS ({len(episodes)} Ep · {len(cast)} Cast · {len(sets)} Set/Prop)"
        if report["status"] == "ok"
        else f"25-Point Verifier: {len(report['errors'])} Masalah"
    )

    issues_html = ""
    if report["errors"] or report["warnings"]:
        items = "".join(f"<li class='err-item'>{html.escape(e)}</li>" for e in report["errors"])
        items += "".join(f"<li class='warn-item'>{html.escape(w)}</li>" for w in report["warnings"])
        issues_html = f"<section class='card'><h2>Temuan Verifier</h2><ul class='issue-list'>{items}</ul></section>"

    cast_cards = []
    for tok, c in cast.items():
        cast_cards.append(
            f"<div class='bible-card'>"
            f"<div class='bible-head'><strong>{html.escape(c['nama'])}</strong><code>[{html.escape(tok)}]</code></div>"
            f"<div class='file-pill'>{html.escape(c['berkas'] or '')}</div>"
            f"<pre class='mono-sm'>{html.escape(c['panjang'].strip())}</pre>"
            f"</div>"
        )
    set_cards = []
    for name, s in sets.items():
        tok_badge = f"<code>[{html.escape(s['token'])}]</code>" if s["token"] else "<span class='tag-muted'>teks-saja</span>"
        file_badge = f"<div class='file-pill'>{html.escape(s['berkas'])}</div>" if s["berkas"] else ""
        set_cards.append(
            f"<div class='bible-card'>"
            f"<div class='bible-head'><strong>{html.escape(name)}</strong>{tok_badge}</div>"
            f"{file_badge}"
            f"<pre class='mono-sm'>{html.escape(s['blok'].strip())}</pre>"
            f"</div>"
        )

    ep_sections = []
    for idx, ep in enumerate(episodes):
        reuse_banner = f"<p class='reuse-note'>{html.escape(ep['reuse'])}</p>" if ep["reuse"] else ""
        asset_blocks = []
        for a in ep["assets"]:
            pid = f"aset-{ep['name']}-{a['token'] or len(asset_blocks)}"
            asset_blocks.append(
                f"<div class='prompt-box'>"
                f"<div class='prompt-top'><div><strong>{html.escape(a['title'])}</strong> · <span class='file-pill'>{html.escape(a['file'])}</span></div>"
                f"<button class='copy-btn' onclick=\"copyPrompt('{pid}', this)\">Salin Prompt Aset</button></div>"
                f"<pre id='{pid}' class='prompt-pre'>{html.escape(a['prompt'])}</pre>"
                f"</div>"
            )

        scene_blocks = []
        for sidx, sc in enumerate(ep["scenes"]):
            spid = f"vid-{ep['name']}-{sidx}"
            att_html = "".join(f"<span class='file-pill'>{html.escape(fn)}</span>" for fn in sc["attachments"])
            total_dur = max(1, sc["dur"])
            timeline_segs = []
            for sb in sc["shot_bars"]:
                pct = (sb["dur"] / total_dur) * 100.0
                sid = f"s{sb['n']:02d}"
                risk_txt = ep["risks"].get(sid, "")
                risk_cls = " seg-risk" if risk_txt else ""
                title_tip = f"SHOT {sb['n']} ({sb['start']}-{sb['end']}s) {sb['meta']}"
                if risk_txt:
                    title_tip += f" | RISIKO: {risk_txt}"
                timeline_segs.append(
                    f"<div class='tl-seg{risk_cls}' style='width:{pct:.2f}%' title='{html.escape(title_tip)}'>"
                    f"<span class='tl-id'>S{sb['n']}</span><span class='tl-sec'>{sb['dur']}s</span>"
                    f"</div>"
                )
            scene_blocks.append(
                f"<div class='prompt-box'>"
                f"<div class='prompt-top'>"
                f"<div><strong>{html.escape(sc['title'])}</strong><div class='att-row'>Lampirkan: {att_html}</div></div>"
                f"<button class='copy-btn copy-primary' onclick=\"copyPrompt('{spid}', this)\">Salin Prompt Video</button>"
                f"</div>"
                f"<div class='tl-bar'>{''.join(timeline_segs)}</div>"
                f"<pre id='{spid}' class='prompt-pre'>{html.escape(sc['prompt'])}</pre>"
                f"</div>"
            )

        shot_rows_html = []
        for sh in ep["shots"]:
            risk_badge = (
                f"<span class='risk-pill' title='{html.escape(ep['risks'][sh['id']])}'>RISIKO</span>"
                if sh["id"] in ep["risks"]
                else "<span class='ok-pill'>AMAN</span>"
            )
            shot_rows_html.append(
                f"<tr><td class='num'>{html.escape(sh['id'])}</td><td class='num'>{sh['dur']}s</td>"
                f"<td>{html.escape(sh['set'])}</td><td>{html.escape(sh['size'])}</td>"
                f"<td>{html.escape(sh['cam'])}</td><td>{html.escape(sh['dlg'])}</td><td>{risk_badge}</td></tr>"
            )

        active_cls = " active" if idx == 0 else ""
        ep_sections.append(
            f"<div id='tab-{html.escape(ep['name'])}' class='ep-panel{active_cls}'>"
            f"<h2>{html.escape(ep['title'])}</h2>"
            f"<h3>Shot List & Audit Risiko</h3>"
            f"<div class='table-wrap'><table><thead><tr><th>Shot</th><th>Durasi</th><th>Set</th><th>Ukuran</th><th>Posisi Kamera</th><th>Dialog</th><th>Status</th></tr></thead>"
            f"<tbody>{''.join(shot_rows_html)}</tbody></table></div>"
            f"<h3>Prompt Aset (Gerbang 5)</h3>{reuse_banner}{''.join(asset_blocks) if asset_blocks else '<p class=muted>Semua aset memakai ulang dari episode sebelumnya.</p>'}"
            f"<h3>Prompt Video (Gerbang 6)</h3>{''.join(scene_blocks)}"
            f"</div>"
        )

    ep_tabs = "".join(
        f"<button class='tab-btn{' active' if i == 0 else ''}' onclick=\"showTab('{html.escape(ep['name'])}', this)\">{html.escape(ep['name'].upper())}</button>"
        for i, ep in enumerate(episodes)
    )

    doc_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Microdrama Studio — {html.escape(brief.get('Title', 'Proyek'))}</title>
<style>
  :root {{
    --bg: #0c0f14; --surface: #141922; --surface-2: #1b222e; --border: #262e3d;
    --text: #eef2f7; --muted: #93a0b4; --accent: #f59e0b; --ok: #10b981; --err: #ef4444;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
  .wrap {{ max-width: 1200px; margin: 0 auto; padding: 24px 20px 64px; }}
  .topbar {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px; border-bottom: 1px solid var(--border); padding-bottom: 18px; margin-bottom: 24px; }}
  h1 {{ margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }}
  h2 {{ font-size: 17px; margin: 0 0 12px; font-weight: 600; }}
  h3 {{ font-size: 14px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 24px 0 10px; }}
  .sub {{ color: var(--muted); font-size: 13px; margin-top: 4px; }}
  .badge-ok {{ background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.35); padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums; }}
  .badge-err {{ background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.35); padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; }}
  .grid-meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 20px; }}
  .meta-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; }}
  .meta-k {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }}
  .meta-v {{ font-size: 14px; font-weight: 600; margin-top: 4px; font-variant-numeric: tabular-nums; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 18px; margin-bottom: 20px; }}
  .bible-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 14px; }}
  .bible-card {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px; padding: 14px; }}
  .bible-head {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; color: var(--accent); }}
  .file-pill {{ display: inline-block; font-family: ui-monospace, monospace; font-size: 11px; background: #0d121a; border: 1px solid var(--border); color: #cbd5e1; padding: 2px 7px; border-radius: 4px; margin: 2px 4px 2px 0; }}
  .mono-sm {{ font-family: ui-monospace, monospace; font-size: 11.5px; color: #cbd5e1; white-space: pre-wrap; margin: 8px 0 0; line-height: 1.45; }}
  .tabs {{ display: flex; gap: 8px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; }}
  .tab-btn {{ background: var(--surface); border: 1px solid var(--border); color: var(--muted); padding: 7px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; }}
  .tab-btn.active {{ background: var(--surface-2); color: var(--text); border-color: var(--accent); }}
  .ep-panel {{ display: none; }}
  .ep-panel.active {{ display: block; }}
  .table-wrap {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 8px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; background: var(--surface); }}
  th, td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--border); }}
  th {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); background: var(--surface-2); }}
  td.num {{ font-variant-numeric: tabular-nums; font-family: ui-monospace, monospace; white-space: nowrap; }}
  .risk-pill {{ background: rgba(245,158,11,0.14); color: #fbbf24; border: 1px solid rgba(245,158,11,0.35); padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
  .ok-pill {{ background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.28); padding: 2px 7px; border-radius: 4px; font-size: 11px; font-weight: 600; }}
  .prompt-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-bottom: 16px; }}
  .prompt-top {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 10px; }}
  .att-row {{ margin-top: 4px; font-size: 12px; color: var(--muted); }}
  .copy-btn {{ background: var(--surface-2); border: 1px solid var(--border); color: var(--text); padding: 7px 13px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }}
  .copy-btn:hover {{ border-color: var(--accent); }}
  .copy-primary {{ background: #f59e0b; color: #0c0f14; border-color: #f59e0b; }}
  .tl-bar {{ display: flex; gap: 3px; margin-bottom: 10px; height: 28px; }}
  .tl-seg {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: 4px; display: flex; align-items: center; justify-content: space-between; padding: 0 7px; font-size: 11px; font-family: ui-monospace, monospace; font-variant-numeric: tabular-nums; overflow: hidden; }}
  .tl-seg.seg-risk {{ border-color: rgba(245,158,11,0.65); background: rgba(245,158,11,0.08); }}
  .tl-sec {{ color: var(--muted); }}
  .prompt-pre {{ background: #0a0d12; border: 1px solid var(--border); border-radius: 6px; padding: 12px; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; color: #dbe3ee; white-space: pre-wrap; max-height: 360px; overflow-y: auto; margin: 0; }}
  .reuse-note {{ font-size: 13px; color: var(--accent); margin: 4px 0 12px; }}
  .muted {{ color: var(--muted); font-size: 13px; }}
  .issue-list {{ margin: 0; padding-left: 18px; font-size: 13px; }}
  .err-item {{ color: #f87171; margin-bottom: 4px; }}
  .warn-item {{ color: #fbbf24; margin-bottom: 4px; }}
</style>
</head>
<body>
<div class="wrap">
  <header class="topbar">
    <div>
      <h1>Microdrama Studio · {html.escape(brief.get('Title', 'Proyek'))}</h1>
      <div class="sub">{html.escape(brief.get('Topik', ''))}</div>
    </div>
    <div class="{badge_cls}">{html.escape(badge_txt)}</div>
  </header>

  <section class="grid-meta">
    <div class="meta-box"><div class="meta-k">Format</div><div class="meta-v">{html.escape(brief.get('Format', '—'))}</div></div>
    <div class="meta-box"><div class="meta-k">Rasio (UI AI Video)</div><div class="meta-v">{html.escape(brief.get('Rasio', '—'))}</div></div>
    <div class="meta-box"><div class="meta-k">Durasi Target</div><div class="meta-v">{html.escape(brief.get('Durasi', '—'))}</div></div>
    <div class="meta-box"><div class="meta-k">Bahasa Dialog</div><div class="meta-v">{html.escape(brief.get('Bahasa dialog', '—'))}</div></div>
    <div class="meta-box"><div class="meta-k">Look</div><div class="meta-v">{html.escape(brief.get('Look', '—'))}</div></div>
  </section>

  {issues_html}

  <section class="card">
    <h2>Konsep & Rubrik</h2>
    <p><strong>Logline:</strong> {html.escape(konsep['logline'])}</p>
    <p><strong>Hook Dipilih:</strong> {html.escape(konsep['hook'])}</p>
    <p><strong>Rubrik:</strong> <code>{html.escape(konsep['rubrik'])}</code></p>
  </section>

  <section class="card">
    <h2>Cast & Set Bible Terkunci</h2>
    <div class="bible-grid">{''.join(cast_cards + set_cards)}</div>
  </section>

  <nav class="tabs">{ep_tabs}</nav>
  {''.join(ep_sections)}
</div>
<script>
function showTab(ep, btn) {{
  document.querySelectorAll('.ep-panel').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  const target = document.getElementById('tab-' + ep);
  if (target) target.classList.add('active');
  if (btn) btn.classList.add('active');
}}
function copyPrompt(id, btn) {{
  const text = document.getElementById(id).innerText;
  navigator.clipboard.writeText(text).then(() => {{
    const prev = btn.innerText;
    btn.innerText = 'Tersalin!';
    setTimeout(() => btn.innerText = prev, 1400);
  }});
}}
</script>
</body>
</html>
"""
    out_path.write_text(doc_html, encoding="utf-8")
    print(f"Studio Produksi HTML dibuat di: {out_path}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    check_args = [args.folder]
    if args.json:
        check_args.append("--json")
    if args.strict:
        check_args.append("--strict")
    return verifier.main(check_args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Microdrama v2.0 Production CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Buat proyek Microdrama baru dari template")
    p_init.add_argument("folder")
    p_init.add_argument("--title", default=None)
    p_init.add_argument("--force", action="store_true")

    p_add = sub.add_parser("add-ep", help="Tambah episode baru + daftar reuse aset")
    p_add.add_argument("folder")
    p_add.add_argument("ep_num", type=int)
    p_add.add_argument("--title", default=None)
    p_add.add_argument("--force", action="store_true")

    p_sync = sub.add_parser("sync", help="Sinkronkan blok cast/set terkunci & Lampirkan ke seluruh episode")
    p_sync.add_argument("folder")

    p_board = sub.add_parser("board", help="Generate Studio Produksi HTML interaktif (board.html)")
    p_board.add_argument("folder")
    p_board.add_argument("--out", default=None)

    p_chk = sub.add_parser("check", help="Jalankan verifikator 25-poin")
    p_chk.add_argument("folder")
    p_chk.add_argument("--json", action="store_true")
    p_chk.add_argument("--strict", action="store_true")

    args = parser.parse_args(argv)
    dispatch = {
        "init": cmd_init,
        "add-ep": cmd_add_ep,
        "sync": cmd_sync,
        "board": cmd_board,
        "check": cmd_check,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
