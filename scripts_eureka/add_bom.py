"""
Add UTF-8 BOM to all text files in src_eureka/
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EUREKA_DIR = REPO_ROOT / "src_eureka"

BOM = b'\xef\xbb\xbf'

def add_bom_to_file(file_path: Path):
    """Add BOM to a file if it doesn't have one."""
    content = file_path.read_bytes()

    if content.startswith(BOM):
        return False  # Already has BOM

    # Add BOM
    file_path.write_bytes(BOM + content)
    return True

def main():
    # File extensions that need BOM
    text_extensions = {'.txt', '.yml', '.gui', '.gfx', '.asset', '.md'}

    files_processed = 0
    files_updated = 0

    for file_path in EUREKA_DIR.rglob('*'):
        if file_path.is_file() and file_path.suffix in text_extensions:
            files_processed += 1
            if add_bom_to_file(file_path):
                files_updated += 1
                print(f"Added BOM: {file_path.relative_to(REPO_ROOT)}")

    print(f"\nProcessed {files_processed} files, added BOM to {files_updated} files.")

if __name__ == "__main__":
    main()
