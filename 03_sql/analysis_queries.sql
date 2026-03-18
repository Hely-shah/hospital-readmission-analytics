-- ============================================================
-- Hospital Readmission Analytics — SQL Analysis
-- Author: Hely Shah
-- Dataset: UCI Diabetes 130-US Hospitals (1999-2008)
-- ============================================================


-- ── QUERY 1: Readmission Rate by Age Group ─────────────────
-- Shows which age groups have the highest 30-day readmission rates
-- Skills: GROUP BY, aggregation, calculated fields, ORDER BY

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
ORDER BY readmission_rate_pct DESC;


-- ── QUERY 2: Risk Stratification with Window Functions ─────
-- Ranks risk categories by readmission rate
-- Skills: CTE, window function (RANK), aggregation

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
ORDER BY readmission_rate_pct DESC;


-- ── QUERY 3: Diagnosis Category Analysis ─────────────────────
-- Breaks down encounters and readmissions by primary diagnosis
-- Skills: CTE, subquery, percentage of total calculation

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
ORDER BY d.total_encounters DESC;


-- ── QUERY 4: Admission Type Analysis ─────────────────────────
-- Compares readmission rates across admission types
-- Skills: GROUP BY, HAVING, aggregation

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
ORDER BY readmission_rate_pct DESC;


-- ── QUERY 5: High-Risk Patient Profile ───────────────────────
-- Identifies the highest-risk patient segments by age, gender, diagnosis
-- Skills: WHERE with multiple conditions, GROUP BY, HAVING, ORDER BY

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
LIMIT 15;


-- ── QUERY 6: Length of Stay Impact — Window Functions ────────
-- Analyses how length of stay affects readmission rates
-- Skills: CTE, CASE WHEN, window functions (SUM OVER, RANK OVER)

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
    END;
