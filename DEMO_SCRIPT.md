# DATAVYRN — Complete Interactive Demo & Evaluation Script

This step-by-step walkthrough guides reviewers, recruiters, and engineers through the complete end-to-end capabilities of **DATAVYRN**.

---

## 🚀 Scenario Overview
In this 5-minute evaluation, you will:
1. Review the operational workspace metrics on the **Overview** dashboard.
2. Inspect dataset health and automated quality scoring in **Datasets**.
3. Draw, inspect, and export object bounding boxes in the **Annotation Studio**.
4. Apply an audited transformation recipe in the **Data Preparation Studio**.
5. Configure and train a machine learning model in the **Training Lab**.
6. Inspect the confusion matrix and diagnostic curves in **Model Evaluation**.
7. Audit misclassified records in **Error Analysis**.
8. Benchmark experiment runs in the **Experiments Leaderboard**.
9. Generate a formal publication-ready PDF in **Reports**.

---

## Step 1: Overview Dashboard
1. Launch DATAVYRN (`.\run.bat`) and navigate to `http://localhost:8501`.
2. Inspect the **Top Metric Row**:
   - Verify *Active Projects*, *Total Datasets*, *Annotated Images*, *Completed Tasks*, and *Trained Models* reflect real database records.
3. Observe the **Recent Annotation Activity** live gallery showing thumbnails with labeled bounding boxes.
4. Review the **Annotation Review Quality Trend** showing historical QA agreement rates.

---

## Step 2: Datasets & Profiling
1. Click **Datasets** in the left navigation sidebar.
2. Select the seeded `Wine Recognition (v1)` dataset from the dropdown.
3. Review the **Data Quality Score (0–100)**:
   - Notice transparent mathematical penalties for missing cells, duplicates, cardinality, and outliers.
4. Explore the **Column Statistics Table**:
   - Inspect Mean, Std Dev, Min, Max, Skewness, and Null Counts.
5. Switch dataset type to **Computer Vision** to view image formats, resolutions, and annotation coverage.

---

## Step 3: Computer Vision Annotation Studio
1. Select **Annotation Studio** from the sidebar.
2. Choose an image from the queue (e.g. `test_img_0.png`).
3. Select an active class (e.g., `Defect`, `IC_Chip`, or `Capacitor`).
4. Draw a new bounding box on the canvas or click an existing box to inspect coordinates ($x, y, w, h$).
5. In the right-hand **Property Inspector**:
   - Adjust stroke width and box labels.
   - Click **Approve** or **Reject** to test the QA Review workflow.
6. Click **Export Annotations**:
   - Select **COCO JSON**, **YOLO TXT**, or **Pascal VOC XML** to download standardized export bundles.

---

## Step 4: Data Preparation Studio
1. Navigate to **Data Preparation**.
2. Select `Wine Recognition (v1)`.
3. In the **Transformation Recipe Builder**:
   - Add a missing-value strategy (e.g., *Impute with Median*).
   - Add a scaler (e.g., *StandardScaler*).
   - Click **Apply Recipe & Create New Version**.
4. Observe the lineage increment from `v1` to `v2` without modifying raw data.

---

## Step 5: Training Lab
1. Navigate to **Training Lab**.
2. Select the dataset and target variable (`target`).
3. Choose a model algorithm:
   - *Random Forest Classifier*
   - *Gradient Boosting Classifier*
   - *Logistic Regression*
   - *Support Vector Machine (SVM)*
4. Configure hyperparameters:
   - Estimators: `100`, Max Depth: `8`, Train/Test Split: `80/20`.
5. Click **Start Model Training**:
   - Watch the real-time progress bar.
   - Review validation accuracy, Precision, Recall, and F1 Score upon completion.

---

## Step 6: Model Evaluation
1. Select **Model Evaluation**.
2. Review the interactive **Confusion Matrix**:
   - Hover over cells to see True Positives, False Positives, and False Negatives.
3. Inspect the **ROC Curves** and **Precision-Recall Curves** with multiclass one-vs-rest AUC values.
4. Review the detailed tabular **Classification Report** broken down by class.

---

## Step 7: Error Analysis & Forensics
1. Click **Error Analysis** in the sidebar.
2. Select the latest experiment run.
3. Examine the **Misclassified Samples Table**:
   - View true target vs predicted label, along with model prediction confidence.
4. Review the **Confidence Distribution Histogram** comparing high-confidence correct predictions versus uncertain edge cases.

---

## Step 8: Experiments Leaderboard
1. Navigate to **Experiments**.
2. Review the leaderboard table sorting experiments by Accuracy, F1 Score, and Train Time.
3. Select two experiments to view a side-by-side **Hyperparameter & Metric Diff**.

---

## Step 9: Enterprise PDF Report Generation
1. Select **Reports** from the navigation sidebar.
2. Choose an experiment to generate a technical brief for.
3. Click **Generate PDF Audit Report**:
   - Open the generated PDF to review executive summaries, confusion matrix graphics, dataset quality metrics, and full model hyperparameters.
4. Click **Export CSV Summary** to download tabular benchmark archives.

---

## Step 10: System Diagnostics & Settings
1. Click **Settings** in the bottom left sidebar.
2. Check the real-time diagnostics:
   - Database health, SQLite version, active storage size, CPU/Memory status.
3. Verify the **Reset Demo Workspace** button re-seeds fresh data cleanly at any time.
