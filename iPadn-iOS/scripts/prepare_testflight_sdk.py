#!/usr/bin/env python3
"""Prepare the pinned upstream AppleAuth Swift SDK. No credentials are used."""
import hashlib
import pathlib
import shutil
import stat
import subprocess
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
URL = "https://github.com/apple-auth/apple-auth/releases/download/v0.1.3/AppleAuth.zip"
SHA256 = "183c9bb77a97f98d2c1369be0ade5a5238170b8598536c050dc52213550b98fd"
vendor = ROOT / "vendor"
dest = vendor / "AppleAuth"
vendor.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="appleauth-sdk-", dir=vendor) as tmp:
    tmp = pathlib.Path(tmp)
    archive = tmp / "AppleAuth.zip"
    subprocess.run(["curl", "--fail", "--location", "--silent", "--show-error",
                    "--retry", "2", "--max-time", "180", "--output", str(archive), URL], check=True)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise SystemExit("AppleAuth SDK SHA-256 mismatch")
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            path = pathlib.PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != "AppleAuth" or stat.S_ISLNK(entry.external_attr >> 16):
                raise SystemExit("Unexpected SDK archive entry")
        bundle.extractall(tmp)
    package = tmp / "AppleAuth"
    for path in ("Package.swift", "LICENSE", "THIRD_PARTY_NOTICES.md",
                 "Licenses", "Artifacts/apple_auth.xcframework/Info.plist"):
        if not (package / path).exists():
            raise SystemExit("Incomplete upstream SDK: " + path)
    if dest.is_symlink():
        raise SystemExit("Refusing to replace a symlinked vendor directory")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(package), str(dest))
print("Prepared AppleAuth v0.1.3 (SHA-256 verified)")
