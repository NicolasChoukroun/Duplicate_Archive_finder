import argparse
import hashlib
import os
from collections import defaultdict

ARCHIVE_EXTENSIONS = {".zip", ".rar", ".7z"}
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def get_checksum(filepath, chunk_size=8192):
    """Compute the MD5 checksum of a file, reading in chunks to handle large files."""
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def find_duplicates(root_dir):
    """Scan only root_dir (no subfolders), return {checksum: [duplicate filepaths]}."""

    # --- PHASE 1: pre-filter by size (cheap, avoids hashing files that can't have a dupe) ---
    size_groups = defaultdict(list)
    with os.scandir(root_dir) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            if os.path.splitext(entry.name)[1].lower() not in ARCHIVE_EXTENSIONS:
                continue
            try:
                size_groups[entry.stat().st_size].append(entry.path)
            except OSError as e:
                print(f"Skipping {entry.path}: {e}")

    # --- PHASE 2: compute MD5 for every candidate file EXACTLY ONCE, store in memory ---
    checksums = defaultdict(list)  # {md5: [filepaths]}
    for size, paths in size_groups.items():
        if len(paths) < 2:
            continue
        for filepath in paths:
            print(f"Hashing: {filepath}")
            try:
                checksum = get_checksum(filepath)
                checksums[checksum].append(filepath)
            except (OSError, PermissionError) as e:
                print(f"Skipping {filepath}: {e}")

    # --- PHASE 3: pure comparison, no re-hashing ---
    return {h: p for h, p in checksums.items() if len(p) > 1}

def delete_duplicates(dupes):
    """For each duplicate group, keep the first file (sorted) and delete the rest."""
    for checksum, paths in dupes.items():
        paths_sorted = sorted(paths)
        keep = paths_sorted[0]
        print(f"{YELLOW}Keeping:{RESET} {keep}")
        for filepath in paths_sorted[1:]:
            try:
                os.remove(filepath)
                print(f"{RED}Deleted:{RESET} {filepath}")
            except OSError as e:
                print(f"Could not delete {filepath}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find duplicate archive files by MD5 checksum.")
    parser.add_argument(
        "-delete",
        action="store_true",
        help="Delete duplicate files, keeping only one copy of each."
    )
    args = parser.parse_args()

    print("Scans the current folder for duplicate .zip/.rar/.7z archives using MD5 checksums.")
    print("Use -delete to remove duplicates automatically, keeping only one copy of each file.\n")

    root = os.getcwd()
    dupes = find_duplicates(root)

    if not dupes:
        print("No duplicate archives found.")
    elif args.delete:
        delete_duplicates(dupes)
    else:
        for checksum, paths in dupes.items():
            for p in paths:
                print(f"{RED}Duplicate:{RESET} {p}")