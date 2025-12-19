# 🧭 Project Compass | פרויקט המצפן

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> End-to-end intelligence data pipeline for automatic extraction and validation of geographic coordinates from Hebrew text reports.

**תהליך נתונים מקצה-לקצה לחילוץ ואימות אוטומטי של נקודות ציון (נ.צ) מדיווחים מודיעיניים בעברית.**

---

## 📋 Overview | סקירה

Project Compass is a complete data science pipeline that:
- ✅ Cleans and preprocesses 10,000 raw Hebrew intelligence reports
- 📊 Provides an interactive Plotly Dash dashboard for data exploration
- 🎯 Extracts geographic coordinates using NLP-based anchor word patterns
- 🏷️ Generates stratified sampling for human validation
- 📈 Evaluates model performance with detailed error analysis

**Key Achievement:** 89% accuracy with actionable insights for improvement.

---

## 🚀 Quick Start | התחלה מהירה

### Prerequisites | דרישות מקדימות
```bash
Python 3.11+
pip
```

### Installation | התקנה

1. **Clone the repository:**
```bash
git clone https://github.com/tehila99/compass-project.git
cd compass-project
```

2. **Create virtual environment:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## 📂 Project Structure | מבנה הפרויקט

```
compass-project/
│
├── data/
│   ├── raw/                          # Raw mission data (not included)
│   ├── processed/                    # Cleaned data
│   └── tagging/                      # Human-tagged samples
│
├── src/
│   ├── data_cleansing.py            # Stage 1: Data cleaning
│   ├── feature_engineering.py       # Stage 3: Coordinate extraction
│   ├── tagging_generator.py         # Stage 4: Sampling for validation
│   ├── performance_eval.py          # Stage 5: Performance evaluation
│   └── extract_errors.py            # Error analysis tool
│
├── dashboards/
│   └── compass_dashboard.py         # Stage 2: Interactive dashboard
│
├── outputs/
│   ├── reports/                     # Generated reports
│   └── visualizations/              # Performance charts
│
├── COMPASS_PROJECT_FULL_DOCUMENTATION.md  # Complete Hebrew documentation
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## 🎯 Pipeline Stages | שלבי התהליך

### Stage 1: Data Cleaning | ניקוי נתונים
```bash
python src/data_cleansing.py
```
- Removes duplicates, nulls, and invalid records
- Standardizes text encoding (UTF-8)
- **Output:** 7,322 clean reports

### Stage 2: Interactive Dashboard | דשבורד אינטראקטיבי
```bash
python dashboards/compass_dashboard.py
```
- **Access:** http://127.0.0.1:8050/
- 6 interactive visualizations
- Filters by sector, urgency, reliability
- Drill-down capabilities

### Stage 3: Coordinate Extraction | חילוץ נ.צ
```bash
python src/feature_engineering.py
```
- Pattern-based extraction using anchor words
- 5 regex patterns for different formats
- **Output:** 1,448 coordinates extracted (19.78%)

### Stage 4: Tagging Samples | יצירת מדגם תיוג
```bash
python src/tagging_generator.py
```
- Stratified sampling: 80 regular + 20 edge cases
- Balanced across sectors and urgency levels
- **Output:** `tagging_task.csv` ready for human validation

### Stage 5: Performance Evaluation | הערכת ביצועים
```bash
python src/performance_eval.py
```
- Confusion matrix (TP, FP, TN, FN)
- Performance metrics: 89.0% accuracy, 90.0% precision
- Error analysis by sector and reliability score
- **Key Finding:** 100% of False Positives come from D4 (low reliability) sources
- 📄 **Detailed errors file:** [`errors_analysis_11_cases.csv`](outputs/reports/errors_analysis_11_cases.csv) - All 11 errors with full details for manual inspection

---

## 📊 Key Results | תוצאות מרכזיות

| Metric | Value |
|--------|-------|
| **Accuracy** | 89.0% |
| **Precision** | 90.0% |
| **Recall** | 88.2% |
| **F1-Score** | 89.1% |

### Critical Insight 🔍
All 5 False Positives (100%) originate from **D4 reliability** reports ("requires verification"). This suggests implementing additional validation for D4-source extractions.

---

## 🛠️ Technologies | טכנולוגיות

- **Python 3.11** - Core language
- **Pandas 2.1.4** - Data manipulation
- **Plotly Dash 2.14.2** - Interactive dashboards
- **Regex** - Pattern matching for coordinate extraction
- **Matplotlib/Seaborn** - Static visualizations

---

## 📸 Visual Gallery | גלריית תמונות

### Stage 2: Dashboard Visualizations | ויזואליזציות דשבורד

<details>
<summary>📊 Click to view dashboard screenshots (6 visualizations)</summary>

#### 1. Timeline Analysis
![Timeline](outputs/visualizations/01_timeline.png)

#### 2. Urgency Distribution
![Urgency](outputs/visualizations/02_urgency_distribution.png)

#### 3. Reliability Scores
![Reliability Pie](outputs/visualizations/03_reliability_pie.png)
![Reliability Bar](outputs/visualizations/04_reliability_bar.png)

#### 4. Geographic Analysis
![Geographic Comparison](outputs/visualizations/05_geographic_comparison.png)
![Sector Geographic](outputs/visualizations/06_sector_geographic.png)

</details>

### Stage 5: Performance Evaluation | הערכת ביצועים

<details>
<summary>📈 Click to view performance charts (5 visualizations)</summary>

#### Confusion Matrix
![Confusion Matrix](outputs/visualizations/07_confusion_matrix.png)

#### Performance Metrics
![Performance Metrics](outputs/visualizations/08_performance_metrics.png)

#### Sector Performance
![Sector Performance](outputs/visualizations/09_sector_performance.png)

#### Prediction Distribution
![Prediction Distribution](outputs/visualizations/10_prediction_distribution.png)

#### Urgency Comparison
![Urgency Comparison](outputs/visualizations/11_urgency_comparison.png)

</details>

---

## 📖 Documentation | תיעוד

**Full Hebrew documentation:** [`COMPASS_PROJECT_FULL_DOCUMENTATION.md`](./COMPASS_PROJECT_FULL_DOCUMENTATION.md)

Includes:
- ✅ Detailed methodology for each stage
- ✅ Complete code explanations
- ✅ Visual examples and screenshots
- ✅ Performance analysis and recommendations

---

## 📝 License | רישיון

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author | יוצר

**Tehila Hager**

- 🔗 GitHub: [@tehila99](https://github.com/tehila99)
- 📂 Repository: [compass-project](https://github.com/tehila99/compass-project)
- 📧 Email: t5807679@gmail.com

---

## 📌 About This Project | אודות הפרויקט

This project was developed as part of an intelligence data analysis assignment, demonstrating:
- ✅ End-to-end data pipeline development
- ✅ NLP-based information extraction from Hebrew text
- ✅ Interactive data visualization with Plotly Dash
- ✅ Statistical analysis and model evaluation
- ✅ Professional documentation and code quality

---

**⭐ If you find this project interesting, please consider giving it a star!**
