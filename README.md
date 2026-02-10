# PR-Agent

An autonomous repo-maintainer that listens for GitHub issues and automatically generates code fixes, commits them, and opens pull requests — powered by a local LLM via [Ollama](https://ollama.com).

## How It Works

```
GitHub Issue Opened
        |
        v
  GitHub Webhook (POST /webhook)
        |
        v
  listener.py (FastAPI server)
        |
        v
  agent.py
    ├── scanner.py  →  Ollama identifies the relevant file
    ├── Ollama generates the code fix
    ├── git commit & push to new branch
    └── gh pr create  →  Pull Request opened
```

1. A new issue is opened on your GitHub repository.
2. GitHub sends a webhook to the listener.
3. The listener triggers the agent with the issue title and body.
4. The scanner uses Ollama (Llama 3.1) to identify which file the issue relates to.
5. The agent reads the file, asks Ollama to generate a fix, and writes it back.
6. The agent commits the change, pushes a new branch, and opens a PR via the GitHub CLI.

## Prerequisites

- **Python 3.10+**
- **[Ollama](https://ollama.com)** installed and running locally
- **[GitHub CLI (`gh`)](https://cli.github.com)** authenticated (`gh auth login`)
- **[ngrok](https://ngrok.com)** (free tier) for exposing the local server to GitHub

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/yashasviudayan-py/PR-Agent.git
cd PR-Agent
pip install -r requirements.txt
```

### 2. Pull the Ollama model

```bash
ollama pull llama3.1:8b-instruct-q8_0
```

### 3. Start Ollama

```bash
ollama serve
```

### 4. Start the listener

```bash
python listener.py
```

You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`

### 5. Expose with ngrok

In a separate terminal:

```bash
ngrok http 8000
```

Copy the `Forwarding` URL (e.g., `https://abc123.ngrok-free.app`).

### 6. Configure the GitHub webhook

1. Go to your repository on GitHub.
2. Navigate to **Settings > Webhooks > Add webhook**.
3. **Payload URL:** `<your-ngrok-url>/webhook`
4. **Content type:** `application/json`
5. **Events:** Select "Let me select individual events" and check **Issues**.
6. Click **Add webhook**.

## Usage

Open an issue on the repository. The agent will automatically:

1. Identify the relevant file.
2. Generate a code fix using Ollama.
3. Open a pull request with the changes.

## Project Structure

```
.
├── listener.py        # FastAPI webhook server
├── agent.py           # Orchestrator: scan → fix → commit → PR
├── scanner.py         # LLM-powered file identification
├── requirements.txt   # Python dependencies
├── .env               # Environment variables (not committed)
└── .gitignore
```

## License

MIT
