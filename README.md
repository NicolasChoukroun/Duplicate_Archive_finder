# Duplicate Archive Finder

A lightweight Python script that scans the current folder for duplicate `.zip`, `.rar`, and `.7z` archives by comparing MD5 checksums — not just filenames.

## How it works

Duplicate detection runs in three phases for efficiency, so no file's checksum is ever computed more than once:

1. **Size pre-filter** — Groups files by file size first. Files with a unique size can't have a duplicate, so they're skipped entirely, avoiding unnecessary hashing.
2. **Single-pass hashing** — Computes the MD5 checksum of every remaining candidate file exactly once and stores the results in memory.
3. **Grouping** — Compares the stored checksums (no re-reading files from disk) and reports any files that share an identical hash as duplicates.

## Usage

Place the script in the folder you want to check and run:

```bash
python find_duplicates.py
```

The script only scans the **current directory** (non-recursive — subfolders are not checked) and defaults to wherever it's run from.

Every run prints a short description of what the script does before scanning:

```
Scans the current folder for duplicate .zip/.rar/.7z archives using MD5 checksums.
Use -delete to remove duplicates automatically, keeping only one copy of each file.
```

### Report-only mode (default)

```bash
python find_duplicates.py
```

Every file being hashed is printed as it's checked:

```
Hashing: ./backup_2024.zip
Hashing: ./backup_2024_copy.zip
```

Any duplicates found are printed in red:

```
Duplicate: ./backup_2024.zip
Duplicate: ./backup_2024_copy.zip
```

If no duplicates are found among the scanned files, the script says so and exits.

### Delete mode (`-delete`)

```bash
python find_duplicates.py -delete
```

For each group of duplicate files, the script keeps exactly one copy and deletes the rest. Within a duplicate group, files are sorted alphabetically by path and the **first one is kept** — this is an arbitrary rule, not "oldest file" or "shortest name," so double-check the output if that distinction matters to you.

```
Keeping: ./backup_2024.zip
Deleted: ./backup_2024_copy.zip
```

⚠️ **This permanently deletes files.** There is no confirmation prompt and no undo. Run without `-delete` first to review what would be flagged as a duplicate before deleting anything.

## Requirements

- Python 3.8+ (uses the walrus operator `:=`)
- No external dependencies — uses only the Python standard library (`hashlib`, `os`, `collections`)

## Notes

- Colored output uses ANSI escape codes, which work natively on Linux, macOS, and modern Windows Terminal. On legacy Windows `cmd.exe`, you may need to enable ANSI support (e.g. `os.system("")` at the top of the script) for colors to render correctly.
- File extensions are matched case-insensitively (`.ZIP`, `.Rar`, etc. are all detected).
- To scan the archive's actual contents for duplicates (rather than the archive files themselves), you'd need to extract and hash the files inside each archive — this script only compares the archives as whole files.
