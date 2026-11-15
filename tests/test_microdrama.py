import json
import pathlib
import shutil
import sys
import tempfile
import unittest

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT_DIR / "assets" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import microdrama_cli  # noqa: E402
import check_prompts  # noqa: E402
import dissect_video  # noqa: E402


class TestMicrodramaPrecision(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = pathlib.Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _clone_project(self, name: str) -> pathlib.Path:
        src = ROOT_DIR / "assets" / "contoh" / name
        dst = self.tmp_path / name
        shutil.copytree(src, dst)
        return dst

    def test_benchmark_alamat_yang_sama_passes_strict(self) -> None:
        report = check_prompts.run_checks(ROOT_DIR / "assets" / "contoh" / "alamat-yang-sama", strict=True)
        self.assertEqual(report["status"], "ok", f"Errors: {report['errors']}")
        self.assertEqual(report["warnings"], [])

    def test_benchmark_unit_7_passes_strict(self) -> None:
        report = check_prompts.run_checks(ROOT_DIR / "assets" / "contoh" / "unit-7", strict=True)
        self.assertEqual(report["status"], "ok", f"Errors: {report['errors']}")
        self.assertEqual(report["warnings"], [])

    def test_catches_paraphrased_character_block(self) -> None:
        proj = self._clone_project("unit-7")
        pv = proj / "ep01" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8").replace("dark navy technician uniform", "blue mechanic outfit"),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("tidak identik dengan cast.md" in e for e in report["errors"]))

    def test_catches_consecutive_same_camera_position_in_naskah(self) -> None:
        proj = self._clone_project("unit-7")
        naskah = proj / "ep01" / "naskah.md"
        text = naskah.read_text(encoding="utf-8").replace(
            "| s02 | 6 s | Ruang rapat | Rafa, Bu Dian, 12 karyawan | WIDE | ujung jauh meja rapat |",
            "| s02 | 6 s | Ruang rapat | Rafa, Bu Dian, 12 karyawan | WIDE | rendah, di samping baki tangga |",
        )
        naskah.write_text(text, encoding="utf-8")
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("posisi kamera sama" in e for e in report["errors"]))

    def test_catches_missing_location_tag_in_multi_plate_scene(self) -> None:
        proj = self._clone_project("alamat-yang-sama")
        pv = proj / "ep01" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8").replace(
                "SHOT 7 (26-30s) — INSIDE, living-room floor, seen through the gap — 50mm",
                "SHOT 7 (26-30s), 50mm",
            ),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("SHOT 7 tanpa tag lokasi" in e for e in report["errors"]))

    def test_catches_raw_digits_in_spoken_dialogue(self) -> None:
        proj = self._clone_project("unit-7")
        pv = proj / "ep01" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8").replace("Masuk dua ribu sebelas.", "Masuk 2011."),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("angka mentah" in e for e in report["errors"]))

    def test_catches_excessive_speech_rate_strict(self) -> None:
        proj = self._clone_project("unit-7")
        pv = proj / "ep01" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8").replace(
                'BU DIAN (off-screen): "Orang kayak kamu nggak akan pernah duduk di kursi ini."',
                'BU DIAN (off-screen): "Orang kayak kamu tidak akan pernah bisa duduk di kursi pimpinan perusahaan ini sekarang juga sampai kapanpun."',
            ),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj, strict=True)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("kecepatan bicara" in e for e in report["errors"]))

    def test_catches_indonesian_cliche_in_naskah(self) -> None:
        proj = self._clone_project("unit-7")
        naskah = proj / "ep01" / "naskah.md"
        naskah.write_text(
            naskah.read_text(encoding="utf-8").replace(
                '"Tiga tahun saya di sini. Nggak pernah ada yang ngatur saya."',
                '"Kamu akan menyesal."',
            ),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("klise sinetron" in e for e in report["errors"]))

    def test_catches_unauthorized_facial_mark(self) -> None:
        proj = self._clone_project("unit-7")
        cast_p = proj / "cast.md"
        cast_p.write_text(
            cast_p.read_text(encoding="utf-8").replace("strong\njaw,", "strong\njaw, small scar above left eyebrow,"),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("tanda wajah" in e for e in report["errors"]))

    def test_catches_peephole_person_contamination(self) -> None:
        proj = self._clone_project("alamat-yang-sama")
        pv = proj / "ep01" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8").replace(
                "Everything inside is still.",
                "Everything inside is still, no face visible.",
            ),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("shot lewat celah/kaca" in e for e in report["errors"]))

    def test_catches_crowd_missing_antisync_movement_note(self) -> None:
        proj = self._clone_project("unit-7")
        pv = proj / "ep01" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8").replace(
                "The twelve staff NEVER react as a block — one looks down, one looks\naway, one keeps watching; never a synchronised crowd turn.",
                "The twelve staff sit around the table and watch quietly.",
            ),
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("melarang gerakan serempak" in e for e in report["errors"]))

    def test_catches_cross_episode_duplicate_asset_generation(self) -> None:
        proj = self._clone_project("alamat-yang-sama")
        ep2_aset = proj / "ep02" / "prompt-aset.md"
        ep1_adit = (proj / "ep01" / "prompt-aset.md").read_text(encoding="utf-8").split("## Set plate")[0]
        sheet_part = ep1_adit.split("## Sheet karakter · ADIT")[1]
        ep2_aset.write_text(
            ep2_aset.read_text(encoding="utf-8") + "\n\n## Sheet karakter · ADIT" + sheet_part,
            encoding="utf-8",
        )
        report = check_prompts.run_checks(proj)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("sudah dibuat di ep01" in e for e in report["errors"]))

    def test_cli_init_add_ep_sync_and_board(self) -> None:
        new_proj = self.tmp_path / "proyek-uji"
        rc = microdrama_cli.main(["init", str(new_proj), "--title", "Proyek Uji"])
        self.assertEqual(rc, 0)
        self.assertTrue((new_proj / "brief.md").exists())
        self.assertTrue((new_proj / "ep01" / "prompt-video.md").exists())

        # Test sync repairs deliberate drift in cloned unit-7
        cloned = self._clone_project("unit-7")
        pv = cloned / "ep01" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8")
            .replace("dark navy technician uniform", "WRONG OUTFIT")
            .replace("Lampirkan: `rafa_sheet.png`, `bu_dian_sheet.png`, `ruang_rapat_plate.png`", "Lampirkan: `rafa_sheet.png`"),
            encoding="utf-8",
        )
        self.assertEqual(check_prompts.run_checks(cloned)["status"], "error")
        self.assertEqual(microdrama_cli.main(["sync", str(cloned)]), 0)
        self.assertEqual(check_prompts.run_checks(cloned, strict=True)["status"], "ok")

        # Test add-ep on cloned project collects existing sheets/plates
        self.assertEqual(microdrama_cli.main(["add-ep", str(cloned), "2", "--title", "Basement"]), 0)
        ep2_aset_txt = (cloned / "ep02" / "prompt-aset.md").read_text(encoding="utf-8")
        self.assertIn("rafa_sheet.png", ep2_aset_txt)
        self.assertIn("ruang_rapat_plate.png", ep2_aset_txt)

        # Test board generation (Studio v2.1)
        board_out = self.tmp_path / "board_out.html"
        self.assertEqual(microdrama_cli.main(["board", str(cloned), "--out", str(board_out)]), 0)
        html_txt = board_out.read_text(encoding="utf-8")
        self.assertIn("Microdrama Studio", html_txt)
        self.assertIn("Salin Prompt Video", html_txt)
        self.assertIn("Salin Negative (Avoid)", html_txt)
        self.assertIn("Salin Mode @Element", html_txt)
        self.assertIn("Diagnosa Cepat 24 Gejala", html_txt)
        self.assertIn("<th>WPS</th>", html_txt)

    def test_cli_status_on_init_and_completed_project(self) -> None:
        fresh = self.tmp_path / "status-init"
        self.assertEqual(microdrama_cli.main(["init", str(fresh), "--title", "Uji Status"]), 0)
        fresh_status = microdrama_cli.inspect_project_status(fresh)
        self.assertFalse(fresh_status["ready"])
        self.assertEqual(fresh_status["gates"][0]["status"], "PASS")
        self.assertEqual(fresh_status["gates"][1]["status"], "PENDING")
        self.assertEqual(fresh_status["next_gate"]["gate"], 1)
        self.assertEqual(microdrama_cli.main(["status", str(fresh)]), 0)
        self.assertEqual(microdrama_cli.main(["status", str(fresh), "--strict"]), 1)

        completed = ROOT_DIR / "assets" / "contoh" / "alamat-yang-sama"
        comp_status = microdrama_cli.inspect_project_status(completed)
        self.assertTrue(comp_status["ready"])
        self.assertTrue(all(g["status"] == "PASS" for g in comp_status["gates"]))
        self.assertIsNone(comp_status["next_gate"])
        self.assertEqual(microdrama_cli.main(["status", str(completed), "--strict"]), 0)

    def test_cli_export_bundle(self) -> None:
        export_out = self.tmp_path / "bundle.json"
        alamat = ROOT_DIR / "assets" / "contoh" / "alamat-yang-sama"
        self.assertEqual(microdrama_cli.main(["export", str(alamat), "--out", str(export_out)]), 0)
        bundle = json.loads(export_out.read_text(encoding="utf-8"))
        self.assertEqual(bundle["schema_version"], "microdrama.export.v1")
        self.assertEqual(bundle["plugin_version"], "2.1.0")
        self.assertEqual(bundle["verifier"]["status"], "ok")
        self.assertGreaterEqual(len(bundle["episodes"]), 3)
        ep1 = bundle["episodes"][0]
        self.assertTrue(ep1["assets"])
        self.assertTrue(ep1["assets"][0]["positive_prompt"])
        self.assertTrue(ep1["assets"][0]["negative_prompt"])
        self.assertNotIn("Avoid:", ep1["assets"][0]["negative_prompt"])
        self.assertTrue(ep1["scenes"])
        sc0 = ep1["scenes"][0]
        self.assertTrue(sc0["element_slots"])
        self.assertEqual(sc0["element_slots"][0]["slot"], 1)
        self.assertEqual(sc0["element_slots"][0]["element"], "@Element1")
        self.assertIn("@Element1", sc0["prompt_element_mode"])
        self.assertNotIn("[gambar_", sc0["prompt_element_mode"])
        self.assertTrue(any(sh["wps"] > 0 for sh in ep1["shots"]))

    def test_sync_repairs_placeholder_character_and_set_drift(self) -> None:
        cloned = self._clone_project("alamat-yang-sama")
        pv = cloned / "ep02" / "prompt-video.md"
        pv.write_text(
            pv.read_text(encoding="utf-8")
            .replace("faded green driver jacket with no logos", "WRONG JACKET")
            .replace("Mossy grey cement walls.", "Brick red walls."),
            encoding="utf-8",
        )
        self.assertEqual(check_prompts.run_checks(cloned)["status"], "error")
        self.assertEqual(microdrama_cli.main(["sync", str(cloned)]), 0)
        self.assertEqual(check_prompts.run_checks(cloned, strict=True)["status"], "ok")
        synced_text = pv.read_text(encoding="utf-8")
        self.assertIn("edging sideways down a narrow passage with a package under his arm.", check_prompts.rata(synced_text))
        self.assertIn("Mossy grey cement walls.", synced_text)

    def test_dissector_diagnose_branch_and_promote(self) -> None:
        self.assertEqual(dissect_video.main(["diagnose", "wajah berubah"]), 0)
        cloned = self._clone_project("unit-7")
        pv = cloned / "ep01" / "prompt-video.md"
        self.assertEqual(dissect_video.main(["branch", str(pv), "--note", "Uji kamera"]), 0)
        v2 = cloned / "ep01" / "prompt-video-v2.md"
        self.assertTrue(v2.exists())
        self.assertIn("Branch v2", v2.read_text(encoding="utf-8"))
        self.assertEqual(dissect_video.main(["promote", str(v2)]), 0)
        self.assertNotIn("Branch v2", pv.read_text(encoding="utf-8"))

    def test_plugin_manifest_and_sync_parity(self) -> None:
        root_manifest = json.loads((ROOT_DIR / "plugin.json").read_text(encoding="utf-8"))
        claude_manifest = json.loads((ROOT_DIR / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        gemini_manifest = json.loads((ROOT_DIR / "gemini-extension.json").read_text(encoding="utf-8"))
        codex_manifest = json.loads((ROOT_DIR / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        for manifest in (root_manifest, claude_manifest, gemini_manifest, codex_manifest):
            self.assertEqual(manifest["name"], "microdrama")
            self.assertEqual(manifest["version"], "2.1.0")
            self.assertEqual(manifest["author"]["name"], "Roedy Rustam")
        self.assertTrue((ROOT_DIR / "agents" / "microdrama-director.md").exists())
        self.assertTrue((ROOT_DIR / "rules" / "AGENTS.md").exists())
        self.assertTrue((ROOT_DIR / "CODEX.md").exists())
        self.assertTrue((ROOT_DIR / ".codex" / "rules" / "microdrama.md").exists())
        self.assertTrue((ROOT_DIR / "assets" / "logo.svg").exists())
        self.assertEqual(microdrama_cli.main(["sync-plugin", "--check"]), 0)


if __name__ == "__main__":
    unittest.main()
