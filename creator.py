import subprocess
import sys
import os

def create_commits(timestamp_file):
    # Ensure we are inside a git repository
    if not os.path.exists(".git"):
        raise SystemExit("Error: This directory is not a Git repository. Run 'git init' first.")

    # Open and read the timestamp file
    try:
        with open(timestamp_file, 'r') as file:
            timestamps = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        raise SystemExit(f"Error: File '{timestamp_file}' not found.")

    print(f"Found {len(timestamps)} timestamps. Starting commits...")

    for idx, ts in enumerate(timestamps, 1):
        print(f"[{idx}/{len(timestamps)}] Committing for date: {ts}")

        # Git command to create an empty commit with a specific date
        cmd = [
            "git", "commit",
            "--allow-empty",
            f"--date={ts}",
            "-m", f"Automated backdated commit for {ts}"
        ]

        # Override BOTH author and committer environment variables to enforce the timestamp
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = ts
        env["GIT_COMMITTER_DATE"] = ts

        # Execute the git command
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Failed to commit for timestamp '{ts}': {result.stderr.strip()}")
            # Optional: break or continue depending on preference
            continue

    print("✅ All commits processed successfully!")

if __name__ == "__main__":
    # Expects the path to the text file as an argument
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python make_commits.py <path_to_timestamps_file>")

    create_commits(sys.argv[1])
