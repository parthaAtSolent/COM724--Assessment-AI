# Complete Guide: Uploading GitHub Repo to Hugging Face Spaces
### Cryptocurrency Price Forecasting App — Windows Step-by-Step

---

## ⚙️ PART 1 — ONE-TIME SETUP

### Step 1.1 — Install Git
Download and install from: https://git-scm.com/download/win
During installation, keep all default options.

Verify installation:
```cmd
git --version
```

---

### Step 1.2 — Install Git LFS
Download and install from: https://git-lfs.github.com/

Then initialise it:
```cmd
git lfs install
```

You should see: `Git LFS initialized.`

---

### Step 1.3 — Install Python & pip
Download Python 3.12.7 from: https://www.python.org/downloads/

> ⚠️ During installation, tick **"Add Python to PATH"**

Verify:
```cmd
python --version
pip --version
```

---

### Step 1.4 — Install Hugging Face CLI
```cmd
pip install huggingface_hub
```

Verify:
```cmd
huggingface-cli --version
```

---

### Step 1.5 — Create a Hugging Face Account
Go to https://huggingface.co and sign up or log in.

---

### Step 1.6 — Generate a Write Access Token
1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Give it a name (e.g. `my-write-token`)
4. Set **Role** to **"Write"**
5. Click **Generate token**
6. **Copy and save the token somewhere safe** — you'll need it shortly

> ⚠️ Never share your token publicly. If you accidentally share it, go back to https://huggingface.co/settings/tokens, delete it, and create a new one immediately.

---

## 🌐 PART 2 — CREATE YOUR HUGGING FACE SPACE

### Step 2.1 — Create a New Space
1. Go to: https://huggingface.co/new-space
2. Fill in the details:
   - **Owner:** your HF username (e.g. `patrick078`)
   - **Space name:** e.g. `crypto_app`
   - **SDK:** Select **Streamlit**
   - **Visibility:** Public or Private
3. Click **Create Space**

Your Space URL will be:
`https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

---

## 💻 PART 3 — SET UP YOUR LOCAL FOLDER

### Step 3.1 — Open Command Prompt
Press `Win + R`, type `cmd`, press Enter.

Navigate to your working folder:
```cmd
cd "D:\Solent University\Applied AI in Business (COM724)"
```

---

### Step 3.2 — Clone your Hugging Face Space
```cmd
git clone https://YOUR_USERNAME:YOUR_HF_TOKEN@huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

**Your specific command:**
```cmd
git clone https://patrick078:YOUR_HF_TOKEN@huggingface.co/spaces/patrick078/crypto_app
```

Then enter the folder:
```cmd
cd crypto_app
```

---

### Step 3.3 — Clone your GitHub Repo (separate folder)
```cmd
cd ..
git clone https://github.com/parthaAtSolent/COM724--Assessment-AI
```

---

### Step 3.4 — Copy GitHub files into the HF Space folder
```cmd
xcopy /E /I /Y "COM724--Assessment-AI\*" "crypto_app\"
cd crypto_app
```

---

### Step 3.5 — Remove unwanted folders
These folders should NOT be uploaded to HF:
```cmd
rmdir /S /Q venv
rmdir /S /Q latex
rmdir /S /Q .vscode
```

---

## 📄 PART 4 — CONFIGURE YOUR FILES

### Step 4.1 — Fix your README.md
Open the README.md:
```cmd
notepad README.md
```

Make sure the **very top** of the file looks exactly like this (no extra quotes, no missing fields):

```yaml
---
title: Cryptocurrency Price Forecasting App
emoji: 📈
colorFrom: blue
colorTo: green
sdk: streamlit
app_file: main.py
python_version: 3.12.7
pinned: false
---
```

> ⚠️ Key rules:
> - No quotes around `3.12.7`
> - `app_file` must match your actual entry Python file (`main.py`)
> - This block must be at the very top of the file — nothing before the `---`

Save and close.

---

### Step 4.2 — Fix your requirements.txt
Open the file:
```cmd
notepad requirements.txt
```

Make sure there is **only one version of streamlit** listed. HF installs `streamlit==1.55.0` by default, so either:
- **Remove** the streamlit line entirely (HF will install it automatically), OR
- **Set it to:** `streamlit==1.55.0`

> ⚠️ Do NOT have both `streamlit==1.39.0` and `streamlit==1.55.0` — this causes a conflict error.

Save and close.

---

### Step 4.3 — Create a .gitignore file
```cmd
notepad .gitignore
```

Paste the following:
```
venv/
latex/
.vscode/
__pycache__/
*.pyc
.env
*.log
```

Save and close.

---

## 📦 PART 5 — TRACK LARGE & BINARY FILES WITH GIT LFS

HF rejects binary files (images, models, etc.) larger than 10MB unless they go through Git LFS.

### Step 5.1 — Track all common binary file types
```cmd
git lfs track "assets/*"
git lfs track "*.pkl"
git lfs track "*.h5"
git lfs track "*.pt"
git lfs track "*.bin"
git lfs track "*.joblib"
git lfs track "*.csv"
git lfs track "*.png"
git lfs track "*.jpg"
git lfs track "*.jpeg"
git lfs track "*.gif"
git lfs track "*.ico"
```

### Step 5.2 — Save the LFS tracking config
```cmd
git add .gitattributes
```

---

## 🚀 PART 6 — PUSH TO HUGGING FACE

### Step 6.1 — Set the remote URL with your token
This ensures you have write access:
```cmd
git remote set-url origin https://YOUR_USERNAME:YOUR_HF_TOKEN@huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
```

**Your specific command:**
```cmd
git remote set-url origin https://patrick078:YOUR_HF_TOKEN@huggingface.co/spaces/patrick078/crypto_app
```

---

### Step 6.2 — Stage all files
```cmd
git add .
```

---

### Step 6.3 — Commit
```cmd
git commit -m "Initial upload - Crypto forecasting app"
```

---

### Step 6.4 — Push to Hugging Face
```cmd
git push --force
```

You should see LFS objects uploading and then the Git objects being pushed. Wait for it to complete fully.

---

## 👀 PART 7 — MONITOR THE BUILD

### Step 7.1 — Check your Space
Go to: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`

### Step 7.2 — View Build Logs
Click the **"Logs"** tab at the top of your Space page.

You'll see two sections:
- **Build logs** — installing packages from `requirements.txt`
- **Container logs** — running your Streamlit app

The build typically takes **2–5 minutes**.

### Step 7.3 — Factory Reboot (if stuck)
If the Space is stuck loading with no logs:
1. Click the **three dots (⋮)** in the top right of your Space page
2. Click **"Factory reboot"**

---

## ❗ PART 8 — COMMON ERRORS & FIXES

### Error: Files larger than 10 MiB
```
Your push was rejected because it contains files larger than 10 MiB
```
**Fix:** The large file is still in Git history. Run:
```cmd
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch PATH/TO/FILE" --prune-empty --tag-name-filter cat -- --all
git push --force
```
Replace `PATH/TO/FILE` with the offending file shown in the error.

---

### Error: Binary files rejected
```
Your push was rejected because it contains binary files
```
**Fix:**
```cmd
git lfs track "*.png"
git add .gitattributes
git add assets/
git commit -m "Track binary files with LFS"
git push --force
```

---

### Error: Non-fast-forward
```
[rejected] main -> main (non-fast-forward)
```
**Fix:**
```cmd
git push --force
```

---

### Error: 403 / Read access but not write permissions
```
batch response: You have read access but not the required permissions
```
**Fix:** Your token doesn't have write access. Generate a new **Write** token at https://huggingface.co/settings/tokens then:
```cmd
git remote set-url origin https://YOUR_USERNAME:YOUR_NEW_TOKEN@huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git push --force
```

---

### Error: Streamlit version conflict
```
Cannot install streamlit==1.39.0 and streamlit==1.55.0
```
**Fix:** Open `requirements.txt` and remove or update the streamlit line to `streamlit==1.55.0`. Then:
```cmd
git add requirements.txt
git commit -m "Fix streamlit version"
git push
```

---

### Error: huggingface-cli not recognized
```
'huggingface-cli' is not recognized
```
**Fix:**
```cmd
pip install huggingface_hub
```
Or use the token in the remote URL directly (see Step 6.1).

---

## 🔄 PART 9 — MAKING FUTURE UPDATES

Whenever you make changes to your project and want to update HF:

```cmd
cd "D:\Solent University\Applied AI in Business (COM724)\crypto_app"
git add .
git commit -m "Describe your changes here"
git push
```

---

## ✅ FINAL CHECKLIST

- [ ] Git and Git LFS installed
- [ ] HF account created and Write token generated
- [ ] HF Space created with Streamlit SDK
- [ ] README.md has correct YAML header (no quotes around python_version)
- [ ] requirements.txt has no conflicting package versions
- [ ] `venv/`, `latex/`, `.vscode/` folders removed
- [ ] `.gitignore` created
- [ ] Binary files tracked with Git LFS
- [ ] Remote URL set with your token
- [ ] Successfully pushed with `git push --force`
- [ ] Build logs show successful build on HF
- [ ] App is live and running at your Space URL

---

*Guide prepared for: COM724 Assessment — Cryptocurrency Price Forecasting App*
*HF Space: https://huggingface.co/spaces/patrick078/crypto_app*
*GitHub Repo: https://github.com/parthaAtSolent/COM724--Assessment-AI*
