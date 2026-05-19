# 🚀 Steps to Run AICyberAuditBox

Follow these instructions to launch the application and its dependencies (Ollama & ShaktiDB) from a fresh start.

---

## 1. Prerequisites (Ensure these are running first)

* 🦙 **Ollama:** Make sure the Ollama application is active. You should see the Ollama icon in your Windows system tray.
* 🐳 **Docker Desktop:** Ensure Docker Desktop is open and fully running (this hosts **ShaktiDB** on port `15234`).

---

## 2. First-Time Setup (Only do this once)

If you have not downloaded the local AI models yet, run the model downloader script in your terminal:
```powershell
.\pull_models.bat
```
*(This pulls `qwen2.5:7b` and `llama3.1:8b` directly to your local Ollama engine).*

---

## 3. Running the Application (Every fresh start)

Open a terminal (PowerShell / Command Prompt) in your project directory (`c:\Users\HP\Desktop\Rag_Project`) and run:
```powershell
.\run_demo.bat
```

### What this launcher script does automatically:
1. **Ollama Check:** Validates that the Ollama service is active.
2. **ShaktiDB Launch:** Prompts Docker to spin up the database container (`docker-compose up -d`). If Docker is down, the system gracefully self-heals by connecting to a local SQLite database (`shakthidb_local.db`).
3. **App Start:** Installs/updates python dependencies and launches the Streamlit server on port **`8501`**, automatically opening the dashboard in your default browser.
