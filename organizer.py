import os
import shutil
import hashlib
from pathlib import Path

# mapping extensions to category folders
EXTENSIONS = {
    'Documents': ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.csv'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
    'Videos': ['.mp4', '.mkv', '.mov', '.avi', '.flv'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac', '.m4a'],
    'Archives': ['.zip', '.rar', '.tar', '.gz', '.7z'],
    'Code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.json']
}

def get_category(filename):
    ext = Path(filename).suffix.lower()
    for category, ext_list in EXTENSIONS.items():
        if ext in ext_list:
            return category
    return 'Others'

def get_safe_destination(dest_dir, filename):
    base = Path(filename).stem
    ext = Path(filename).suffix
    counter = 1
    new_path = Path(dest_dir) / filename
    
    # if file already exists, add a number suffix
    while new_path.exists():
        new_path = Path(dest_dir) / f"{base}_{counter}{ext}"
        counter += 1
    return new_path

def get_file_hash(file_path):
    # calculate md5 hash to check if files are identical
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def organize_files(folder_path, dry_run=False):
    target = Path(folder_path)
    if not target.exists() or not target.is_dir():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    # create category folders + Duplicates
    categories = list(EXTENSIONS.keys()) + ['Others', 'Duplicates']
    if not dry_run:
        for cat in categories:
            (target / cat).mkdir(exist_ok=True)

    seen_hashes = {}
    
    for item in target.iterdir():
        # skip directories so we don't process already organized folders
        if item.is_dir():
            continue

        try:
            file_hash = get_file_hash(item)
            
            # check for duplicates
            if file_hash in seen_hashes:
                dest_folder = target / 'Duplicates'
                dest_file = get_safe_destination(dest_folder, item.name)
                if dry_run:
                    print(f"[DRY-RUN] Duplicate found: {item.name} -> Duplicates (matches {seen_hashes[file_hash]})")
                else:
                    shutil.move(str(item), str(dest_file))
                    print(f"Duplicate moved: {item.name} -> Duplicates")
                continue

            seen_hashes[file_hash] = item.name

            category = get_category(item.name)
            dest_folder = target / category
            dest_file = get_safe_destination(dest_folder, item.name)

            if dry_run:
                print(f"[DRY-RUN] Would move: {item.name} -> {category}")
            else:
                shutil.move(str(item), str(dest_file))
                print(f"Moved: {item.name} -> {category}")

        except Exception as e:
            print(f"Error processing {item.name}: {e}")

if __name__ == '__main__':
    folder = input("Enter folder path: ").strip()
    organize_files(folder)
