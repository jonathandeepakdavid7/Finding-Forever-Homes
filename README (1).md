# Finding Forever Homes
## Adoption Patterns at the Austin Animal Center

CS7510 — Communication and Presentation for Data Science  
Fall 2026

### Project Overview
This project examines recorded dog and cat shelter outcomes at the Austin Animal Center from 2019 through 2024.

The analysis compares:
- Adoption shares over time
- Adoption shares across animal age groups
- Shelter outcome categories
- Annual outcome volumes

### Dataset
Source: City of Austin, Austin Animal Center Outcomes

The cleaned dataset contains 72,147 known outcome records.

Adoption share is the percentage of known outcomes classified as "Adoption." It is not an individual animal's probability of adoption.

### Project Files
- Animal_Shelter_Analysis.ipynb — Data cleaning, analysis, and visualizations
- animal_shelter_clean.csv — Cleaned dataset
- finding_forever_homes.py — Interactive Streamlit dashboard
- requirements.txt — Required Python libraries
- Four HTML files — Interactive visualizations

### Running the Streamlit Dashboard
Open Terminal in the project folder and run:

    python -m pip install -r requirements.txt
    python -m streamlit run finding_forever_homes.py

Streamlit will provide a local browser address, usually http://localhost:8501.

### Limitations
The dataset contains recorded shelter outcomes, not necessarily unique animals. The analysis identifies patterns but does not establish their causes.
