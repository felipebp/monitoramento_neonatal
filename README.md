# 👶🏽 Neonatal Mortality Risk Monitoring & Predictive Analytics (Ceará, 2019–2024)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

## 📌 Project Overview
This end-to-end Data Science and Public Health Analytics project investigates neonatal mortality determinants and builds an interpretable predictive screening pipeline for newborns in the state of **Ceará, Brazil (2019–2024)**.

By integrating and cross-referencing official public health records from **DATASUS**—specifically **SINASC** (Live Births Information System) and **SIM** (Mortality Information System)—the solution processes **594,740 birth records** to identify high-risk clinical and sociodemographic profiles, delivering actionable insights through an interactive **Streamlit** clinical decision-support dashboard.

---

## 🎯 Business & Public Health Problem
Neonatal mortality (deaths occurring within the first 28 days of life) represents the largest component of infant mortality in Brazil and is strongly linked to preventable perinatal factors, maternal care access, and congenital conditions. Public health managers need interpretable, data-driven tools capable of:
1. **Quantifying risk factors** across large-scale epidemiological cohorts.
2. **Supporting early triage** at birth using standardized clinical indicators (such as Apgar scores, birth weight, gestational age, and congenital anomalies).
3. **Balancing sensitivity and clinical interpretability**, avoiding "black-box" predictions in healthcare settings.

---

## 🏗️ Data Architecture & Pipeline

```text
[DATASUS Microdata: SINASC & SIM (2019–2024)]
                     │
                     ▼
   [PostgreSQL Relational Data Warehouse]
   (Schema normalization, indexing & cohort linkage)
                     │
                     ▼
   [Preprocessing & Feature Engineering (Python)]
   (SUS domain cleaning, missing/ignored code handling)
                     │
                     ▼
   [Predictive Modeling (Scikit-Learn)]
   (Balanced Logistic Regression | ROC-AUC: 0.9493)
                     │
                     ▼
   [Streamlit Web Application]
   (Epidemiological Overview + Individual Risk Screening + Odds Ratio Explainability)
```
### Data Engineering & Cleaning (PostgreSQL + Python)

   - Cohort Scale: 594,740 live birth records from Ceará (2019–2024) stored and queried via PostgreSQL.

   - Domain-Specific Data Hygiene:

     - Filtered standardized SUS "ignored/unknown" sentinel codes (e.g., removing code 99 in apgar5 and sexo_IGN records) to prevent synthetic distortion in clinical distributions.

     - Engineered clinical determinants including 5th-minute Apgar score (apgar5), birth weight, gestational weeks, maternal profile, and congenital anomaly indicator (anomalia_cong).
   
### Modeling & Clinical Explainability

  - Algorithm: Logistic Regression with class-imbalance compensation (class_weight='balanced') to prioritize recall on rare, high-severity neonatal mortality events.

  - Performance: Achieved 0.9493 ROC-AUC on holdout evaluation.

  - Interpretability: Extracted Odds Ratios (OR) directly from model coefficients so healthcare professionals can understand the exact weight and direction of each clinical variable in an individual risk score.

### 🖥️ Dashboard Features (Streamlit)
The interactive web application is structured into three core analytical modules:

- Cohort Epidemiology Indicators: Macro-level KPIs, temporal evolution (2019–2024), birth weight/Apgar distributions, and mortality rates across Ceará.

- Individual Risk Screening Simulator: Real-time clinical calculator allowing users to input newborn and maternal parameters to estimate mortality risk probability and risk tier.

- Model Explainability (Odds Ratios): Visual breakdown of clinical risk drivers (anomalia_cong, apgar5, prematurity, low birth weight) for transparent clinical validation.


