import os
import shutil
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

def organize_files(folder_path):
    target = Path(folder_path)
    if not target.exists() or not target.is_dir():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return

    # create category folders
    for category in EXTENSIONS.keys():
        (target / category).mkdir(exist_ok=True)
    (target / 'Others').mkdir(exist_ok=True)

    for item in target.iterdir():
        if item.is_file():
            category = get_category(item.name)
            dest_folder = target / category
            dest_file = get_safe_destination(dest_folder, item.name)
            shutil.move(str(item), str(dest_file))
            print(f"Moved: {item.name} -> {category}")

if __name__ == '__main__':
    folder = input("Enter folder path: ").strip()
    organize_files(folder)
