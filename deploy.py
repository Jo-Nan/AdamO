#!/usr/bin/env python3
"""Deploy this static homepage with Git.

Default behavior:
1. Ensure the repository is initialized.
2. Stage the homepage files.
3. Commit them if there is anything new.
4. Push the current branch to the configured remote.

This is intentionally tiny and dependency-free.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def ensure_repo() -> None:
    if not (ROOT / ".git").exists():
        run_git("init")


def has_changes() -> bool:
    result = run_git("status", "--porcelain", check=True)
    return bool(result.stdout.strip())


def ensure_remote(remote: str, url: str) -> None:
    result = run_git("remote", check=False)
    remotes = result.stdout.split()
    if remote in remotes:
        current = run_git("remote", "get-url", remote).stdout.strip()
        if current != url:
            run_git("remote", "set-url", remote, url)
    else:
        run_git("remote", "add", remote, url)


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy the homepage through Git.")
    parser.add_argument("-m", "--message", default="deploy", help="Commit message")
    parser.add_argument("--remote", default="origin", help="Git remote name")
    parser.add_argument(
        "--url",
        default="https://github.com/Jo-Nan/AdamO.git",
        help="Git remote URL",
    )
    parser.add_argument("--branch", default="main", help="Branch to push")
    parser.add_argument(
        "--skip-push",
        action="store_true",
        help="Create the commit but do not push it",
    )
    args = parser.parse_args()

    if not (ROOT / "index.html").exists():
        print("index.html not found in the repository root.", file=sys.stderr)
        return 1

    ensure_repo()
    ensure_remote(args.remote, args.url)

    run_git("add", "-A")

    if has_changes():
        run_git("commit", "-m", args.message)
    else:
        print("No changes to deploy.")

    run_git("branch", "-M", args.branch)

    if not args.skip_push:
        run_git("push", "-u", args.remote, args.branch)

    print("Deployment complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
