# Hospital Readmission Analytics

**Python · SQL · Pandas · Matplotlib · ETL · EDA · Risk Stratification**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white&style=flat-square)
![SQL](https://img.shields.io/badge/SQL-SQLite-003B57?logo=sqlite&logoColor=white&style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white&style=flat-square)
![Dataset](https://img.shields.io/badge/Dataset-UCI%20Real%20Data-brightgreen?style=flat-square)

## Overview

End-to-end analytics project analysing 30-day hospital readmissions for diabetes
patients using real clinical data from 130 US hospitals (1999–2008).
101,766 actual patient encounters from the UCI Machine Learning Repository.

**Dataset:** [UCI Diabetes 130-US Hospitals — Kaggle](https://www.kaggle.com/datasets/brandao/diabetes)

## Dashboard Preview

![Executive Overview](04_dashboard_exports/01_executive_overview.png)
![Patient Demographics](04_dashboard_exports/02_patient_demographics.png)
![Clinical Risk Analysis](04_dashboard_exports/03_clinical_risk_analysis.png)

## Key Findings

- 30-day readmission rate: **8.80%** across 71,518 encounters
- Patients aged **70-90** have highest readmission rates (10%+)
- **Very High Risk** patients: 10.85% vs 1.98% for Low Risk
- Longer stays (8-14 days): **11.41% readmission rate**

## How to Run

```bash
pip3 install pandas numpy matplotlib
python3 02_notebooks/01_data_cleaning.py
python3 02_notebooks/02_eda_analysis.py
python3 02_notebooks/03_sql_analysis.py
```

## Author

**Hely Shah** — MS Computer Science, Hofstra University, May 2026
