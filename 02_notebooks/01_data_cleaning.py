"""
Hospital Readmission Analytics
Step 1: Data Cleaning and Preparation
Author: Hely Shah
Dataset: UCI Diabetes 130-US Hospitals (1999-2008)
Source: https://www.kaggle.com/datasets/brandao/diabetes

This script cleans the raw diabetic_data.csv and produces
analytics-ready tables for SQL analysis and dashboarding.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────
BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW       = os.path.join(BASE, "01_data", "raw")
PROCESSED = os.path.join(BASE, "01_data", "processed")
os.makedirs(PROCESSED, exist_ok=True)

print("=" * 60)
print("HOSPITAL READMISSION ANALYTICS — DATA CLEANING")
print("=" * 60)

# ── Load raw data ──────────────────────────────────────────────
df = pd.read_csv(os.path.join(RAW, "diabetic_data.csv"))
print(f"\nRaw data loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ── Step 1: Replace '?' with NaN ──────────────────────────────
print("\n[Step 1] Replacing missing value markers ('?') with NaN...")
df.replace("?", np.nan, inplace=True)
print(f"  Columns with nulls after replacement:")
null_counts = df.isnull().sum()
for col, n in null_counts[null_counts > 0].items():
    pct = n / len(df) * 100
    print(f"    {col}: {n:,} nulls ({pct:.1f}%)")

# ── Step 2: Drop columns with excessive missing data ──────────
print("\n[Step 2] Dropping columns with >40% missing data...")
threshold = 0.40
cols_before = df.shape[1]
high_null_cols = [c for c in df.columns if df[c].isnull().mean() > threshold]
df.drop(columns=high_null_cols, inplace=True)
print(f"  Dropped: {high_null_cols}")
print(f"  Columns reduced: {cols_before} → {df.shape[1]}")

# ── Step 3: Remove duplicates (keep first encounter per patient)
print("\n[Step 3] Removing duplicate patient encounters...")
before = len(df)
df.drop_duplicates(subset=["patient_nbr"], keep="first", inplace=True)
print(f"  Rows removed: {before - len(df):,} | Remaining: {len(df):,}")

# ── Step 4: Create readmission binary flag ─────────────────────
print("\n[Step 4] Engineering target variable: readmitted_30days...")
df["readmitted_30days"] = (df["readmitted"] == "<30").astype(int)
readmit_rate = df["readmitted_30days"].mean() * 100
print(f"  30-day readmission rate: {readmit_rate:.2f}%")
print(f"  Readmitted within 30 days: {df['readmitted_30days'].sum():,}")
print(f"  Not readmitted / >30 days: {(df['readmitted_30days']==0).sum():,}")

# ── Step 5: Map age groups to numeric midpoints ────────────────
print("\n[Step 5] Mapping age bands to numeric values...")
age_map = {
    "[0-10)": 5,  "[10-20)": 15, "[20-30)": 25, "[30-40)": 35,
    "[40-50)": 45, "[50-60)": 55, "[60-70)": 65, "[70-80)": 75,
    "[80-90)": 85, "[90-100)": 95
}
df["age_numeric"] = df["age"].map(age_map)
print(f"  Age range: {df['age_numeric'].min()} to {df['age_numeric'].max()}")

# ── Step 6: Map admission type IDs to labels ───────────────────
print("\n[Step 6] Mapping admission type IDs to readable labels...")
admission_map = {1:"Emergency", 2:"Urgent", 3:"Elective",
                 4:"Newborn", 5:"Not Available", 7:"Trauma Center", 8:"Not Mapped"}
df["admission_type"] = df["admission_type_id"].map(admission_map).fillna("Other")

# ── Step 7: Classify primary diagnosis into categories ─────────
print("\n[Step 7] Classifying ICD-9 diagnosis codes into categories...")
def classify_diagnosis(code):
    if pd.isnull(code):
        return "Unknown"
    try:
        c = str(code)
        if c.startswith("V") or c.startswith("E"):
            return "External/Other"
        val = float(c)
        if 390 <= val <= 459 or val == 785:
            return "Circulatory"
        elif 460 <= val <= 519 or val == 786:
            return "Respiratory"
        elif 520 <= val <= 579 or val == 787:
            return "Digestive"
        elif 250 <= val <= 250.99:
            return "Diabetes"
        elif 800 <= val <= 999:
            return "Injury"
        elif 710 <= val <= 739:
            return "Musculoskeletal"
        elif 580 <= val <= 629 or val == 788:
            return "Genitourinary"
        elif 140 <= val <= 239:
            return "Neoplasms"
        else:
            return "Other"
    except:
        return "Unknown"

df["diag_1_category"] = df["diag_1"].apply(classify_diagnosis)
print(f"  Diagnosis categories created: {df['diag_1_category'].value_counts().to_dict()}")

# ── Step 8: Insulin usage simplified ──────────────────────────
print("\n[Step 8] Simplifying medication/insulin fields...")
df["insulin_used"] = df["insulin"].apply(
    lambda x: "Yes" if x in ["Up","Down","Steady"] else "No"
)
df["diabetes_med_count"] = df[[
    "metformin","glipizide","glyburide","pioglitazone",
    "rosiglitazone","insulin"
]].apply(lambda row: sum(1 for v in row if v not in ["No", np.nan]), axis=1)

# ── Step 9: Length of stay band ───────────────────────────────
print("\n[Step 9] Creating length of stay bands...")
df["los_band"] = pd.cut(
    df["time_in_hospital"],
    bins=[0, 2, 4, 7, 14, 100],
    labels=["1-2 days", "3-4 days", "5-7 days", "8-14 days", "14+ days"]
)

# ── Step 10: Risk score (simple composite) ────────────────────
print("\n[Step 10] Creating composite readmission risk score...")
df["risk_score"] = (
    (df["number_inpatient"] * 2) +
    (df["number_emergency"] * 1.5) +
    (df["number_diagnoses"] * 0.5) +
    (df["num_medications"] * 0.3) +
    (df["time_in_hospital"] * 0.2)
).round(2)

risk_bins = [0, 2, 5, 10, 1000]
risk_labels = ["Low Risk", "Medium Risk", "High Risk", "Very High Risk"]
df["risk_category"] = pd.cut(df["risk_score"], bins=risk_bins, labels=risk_labels)

# ── Step 11: Fill remaining nulls ─────────────────────────────
print("\n[Step 11] Filling remaining nulls...")
df["race"] = df["race"].fillna("Unknown")
df["gender"] = df["gender"].replace("Unknown/Invalid", "Unknown")

# ── Step 12: Select final columns for analytics ────────────────
print("\n[Step 12] Selecting analytics-ready columns...")
analytics_cols = [
    "encounter_id", "patient_nbr",
    "race", "gender", "age", "age_numeric",
    "admission_type", "admission_type_id",
    "discharge_disposition_id",
    "time_in_hospital", "los_band",
    "num_lab_procedures", "num_procedures",
    "num_medications", "diabetes_med_count",
    "number_outpatient", "number_emergency", "number_inpatient",
    "number_diagnoses",
    "diag_1", "diag_1_category",
    "insulin", "insulin_used",
    "change", "diabetesMed",
    "readmitted", "readmitted_30days",
    "risk_score", "risk_category"
]
df_clean = df[analytics_cols].copy()

# ── Save outputs ───────────────────────────────────────────────
print("\n[Saving] Writing cleaned files...")

# Main analytics dataset
out1 = os.path.join(PROCESSED, "cleaned_diabetes.csv")
df_clean.to_csv(out1, index=False)
print(f"  cleaned_diabetes.csv → {len(df_clean):,} rows")

# Readmission summary by age group
age_summary = df_clean.groupby("age").agg(
    total_encounters  =("encounter_id", "count"),
    readmitted_30days =("readmitted_30days", "sum"),
    avg_time_in_hospital=("time_in_hospital", "mean"),
    avg_num_medications =("num_medications", "mean"),
    avg_num_procedures  =("num_procedures", "mean"),
).reset_index()
age_summary["readmission_rate_pct"] = (
    age_summary["readmitted_30days"] / age_summary["total_encounters"] * 100
).round(2)
age_summary["avg_time_in_hospital"] = age_summary["avg_time_in_hospital"].round(2)
age_summary["avg_num_medications"]  = age_summary["avg_num_medications"].round(2)
age_summary.to_csv(os.path.join(PROCESSED, "readmission_by_age.csv"), index=False)
print(f"  readmission_by_age.csv")

# Readmission by diagnosis category
diag_summary = df_clean.groupby("diag_1_category").agg(
    total_encounters  =("encounter_id", "count"),
    readmitted_30days =("readmitted_30days", "sum"),
    avg_time_in_hospital=("time_in_hospital", "mean"),
    avg_medications   =("num_medications", "mean"),
).reset_index()
diag_summary["readmission_rate_pct"] = (
    diag_summary["readmitted_30days"] / diag_summary["total_encounters"] * 100
).round(2)
diag_summary["avg_time_in_hospital"] = diag_summary["avg_time_in_hospital"].round(2)
diag_summary.to_csv(os.path.join(PROCESSED, "readmission_by_diagnosis.csv"), index=False)
print(f"  readmission_by_diagnosis.csv")

# Risk stratification summary
risk_summary = df_clean.groupby("risk_category", observed=True).agg(
    total_patients   =("encounter_id", "count"),
    readmitted_30days=("readmitted_30days", "sum"),
    avg_los          =("time_in_hospital", "mean"),
    avg_medications  =("num_medications", "mean"),
    avg_risk_score   =("risk_score", "mean"),
).reset_index()
risk_summary["readmission_rate_pct"] = (
    risk_summary["readmitted_30days"] / risk_summary["total_patients"] * 100
).round(2)
risk_summary.to_csv(os.path.join(PROCESSED, "risk_stratification.csv"), index=False)
print(f"  risk_stratification.csv")

# Admission type summary
adm_summary = df_clean.groupby("admission_type").agg(
    total_encounters  =("encounter_id", "count"),
    readmitted_30days =("readmitted_30days", "sum"),
    avg_time_in_hospital=("time_in_hospital", "mean"),
).reset_index()
adm_summary["readmission_rate_pct"] = (
    adm_summary["readmitted_30days"] / adm_summary["total_encounters"] * 100
).round(2)
adm_summary.to_csv(os.path.join(PROCESSED, "readmission_by_admission_type.csv"), index=False)
print(f"  readmission_by_admission_type.csv")

# Medication impact
med_summary = df_clean.groupby("insulin_used").agg(
    total_patients   =("encounter_id", "count"),
    readmitted_30days=("readmitted_30days", "sum"),
    avg_medications  =("num_medications", "mean"),
    avg_los          =("time_in_hospital", "mean"),
).reset_index()
med_summary["readmission_rate_pct"] = (
    med_summary["readmitted_30days"] / med_summary["total_patients"] * 100
).round(2)
med_summary.to_csv(os.path.join(PROCESSED, "insulin_impact.csv"), index=False)
print(f"  insulin_impact.csv")

# LOS band summary (for Power BI)
los_summary = df_clean.groupby("los_band", observed=True).agg(
    total_encounters  =("encounter_id", "count"),
    readmitted_30days =("readmitted_30days", "sum"),
    avg_medications   =("num_medications", "mean"),
).reset_index()
los_summary["readmission_rate_pct"] = (
    los_summary["readmitted_30days"] / los_summary["total_encounters"] * 100
).round(2)
los_summary.to_csv(os.path.join(PROCESSED, "readmission_by_los.csv"), index=False)
print(f"  readmission_by_los.csv")

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETE")
print(f"Final dataset: {len(df_clean):,} rows x {len(df_clean.columns)} columns")
print(f"30-day readmission rate: {df_clean['readmitted_30days'].mean()*100:.2f}%")
print(f"Output folder: {PROCESSED}")
print("=" * 60)
