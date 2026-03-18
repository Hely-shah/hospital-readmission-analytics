"""
Hospital Readmission Analytics
Step 2: Exploratory Data Analysis & Business Insights
Author: Hely Shah
Dataset: UCI Diabetes 130-US Hospitals (1999-2008)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE, "01_data", "processed")
OUT       = os.path.join(BASE, "04_dashboard_exports")
os.makedirs(OUT, exist_ok=True)

# Colors
C_BLUE   = "#1D4ED8"
C_RED    = "#DC2626"
C_GREEN  = "#16A34A"
C_AMBER  = "#D97706"
C_TEAL   = "#0891B2"
C_PURPLE = "#7C3AED"
C_GRAY   = "#64748B"
BG       = "#F8FAFC"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.facecolor": BG,
    "figure.facecolor": "white",
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# Load data
df = pd.read_csv(os.path.join(PROCESSED, "cleaned_diabetes.csv"))
age_df  = pd.read_csv(os.path.join(PROCESSED, "readmission_by_age.csv"))
diag_df = pd.read_csv(os.path.join(PROCESSED, "readmission_by_diagnosis.csv"))
risk_df = pd.read_csv(os.path.join(PROCESSED, "risk_stratification.csv"))
los_df  = pd.read_csv(os.path.join(PROCESSED, "readmission_by_los.csv"))
adm_df  = pd.read_csv(os.path.join(PROCESSED, "readmission_by_admission_type.csv"))
ins_df  = pd.read_csv(os.path.join(PROCESSED, "insulin_impact.csv"))

print("=" * 60)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 60)
print(f"Total patient encounters: {len(df):,}")
print(f"30-day readmission rate:  {df['readmitted_30days'].mean()*100:.2f}%")
print(f"Average length of stay:   {df['time_in_hospital'].mean():.2f} days")
print(f"Average medications:      {df['num_medications'].mean():.2f}")

# ════════════════════════════════════════════════════════════════
# CHART 1 — EXECUTIVE OVERVIEW (KPI DASHBOARD)
# ════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(18, 12), facecolor="white")
fig.suptitle(
    "Hospital Readmission Analytics — Executive Overview  |  UCI Diabetes Dataset (130 US Hospitals, 1999–2008)",
    fontsize=14, fontweight="bold", color="#1E293B", y=0.99
)

# KPI cards
kpis = [
    ("Total Encounters",      f"{len(df):,}",                               C_BLUE),
    ("30-Day Readmissions",   f"{df['readmitted_30days'].sum():,}",          C_RED),
    ("Readmission Rate",      f"{df['readmitted_30days'].mean()*100:.2f}%",  C_AMBER),
    ("Avg Length of Stay",    f"{df['time_in_hospital'].mean():.1f} days",   C_TEAL),
    ("Avg Medications",       f"{df['num_medications'].mean():.1f}",         C_PURPLE),
    ("Avg Lab Procedures",    f"{df['num_lab_procedures'].mean():.1f}",      C_GRAY),
]
for i, (label, val, col) in enumerate(kpis):
    ax = fig.add_axes([0.02 + i * 0.163, 0.84, 0.145, 0.12])
    ax.set_facecolor(col)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.text(0.5, 0.60, val, ha="center", va="center",
            fontsize=19, fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.20, label, ha="center", va="center",
            fontsize=8.5, color="white", alpha=0.92, transform=ax.transAxes)

# Readmission by age group
ax1 = fig.add_axes([0.02, 0.46, 0.44, 0.34])
age_order = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
             "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]
age_plot = age_df.set_index("age").reindex(age_order).reset_index()
bar_cols = [C_RED if v > 10 else C_BLUE for v in age_plot["readmission_rate_pct"]]
bars = ax1.bar(age_plot["age"], age_plot["readmission_rate_pct"], color=bar_cols, alpha=0.85)
ax1.axhline(df["readmitted_30days"].mean() * 100, color=C_AMBER, linestyle="--",
            lw=1.5, label=f"Overall avg {df['readmitted_30days'].mean()*100:.1f}%")
ax1.set_title("30-Day Readmission Rate by Age Group")
ax1.set_ylabel("Readmission Rate (%)")
ax1.set_xlabel("Age Group")
ax1.tick_params(axis="x", rotation=30)
ax1.legend(fontsize=8)
for bar in bars:
    h = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
             f"{h:.1f}%", ha="center", va="bottom", fontsize=7)

# Readmission by diagnosis
ax2 = fig.add_axes([0.54, 0.46, 0.44, 0.34])
diag_plot = diag_df.sort_values("readmission_rate_pct", ascending=True)
diag_cols = [C_RED if v > 10 else C_TEAL for v in diag_plot["readmission_rate_pct"]]
ax2.barh(diag_plot["diag_1_category"], diag_plot["readmission_rate_pct"],
         color=diag_cols, alpha=0.85)
ax2.axvline(df["readmitted_30days"].mean() * 100, color=C_AMBER,
            linestyle="--", lw=1.5)
ax2.set_title("30-Day Readmission Rate by Primary Diagnosis")
ax2.set_xlabel("Readmission Rate (%)")
for i, v in enumerate(diag_plot["readmission_rate_pct"]):
    ax2.text(v + 0.1, i, f"{v:.1f}%", va="center", fontsize=8)

# Risk stratification
ax3 = fig.add_axes([0.02, 0.05, 0.28, 0.34])
risk_plot = risk_df.dropna(subset=["risk_category"])
risk_order = ["Low Risk", "Medium Risk", "High Risk", "Very High Risk"]
risk_plot = risk_plot.set_index("risk_category").reindex(risk_order).reset_index()
risk_cols = [C_GREEN, C_AMBER, C_RED, "#7F1D1D"]
ax3.bar(risk_plot["risk_category"], risk_plot["readmission_rate_pct"],
        color=risk_cols, alpha=0.87)
ax3.set_title("Readmission Rate by Risk Category")
ax3.set_ylabel("Rate (%)")
ax3.tick_params(axis="x", rotation=15)
for i, v in enumerate(risk_plot["readmission_rate_pct"]):
    if not pd.isna(v):
        ax3.text(i, v + 0.2, f"{v:.1f}%", ha="center", fontsize=9)

# LOS vs readmission
ax4 = fig.add_axes([0.37, 0.05, 0.28, 0.34])
los_order = ["1-2 days", "3-4 days", "5-7 days", "8-14 days", "14+ days"]
los_plot = los_df.set_index("los_band").reindex(los_order).reset_index()
ax4.bar(los_plot["los_band"], los_plot["readmission_rate_pct"],
        color=C_PURPLE, alpha=0.85)
ax4.set_title("Readmission Rate by Length of Stay")
ax4.set_ylabel("Rate (%)")
ax4.tick_params(axis="x", rotation=20)
for i, v in enumerate(los_plot["readmission_rate_pct"]):
    if not pd.isna(v):
        ax4.text(i, v + 0.1, f"{v:.1f}%", ha="center", fontsize=9)

# Admission type
ax5 = fig.add_axes([0.72, 0.05, 0.26, 0.34])
adm_plot = adm_df[adm_df["admission_type"].isin(
    ["Emergency", "Urgent", "Elective", "Trauma Center"]
)].sort_values("readmission_rate_pct", ascending=False)
ax5.bar(adm_plot["admission_type"], adm_plot["readmission_rate_pct"],
        color=[C_RED, C_AMBER, C_TEAL, C_PURPLE], alpha=0.85)
ax5.set_title("Readmission Rate by Admission Type")
ax5.set_ylabel("Rate (%)")
ax5.tick_params(axis="x", rotation=15)
for i, v in enumerate(adm_plot["readmission_rate_pct"]):
    ax5.text(i, v + 0.1, f"{v:.1f}%", ha="center", fontsize=9)

plt.savefig(os.path.join(OUT, "01_executive_overview.png"), dpi=150, bbox_inches="tight")
plt.close()
print("\nSaved: 01_executive_overview.png")

# ════════════════════════════════════════════════════════════════
# CHART 2 — PATIENT DEMOGRAPHICS & CLINICAL ANALYSIS
# ════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle(
    "Hospital Readmission Analytics — Patient Demographics & Clinical Patterns",
    fontsize=14, fontweight="bold", color="#1E293B"
)

# Gender split
ax = axes[0, 0]
gender = df["gender"].value_counts()
ax.pie(gender.values, labels=gender.index, autopct="%1.1f%%",
       colors=[C_BLUE, C_RED, C_GRAY], startangle=90,
       wedgeprops=dict(width=0.55))
ax.set_title("Patient Distribution by Gender")

# Race distribution
ax = axes[0, 1]
race = df["race"].value_counts().head(6)
ax.barh(race.index, race.values, color=C_TEAL, alpha=0.8)
ax.set_title("Patient Distribution by Race")
ax.set_xlabel("Number of Encounters")
for i, v in enumerate(race.values):
    ax.text(v + 100, i, f"{v:,}", va="center", fontsize=8)

# Number of medications distribution
ax = axes[0, 2]
med_bins = pd.cut(df["num_medications"], bins=[0, 5, 10, 15, 20, 100],
                   labels=["1-5", "6-10", "11-15", "16-20", "21+"])
med_dist = med_bins.value_counts().sort_index()
ax.bar(med_dist.index, med_dist.values, color=C_PURPLE, alpha=0.8)
ax.set_title("Distribution of Medications per Patient")
ax.set_ylabel("Number of Patients")
ax.set_xlabel("Medication Count")

# Readmitted vs not — time in hospital
ax = axes[1, 0]
readmit_yes = df[df["readmitted_30days"] == 1]["time_in_hospital"]
readmit_no  = df[df["readmitted_30days"] == 0]["time_in_hospital"]
ax.hist(readmit_no, bins=14, alpha=0.6, color=C_BLUE, label="Not readmitted", density=True)
ax.hist(readmit_yes, bins=14, alpha=0.6, color=C_RED, label="Readmitted <30 days", density=True)
ax.set_title("Length of Stay: Readmitted vs Not")
ax.set_xlabel("Days in Hospital")
ax.set_ylabel("Density")
ax.legend(fontsize=8)

# Insulin usage vs readmission
ax = axes[1, 1]
x = np.arange(len(ins_df))
bars1 = ax.bar(x - 0.2, ins_df["total_patients"], 0.35, color=C_BLUE, alpha=0.7, label="Total Patients")
ax2b = ax.twinx()
ax2b.plot(x, ins_df["readmission_rate_pct"], color=C_RED, marker="o",
          lw=2, ms=8, label="Readmission Rate %")
ax.set_xticks(x)
ax.set_xticklabels(ins_df["insulin_used"])
ax.set_title("Insulin Usage vs Readmission Rate")
ax.set_ylabel("Patient Count"); ax2b.set_ylabel("Readmission Rate (%)")
ax.legend(loc="upper left", fontsize=8)
ax2b.legend(loc="upper right", fontsize=8)
ax.spines["top"].set_visible(False); ax2b.spines["top"].set_visible(False)

# Number of diagnoses vs readmission
ax = axes[1, 2]
diag_n = df.groupby("number_diagnoses")["readmitted_30days"].mean() * 100
ax.plot(diag_n.index, diag_n.values, color=C_AMBER, marker="o", lw=2, ms=5)
ax.set_title("Readmission Rate by Number of Diagnoses")
ax.set_xlabel("Number of Diagnoses")
ax.set_ylabel("30-Day Readmission Rate (%)")
ax.fill_between(diag_n.index, diag_n.values, alpha=0.15, color=C_AMBER)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "02_patient_demographics.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved: 02_patient_demographics.png")

# ════════════════════════════════════════════════════════════════
# CHART 3 — CLINICAL RISK & MEDICATION ANALYSIS
# ════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle(
    "Hospital Readmission Analytics — Clinical Risk & Medication Patterns",
    fontsize=14, fontweight="bold", color="#1E293B"
)

# Diagnosis category volume + rate
ax = axes[0, 0]
diag_sorted = diag_df.sort_values("total_encounters", ascending=False)
x = range(len(diag_sorted))
ax.bar(x, diag_sorted["total_encounters"], color=C_TEAL, alpha=0.7, label="Encounters")
ax2b = ax.twinx()
ax2b.plot(list(x), diag_sorted["readmission_rate_pct"], color=C_RED,
          marker="D", lw=2, ms=6, label="Readmission Rate %")
ax.set_xticks(list(x))
ax.set_xticklabels(diag_sorted["diag_1_category"], rotation=25, ha="right", fontsize=8)
ax.set_title("Encounter Volume vs Readmission Rate by Diagnosis")
ax.set_ylabel("Number of Encounters")
ax2b.set_ylabel("Readmission Rate (%)")
ax.spines["top"].set_visible(False); ax2b.spines["top"].set_visible(False)

# Number of inpatient visits vs readmission
ax = axes[0, 1]
inp = df.groupby("number_inpatient")["readmitted_30days"].agg(["mean", "count"]).reset_index()
inp = inp[inp["count"] >= 50]
inp["mean"] = inp["mean"] * 100
ax.bar(inp["number_inpatient"], inp["count"], color=C_BLUE, alpha=0.6, label="Count")
ax2b = ax.twinx()
ax2b.plot(inp["number_inpatient"], inp["mean"], color=C_RED,
          marker="o", lw=2, ms=6, label="Readmission Rate %")
ax.set_title("Prior Inpatient Visits vs Readmission Rate")
ax.set_xlabel("Number of Prior Inpatient Visits")
ax.set_ylabel("Patient Count"); ax2b.set_ylabel("Readmission Rate (%)")
ax.spines["top"].set_visible(False); ax2b.spines["top"].set_visible(False)

# Emergency visits vs readmission
ax = axes[1, 0]
emer = df.groupby("number_emergency")["readmitted_30days"].agg(["mean", "count"]).reset_index()
emer = emer[emer["count"] >= 30]
emer["mean"] = emer["mean"] * 100
ax.plot(emer["number_emergency"], emer["mean"], color=C_AMBER,
        marker="s", lw=2.5, ms=7)
ax.fill_between(emer["number_emergency"], emer["mean"], alpha=0.15, color=C_AMBER)
ax.set_title("Prior Emergency Visits vs 30-Day Readmission Rate")
ax.set_xlabel("Number of Prior Emergency Visits")
ax.set_ylabel("Readmission Rate (%)")

# Race vs readmission
ax = axes[1, 1]
race_r = df.groupby("race")["readmitted_30days"].agg(["mean", "count"]).reset_index()
race_r = race_r[race_r["count"] >= 100].sort_values("mean", ascending=False)
race_r["mean"] = race_r["mean"] * 100
bars = ax.bar(race_r["race"], race_r["mean"], color=C_PURPLE, alpha=0.85)
ax.axhline(df["readmitted_30days"].mean() * 100, color=C_RED,
           linestyle="--", lw=1.5, label="Overall avg")
ax.set_title("30-Day Readmission Rate by Race")
ax.set_ylabel("Readmission Rate (%)")
ax.tick_params(axis="x", rotation=15)
ax.legend(fontsize=8)
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 0.1,
            f"{h:.1f}%", ha="center", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(OUT, "03_clinical_risk_analysis.png"), dpi=150, bbox_inches="tight")
plt.close()
print("Saved: 03_clinical_risk_analysis.png")

# ════════════════════════════════════════════════════════════════
# PRINT KEY BUSINESS INSIGHTS
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("KEY BUSINESS INSIGHTS")
print("=" * 60)

overall_rate = df["readmitted_30days"].mean() * 100
print(f"\n1. OVERALL READMISSION")
print(f"   Overall 30-day readmission rate: {overall_rate:.2f}%")
print(f"   Total readmissions: {df['readmitted_30days'].sum():,} of {len(df):,} encounters")

top_diag = diag_df.sort_values("readmission_rate_pct", ascending=False).iloc[0]
print(f"\n2. HIGHEST RISK DIAGNOSIS")
print(f"   {top_diag['diag_1_category']} has the highest readmission rate: {top_diag['readmission_rate_pct']:.1f}%")

top_age = age_df.sort_values("readmission_rate_pct", ascending=False).iloc[0]
print(f"\n3. HIGHEST RISK AGE GROUP")
print(f"   Age group {top_age['age']} has the highest readmission rate: {top_age['readmission_rate_pct']:.1f}%")

vh_risk = risk_df[risk_df["risk_category"] == "Very High Risk"].iloc[0] if "Very High Risk" in risk_df["risk_category"].values else None
if vh_risk is not None:
    print(f"\n4. VERY HIGH RISK PATIENTS")
    print(f"   Very High Risk patients: {vh_risk['total_patients']:,}")
    print(f"   Readmission rate: {vh_risk['readmission_rate_pct']:.1f}%")

avg_los_readmit = df[df["readmitted_30days"]==1]["time_in_hospital"].mean()
avg_los_no      = df[df["readmitted_30days"]==0]["time_in_hospital"].mean()
print(f"\n5. LENGTH OF STAY IMPACT")
print(f"   Readmitted patients avg LOS: {avg_los_readmit:.1f} days")
print(f"   Non-readmitted patients avg LOS: {avg_los_no:.1f} days")

print(f"\n6. INSULIN USAGE IMPACT")
for _, row in ins_df.iterrows():
    print(f"   Insulin {row['insulin_used']}: {row['readmission_rate_pct']:.1f}% readmission rate")

print(f"\nAll charts saved to: {OUT}")
print("=" * 60)
