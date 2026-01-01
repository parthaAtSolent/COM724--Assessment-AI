Absolutely 👍
Below is a **revised, professional `README.md`** that:

✅ Adds **project structure at the beginning**
✅ Clearly states **`assets/` lives in a different branch**
✅ Explicitly mentions **NO README inside the LaTeX folder**
✅ Includes **manual LaTeX compilation steps (clearly explained)**
✅ Uses **clean comments + professional emojis**
✅ Is ready for **GitHub / university submission**

---

````markdown
# 📝 LaTeX Report Writing in VS Code

This repository documents how to set up **LaTeX for academic report writing using Visual Studio Code**, including compiler installation, editor configuration, custom fonts, and manual compilation.  
The workflow is designed for **LuaLaTeX / XeLaTeX** and supports professional academic writing standards.

---

## 📂 Project Structure

The repository follows a **clean, modular structure** to separate source code and large assets.

```text
.
├── latex/
│   └── report/
│       └── main.tex
│
└── assets/   (separate branch)
    ├── figures/
    ├── charts/
    └── dashboards/
````

### 📌 Important Notes

* The **`assets/` directory is maintained in a separate branch** to keep the main branch lightweight
* The **LaTeX source folder does NOT contain a README**
* All documentation is maintained at the **repository root level**
* Figures are referenced in LaTeX via relative paths when needed

---

## 📦 Prerequisites

To compile LaTeX documents successfully in VS Code, the following tools must be installed.

---

### 1️⃣ Install MiKTeX (LaTeX Distribution)

MiKTeX provides the LaTeX engine and manages required packages.

🔗 **Download Link:**
[https://miktex.org/download](https://miktex.org/download)

✅ **Installation Tips:**

* Enable **“Install missing packages on-the-fly”**
* Restart your system after installation
* Keep MiKTeX updated via the MiKTeX Console

---

### 2️⃣ Install LaTeX Workshop (VS Code Extension)

LaTeX Workshop enables:

* One-click compilation
* PDF preview
* Error highlighting
* IntelliSense for LaTeX

📌 **Steps:**

1. Open **Visual Studio Code**
2. Go to **Extensions** (`Ctrl + Shift + X`)
3. Search for **LaTeX Workshop**
4. Click **Install**

---

### 3️⃣ Install Perl (Required Dependency)

Some LaTeX tools and package scripts require Perl.

🔗 **Download Link:**
[https://strawberryperl.com/](https://strawberryperl.com/)

✅ **Recommended Version:**
**Strawberry Perl (64-bit)**

📌 **Important:**
Ensure Perl is added to the **system PATH** during installation.

---

## 🖋️ Adding a Custom Font in LaTeX (VS Code)

To use system-installed fonts (e.g., *Trebuchet MS*), **LuaLaTeX or XeLaTeX is mandatory**.

---

### 📄 LaTeX Code Snippet (Main Font Configuration)

```latex
% =========================================
% Font configuration (LuaLaTeX or XeLaTeX REQUIRED)
% =========================================
\usepackage{fontspec}

% Set main document font (must be installed on OS)
\setmainfont{Trebuchet MS}
```

📌 **Key Notes:**

* The font must already be installed on your operating system
* `pdflatex` ❌ will NOT work with `fontspec`
* Always compile using **lualatex** or **xelatex**

---

## ▶️ Compiling the LaTeX Document Manually

Manual compilation is recommended for:

* Debugging errors
* Verifying font loading
* Ensuring reproducibility before submission

---

### 📍 Step 1: Navigate to the Report Directory

```bash
cd latex/report
```

---

### 📍 Step 2: Compile Using LuaLaTeX

```bash
lualatex main.tex
```

📄 This command generates:

* `main.pdf` (final report)
* `.aux`, `.log`, `.toc` and other helper files

---

### 🔁 (Optional) Recompile for References or TOC

If your document contains:

* Table of contents
* Cross-references
* Citations

Run LuaLaTeX **twice**:

```bash
lualatex main.tex
lualatex main.tex
```

---

## ⚙️ Recommended VS Code Compiler Settings

Ensure LaTeX Workshop uses **LuaLaTeX**:

* Click the **compiler selector** in the VS Code status bar
* Choose **LuaLaTeX**
* Avoid `pdfLaTeX`

This ensures compatibility with:

* `fontspec`
* Unicode fonts
* Modern typography

## 🎓 Best Practices for Academic LaTeX Projects

✔ Use **LuaLaTeX** for modern font support
✔ Keep figures in a **separate assets branch**
✔ Maintain a clean directory hierarchy
✔ Compile manually before submission
✔ Use Git for version control and traceability


This setup ensures **professional, reproducible, and submission-ready academic reports**.

---

📌 **Author:** Partha Pratim Mazumder
📘 **Module:** Data Analytics and Visualisation (COM725)
🏫 **Institution:** Solent University

