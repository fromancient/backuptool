import os
import json
import hashlib
import argparse
import datetime
from pathlib import Path
import base64
import time
import threading

SNAPSHOT_DIR = 'snapshots'


def hash_file(file_path):
    """Return the SHA-256 hash of the file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_database(filename):
    """Load the backup database from a JSON file."""
    if not os.path.exists(filename):
        return {'files': {}}
    with open(filename, 'r') as f:
        return json.load(f)


def save_database(database, filename):
    """Save the backup database to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(database, f, indent=4)


def get_directory_size(directory):
    """Get the total size of the directory in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            fp = Path(dirpath) / filename
            total_size += fp.stat().st_size
    return total_size


def snapshot(target_directory):
    """Take a snapshot of the target directory and record disk usage."""
    Path(SNAPSHOT_DIR).mkdir(exist_ok=True)

    # Create a timestamp for the snapshot
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    snapshot_file_path = Path(SNAPSHOT_DIR) / f'snapshot_{timestamp}.json'
    snapshot_data = {'timestamp': timestamp, 'files': {}, 'file_contents': {},
                     'directory_size': 0, 'snapshot_size': 0}

    # Calculate total size of the directory to be snapshotted
    snapshot_data['directory_size'] = get_directory_size(target_directory)

    # Loop through each file in the target directory
    for dirpath, _, filenames in os.walk(target_directory):
        for filename in filenames:
            file_path = Path(dirpath) / filename
            file_hash = hash_file(file_path)
            snapshot_data['files'][str(file_path)] = file_hash

            # Store file content in file_contents using Base64
            if file_hash not in snapshot_data['file_contents']:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    snapshot_data['file_contents'][file_hash] = base64.b64encode(content).decode('utf-8')  # Store as Base64 string

            # Calculate size required for snapshot (unique files)
            snapshot_data['snapshot_size'] += file_path.stat().st_size

    save_database(snapshot_data, snapshot_file_path)
    print(f'Snapshot saved to {snapshot_file_path}')


def list_snapshots():
    """List all available snapshots with additional disk usage metrics."""
    print("Available Snapshots:")
    total_database_size = 0
    
    for file in os.listdir(SNAPSHOT_DIR):
        if file.endswith('.json'):
            snapshot_file_path = Path(SNAPSHOT_DIR) / file
            database = load_database(snapshot_file_path)
            snapshot_size = os.path.getsize(snapshot_file_path)  # Size of the snapshot file itself
            total_database_size += snapshot_size

            # Extract the timestamp for better readability
            timestamp = database.get('timestamp', 'Unknown Timestamp')
            print(f" - {file} (Snapshot Time: {timestamp}):")
            print(f"   - Directory Size at Snapshot Time: {database['directory_size']} bytes")
            print(f"   - Snapshot Size (Unique Files): {database['snapshot_size']} bytes")
            print(f"   - Size of Snapshot JSON File: {snapshot_size} bytes")

    print(f"Total size of all snapshots in database: {total_database_size} bytes")



def restore(snapshot_filename, output_directory):
    """Restore files from a snapshot."""
    snapshot_file_path = Path(SNAPSHOT_DIR) / snapshot_filename
    if not snapshot_file_path.exists():
        print(f"Snapshot file '{snapshot_filename}' not found.")
        return

    database = load_database(snapshot_file_path)
    for file_path, file_hash in database['files'].items():
        output_path = Path(output_directory) / Path(file_path).relative_to(Path(file_path).parent)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Decode the Base64 encoded content back to bytes
        content = base64.b64decode(database['file_contents'][file_hash])
        with open(output_path, 'wb') as f:
            f.write(content)  # Write the original bytes

    print(f"Restored snapshot '{snapshot_filename}' to '{output_directory}'")


def prune(snapshot_to_keep):
    """Prune old snapshots, keeping only the specified number."""
    # Get a list of all snapshot files
    snapshot_files = [f for f in os.listdir(SNAPSHOT_DIR) if f.endswith('.json')]
    
    # Sort the list of snapshot files by their creation time (timestamp in filename)
    snapshot_files.sort()  # The filenames have the timestamp, so this works.

    # If the number of snapshots already meets or is below the specified amount, do nothing
    if len(snapshot_files) <= snapshot_to_keep:
        print(f"Number of snapshots ({len(snapshot_files)}) is within the limit of {snapshot_to_keep}. No pruning needed.")
        return

    # Calculate how many snapshots to remove
    snapshots_to_remove = len(snapshot_files) - snapshot_to_keep
    for i in range(snapshots_to_remove):
        snapshot_to_remove = snapshot_files[i]
        os.remove(Path(SNAPSHOT_DIR) / snapshot_to_remove)
        print(f"Removed snapshot: {snapshot_to_remove}")
        
    print(f"Pruned to keep only the most recent {snapshot_to_keep} snapshots.")


def snapshot_job(target_directory, interval, duration):
    """Take snapshots recursively every 'interval' seconds for 'duration' seconds."""
    end_time = time.time() + duration
    while time.time() < end_time:
        snapshot(target_directory)
        time.sleep(interval)






def main():
    parser = argparse.ArgumentParser(description='Backup Tool')
    subparsers = parser.add_subparsers(dest='command')

    # Snapshot command
    snapshot_parser = subparsers.add_parser('snapshot')
    snapshot_parser.add_argument('--target-directory', required=True, help='The directory to snapshot.')

    # List command
    list_parser = subparsers.add_parser('list')

    # Restore command
    restore_parser = subparsers.add_parser('restore')
    restore_parser.add_argument('--snapshot-file', required=True, help='The snapshot JSON filename to restore from.')
    restore_parser.add_argument('--output-directory', required=True, help='Where to restore the snapshot to.')

    # Prune command
    prune_parser = subparsers.add_parser('prune')
    prune_parser.add_argument('--snapshot-number', type=int, required=True, help='The snapshot number to keep.')

    # New snapshot job command
    job_parser = subparsers.add_parser('job')
    job_parser.add_argument('--target-directory', required=True, help='The directory to snapshot.')
    job_parser.add_argument('--interval', type=int, required=True, help='Interval in seconds between snapshots.')
    job_parser.add_argument('--duration', type=int, required=True, help='Total duration in seconds for the job.')

    args = parser.parse_args()
    if args.command == 'snapshot':
        snapshot(args.target_directory)
    elif args.command == 'list':
        list_snapshots()
    elif args.command == 'restore':
        restore(args.snapshot_file, args.output_directory)
    elif args.command == 'prune':
        prune(args.snapshot_number)
    elif args.command == 'job':
        # Start a thread to run the snapshot job
        job_thread = threading.Thread(target=snapshot_job, args=(args.target_directory, args.interval, args.duration))
        job_thread.start()
        job_thread.join()  # Wait for the job to complete


if __name__ == '__main__':
    Path(SNAPSHOT_DIR).mkdir(exist_ok=True)  # Ensure the snapshot directory is created
    main()

if __name__ == '__main__':
    Path(SNAPSHOT_DIR).mkdir(exist_ok=True)  # Ensure the snapshot directory is created
    main()
