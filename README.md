# File Organizer & Productivity Automation Tool
**Day 45 | Day 1 of 4 - Project 1**  
*Internship at Veda Technology*

---

## 📌 Project Overview & Objective

Working with unorganized directories, cluttered downloads, and duplicate files slows down productivity and wastes storage. The **File Organizer & Productivity Automation Tool** is a lightweight Python automation script designed to clean and structure any target directory. 

The primary objective for Day 1 is to scan a folder, classify files by their extension, move them into neat category folders, safely isolate duplicates using content hashing, and provide full transparency with a run summary report and timestamped activity logging.

---

## ✨ Features

1. **Automated File Organization**: Scans any user-specified folder via command-line argument or interactive prompt and moves files into organized category directories.
2. **File Categorization**: Automatically groups files into:
   - `Documents` (`.pdf`, `.docx`, `.doc`, `.txt`, `.xlsx`, `.xls`, `.pptx`, `.csv`)
   - `Images` (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`)
   - `Videos` (`.mp4`, `.mkv`, `.mov`, `.avi`, `.flv`)
   - `Audio` (`.mp3`, `.wav`, `.aac`, `.flac`, `.m4a`)
   - `Archives` (`.zip`, `.rar`, `.tar`, `.gz`, `.7z`)
   - `Code` (`.py`, `.js`, `.html`, `.css`, `.cpp`, `.java`, `.json`)
   - `Others` (unrecognized formats and files without extensions)
3. **Duplicate Detection via MD5 Hashing**: Computes MD5 checksums in chunks to detect identical file contents (even if filenames differ) and moves duplicates into a dedicated `Duplicates` folder without deleting data.
4. **Collision-Safe Renaming**: Prevents accidental overwrites. If a file with the same name already exists in the destination folder, it appends an incremental counter (e.g., `file_1.pdf`).
5. **Dry-Run Mode**: Enables users to test and preview planned file movements without touching or altering any files (`--dry-run` or interactive `y/n` prompt).
6. **Detailed Summary Report**: Generates `summary_report.txt` recording execution timestamp, total files scanned, category breakdown with file counts, and total size per category.
7. **Comprehensive Activity Logging**: Uses Python's standard `logging` module to generate `organizer.log`, logging every moved, skipped, sanitized, and failed operation.
8. **Robust Error Handling**: Gracefully catches `PermissionError`, `FileNotFoundError`, and `OSError` (e.g., locked files in use) so the program never crashes.
9. **Regex Sanitization**: Uses Python's `re` module to strip and normalize illegal and special characters (`< > : " / \ | ? * # $ @ ! % ^ &`) from filenames before moving.
10. **Re-process Prevention**: Automatically ignores the output category folders, `.git`, `organizer.log`, and `summary_report.txt` during directory scans.

---

## 🚀 How to Install and Run

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Only Python standard library modules are used — no external third-party dependencies required.

```bash
# Clone the repository
git clone https://github.com/<your-username>/day-45-file-organizer-automation-tool.git
cd day-45-file-organizer-automation-tool
```

### Usage Examples

#### 1. Interactive Mode
Run the script without arguments; it will prompt you for the folder path and whether to run in dry-run mode:
```bash
python organizer.py
```

#### 2. Dry-Run Mode (Preview Only)
Preview what will be moved without modifying any files:
```bash
python organizer.py sample_input --dry-run
# or using short flag:
python organizer.py sample_input -d
```

#### 3. Real Run (Organize Files)
Organize files in the specified directory:
```bash
python organizer.py sample_input
```

---

## 📂 Project Structure

```text
day-45-file-organizer-automation-tool/
│
├── organizer.py             # Main automation script (~240 lines)
├── README.md                # Project documentation and intern daily notes
├── requirements.txt         # Dependency documentation (standard library only)
├── .gitignore               # Ignored cache and temp files
│
├── sample_input/            # Untouched test folder (24 dummy files for re-running)
│   ├── internship_report.pdf
│   ├── internship_report_copy.pdf  (duplicate)
│   ├── financial_budget#2024$draft!.xlsx (weird characters)
│   └── ... (images, videos, audio, archives, code, docs)
│
└── sample_output/           # Output folder containing organized results
    ├── Archives/            # .zip, .tar.gz
    ├── Audio/               # .mp3, .wav
    ├── Code/                # .py
    ├── Documents/           # .pdf, .docx, .txt, .xlsx
    ├── Duplicates/          # Duplicate copies moved here safely
    ├── Images/              # .png, .jpg
    ├── Others/              # Files without extension (e.g. LICENSE, DOCKERFILE)
    ├── Videos/              # .mp4
    ├── dry_run_output.txt   # Captured terminal output from the dry-run execution
    ├── organizer.log        # Activity log with timestamps
    └── summary_report.txt   # Detailed run summary
```

---

## 📊 Sample Output

### Real `summary_report.txt` Generated:
```text
==================================================
       FILE ORGANIZER SUMMARY REPORT              
==================================================
Run Timestamp      : 2026-11-14 11:40:48
Total Scanned      : 24
Files Moved        : 24
Duplicates Found   : 3
Files Skipped      : 0
Errors/Failed      : 0
--------------------------------------------------
Breakdown by Category:
  - Documents   :  8 files (386 B)
  - Images      :  3 files (93 B)
  - Videos      :  2 files (68 B)
  - Audio       :  2 files (67 B)
  - Archives    :  2 files (57 B)
  - Code        :  2 files (85 B)
  - Others      :  2 files (82 B)
  - Duplicates  :  3 files (134 B)
==================================================
```

### Sample Log Lines (`organizer.log`):
```text
2026-11-14 11:40:48,188 - INFO - Starting file organization in REAL RUN mode for: ...\sample_output
2026-11-14 11:40:48,199 - INFO - Moved: 'assets_bundle.tar.gz' -> 'Archives/assets_bundle.tar.gz'
2026-11-14 11:40:48,224 - INFO - Sanitized filename 'financial_budget#2024$draft!.xlsx' -> 'financial_budget_2024_draft.xlsx'
2026-11-14 11:40:48,227 - INFO - Moved: 'financial_budget#2024$draft!.xlsx' -> 'Documents/financial_budget_2024_draft.xlsx'
2026-11-14 11:40:48,237 - INFO - Moved duplicate: 'internship_report_copy.pdf' -> 'Duplicates/internship_report_copy.pdf'
2026-11-14 11:40:48,305 - INFO - Summary report generated. File organization complete.
```

---

## 💡 Learnings & Takeaways (Day 45)

- **`os` & `pathlib`**: Using `pathlib.Path` simplified file extension detection (`.suffix`), base filename extraction (`.stem`), and path joins compared to legacy `os.path`.
- **`shutil`**: Learned how `shutil.move()` safely transfers files across directories and handles cross-device file descriptors.
- **`hashlib`**: Implemented chunked streaming (`8192` bytes) hashing with MD5. Reading in chunks is essential so large files don't exhaust system RAM.
- **`re` (Regular Expressions)**: Applied `re.sub(r'[<>:"/\\|?*#$@!%^&]', '_', stem)` to clean invalid filename characters across platforms and prevent OS filesystem errors.
- **Exception Handling**: Wrapped file stat, hash calculation, and movement operations with specific exceptions (`PermissionError`, `FileNotFoundError`, `OSError`) to keep automation resilient when encountering locked or restricted files.
- **`logging` Module**: Structured persistent timestamped audit logs with standard formatting instead of relying solely on `print()` statements.

---

## 🔮 Future Improvements (Planned for Days 2 - 4)

- **Day 2**: Undo functionality (store transaction history in a `.manifest.json` file so organized folders can be restored to their original messy state with one command).
- **Day 3**: Scheduled automatic background monitoring using `watchdog` to organize files immediately as they land in the Downloads folder.
- **Day 4**: Modern desktop GUI using `customtkinter` or `PyQt` with drag-and-drop support, visual progress bars, and custom rule configurations.
