# DATAVYRN — Quick Start Guide

Get **DATAVYRN** running locally on Windows in under 60 seconds.

---

## ⚡ 1. Automated Quick Start (Windows)

### Step 1: Run Environment Setup
Double-click `setup.bat` (or run in PowerShell/CMD):
```powershell
.\setup.bat
```
*This automatically creates the Python virtual environment (`.venv`), upgrades pip, and installs all required dependencies from `requirements.txt`.*

### Step 2: Launch the Workbench
Double-click `run.bat` (or execute in PowerShell/CMD):
```powershell
.\run.bat
```
The application opens automatically in your default browser at:
👉 **`http://localhost:8501`**

---

## 🧪 2. Run Automated Verification Tests

To verify all 21 unit, integration, and machine learning pipeline tests:
```powershell
.\test.bat
```
Or directly via the virtual environment:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

---

## 🛠️ 3. Manual Installation (Cross-Platform)

If you prefer to configure the environment manually or are running on macOS/Linux:

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 (Python 3.12 64-bit recommended)
- Git

### 2. Clone Repository
```bash
git clone https://github.com/raguramrrp/DATAVYRN.git
cd DATAVYRN
```

### 3. Create & Activate Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Launch Workbench
```bash
streamlit run app.py --server.port=8501 --theme.base="light"
```

---

## 📂 4. Default Demo Workspace

Upon first launch, DATAVYRN automatically initializes:
- **Default Project:** `Project Alpha: Model Workbench`
- **Tabular Datasets:** Built-in Wine Recognition benchmarking dataset (`v1`).
- **Computer Vision Dataset:** 6 synthetic inspection images featuring PCB circuits, IC chips, capacitors, and annotated solder defects.
- **Trained Baseline Model:** An audited Random Forest classifier with confusion matrix, classification report, and ROC curves ready for evaluation.
- **Local SQLite Database:** Initialized at `storage/database/datavyrn.db`.

---

## 🧭 5. Module Navigation Overview

| Module | Purpose | Key Actions |
| :--- | :--- | :--- |
| **Overview** | Executive Operations & Workspace KPIs | View active projects, models, dataset metrics, and recent annotations |
| **Datasets** | Data Ingestion & Quality Profiling | Upload CSV/Excel/Images, view transparent Quality Score (0–100) |
| **Annotation Studio** | Computer Vision Labeling | Draw bounding boxes, assign classes, review QA status, export COCO/YOLO/VOC |
| **Data Preparation** | Pipeline & Feature Engineering | Clean data, impute missing values, scale features, create versioned datasets |
| **Training Lab** | ML Model Training & Hyperparameters | Select target, configure splits, train Random Forest, Logistic Reg, SVM, etc. |
| **Model Evaluation** | Performance & Metric Diagnostics | Analyze confusion matrix, ROC-AUC, Precision-Recall, classification reports |
| **Error Analysis** | Failure Forensics & Misclassifications | Inspect misclassified records, confidence histograms, feature attribution |
| **Experiments** | Leaderboard & Experiment Tracking | Compare runs side-by-side, sort by accuracy/F1/R², inspect hyperparameters |
| **Reports** | Enterprise Reporting & Export | Generate executive PDF reports, export JSON and CSV benchmark data |
| **Settings** | Diagnostics & Workspace Maintenance | Health checks, database statistics, one-click demo data reset |

---

## ❓ 6. Troubleshooting

- **Port in use:** If port 8501 is busy, run:
  ```powershell
  .\.venv\Scripts\streamlit.exe run app.py --server.port=8502
  ```
- **Permission issues with virtual environment activation on Windows:**
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Database Reset:** If you want to reset demo data, navigate to **Settings** in the left sidebar and click **Reset Demo Workspace**.
