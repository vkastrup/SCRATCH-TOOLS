#!/usr/bin/env python3

import shutil
from datetime import datetime
from pathlib import Path

SOURCE_FOLDERS = [
    "/Library/Application Support/Assimilator/Project",
    "/Library/Application Support/Assimilator/Settings",
    "/Library/Application Support/Assimilator/Users",
]

DESTINATION = Path("/your/path/here/ScratchBackups")


def copy_folders_with_timestamp(source_folders, destination_folder):
    if not destination_folder.exists():
        raise RuntimeError(f"Destination not accessible: {destination_folder}")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = destination_folder / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True)

    succeeded, failed = [], []

    try:
        for src in source_folders:
            src = Path(src)
            if not src.exists():
                print(f"  SKIP  {src} (not found)")
                failed.append(src)
                continue
            dest = backup_dir / src.name
            shutil.copytree(src, dest)
            print(f"  OK    {src} -> {dest}")
            succeeded.append(src)
    except Exception:
        shutil.rmtree(backup_dir, ignore_errors=True)
        raise

    print(f"\nBackup complete: {backup_dir}")
    print(f"  {len(succeeded)} copied, {len(failed)} skipped")


if __name__ == "__main__":
    copy_folders_with_timestamp(SOURCE_FOLDERS, DESTINATION)
