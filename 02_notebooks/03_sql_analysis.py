"""
Hospital Readmission Analytics
Step 3: SQL Analysis Layer
Author: Hely Shah

Runs 6 business SQL queries against the cleaned dataset.
Uses SQLite (built into Python — no install needed).
These same queries can be run in any SQL environment.
"""

import sqlite3
import pandas as pd
import os

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE, "01_data", "processed")
SQL_OUT   = os.path.join(BASE, "01_data", "sql_exports")
os.makedirs(SQL_OUT, exist_ok=True)

# Load cleaned data into SQLite
con = sqlite3.connect(":memory:")
df = pd.read_csv(os.path.join(PROCESSED, "cleaned_diabetes.csv"))
df.to_sql("encounters", con, index=False, if_exists="replace")

def run(query, name):
    result = pd.read_sql_query(query, con)
    result.to_csv(os.path.join(SQL_OUT, f"{name}.csv"), index=False)
    print(f"\n{'='*55}")
    print(f"Query: {name}")
    print(result.to_string(index=False))
    return result

print("=" * 55)
print("HOSPITAL READMISSION — SQL ANALYSIS")
print("=" * 55)

# ── Q1: Readmission rate by age group + total volume ──────────
# Uses: GROUP BY, aggregation, calculated field, ORDER BY
run("""
SELECT
    age                                                      AS age_group,
    COUNT(encounter_id)                                      AS total_encounters,
    SUM(readmitted_30days)                                   AS readmissions,
    ROUND(AVG(time_in_hospital), 2)                         AS avg_los_days,
    ROUND(AVG(num_medications), 1)                          AS avg_medications,
    ROUND(SUM(readmitted_30days) * 100.0 /
          COUNT(encounter_id), 2)                           AS readmission_rate_pct
FROM encounters
GROUP BY age
ORDER BY readmission_rate_pct DESC
""", "q1_readmission_by_age")

# ── Q2: Risk stratification — CTE + window function ───────────
# Uses: CTE, window function (RANK), aggregation
run("""
WITH risk_summary AS (
    SELECT
        risk_category,
        COUNT(encounter_id)                                  AS total_patients,
        SUM(readmitted_30days)                               AS readmissions,
        ROUND(AVG(time_in_hospital), 2)                     AS avg_los,
        ROUND(AVG(num_medications), 1)                      AS avg_medications,
        ROUND(AVG(risk_score), 2)                           AS avg_risk_score,
        ROUND(SUM(readmitted_30days) * 100.0 /
              COUNT(encounter_id), 2)                       AS readmission_rate_pct
    FROM encounters
    WHERE risk_category IS NOT NULL
    GROUP BY risk_category
)
SELECT
    risk_category,
    total_patients,
    readmissions,
    avg_los,
    avg_medications,
    avg_risk_score,
    readmission_rate_pct,
    RANK() OVER (ORDER BY readmission_rate_pct DESC)        AS risk_rank
FROM risk_summary
ORDER BY readmission_rate_pct DESC
""", "q2_risk_stratification")

# ── Q3: Diagnosis category analysis — CTE + % of total ────────
# Uses: CTE, subquery, percentage calculation, ORDER BY
run("""
WITH diag_totals AS (
    SELECT
        diag_1_category,
        COUNT(encounter_id)                                  AS total_encounters,
        SUM(readmitted_30days)                               AS readmissions,
        ROUND(AVG(time_in_hospital), 2)                     AS avg_los,
        ROUND(AVG(num_medications), 1)                      AS avg_meds
    FROM encounters
    GROUP BY diag_1_category
),
overall AS (
    SELECT COUNT(*) AS grand_total FROM encounters
)
SELECT
    d.diag_1_category,
    d.total_encounters,
    ROUND(d.total_encounters * 100.0 / o.grand_total, 1)   AS pct_of_total,
    d.readmissions,
    ROUND(d.readmissions * 100.0 / d.total_encounters, 2)  AS readmission_rate_pct,
    d.avg_los,
    d.avg_meds
FROM diag_totals d, overall o
ORDER BY d.total_encounters DESC
""", "q3_diagnosis_analysis")

# ── Q4: Admission type analysis ────────────────────────────────
# Uses: GROUP BY, HAVING, ORDER BY, aggregation
run("""
SELECT
    admission_type,
    COUNT(encounter_id)                                      AS total_encounters,
    SUM(readmitted_30days)                                   AS readmissions,
    ROUND(SUM(readmitted_30days) * 100.0 /
          COUNT(encounter_id), 2)                           AS readmission_rate_pct,
    ROUND(AVG(time_in_hospital), 2)                         AS avg_los_days,
    ROUND(AVG(num_medications), 1)                          AS avg_medications,
    ROUND(AVG(number_diagnoses), 1)                         AS avg_diagnoses
FROM encounters
WHERE admission_type NOT IN ('Not Available', 'Not Mapped', 'Other')
GROUP BY admission_type
HAVING COUNT(encounter_id) > 100
ORDER BY readmission_rate_pct DESC
""", "q4_admission_type_analysis")

# ── Q5: High-risk patient profile — multi-condition filter ─────
# Uses: WHERE with multiple conditions, aggregation, subquery
run("""
SELECT
    age                                                      AS age_group,
    gender,
    diag_1_category,
    COUNT(encounter_id)                                      AS patient_count,
    ROUND(AVG(time_in_hospital), 1)                         AS avg_los,
    ROUND(AVG(num_medications), 1)                          AS avg_medications,
    ROUND(AVG(number_inpatient), 1)                         AS avg_prior_inpatient,
    ROUND(SUM(readmitted_30days) * 100.0 /
          COUNT(encounter_id), 1)                           AS readmission_rate_pct
FROM encounters
WHERE risk_category IN ('High Risk', 'Very High Risk')
  AND number_inpatient >= 1
  AND age_numeric >= 60
GROUP BY age, gender, diag_1_category
HAVING COUNT(encounter_id) >= 20
ORDER BY readmission_rate_pct DESC
LIMIT 15
""", "q5_high_risk_patient_profile")

# ── Q6: Length of stay impact — window function + CTE ─────────
# Uses: CTE, CASE WHEN, window function, LAG
run("""
WITH los_analysis AS (
    SELECT
        los_band,
        COUNT(encounter_id)                                  AS total_patients,
        SUM(readmitted_30days)                               AS readmissions,
        ROUND(AVG(num_medications), 1)                      AS avg_meds,
        ROUND(AVG(number_diagnoses), 1)                     AS avg_diagnoses,
        ROUND(SUM(readmitted_30days) * 100.0 /
              COUNT(encounter_id), 2)                       AS readmission_rate_pct
    FROM encounters
    WHERE los_band IS NOT NULL
    GROUP BY los_band
)
SELECT
    los_band,
    total_patients,
    readmissions,
    readmission_rate_pct,
    avg_meds,
    avg_diagnoses,
    ROUND(total_patients * 100.0 /
          SUM(total_patients) OVER (), 1)                   AS pct_of_patients,
    RANK() OVER (ORDER BY readmission_rate_pct DESC)        AS readmission_rank
FROM los_analysis
ORDER BY
    CASE los_band
        WHEN '1-2 days'  THEN 1
        WHEN '3-4 days'  THEN 2
        WHEN '5-7 days'  THEN 3
        WHEN '8-14 days' THEN 4
        WHEN '14+ days'  THEN 5
    END
""", "q6_los_impact_analysis")

con.close()
print(f"\n\nAll SQL exports saved to: {SQL_OUT}")
print("These files are ready to load into Power BI and Tableau.")
