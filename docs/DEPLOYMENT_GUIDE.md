# Omni-Analyzer: Deployment & Operations Guide

This solution offers two entirely disjoint presentation layers depending on whether you are running a SOC team auditing code, or DevOps engineers automating compliance natively in Git.

---

## 💻 1. Web Dashboard (Interactive Mode)
Built with React, Vite, and vanilla glass-morphic CSS. Designed specifically for security researchers to run manual threat assessments against sandbox architectures.

### Architecture
- **Backend**: Containerized FastAPI Python endpoint. Installs native `Spacy` ML models entirely during the Docker build stage so the server can run entirely disconnected from the World Wide Web in strict VPCs (Air-Gapped environments).
- **Frontend**: Multi-stage Node/Alpine container heavily optimized to statically serve React files over a lightweight `nginx:alpine` routing configuration.

### Deployment Commands
To spin up the web dashboard locally across your enterprise:
```bash
cp .env.example .env
# Populate GOOGLE_API_KEY if utilizing external endpoints, or hook an internal vLLM provider.
docker-compose up --build -d
```
You can now access the interactive React platform at `http://localhost:8080`.

---

## 🛠️ 2. CI/CD Operations (Automated Mode)
Designed for extreme operational friction against broken logic; integrated directly into the Git provider.

### The Mechanism (`ci_runner.py`)
When a developer opens a Pull Request natively in GitHub targeting the `main` branch, `.github/workflows/security-scan.yml` boots a headless version of our backend Docker container (`action.yml`).

It executes the LangGraph flow against `$GITHUB_WORKSPACE`. 
1. If the risk is LOW or non-existent, `ci_runner.py` uses `sys.exit(0)`, and the PR check turns green ✅.
2. If the Compliance Agent detects a `CRITICAL` vulnerability (like leaking PII to console logs, or bypassing your Token Vaults), the script spits the generated fixing `.patch` strings onto the terminal, and throws `sys.exit(1)`. 
3. This hard-fails the CI/CD deployment stage 🚨, preventing the unsafe commit from entering the enterprise `main` branch.
