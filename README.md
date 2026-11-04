# DATAVYRN — Intelligent Data Annotation, Dataset Intelligence & Machine Learning Training Workbench

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit%201.40+-FF4B4B.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/database-SQLite%203%20%7C%20SQLAlchemy-003B57.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/tests-21%20Passed-success.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **DATAVYRN** is an end-to-end, locally executable AI workstation combining dataset intelligence, computer vision bounding-box annotation, tabular feature preprocessing, machine learning model compilation, validation analytics, root-cause error diagnostics, and experiment tracking into a single enterprise developer system.

---

## 1. Executive Summary & Problem Statement

Modern machine learning projects often suffer from fragmented tooling:
- **Disparate Ingestion:** Data profiling and sanity checks occur in isolated Jupyter notebooks or ad-hoc scripts.
- **Disconnected Labeling:** Image annotation requires third-party cloud tools or subscription SaaS platforms with privacy and air-gap constraints.
- **Data Leakage in Preprocessing:** Ad-hoc train/test transformations frequently leak validation statistics into training folds.
- **Fragmented Experiment Tracking:** Model training logs, hyperparameters, and confusion matrices are scattered across log files or external dashboards.
- **Untracked Error Remediation:** Error analysis and dataset correction remain disconnected from dataset versioning, leading to untracked manual edits.

**DATAVYRN** resolves this fragmentation by establishing an end-to-end, locally hosted, air-gapped workstation. All 10 core modules—from dataset ingestion and bounding box annotation to model compilation, confusion matrix forensics, and automated PDF audit reporting—operate over a unified SQLite database and file-backed version registry.

---

## 2. Key Capabilities & Module Architecture

### 📊 1. Overview Operations Dashboard
- **Workspace Metrics:** Real-time metrics calculated from database records: *Active Projects*, *Total Datasets*, *Annotated Images*, *Completed Tasks*, *Trained Models*, and *Top Benchmark*.
- **Visual Image Queue:** Live gallery of recent annotated images featuring bounding box overlays, class tags, and task statuses.
- **Annotation Review Quality Trend:** Chronological review agreement tracker based on verified QA decisions.
- **AI Analytics & Task Distribution:** Distribution donut chart (`Completed`, `In Progress`, `Needs Review`, `Pending`) and live confusion matrix preview.
- **Recent Experiments Feed:** Real-time leaderboard displaying primary metrics, training duration, timestamp, and status.

### 📁 2. Dataset Management & Profiling
- **Supported Formats:** Tabular (`.csv`, `.xlsx`, `.json`) and Computer Vision (`.jpg`, `.jpeg`, `.png`, `.webp`).
- **Tabular Profiler:** Calculates total rows/columns, missing cells, duplicate records, data types, statistical metrics (mean, std, min, median, max, skewness), and categorical cardinality.
- **Image Profiler:** Resolves image count, dimensions, formats, corruption detection, and annotated count.
- **Transparent Data Quality Score (0–100):** Mathematically audited score with documented deductions for missing values (up to 30 pts), duplicates (up to 20 pts), constant features (10 pts each), severe outliers (up to 15 pts), and target class imbalance.
- **Dataset Lineage & Versioning:** Every preprocessing operation increments the version (`v1`, `v2`, etc.) while preserving raw source data.

### 🎯 3. Image Annotation Studio
- **Three-Column Cyber Layout:**
  - *Left Queue:* Searchable image gallery with real-time status and class filters.
  - *Center Canvas:* Canvas drawing tool with zoom/fit, adjustable bounding box stroke widths, and active class color highlights.
  - *Right Property Inspector:* Real-time bounding box coordinate editor ($x, y, w, h$, confidence), class creator with custom color picker, and box deletion.
- **Multi-Format Export:**
  - **COCO JSON:** Standard format including `info`, `images`, `annotations` with bbox `[x, y, width, height]`, and `categories`.
  - **YOLO TXT:** Normalized bounding box format (`<class_id> <x_center> <y_center> <width> <height>`) with `classes.txt`.
  - **Pascal VOC XML:** Standard XML hierarchy with `<folder>`, `<filename>`, `<size>`, and `<bndbox>` coordinates.
- **QA Review System:** Official approval and rejection workflow with rejection reason logging and review audit history.

### 🧹 4. Data Preparation Studio
- **Data Cleaning Tools:**
  - Duplicate row removal.
  - Missing-value handling: row dropping, mean, median, mode, or constant value imputation.
  - Outlier filtering using the Interquartile Range (IQR) method ($Q1 - 1.5 \times IQR$ to $Q3 + 1.5 \times IQR$).
- **Feature Engineering:**
  - Encoders: Label Encoding and One-Hot Encoding.
  - Scalers: StandardScaler ($z = \frac{x - \mu}{\sigma}$) and MinMaxScaler ($x_{scaled} = \frac{x - x_{min}}{x_{max} - x_{min}}$).
  - Train/Test Split: Zero-leakage partitioning with configurable test size and random seed.
- **Traceable Transformation Recipe:** Records every step sequentially, applies them idempotently, and persists a new dataset version.

### ⚡ 5. Model Training Lab
- **Supported Algorithms:**
  - *Classification:* Random Forest Classifier, Gradient Boosting Classifier, Logistic Regression, Support Vector Machine (SVC).
  - *Regression:* Random Forest Regressor, Gradient Boosting Regressor, Linear Regression, Ridge/Lasso Regressor.
  - *Unsupervised:* K-Means Clustering.
- **Hyperparameter Controls:** Estimators, Max Depth, Learning Rate, Regularization ($C$, $\alpha$), Clusters ($k$).
- **Cross-Validation:** Automated $k$-fold cross-validation with fold score logging and standard deviation reporting.
- **Artifact Serialization:** Serialized using Joblib alongside training metadata, feature lists, and test set ground-truth arrays.

### 🏆 6. Model Evaluation Center
- **Interactive Confusion Matrix:** Color-scaled heatmap with absolute counts and normalized percentages.
- **Diagnostic Curves:**
  - Receiver Operating Characteristic (ROC) curves with multi-class One-vs-Rest AUC metrics.
  - Precision-Recall curves.
- **Detailed Metrics:** Precision, Recall, F1-Score, Accuracy, Support, Log Loss, and Brier Score.
- **Regression Diagnostics:** Predicted vs Actual scatter plots, residual distribution histograms, MAE, MSE, and $R^2$.

### 🔍 7. Error Analysis Workbench
- **Failure Identification:** Automated identification of misclassified samples and high-loss records.
- **Confidence Calibration:** Confidence distribution comparing correct predictions against incorrect edge cases.
- **Confused Class Pairs:** Identifies the most common false-positive/false-negative confusion patterns.
- **Guided Dataset Remediation:** One-click sample inspection with diagnostic notes and direct relabeling/row deletion to generate a corrected dataset version.

### 📈 8. Experiment Registry & Comparison
- **Leaderboard:** Comprehensive table of all historical model runs sorted by Accuracy, F1-Score, or $R^2$.
- **Side-by-Side Comparison:** Select any two models to diff hyperparameters, training durations, metrics, and dataset versions.
- **Artifact Inspection:** View model file sizes, parameters, and metadata directly.

### 📑 9. Reports & Technical Documentation
- **Executive PDF Generation:** Automated multi-page PDF compilation using ReportLab with high-resolution metrics, confusion matrices, and audit logs.
- **Tabular Export:** Single-click CSV and JSON exports of all benchmark experiments.

### ⚙️ 10. Settings & Diagnostics
- **Workspace Health:** SQLite connection checks, active database size, system RAM/CPU monitoring.
- **Demo Workspace Seeding:** One-click re-seeding of synthetic datasets, PCB inspection images, and baseline models.

---

## 3. End-to-End System Workflow

```
[RAW DATA INGESTION] (CSV / Excel / JSON / Images)
         │
         ▼
[DATASET MANAGEMENT & PROFILING] (Quality Score 0–100, Deductions, Stats)
         │
         ├─────────────────────────────────────────┐
         ▼                                         ▼
[DATA PREPARATION STUDIO]                [ANNOTATION STUDIO]
(Cleaning, Imputation, Scalers)          (Bounding Boxes, COCO/YOLO/VOC)
         │                                         │
         ▼                                         ▼
(Versioned Dataset v2)                   (QA Approval & Review)
         │
         ▼
[TRAINING LAB] (Scikit-Learn Execution, CV, Joblib Export)
         │
         ▼
[MODEL EVALUATION CENTER] (Heatmaps, ROC Curves, Residuals)
         │
         ▼
[ERROR ANALYSIS WORKBENCH] (Identify Misclassifications & Edge Cases)
         │
         ▼ (Apply Guided Relabeling / Corrections)
[NEW DATASET VERSION GENERATED] ──► (Retrain & Benchmark)
         │
         ▼
[EXPERIMENT REGISTRY & COMPARISON] (Leaderboard & Diff)
         │
         ▼
[TECHNICAL AUDIT REPORTING] (PDF / CSV / JSON Export)
```

---

## 4. Visual Design System

DATAVYRN is engineered to match modern, production-grade developer tooling standards (Vercel, Linear, GitHub Enterprise):

| Element | Specification | Role |
| :--- | :--- | :--- |
| **Surface Background** | `#f8fafc` | Crisp, clean neutral base |
| **Sidebar & Cards** | `#ffffff` | High-contrast elevated surfaces |
| **Borders** | `#e2e8f0` | Subtle, low-opacity neutral borders |
| **Primary Accent** | `#2563eb` | Developer blue for primary actions and active links |
| **Primary Text** | `#0f172a` | High-contrast typography (`Inter` / `Plus Jakarta Sans`) |
| **Muted Text** | `#64748b` | Contextual subtitles and metadata |
| **Monospace Font** | `JetBrains Mono` / `Fira Code` | Numerical metrics, timestamps, and model IDs |
| **Success Color** | `#059669` | High accuracy, approved QA tasks, clean health checks |
| **Warning Color** | `#d97706` | Pending reviews, moderate quality penalties |
| **Danger Color** | `#dc2626` | Rejected annotations, misclassifications |

---

## 5. Technology Stack

- **Frontend & Workstation UI:** Streamlit 1.40+, Custom Enterprise CSS, Plotly Express & Graph Objects, Streamlit Drawable Canvas.
- **Machine Learning & Preprocessing:** Scikit-Learn, Pandas, NumPy, SciPy, Joblib.
- **Image Processing & Computer Vision:** Pillow (PIL), OpenCV (`cv2`).
- **Database & Persistence:** SQLite 3, SQLAlchemy 2.0 (Thread-safe scoped sessions).
- **Report Compilation:** ReportLab (Flowable PDF generation).
- **Automated Testing:** Pytest.

---

## 6. Directory Structure

```
DATAVYRN/
├── app.py                      # Application entrypoint, routing, global styling & session state
├── config.py                   # System paths, color tokens, supported formats
├── requirements.txt            # Python package dependencies
├── README.md                   # Comprehensive documentation & architecture
├── QUICKSTART.md               # 60-second quickstart guide
├── DEMO_SCRIPT.md              # Interactive step-by-step evaluation walkthrough
├── LICENSE                     # MIT License
├── setup.bat                   # Windows automated environment & dependency installer
├── run.bat                     # Windows application launcher
├── test.bat                    # Windows automated pytest suite runner
├── pytest.ini                  # Pytest configuration
│
├── core/                       # Decoupled Business & ML Logic
│   ├── __init__.py
│   ├── database.py             # SQLite connection, engine & scoped session factory
│   ├── models.py               # SQLAlchemy models (Project, Dataset, Version, Annotation, Experiment, etc.)
│   ├── dataset_manager.py      # File parsing, tabular/image profiling, quality scoring, versioning
│   ├── annotation_engine.py    # Bounding boxes, IoU calculations, QA review, COCO/YOLO/VOC exports
│   ├── preprocessing.py        # Tabular cleaning, missing value imputation, scaling, feature engineering
│   ├── training_engine.py      # ML model training, cross-validation, metric calculation, Joblib persistence
│   ├── evaluation_engine.py    # Evaluation analytics, ROC curves, residuals, feature importance
│   ├── error_analyzer.py       # Misclassification detection, error diagnostics, guided dataset correction
│   ├── experiment_manager.py   # Persistent experiment registry, multi-model comparisons & rankings
│   ├── report_generator.py     # PDF (ReportLab), CSV, JSON technical report generation
│   └── demo_data.py            # Wine dataset ingestion, baseline models, synthetic image set
│
├── components/                 # Reusable UI Components
│   ├── __init__.py
│   ├── navigation.py           # Enterprise sidebar with brand mark, project selector & active route
│   ├── header.py               # Top header with breadcrumb navigation & status badges
│   ├── metric_cards.py         # Structured developer KPI cards
│   ├── charts.py               # Plotly light theme chart builders (heatmaps, ROC, bars, donuts)
│   └── annotation_canvas.py    # Canvas drawing integration & bounding box visualizer
│
├── pages_app/                  # Application Page Views
│   ├── __init__.py
│   ├── overview.py             # Executive operations dashboard
│   ├── datasets.py             # Dataset management, profiling & quality assessment
│   ├── annotation_studio.py    # Interactive image annotation workspace with multi-format export
│   ├── data_preparation.py     # Tabular preprocessing & feature engineering studio
│   ├── training_lab.py         # ML model training lab with live execution & hyperparameter controls
│   ├── evaluation.py           # Model evaluation center with interactive heatmaps & curves
│   ├── error_analysis.py       # Detailed error inspector and guided correction workflow
│   ├── experiments.py          # Persistent experiment registry & multi-model comparison
│   ├── reports.py              # Exportable PDF, CSV, JSON analytics reports
│   └── settings.py             # System settings, project management & demo reset
│
├── storage/                    # Local Persistent Storage
│   ├── database/               # datavyrn.db (SQLite database)
│   ├── datasets/               # Ingested and versioned tabular files (.csv)
│   ├── images/                 # Ingested and synthetic image datasets (.png, .jpg)
│   ├── annotations/            # Annotation metadata
│   ├── models/                 # Serialized Joblib model artifacts (.joblib, test_data.json)
│   ├── reports/                # Generated technical PDF reports
│   └── exports/                # Exported COCO JSON, YOLO TXT, Pascal VOC XML bundles
│
├── assets/
│   └── css/
│       └── style.css           # Custom developer CSS stylesheet (Pure Light Theme)
│
└── tests/                      # Automated Test Suite (21 Tests)
    ├── __init__.py
    ├── test_datasets.py        # Tests for dataset profiling and quality scoring
    ├── test_preprocessing.py   # Tests for tabular transformations & versioning
    ├── test_training.py        # Tests for model training, metrics, persistence
    ├── test_evaluation.py      # Tests for confusion matrix, ROC-AUC, residuals
    ├── test_annotations.py     # Tests for annotation storage, review, and COCO/YOLO/VOC export
    └── test_reports.py         # Tests for PDF, CSV, and JSON report generation
```

---

## 7. Windows Installation & Execution Guide

### Prerequisites
- **OS:** Windows 10 or Windows 11 (64-bit).
- **Python:** Python 3.10, 3.11, or 3.12 (Python 3.12 64-bit recommended).

### Option A: One-Click Windows Setup (Recommended)

1. Open File Explorer and navigate to `DATAVYRN`.
2. Double-click `setup.bat`. This automatically:
   - Creates a virtual environment in `.venv`.
   - Upgrades pip.
   - Installs all dependencies from `requirements.txt`.
3. Double-click `run.bat`.
4. Your default browser will launch DATAVYRN at **`http://localhost:8501`**.

---

### Option B: Manual Command-Line Setup (PowerShell / Command Prompt)

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd DATAVYRN
   ```

2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the required dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Launch DATAVYRN:
   ```powershell
   streamlit run app.py --server.port=8501 --theme.base="light"
   ```

6. Open `http://localhost:8501` in your browser.

---

## 8. Automated Testing

DATAVYRN includes an automated test suite covering all core operations.

To run the automated tests on Windows:
```powershell
.\test.bat
```
Or directly using pytest:
```powershell
.\.venv\Scripts\python.exe -m pytest -v tests/
```

### Test Coverage Highlights (21 Passed):
- `test_datasets.py`: Tabular ingestion, feature profiling, missing cell detection, duplicate detection, transparent quality score deduction calculations, versioning $v1 \rightarrow v2$ isolation.
- `test_preprocessing.py`: Duplicate removal, mean/mode imputation, label encoding, one-hot encoding, standard scaling, and zero-leakage train/test partitioning.
- `test_training.py`: Random Forest Classifier, Logistic Regression, and K-Means training, timing verification, accuracy/F1 evaluation, and Joblib artifact serialization.
- `test_evaluation.py`: Multi-class One-vs-Rest ROC curve derivation, AUC calculations, regression residuals, and maximum absolute error computation.
- `test_annotations.py`: IoU bounding box calculations, multi-box persistence, QA review status transitions, and exports to COCO JSON, YOLO TXT, and Pascal VOC XML.
- `test_reports.py`: ReportLab PDF document compilation, table formatting, and CSV/JSON metadata exports.

---

## 9. Interactive Evaluation Walkthrough

Follow the step-by-step demo guide in [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) to evaluate each module in under 5 minutes.

---

## 10. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 **Ragu Ram P**. All rights reserved.
