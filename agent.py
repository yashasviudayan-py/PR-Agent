import argparse
import os
import re
import shlex
import subprocess
import sys
import ollama
from scanner import find_relevant_file

def generate_fix(target_file, title, body):
    """Read the target file, ask Ollama for a fix, and write it back."""
    with open(target_file, "r") as f:
        original_code = f.read()

    body = body or ""
    prompt = (
        f"You are a senior developer. A GitHub issue was filed:\n"
        f"Title: {title}\n"
        f"Description: {body}\n\n"
        f"Here is the current content of `{target_file}`:\n"
        f"```\n{original_code}\n```\n\n"
        f"Return ONLY the complete updated file content that addresses the issue. "
        f"No markdown fences, no explanation, no commentary — just the raw code."
    )

    print(f"Generating fix for {target_file}...")
    response = ollama.chat(
        model="llama3.1:8b-instruct-q8_0",
        messages=[{"role": "user", "content": prompt}],
    )
    fixed_code = response["message"]["content"].strip()

    # Strip markdown fences if the model wrapped them anyway
    fixed_code = re.sub(r"^```[\w]*\n", "", fixed_code)
    fixed_code = re.sub(r"\n```$", "", fixed_code)

    with open(target_file, "w") as f:
        f.write(fixed_code + "\n")

    print(f"Fix written to {target_file}")

def _run_cmd(cmd, check=True):
    """Run a shell command, capturing output. Returns (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"   stderr: {result.stderr.strip()}")
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def run_generate(title, body):
    """Phase 1: Find file, create branch, generate fix, output diff (no commit)."""
    target_file = find_relevant_file(title)
    if not target_file:
        print("No target file found. Aborting.")
        sys.exit(1)
    print(f"Scanner identified: {target_file}")

    branch_name = f"fix-{target_file.split('.')[0]}"
    rc, _, err = _run_cmd(f"git checkout -b {shlex.quote(branch_name)}")
    if rc != 0:
        print(f"Failed to create branch {branch_name}: {err}")
        sys.exit(1)
    print(f"Branch created: {branch_name}")

    generate_fix(target_file, title, body)

    # Output diff (unstaged changes)
    rc, diff_output, _ = _run_cmd(f"git diff -- {shlex.quote(target_file)}", check=False)

    print(f"TARGET_FILE: {target_file}")
    print(f"BRANCH: {branch_name}")
    print("DIFF_START")
    print(diff_output)
    print("DIFF_END")
    print(f"FILES_CHANGED: {target_file}")


def run_commit(title, body, branch_name, target_file):
    """Phase 2: Stage, commit, push, and create PR on an existing branch."""
    # Ensure we're on the right branch
    rc, current_branch, _ = _run_cmd("git branch --show-current", check=False)
    if current_branch != branch_name:
        rc, _, err = _run_cmd(f"git checkout {shlex.quote(branch_name)}")
        if rc != 0:
            print(f"Failed to checkout branch {branch_name}: {err}")
            sys.exit(1)

    safe_title = shlex.quote(f"AI Refactor: {title}")
    safe_body = shlex.quote(body or "")

    rc, _, err = _run_cmd(f"git add {shlex.quote(target_file)}")
    if rc != 0:
        print(f"git add failed: {err}")
        sys.exit(1)

    rc, _, err = _run_cmd(f"git commit -m {safe_title}")
    if rc != 0:
        print(f"git commit failed: {err}")
        sys.exit(1)
    print("Changes committed")

    rc, _, err = _run_cmd(f"git push origin {shlex.quote(branch_name)}")
    if rc != 0:
        print(f"git push failed: {err}")
        sys.exit(1)
    print(f"Pushed to origin/{branch_name}")

    rc, pr_url, err = _run_cmd(
        f"gh pr create --title {shlex.quote(title)} --body {safe_body}"
    )
    if rc != 0:
        print(f"gh pr create failed: {err}")
        sys.exit(1)

    print(f"PR_URL: {pr_url}")
    print(f"FILES_CHANGED: {target_file}")
    print(f"BRANCH: {branch_name}")
    print(f"Pull Request Created for {target_file}!")


def run_agent(title, body):
    """Full mode: find file, create branch, generate fix, commit, push, create PR."""
    target_file = find_relevant_file(title)
    if not target_file:
        print("No target file found. Aborting.")
        sys.exit(1)
    print(f"Scanner identified: {target_file}")

    branch_name = f"fix-{target_file.split('.')[0]}"
    rc, _, err = _run_cmd(f"git checkout -b {shlex.quote(branch_name)}")
    if rc != 0:
        print(f"Failed to create branch {branch_name}: {err}")
        sys.exit(1)
    print(f"Branch created: {branch_name}")

    generate_fix(target_file, title, body)

    safe_title = shlex.quote(f"AI Refactor: {title}")
    safe_body = shlex.quote(body or "")

    rc, _, err = _run_cmd(f"git add {shlex.quote(target_file)}")
    if rc != 0:
        print(f"git add failed: {err}")
        sys.exit(1)

    rc, _, err = _run_cmd(f"git commit -m {safe_title}")
    if rc != 0:
        print(f"git commit failed: {err}")
        sys.exit(1)
    print("Changes committed")

    rc, _, err = _run_cmd(f"git push origin {shlex.quote(branch_name)}")
    if rc != 0:
        print(f"git push failed: {err}")
        sys.exit(1)
    print(f"Pushed to origin/{branch_name}")

    rc, pr_url, err = _run_cmd(
        f"gh pr create --title {shlex.quote(title)} --body {safe_body}"
    )
    if rc != 0:
        print(f"gh pr create failed: {err}")
        sys.exit(1)

    print(f"PR_URL: {pr_url}")
    print(f"FILES_CHANGED: {target_file}")
    print(f"BRANCH: {branch_name}")
    print(f"Pull Request Created for {target_file}!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PR-Agent: AI-powered code fixes")
    parser.add_argument("title", help="Issue/PR title")
    parser.add_argument("body", nargs="?", default="", help="Issue/PR body")
    parser.add_argument(
        "--mode",
        choices=["full", "generate", "commit"],
        default="full",
        help="Execution mode: full (default), generate (preview only), commit (finalize)",
    )
    parser.add_argument("--branch", help="Branch name (required for commit mode)")
    parser.add_argument("--file", help="Target file (required for commit mode)")

    args = parser.parse_args()

    if args.mode == "generate":
        run_generate(args.title, args.body)
    elif args.mode == "commit":
        if not args.branch or not args.file:
            parser.error("--branch and --file are required for commit mode")
        run_commit(args.title, args.body, args.branch, args.file)
    else:
        run_agent(args.title, args.body)
