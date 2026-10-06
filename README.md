# 🔑 GitKey Bot - Android Signing Key Manager & GitHub Secrets Generator

**GitKey Bot** is a production-ready, security-first Telegram Bot designed for Android developers and modders. It allows users to generate real, Android-compatible signing keystores (`.jks` / `.p12`) and prepare the corresponding **GitHub Actions Secrets** (`KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`) directly through a clean, interactive Telegram interface.

---

## ✨ Features

- 🔑 **Real Keystore Generation**: Generates real PKCS12/JKS keystores containing private keys and self-signed X.509 certificates usable by Android Gradle signing configurations.
- 🐙 **GitHub Actions Secrets Generator**: Automatically calculates `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`, and `KEY_PASSWORD` with copyable single-click code blocks and a **Copy All Secrets** workflow.
- 📥 **Complete File Export System**: Download your `.jks` keystore file, `.env` secrets file, and GitHub Actions workflow YAML sample directly in Telegram.
- 🛠️ **14+ Developer Utilities**:
  - *Keystore Generator & Keystore Inspector*
  - *Base64 Encoder & Base64 Decoder*
  - *SHA-256, SHA-1, and MD5 Hash Generators*
  - *APK Certificate & Metadata Inspector*
  - *GitHub Secrets Formatter*
  - *JSON Formatter*
  - *Secure Random Password Generator*
  - *UUID v4 Generator*
- 📂 **My Keys History**: View safe metadata (project name, alias, filename, date, SHA-256 fingerprint) for generated keys. Plaintext passwords are NEVER stored.
- 🔒 **Zero-Trust Security**:
  - Environment variable configuration (`TELEGRAM_BOT_TOKEN`).
  - Zero logging of passwords, private keys, or secret blocks.
  - Per-user session isolation and rate limiting.
  - Automatic temporary file deletion.
- 🚀 **Render.com Web Service Port Scan Compatible**: Embedded HTTP health check server handles Render.com port scans automatically.

---

## 🚀 Quick Start Guide (Local Setup)

### 1. Prerequisites
- Python 3.9 or higher installed on your machine.
- Git installed.

### 2. Get a Telegram Bot Token
1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts to name your bot (e.g. `GitKey Bot`).
3. BotFather will provide an HTTP API token (e.g., `1234567890:ABCdefGHIjklMNOpqrsTUVwxyZ_1234567`).
4. **Copy this token** — you will need it in the next step.

### 3. Installation & Virtual Environment
```bash
# Clone the repository
git clone https://github.com/your-username/gitkey-bot.git
cd gitkey-bot

# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and paste your Telegram Bot Token:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyZ_1234567
PORT=8080
USE_WEBHOOK=false
MAX_FILE_SIZE_MB=20
TEMP_FILE_LIFETIME_SEC=1800
RATE_LIMIT_ACTIONS_PER_MIN=30
```

### 5. Run the Bot Locally
```bash
python main.py
```
Open Telegram and send `/start` to your bot to test the interface!

---

## ☁️ Free Render.com Deployment Guide

Render.com scans for an open HTTP port when deploying a **Web Service**. GitKey Bot includes an embedded lightweight HTTP health check server that responds `200 OK` on `0.0.0.0:PORT` while simultaneously running Telegram polling.

### Step 1: Push Code to GitHub
1. Create a new **private** or public repository on GitHub.
2. Push your project code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit of GitKey Bot"
git branch -M main
git remote add origin https://github.com/your-username/gitkey-bot.git
git push -u origin main
```
> ⚠️ **CRITICAL:** Ensure `.env` is listed in `.gitignore` so your bot token is NEVER pushed to GitHub.

### Step 2: Deploy on Render.com
1. Log in to [Render.com](https://render.com).
2. Click **New +** → **Web Service** (or **Background Worker**).
3. Connect your GitHub repository (`gitkey-bot`).
4. Configure service settings:
   - **Name:** `gitkey-bot`
   - **Region:** Select closest region (e.g. Oregon, Frankfurt, Singapore).
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
   - **Instance Type:** `Free`

### Step 3: Configure Environment Variables
1. In your Render dashboard, go to **Environment**.
2. Add key: `TELEGRAM_BOT_TOKEN`
   Value: Paste your token from @BotFather (`1234567890:ABCdefGHIjklMNO...`).
3. Add key: `PORT`
   Value: `10000` (or leave default assigned by Render).
4. Click **Save Changes**. Render will deploy your bot and detect the open health check port (`==> Port 10000 open! Live!`).

---

## 🔒 Security & Privacy Practices

1. **No Password Persistence**: Keystore passwords and private key material are only kept in memory for the duration of the active creation process and are immediately discarded.
2. **Sanitized Inputs**: All project names, filenames, and distinguished name (DN) fields are sanitized to prevent path traversal or injection.
3. **No Secret Logging**: Standard output and error logs never print tokens, passwords, Base64 secrets, or key material.
4. **Temporary Directory Cleanup**: Temporary files generated during user sessions are stored in an isolated session directory and purged automatically after 30 minutes.
5. **Rate Limiting**: Per-user rate limiting (30 actions/min) protects the server against CPU and memory exhaustion.

---

## 📄 License
Released under the MIT License. Free for open-source and developer use.
