import sys
import os
import re
import shlex
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

    print(f"🤖 Generating fix for {target_file}...")
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

    print(f"✅ Fix written to {target_file}")

def run_agent(title, body):
    # 1. Identify the file locally
    target_file = find_relevant_file(title)
    if not target_file:
        print("❌ No target file found. Aborting.")
        return
    print(f"🔍 Scanner identified: {target_file}")

    # 2. Create a new branch using GH CLI
    branch_name = f"fix-{target_file.split('.')[0]}"
    os.system(f"git checkout -b {shlex.quote(branch_name)}")

    # 3. Generate the fix with Ollama
    generate_fix(target_file, title, body)

    # 4. Push and Open PR via GH CLI
    safe_title = shlex.quote(f"AI Refactor: {title}")
    safe_body = shlex.quote(body or "")
    os.system(f"git add {shlex.quote(target_file)}")
    os.system(f"git commit -m {safe_title}")
    os.system(f"git push origin {shlex.quote(branch_name)}")

    os.system(f"gh pr create --title {shlex.quote(title)} --body {safe_body}")
    print(f"🚀 Pull Request Created for {target_file}!")

if __name__ == "__main__":
    run_agent(sys.argv[1], sys.argv[2])
