import sys
import os
from scanner import find_relevant_file

def run_agent(title, body):
    # 1. Identify the file locally
    target_file = find_relevant_file(title)
    print(f"🔍 Scanner identified: {target_file}")
    
    # 2. Create a new branch using GH CLI
    branch_name = f"fix-{target_file.split('.')[0]}"
    os.system(f"git checkout -b {branch_name}")
    
    # 3. [HANDOFF TO CLAUDE] 
    # At this point, you paste the file content into Claude Pro 
    # and ask for the fix. Then save the fix to target_file.
    
    # 4. Push and Open PR via GH CLI
    os.system(f"git add {target_file}")
    os.system(f"git commit -m 'AI Refactor: {title}'")
    os.system(f"git push origin {branch_name}")
    
    # Use the 'gh' command you just authorized!
    os.system(f"gh pr create --title '{title}' --body '{body}'")
    print(f"🚀 Pull Request Created for {target_file}!")

if __name__ == "__main__":
    run_agent(sys.argv[1], sys.argv[2])