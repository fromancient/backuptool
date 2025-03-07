import os
import shutil
import unittest
import tempfile
from pathlib import Path
import time

# Assuming the main script is named backup_tool.py
FROM_SCRIPT = 'backuptool'  # Make sure this variable matches the script name

class TestBackupTool(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.snapshot_dir = 'snapshots'
        self.create_test_files()

    def create_test_files(self):
        """Create some test files in the test directory."""
        for i in range(5):
            with open(os.path.join(self.test_dir, f'test_file_{i}.txt'), 'w') as f:
                f.write(f'This is test file {i}')

    def test_snapshot_creation(self):
        """Test creating a snapshot."""
        os.system(f'python {FROM_SCRIPT}.py snapshot --target-directory={self.test_dir}')
        self.assertTrue(any(f.endswith('.json') for f in os.listdir(self.snapshot_dir)))

    def test_list_snapshots(self):
        """Test listing snapshots."""
        os.system(f'python {FROM_SCRIPT}.py snapshot --target-directory={self.test_dir}')
        output = os.popen(f'python {FROM_SCRIPT}.py list').read()
        self.assertIn('Available Snapshots:', output)

    def test_restore_snapshot(self):
        """Test restoring a snapshot."""
        os.system(f'python {FROM_SCRIPT}.py snapshot --target-directory={self.test_dir}')
        snapshot_file = next(f for f in os.listdir(self.snapshot_dir) if f.endswith('.json'))
        restore_dir = tempfile.mkdtemp()

        os.system(f'python {FROM_SCRIPT}.py restore --snapshot-file={snapshot_file} --output-directory={restore_dir}')
        
        # Check if files are restored
        for i in range(5):
            self.assertTrue(os.path.exists(os.path.join(restore_dir, f'test_file_{i}.txt')))
        
        # Clean up
        shutil.rmtree(restore_dir)

    def tearDown(self):
        """Clean up test directories and files."""
        shutil.rmtree(self.test_dir)
        if os.path.exists(self.snapshot_dir):
            shutil.rmtree(self.snapshot_dir)

if __name__ == '__main__':
    unittest.main()
