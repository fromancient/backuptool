import os
import tempfile
import shutil
import filecmp
from pathlib import Path
import subprocess
import json

# Constants
SNAPSHOT_DIR = 'snapshots'
TEST_FILES = {
    "test1.txt": "Hello, World!",
    "test2.txt": "This is a test file.",
    "test3.txt": "Backup and restore functionality works."
}

def create_test_files(target_dir):
    """Create test files in the specified directory."""
    for filename, content in TEST_FILES.items():
        with open(Path(target_dir) / filename, 'w') as f:
            f.write(content)

def run_command(command):
    """Run the backup tool command using subprocess."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

def verify_files(original_dir, restored_dir):
    """Verify that all files in the original directory match the restored files."""
    for filename in TEST_FILES.keys():
        original_file = Path(original_dir) / filename
        restored_file = Path(restored_dir) / filename
        if not original_file.is_file() or not restored_file.is_file():
            print(f"File verification failed for {filename}.")
            return False
        
        if not filecmp.cmp(original_file, restored_file, shallow=False):
            print(f"File contents differ for {filename}.")
            return False
            
    return True

def test_backup_tool():
    """Main testing function for the backup tool."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the target directory for backup
        target_dir = Path(temp_dir) / 'backup_test'
        target_dir.mkdir()

        # Create test files
        create_test_files(target_dir)

        # Take a snapshot of the created files
        snapshot_command = f'python backuptool.py snapshot --target-directory={target_dir}'
        result = run_command(snapshot_command)
        print(result.stdout)

        # List snapshots to confirm it was created
        list_command = 'python backuptool.py list'
        list_result = run_command(list_command)
        print(list_result.stdout)

        # Restore the snapshot to a new directory
        restore_dir = Path(temp_dir) / 'restore_dir'
        restore_command = f'python backuptool.py restore --snapshot-file=snapshot_*.json --output-directory={restore_dir}'
        restore_result = run_command(restore_command)
        print(restore_result.stdout)

        # Verify that the restored files match the originals
        if verify_files(target_dir, restore_dir):
            print("Test passed: Files verified successfully!")
        else:
            print("Test failed: Files verification failed.")

if __name__ == '__main__':
    test_backup_tool()
