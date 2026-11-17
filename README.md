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
