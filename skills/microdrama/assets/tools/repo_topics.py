#!/usr/bin/env python3
"""Automated GitHub repository topics & metadata management for Microdrama.

Extracts, validates, and synchronizes repository topics, description,
and homepage with GitHub via REST API (Python 3.10+ stdlib only).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any

REPO_OWNER = "roedyrustam"
REPO_NAME = "microdarama"

CURATED_TOPICS = [
    "microdrama",
    "ai-film",
    "ai-video",
    "prompt-engineering",
    "video-generation",
    "screenplay",
    "kling-ai",
    "sora",
    "runway",
    "wan2-1",
    "flux",
    "production-system",
    "ai-director",
    "cinematography",
    "storyboard",
    "gemini-extension",
    "claude-plugin",
    "antigravity",
    "vertical-video",
    "filmmaking",
]

REPO_DESCRIPTION = (
    "Precision AI Live-Action Video & Microdrama Production System — "
    "7-Gate Workflow, Deterministic 25-Point Semantic Verifier, "
    "Native AI Director Subagent & HTML Studio."
)
REPO_HOMEPAGE = "https://github.com/roedyrustam/microdarama"


def resolve_github_token() -> str | None:
    """Resolve GitHub token from environment variables or git credential helper."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()

    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
        if proc.returncode == 0:
            for line in proc.stdout.splitlines():
                if line.startswith("password="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


def get_curated_topics() -> list[str]:
    """Return sorted, unique GitHub topics conforming to GitHub limits (max 20, <=35 chars, lowercase)."""
    clean: set[str] = set()
    for t in CURATED_TOPICS:
        ct = t.strip().lower()
        if ct and len(ct) <= 35:
            clean.add(ct)
    return sorted(clean)[:20]


def _powershell_http(
    url: str,
    headers: dict[str, str],
    method: str = "GET",
    data: bytes | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    """Execute HTTP JSON request using Windows PowerShell Invoke-RestMethod."""
    hdrs_lines = []
    for k, v in headers.items():
        val = v.replace("'", "''")
        hdrs_lines.append(f"'{k}' = '{val}'")
    hdrs_str = "@{" + "; ".join(hdrs_lines) + "}"

    body_clause = ""
    if data:
        escaped_body = data.decode("utf-8").replace("'", "''")
        body_clause = f"-Body '{escaped_body}' -ContentType 'application/json'"

    ps_script = f"""
$headers = {hdrs_str}
$resp = Invoke-RestMethod -Uri '{url}' -Method {method} -Headers $headers {body_clause}
if ($resp) {{
    $resp | ConvertTo-Json -Depth 5 -Compress
}}
"""
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        try:
            return json.loads(proc.stdout.strip())
        except json.JSONDecodeError:
            pass
    raise RuntimeError(f"PowerShell request failed: {proc.stderr or proc.stdout}")


def _http_request(
    url: str,
    headers: dict[str, str],
    method: str = "GET",
    data: bytes | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    """Execute HTTP JSON request using urllib, with automatic Windows PowerShell fallback."""
    # 1. Try Python urllib
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw.strip() else {}
    except Exception:
        pass

    # 2. On Windows, fallback to PowerShell Invoke-RestMethod
    if sys.platform == "win32":
        try:
            return _powershell_http(url, headers=headers, method=method, data=data, timeout=timeout)
        except Exception:
            pass

    # 3. Fallback to system curl
    cmd = ["curl.exe" if sys.platform == "win32" else "curl", "-s", "-X", method]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    if data:
        cmd.extend(["-d", data.decode("utf-8")])
    cmd.append(url)

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    if proc.returncode == 0 and proc.stdout.strip():
        return json.loads(proc.stdout)
    raise RuntimeError(f"HTTP request failed across urllib, powershell, and curl.")


def fetch_remote_metadata(owner: str, repo: str, token: str | None = None) -> dict[str, Any]:
    """Fetch repository metadata and topics from GitHub REST API."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Microdrama-RepoTopics/2.1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = _http_request(url, headers=headers)

    # Fetch topics specifically
    topics_url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    try:
        topics_data = _http_request(topics_url, headers=headers)
        data["topics"] = topics_data.get("names", data.get("topics", []))
    except Exception:
        pass

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description") or "",
        "homepage": data.get("homepage") or "",
        "topics": sorted(data.get("topics") or []),
    }


def sync_github_metadata(
    owner: str,
    repo: str,
    token: str,
    topics: list[str] | None = None,
    description: str | None = None,
    homepage: str | None = None,
) -> dict[str, Any]:
    """Push topics and metadata updates to GitHub REST API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Microdrama-RepoTopics/2.1",
        "Content-Type": "application/json",
    }
    results: dict[str, Any] = {}

    target_topics = topics if topics is not None else get_curated_topics()
    topics_url = f"https://api.github.com/repos/{owner}/{repo}/topics"
    topics_payload = json.dumps({"names": target_topics}).encode("utf-8")
    res_topics = _http_request(topics_url, headers=headers, method="PUT", data=topics_payload)
    results["topics"] = res_topics.get("names", [])

    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    repo_payload = json.dumps({
        "description": description if description is not None else REPO_DESCRIPTION,
        "homepage": homepage if homepage is not None else REPO_HOMEPAGE,
        "has_issues": True,
        "has_projects": True,
    }).encode("utf-8")
    res_repo = _http_request(repo_url, headers=headers, method="PATCH", data=repo_payload)
    results["description"] = res_repo.get("description")
    results["homepage"] = res_repo.get("homepage")

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Microdrama Automated GitHub Repo Topics & Metadata Manager")
    parser.add_argument("--check", action="store_true", help="Periksa status topics remote vs lokal")
    parser.add_argument("--sync", action="store_true", help="Sinkronkan topics dan deskripsi ke GitHub")
    parser.add_argument("--token", default=None, help="GitHub Personal Access Token (opsional)")
    parser.add_argument("--owner", default=REPO_OWNER, help=f"GitHub owner/org (default: {REPO_OWNER})")
    parser.add_argument("--repo", default=REPO_NAME, help=f"GitHub repo name (default: {REPO_NAME})")
    parser.add_argument("--json", dest="output_json", action="store_true", help="Output dalam format JSON")

    args = parser.parse_args(argv)
    token = args.token or resolve_github_token()
    curated = get_curated_topics()

    if not args.sync and not args.check:
        # Default mode: print curated topics and current status
        args.check = True

    try:
        remote = fetch_remote_metadata(args.owner, args.repo, token)
    except Exception as exc:
        if args.output_json:
            print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
        else:
            print(f"[ERROR] Gagal membaca metadata remote: {exc}", file=sys.stderr)
        return 1

    curated_set = set(curated)
    remote_set = set(remote["topics"])
    missing_on_remote = sorted(curated_set - remote_set)
    extra_on_remote = sorted(remote_set - curated_set)
    in_sync = (curated_set == remote_set) and (remote["description"] == REPO_DESCRIPTION)

    if args.sync:
        if not token:
            msg = "Token GitHub tidak ditemukan. Setel GITHUB_TOKEN atau login lewat git credential."
            if args.output_json:
                print(json.dumps({"status": "error", "message": msg}))
            else:
                print(f"[ERROR] {msg}", file=sys.stderr)
            return 1

        try:
            synced = sync_github_metadata(
                owner=args.owner,
                repo=args.repo,
                token=token,
                topics=curated,
                description=REPO_DESCRIPTION,
                homepage=REPO_HOMEPAGE,
            )
            if args.output_json:
                print(json.dumps({"status": "ok", "action": "synced", "data": synced}, indent=2))
            else:
                print(f"[SUCCESS] Berhasil menyinkronkan {len(synced.get('topics', []))} topics ke {args.owner}/{args.repo}:")
                for t in synced.get("topics", []):
                    print(f"  - {t}")
                print(f"Deskripsi: {synced.get('description')}")
                print(f"Homepage : {synced.get('homepage')}")
            return 0
        except Exception as exc:
            if args.output_json:
                print(json.dumps({"status": "error", "message": str(exc)}, indent=2))
            else:
                print(f"[ERROR] Gagal sinkronisasi ke GitHub: {exc}", file=sys.stderr)
            return 1

    # Check mode
    if args.output_json:
        payload = {
            "status": "ok" if in_sync else "drift",
            "remote": remote,
            "curated": curated,
            "missing_on_remote": missing_on_remote,
            "extra_on_remote": extra_on_remote,
            "in_sync": in_sync,
        }
        print(json.dumps(payload, indent=2))
    else:
        print(f"Status Topics GitHub Repository: {args.owner}/{args.repo}")
        print("-" * 60)
        print(f"Jumlah topics remote : {len(remote['topics'])}")
        print(f"Jumlah topics curated: {len(curated)}")
        print(f"Status keselarasan   : {'TERLENGKAPI & SINKRON' if in_sync else 'PERLU SINKRONISASI'}")
        if missing_on_remote:
            print(f"Topics belum ada di remote ({len(missing_on_remote)}): {', '.join(missing_on_remote)}")
        if extra_on_remote:
            print(f"Topics tambahan di remote ({len(extra_on_remote)}): {', '.join(extra_on_remote)}")
        print(f"Remote Description   : {remote['description']}")
        print(f"Remote Homepage      : {remote['homepage']}")
        print("-" * 60)
        if not in_sync:
            print("Jalankan dengan flag --sync untuk menyinkronkan otomatis:")
            print(f"  python assets/tools/repo_topics.py --sync")

    return 0 if in_sync else 2


if __name__ == "__main__":
    sys.exit(main())
