from fastapi import FastAPI, Request
import subprocess

app = FastAPI()

@app.post("/webhook")
async def handle_github_issue(request: Request):
    payload = await request.json()
    
    # We only act when a new issue is 'opened'
    if payload.get("action") == "opened":
        issue_title = payload["issue"]["title"]
        issue_body = payload["issue"]["body"]
        print(f"🛠️ New Task: {issue_title}")
        
        # TRIGGER: Call the agent script with the issue details
        subprocess.Popen(["python", "agent.py", issue_title, issue_body or ""])
        
    return {"status": "accepted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)