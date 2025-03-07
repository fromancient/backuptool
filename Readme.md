# Backup Tool

## Overview

This Backup Tool allows you to take snapshots of a specific directory, listing existing snapshots, restoring files from snapshots, and optionally taking snapshots at regular intervals for a specified duration. The backups are saved as JSON files, storing both the metadata of files (like paths and hashes) and their content encoded in Base64 format.

## Features

- Take snapshots of a target directory.
- List all available snapshots.
- Restore files from a selected snapshot.
- Run a snapshot job to take continuous snapshots at defined intervals.
- Prune old snapshots (to be implemented).

## Installation

Ensure you have Python 3 installed. You can run the script directly, as it doesn't require any additional dependencies.

## Usage

Run the script from the command line using the following commands:

### 1. Snapshot

Take a snapshot of a target directory.

```bash
python backuptool.py snapshot --target-directory /path/to/your/directory
```

### 2. List

List all available snapshots.

```bash
python backuptool.py list
```

### 3. Restore

Restore files from a selected snapshot to a specified output directory.

```bash
python backuptool.py restore --snapshot-file snapshot_filename.json --output-directory /path/to/restore/directory
```

### 4. Prune

Prune old snapshots, keeping only the specified number.

```bash
python backuptool.py prune --snapshot-number N
```

### 5. Snapshot Job

Run a job to take snapshots of a target directory at specified intervals for a defined duration.

```bash
python backuptool.py job --target-directory /path/to/your/directory --interval INTERVAL_DURATION --duration TOTAL_DURATION
```

- `INTERVAL_DURATION`: The time to wait between each snapshot in seconds.
- `TOTAL_DURATION`: The total time the job should run in seconds.

#### Example:

To take snapshots every 10 seconds for 1 minute:

```bash
python backuptool.py job --target-directory /path/to/your/directory --interval 10 --duration 60
```

## File Structure

- **snapshots/**: Directory where all snapshot JSON files will be saved.
- The script itself will create the snapshots directory if it does not exist.

## Requirements

- Python 3.x

## License

This project is licensed under the MIT License - see the [LICENSE](./Instruction.md) file for details.

## Acknowledgments

- Thanks to the open-source community for the frameworks and libraries that make this possible.
