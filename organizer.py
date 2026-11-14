import os
import sys
import shutil
import hashlib
import logging
import re
from datetime import datetime
from pathlib import Path

# Extension mapping for file categorization
CATEGORIES = {
    'Documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.csv'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
    'Videos': ['.mp4', '.mkv', '.mov', '.avi', '.flv'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac', '.m4a'],
    'Archives': ['.zip', '.rar', '.tar', '.gz', '.7z'],
    'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.json']
}

MANAGED_FOLDERS = set(CATEGORIES.keys()) | {'Others', 'Duplicates'}
IGNORED_FILES = {'organizer.log', 'summary_report.txt', 'dry_run_output.txt'}

def setup_logger(log_file_path):
    logger = logging.getLogger('FileOrganizer')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def clean_filename(filename):
    # Regex to clean invalid/problematic characters from filenames
    stem = Path(filename).stem
    ext = Path(filename).suffix
    cleaned_stem = re.sub(r'[<>:"/\\|?*#$@!%^&]', '_', stem)
    cleaned_stem = re.sub(r'_+', '_', cleaned_stem).strip('_')
    return f"{cleaned_stem or 'unnamed_file'}{ext}"

def get_category(filename):
    ext = Path(filename).suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return 'Others'

def get_safe_destination(dest_dir, filename):
    # Prevent overwriting existing files by appending _1, _2
    base = Path(filename).stem
    ext = Path(filename).suffix
    counter = 1
    dest_path = Path(dest_dir) / filename
    while dest_path.exists():
        dest_path = Path(dest_dir) / f"{base}_{counter}{ext}"
        counter += 1
    return dest_path

def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"

def write_summary_report(report_path, stats, start_time):
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write("       FILE ORGANIZER SUMMARY REPORT              \n")
        f.write("==================================================\n")
        f.write(f"Run Timestamp      : {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Scanned      : {stats['total_scanned']}\n")
        f.write(f"Files Moved        : {stats['total_moved']}\n")
        f.write(f"Duplicates Found   : {stats['duplicates_count']}\n")
        f.write(f"Files Skipped      : {stats['skipped_count']}\n")
        f.write(f"Errors/Failed      : {stats['failed_count']}\n")
        f.write("--------------------------------------------------\n")
        f.write("Breakdown by Category:\n")
        for cat in list(CATEGORIES.keys()) + ['Others', 'Duplicates']:
            count = stats['category_counts'].get(cat, 0)
            size = stats['category_sizes'].get(cat, 0)
            f.write(f"  - {cat:<12}: {count:>2} files ({format_size(size)})\n")
        f.write("==================================================\n")

def organize_folder(folder_path, dry_run=False):
    target = Path(folder_path).resolve()
    if not target.exists() or not target.is_dir():
        print(f"Error: Folder '{folder_path}' does not exist or is not a directory.")
        return

    start_time = datetime.now()
    log_path = target / 'organizer.log'
    report_path = target / 'summary_report.txt'
    logger = setup_logger(log_path)

    mode = "DRY-RUN" if dry_run else "REAL RUN"
    logger.info(f"Starting file organization in {mode} mode for: {target}")
    print(f"\n--- Starting File Organizer ({mode}) ---")
    print(f"Target folder: {target}\n")

    stats = {
        'total_scanned': 0, 'total_moved': 0, 'duplicates_count': 0,
        'skipped_count': 0, 'failed_count': 0,
        'category_counts': {c: 0 for c in list(CATEGORIES.keys()) + ['Others', 'Duplicates']},
        'category_sizes': {c: 0 for c in list(CATEGORIES.keys()) + ['Others', 'Duplicates']}
    }

    if not dry_run:
        for cat in MANAGED_FOLDERS:
            try:
                (target / cat).mkdir(exist_ok=True)
            except PermissionError as e:
                logger.error(f"Permission denied creating '{cat}': {e}")
                print(f"Error creating folder {cat}: {e}")
                return

    seen_hashes = {}
    try:
        items = list(target.iterdir())
    except PermissionError as e:
        logger.error(f"Cannot access folder {target}: {e}")
        print(f"Permission error: {e}")
        return

    for item in items:
        if item.is_dir():
            if item.name not in MANAGED_FOLDERS and not item.name.startswith('.'):
                stats['skipped_count'] += 1
                logger.info(f"Skipped sub-directory: {item.name}")
            continue

        if item.name in IGNORED_FILES:
            continue

        stats['total_scanned'] += 1
        try:
            file_size = item.stat().st_size
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Failed to access {item.name}: {e}")
            stats['failed_count'] += 1
            continue

        clean_name = clean_filename(item.name)
        if clean_name != item.name:
            logger.info(f"Sanitized filename '{item.name}' -> '{clean_name}'")

        try:
            file_hash = get_file_hash(item)
        except (PermissionError, OSError) as e:
            logger.error(f"Failed to read/hash {item.name} (file in use): {e}")
            print(f"Skipping (file in use or unreadable): {item.name}")
            stats['failed_count'] += 1
            continue

        # Handle duplicates
        if file_hash in seen_hashes:
            orig = seen_hashes[file_hash]
            stats['duplicates_count'] += 1
            stats['category_counts']['Duplicates'] += 1
            stats['category_sizes']['Duplicates'] += file_size
            dest_file = get_safe_destination(target / 'Duplicates', clean_name)

            if dry_run:
                print(f"[DRY-RUN] Duplicate: {item.name} -> Duplicates/ (matches {orig})")
                logger.info(f"[DRY-RUN] Detected duplicate {item.name} (matches {orig})")
            else:
                try:
                    shutil.move(str(item), str(dest_file))
                    print(f"Duplicate moved: {item.name} -> Duplicates/{dest_file.name}")
                    logger.info(f"Moved duplicate: '{item.name}' -> 'Duplicates/{dest_file.name}'")
                    stats['total_moved'] += 1
                except (PermissionError, OSError) as e:
                    logger.error(f"Failed to move duplicate {item.name}: {e}")
                    stats['failed_count'] += 1
            continue

        seen_hashes[file_hash] = item.name

        # Move to category
        cat = get_category(item.name)
        stats['category_counts'][cat] += 1
        stats['category_sizes'][cat] += file_size
        dest_file = get_safe_destination(target / cat, clean_name)

        if dry_run:
            print(f"[DRY-RUN] Would move: {item.name} -> {cat}/{dest_file.name}")
            logger.info(f"[DRY-RUN] Planned move: '{item.name}' -> '{cat}/{dest_file.name}'")
        else:
            try:
                shutil.move(str(item), str(dest_file))
                print(f"Moved: {item.name} -> {cat}/{dest_file.name}")
                logger.info(f"Moved: '{item.name}' -> '{cat}/{dest_file.name}'")
                stats['total_moved'] += 1
            except (PermissionError, OSError) as e:
                logger.error(f"Failed to move {item.name}: {e}")
                stats['failed_count'] += 1

    if not dry_run:
        write_summary_report(report_path, stats, start_time)
        logger.info("Summary report generated. File organization complete.")

    print("\n--- Organization Finished ---")
    print(f"Total scanned: {stats['total_scanned']}")
    if dry_run:
        print(f"Duplicates found: {stats['duplicates_count']}")
        print("Note: No files were touched (dry-run mode).")
    else:
        print(f"Total moved: {stats['total_moved']}")
        print(f"Duplicates moved: {stats['duplicates_count']}")
        print(f"Summary report saved: {report_path.name}")
        print(f"Activity log saved: {log_path.name}")

def main():
    target_folder = None
    dry_run = False
    args = sys.argv[1:]

    for arg in args:
        if arg in ('--dry-run', '-d'):
            dry_run = True
        elif not target_folder:
            target_folder = arg

    if not target_folder:
        target_folder = input("Enter folder path to organize: ").strip()

    if '--dry-run' not in args and '-d' not in args:
        ans = input("Run in dry-run mode? (y/n): ").strip().lower()
        if ans in ('y', 'yes'):
            dry_run = True

    organize_folder(target_folder, dry_run=dry_run)

if __name__ == '__main__':
    main()
