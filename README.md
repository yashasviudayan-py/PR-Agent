# PR-Agent

[![CI](https://github.com/yashasviudayan-py/PR-Agent/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/yashasviudayan-py/PR-Agent/actions/workflows/docker-publish.yml)
[![Docker](https://img.shields.io/badge/Docker%20Hub-pr--agent-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/yashasviudayan/pr-agent)
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/yashasviudayan-py/PR-Agent?color=green)](LICENSE)

An autonomous repo-maintainer that listens for GitHub issues and automatically generates code fixes, commits them, and opens pull requests — powered by a local LLM via [Ollama](https://ollama.com).

---

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

---

## Prerequisites

| Dependency | Purpose |
|---|---|
| [Python 3.10+](https://www.python.org) | Runtime |
| [Ollama](https://ollama.com) | Local LLM inference |
| [GitHub CLI (`gh`)](https://cli.github.com) | PR creation & auth |
| [ngrok](https://ngrok.com) | Expose local server to GitHub |

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/yashasviudayan-py/PR-Agent.git
cd PR-Agent
pip install -r requirements.txt
```

### 2. Pull the model and start Ollama

```bash
ollama pull llama3.1:8b-instruct-q8_0
ollama serve
```

### 3. Start the listener

```bash
python listener.py
```

You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`

### 4. Expose with ngrok

In a separate terminal:

```bash
ngrok http 8000
```

Copy the `Forwarding` URL (e.g., `https://abc123.ngrok-free.app`).

### 5. Configure the GitHub webhook

1. Go to your repository on GitHub.
2. Navigate to **Settings > Webhooks > Add webhook**.
3. **Payload URL:** `<your-ngrok-url>/webhook`
4. **Content type:** `application/json`
5. **Events:** Select "Let me select individual events" and check **Issues**.
6. Click **Add webhook**.

---

## Docker

Pull the pre-built image from Docker Hub:

```bash
docker pull yashasviudayan/pr-agent:latest
```

Or run it directly:

```bash
docker run -p 8000:8000 yashasviudayan/pr-agent:latest
```

> **Note:** The container includes Python, git, and GitHub CLI. You still need Ollama running on the host (accessible at `host.docker.internal:11434`).

---

## Usage

Open an issue on the repository. The agent will automatically:

1. Identify the relevant file.
2. Generate a code fix using Ollama.
3. Open a pull request with the changes.

---

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── docker-publish.yml   # CI/CD: auto-push to Docker Hub
├── listener.py                  # FastAPI webhook server
├── agent.py                     # Orchestrator: scan → fix → commit → PR
├── scanner.py                   # LLM-powered file identification
├── Dockerfile                   # Container image definition
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
├── .env                         # Environment variables (not committed)
├── .dockerignore
└── .gitignore
```

---

## License

This project is licensed under the [MIT License](LICENSE).
