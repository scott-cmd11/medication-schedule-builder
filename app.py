# -*- coding: utf-8 -*-
"""
RxFlow Canada - Safety-Critical Medication Schedule Builder
A mobile-first Streamlit application with strict "Checks & Balances"
"""

import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta
import re

# =============================================================================
# PAGE CONFIG & CUSTOM CSS
# =============================================================================

st.set_page_config(
    page_title="RxFlow Canada",
    page_icon=":pill:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    .stButton > button {
        min-height: 48px;
        font-size: 1rem;
        border-radius: 8px;
        width: 100%;
    }

    .stCheckbox > label {
        min-height: 44px;
        display: flex;
        align-items: center;
        font-size: 1rem;
    }

    .verified-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #e3f2fd 100%);
        border-left: 5px solid #2e7d32;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .verified-badge {
        background-color: #2e7d32;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }

    .manual-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffebee 100%);
        border-left: 5px solid #e65100;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .manual-badge {
        background-color: #e65100;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }

    .manual-warning {
        background-color: #ff5722;
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
    }

    .stButton > button:disabled {
        background-color: #9e9e9e !important;
        color: #616161 !important;
        cursor: not-allowed;
    }

    .med-name {
        font-size: 1.25rem;
        font-weight: bold;
        color: #1a237e;
        margin-bottom: 0.5rem;
    }

    .med-details {
        font-size: 0.95rem;
        color: #424242;
    }

    .time-slots {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 0.5rem;
    }

    .time-slot {
        background-color: #1976d2;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.85rem;
    }

    .verify-section {
        background-color: #fff8e1;
        padding: 0.75rem;
        border-radius: 4px;
        border: 2px dashed #ffc107;
        margin-top: 0.5rem;
    }

    .app-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1976d2;
        margin-bottom: 1.5rem;
    }

    .app-title {
        font-size: 1.75rem;
        font-weight: bold;
        color: #1976d2;
        margin: 0;
    }

    .app-subtitle {
        font-size: 0.9rem;
        color: #616161;
        margin-top: 0.25rem;
    }

    .status-bar {
        background-color: #263238;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }

    .calendar-container {
        margin: 1rem 0;
        overflow-x: auto;
    }

    .calendar-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }

    .calendar-table th {
        background-color: #1976d2;
        color: white;
        padding: 12px 8px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #1565c0;
    }

    .calendar-table td {
        border: 1px solid #e0e0e0;
        padding: 8px;
        vertical-align: top;
        min-width: 120px;
        height: 80px;
    }

    .calendar-table .time-header {
        background-color: #f5f5f5;
        font-weight: bold;
        text-align: center;
        width: 100px;
    }

    .calendar-med {
        background-color: #e3f2fd;
        border-left: 3px solid #1976d2;
        padding: 4px 6px;
        margin: 2px 0;
        border-radius: 3px;
        font-size: 0.8rem;
    }

    .calendar-med.manual {
        background-color: #fff3e0;
        border-left-color: #e65100;
    }

    .calendar-med .med-title {
        font-weight: bold;
        color: #1a237e;
    }

    .calendar-med .med-dose {
        color: #616161;
        font-size: 0.75rem;
    }

    .preview-container {
        background-color: #fafafa;
        border: 2px solid #1976d2;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .preview-header {
        background-color: #1976d2;
        color: white;
        padding: 10px;
        margin: -1rem -1rem 1rem -1rem;
        border-radius: 6px 6px 0 0;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# TOP PRESCRIBED MEDICATIONS DATABASE
# Based on IQVIA Canada 2024 data, ClinCalc Top 300, and Health Canada data
# =============================================================================

MEDICATION_DATABASE = [
    # =========================================================================
    # TOP 20 MOST DISPENSED IN CANADA (2024) - IQVIA Data
    # =========================================================================
    {"brand_name": "SYNTHROID", "company": "AbbVie", "category": "Thyroid - #1 in Canada"},
    {"brand_name": "LEVOTHYROXINE", "company": "Various", "category": "Thyroid - #1 Generic"},
    {"brand_name": "ELTROXIN", "company": "Aspen", "category": "Thyroid"},
    {"brand_name": "OZEMPIC", "company": "Novo Nordisk", "category": "Diabetes - #3 in Canada"},
    {"brand_name": "SEMAGLUTIDE", "company": "Novo Nordisk", "category": "Diabetes"},
    {"brand_name": "JARDIANCE", "company": "Boehringer", "category": "Diabetes - #5 in Canada"},
    {"brand_name": "EMPAGLIFLOZIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "ROSUVASTATIN", "company": "Various", "category": "Cholesterol - #6 in Canada"},
    {"brand_name": "CRESTOR", "company": "AstraZeneca", "category": "Cholesterol"},
    {"brand_name": "AMLODIPINE", "company": "Various", "category": "Blood Pressure - #9 in Canada"},
    {"brand_name": "NORVASC", "company": "Pfizer", "category": "Blood Pressure"},
    {"brand_name": "SALBUTAMOL", "company": "Various", "category": "Asthma - #10 in Canada"},
    {"brand_name": "VENTOLIN", "company": "GSK", "category": "Asthma"},
    {"brand_name": "VYVANSE", "company": "Takeda", "category": "ADHD - #12 in Canada"},
    {"brand_name": "LISDEXAMFETAMINE", "company": "Various", "category": "ADHD"},

    # =========================================================================
    # CARDIOVASCULAR - Most Prescribed Category
    # =========================================================================
    {"brand_name": "ATORVASTATIN", "company": "Various", "category": "Cholesterol"},
    {"brand_name": "LIPITOR", "company": "Pfizer", "category": "Cholesterol"},
    {"brand_name": "SIMVASTATIN", "company": "Various", "category": "Cholesterol"},
    {"brand_name": "ZOCOR", "company": "Merck", "category": "Cholesterol"},
    {"brand_name": "PRAVASTATIN", "company": "Various", "category": "Cholesterol"},
    {"brand_name": "PRAVACHOL", "company": "Bristol-Myers", "category": "Cholesterol"},
    {"brand_name": "EZETIMIBE", "company": "Various", "category": "Cholesterol"},
    {"brand_name": "EZETROL", "company": "Merck", "category": "Cholesterol"},
    {"brand_name": "RAMIPRIL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "ALTACE", "company": "Sanofi", "category": "Blood Pressure"},
    {"brand_name": "LISINOPRIL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "ZESTRIL", "company": "AstraZeneca", "category": "Blood Pressure"},
    {"brand_name": "ENALAPRIL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "VASOTEC", "company": "Valeant", "category": "Blood Pressure"},
    {"brand_name": "PERINDOPRIL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "COVERSYL", "company": "Servier", "category": "Blood Pressure"},
    {"brand_name": "LOSARTAN", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "COZAAR", "company": "Merck", "category": "Blood Pressure"},
    {"brand_name": "VALSARTAN", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "DIOVAN", "company": "Novartis", "category": "Blood Pressure"},
    {"brand_name": "IRBESARTAN", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "AVAPRO", "company": "Sanofi", "category": "Blood Pressure"},
    {"brand_name": "CANDESARTAN", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "ATACAND", "company": "AstraZeneca", "category": "Blood Pressure"},
    {"brand_name": "TELMISARTAN", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "MICARDIS", "company": "Boehringer", "category": "Blood Pressure"},
    {"brand_name": "METOPROLOL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "LOPRESSOR", "company": "Novartis", "category": "Blood Pressure"},
    {"brand_name": "ATENOLOL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "TENORMIN", "company": "AstraZeneca", "category": "Blood Pressure"},
    {"brand_name": "BISOPROLOL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "CARVEDILOL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "COREG", "company": "GSK", "category": "Blood Pressure"},
    {"brand_name": "PROPRANOLOL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "INDERAL", "company": "Pfizer", "category": "Blood Pressure"},
    {"brand_name": "HYDROCHLOROTHIAZIDE", "company": "Various", "category": "Diuretic"},
    {"brand_name": "FUROSEMIDE", "company": "Various", "category": "Diuretic"},
    {"brand_name": "LASIX", "company": "Sanofi", "category": "Diuretic"},
    {"brand_name": "SPIRONOLACTONE", "company": "Various", "category": "Diuretic"},
    {"brand_name": "ALDACTONE", "company": "Pfizer", "category": "Diuretic"},
    {"brand_name": "INDAPAMIDE", "company": "Various", "category": "Diuretic"},
    {"brand_name": "DILTIAZEM", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "CARDIZEM", "company": "Valeant", "category": "Blood Pressure"},
    {"brand_name": "VERAPAMIL", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "NIFEDIPINE", "company": "Various", "category": "Blood Pressure"},
    {"brand_name": "ADALAT", "company": "Bayer", "category": "Blood Pressure"},

    # Blood Thinners
    {"brand_name": "APIXABAN", "company": "Various", "category": "Blood Thinner"},
    {"brand_name": "ELIQUIS", "company": "Bristol-Myers", "category": "Blood Thinner"},
    {"brand_name": "RIVAROXABAN", "company": "Various", "category": "Blood Thinner"},
    {"brand_name": "XARELTO", "company": "Bayer", "category": "Blood Thinner"},
    {"brand_name": "DABIGATRAN", "company": "Various", "category": "Blood Thinner"},
    {"brand_name": "PRADAXA", "company": "Boehringer", "category": "Blood Thinner"},
    {"brand_name": "WARFARIN", "company": "Various", "category": "Blood Thinner"},
    {"brand_name": "COUMADIN", "company": "Bristol-Myers", "category": "Blood Thinner"},
    {"brand_name": "CLOPIDOGREL", "company": "Various", "category": "Blood Thinner"},
    {"brand_name": "PLAVIX", "company": "Sanofi", "category": "Blood Thinner"},
    {"brand_name": "ASA", "company": "Various", "category": "Blood Thinner"},
    {"brand_name": "ASPIRIN", "company": "Bayer", "category": "Blood Thinner"},

    # =========================================================================
    # DIABETES MEDICATIONS
    # =========================================================================
    {"brand_name": "METFORMIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "GLUCOPHAGE", "company": "Bristol-Myers", "category": "Diabetes"},
    {"brand_name": "SITAGLIPTIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "JANUVIA", "company": "Merck", "category": "Diabetes"},
    {"brand_name": "JANUMET", "company": "Merck", "category": "Diabetes"},
    {"brand_name": "DAPAGLIFLOZIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "FORXIGA", "company": "AstraZeneca", "category": "Diabetes"},
    {"brand_name": "CANAGLIFLOZIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "INVOKANA", "company": "Janssen", "category": "Diabetes"},
    {"brand_name": "DULAGLUTIDE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "TRULICITY", "company": "Eli Lilly", "category": "Diabetes"},
    {"brand_name": "LIRAGLUTIDE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "VICTOZA", "company": "Novo Nordisk", "category": "Diabetes"},
    {"brand_name": "SAXENDA", "company": "Novo Nordisk", "category": "Weight Loss"},
    {"brand_name": "WEGOVY", "company": "Novo Nordisk", "category": "Weight Loss"},
    {"brand_name": "MOUNJARO", "company": "Eli Lilly", "category": "Diabetes/Weight"},
    {"brand_name": "TIRZEPATIDE", "company": "Eli Lilly", "category": "Diabetes/Weight"},
    {"brand_name": "RYBELSUS", "company": "Novo Nordisk", "category": "Diabetes"},
    {"brand_name": "GLYBURIDE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "DIABETA", "company": "Sanofi", "category": "Diabetes"},
    {"brand_name": "GLICLAZIDE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "DIAMICRON", "company": "Servier", "category": "Diabetes"},
    {"brand_name": "GLIMEPIRIDE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "AMARYL", "company": "Sanofi", "category": "Diabetes"},
    {"brand_name": "PIOGLITAZONE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "ACTOS", "company": "Takeda", "category": "Diabetes"},
    {"brand_name": "LINAGLIPTIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "TRAJENTA", "company": "Boehringer", "category": "Diabetes"},
    {"brand_name": "INSULIN GLARGINE", "company": "Sanofi", "category": "Insulin"},
    {"brand_name": "LANTUS", "company": "Sanofi", "category": "Insulin"},
    {"brand_name": "BASAGLAR", "company": "Eli Lilly", "category": "Insulin"},
    {"brand_name": "TOUJEO", "company": "Sanofi", "category": "Insulin"},
    {"brand_name": "INSULIN LISPRO", "company": "Various", "category": "Insulin"},
    {"brand_name": "HUMALOG", "company": "Eli Lilly", "category": "Insulin"},
    {"brand_name": "INSULIN ASPART", "company": "Various", "category": "Insulin"},
    {"brand_name": "NOVORAPID", "company": "Novo Nordisk", "category": "Insulin"},
    {"brand_name": "NOVOLOG", "company": "Novo Nordisk", "category": "Insulin"},
    {"brand_name": "INSULIN DEGLUDEC", "company": "Various", "category": "Insulin"},
    {"brand_name": "TRESIBA", "company": "Novo Nordisk", "category": "Insulin"},
    {"brand_name": "INSULIN NPH", "company": "Various", "category": "Insulin"},
    {"brand_name": "HUMULIN N", "company": "Eli Lilly", "category": "Insulin"},
    {"brand_name": "NOVOLIN", "company": "Novo Nordisk", "category": "Insulin"},
    {"brand_name": "FIASP", "company": "Novo Nordisk", "category": "Insulin"},

    # =========================================================================
    # MENTAL HEALTH - Antidepressants & Anxiety
    # =========================================================================
    {"brand_name": "SERTRALINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "ZOLOFT", "company": "Pfizer", "category": "Antidepressant"},
    {"brand_name": "ESCITALOPRAM", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "CIPRALEX", "company": "Lundbeck", "category": "Antidepressant"},
    {"brand_name": "LEXAPRO", "company": "Forest", "category": "Antidepressant"},
    {"brand_name": "CITALOPRAM", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "CELEXA", "company": "Forest", "category": "Antidepressant"},
    {"brand_name": "FLUOXETINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "PROZAC", "company": "Eli Lilly", "category": "Antidepressant"},
    {"brand_name": "PAROXETINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "PAXIL", "company": "GSK", "category": "Antidepressant"},
    {"brand_name": "VENLAFAXINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "EFFEXOR", "company": "Pfizer", "category": "Antidepressant"},
    {"brand_name": "DESVENLAFAXINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "PRISTIQ", "company": "Pfizer", "category": "Antidepressant"},
    {"brand_name": "DULOXETINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "CYMBALTA", "company": "Eli Lilly", "category": "Antidepressant"},
    {"brand_name": "BUPROPION", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "WELLBUTRIN", "company": "GSK", "category": "Antidepressant"},
    {"brand_name": "MIRTAZAPINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "REMERON", "company": "Organon", "category": "Antidepressant"},
    {"brand_name": "TRAZODONE", "company": "Various", "category": "Antidepressant/Sleep"},
    {"brand_name": "AMITRIPTYLINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "NORTRIPTYLINE", "company": "Various", "category": "Antidepressant"},
    {"brand_name": "DOXEPIN", "company": "Various", "category": "Antidepressant"},

    # Anxiety & Sleep
    {"brand_name": "LORAZEPAM", "company": "Various", "category": "Anxiety"},
    {"brand_name": "ATIVAN", "company": "Pfizer", "category": "Anxiety"},
    {"brand_name": "CLONAZEPAM", "company": "Various", "category": "Anxiety"},
    {"brand_name": "RIVOTRIL", "company": "Roche", "category": "Anxiety"},
    {"brand_name": "DIAZEPAM", "company": "Various", "category": "Anxiety"},
    {"brand_name": "VALIUM", "company": "Roche", "category": "Anxiety"},
    {"brand_name": "ALPRAZOLAM", "company": "Various", "category": "Anxiety"},
    {"brand_name": "XANAX", "company": "Pfizer", "category": "Anxiety"},
    {"brand_name": "BUSPIRONE", "company": "Various", "category": "Anxiety"},
    {"brand_name": "BUSPAR", "company": "Bristol-Myers", "category": "Anxiety"},
    {"brand_name": "ZOPICLONE", "company": "Various", "category": "Sleep"},
    {"brand_name": "IMOVANE", "company": "Sanofi", "category": "Sleep"},
    {"brand_name": "ZOLPIDEM", "company": "Various", "category": "Sleep"},
    {"brand_name": "SUBLINOX", "company": "Paladin", "category": "Sleep"},

    # Antipsychotics
    {"brand_name": "QUETIAPINE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "SEROQUEL", "company": "AstraZeneca", "category": "Antipsychotic"},
    {"brand_name": "OLANZAPINE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "ZYPREXA", "company": "Eli Lilly", "category": "Antipsychotic"},
    {"brand_name": "RISPERIDONE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "RISPERDAL", "company": "Janssen", "category": "Antipsychotic"},
    {"brand_name": "ARIPIPRAZOLE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "ABILIFY", "company": "Bristol-Myers", "category": "Antipsychotic"},
    {"brand_name": "PALIPERIDONE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "INVEGA", "company": "Janssen", "category": "Antipsychotic"},
    {"brand_name": "LURASIDONE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "LATUDA", "company": "Sunovion", "category": "Antipsychotic"},
    {"brand_name": "CLOZAPINE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "CLOZARIL", "company": "Novartis", "category": "Antipsychotic"},
    {"brand_name": "ZIPRASIDONE", "company": "Various", "category": "Antipsychotic"},
    {"brand_name": "LITHIUM", "company": "Various", "category": "Mood Stabilizer"},
    {"brand_name": "LITHANE", "company": "Pfizer", "category": "Mood Stabilizer"},

    # =========================================================================
    # PAIN MEDICATIONS
    # =========================================================================
    {"brand_name": "ACETAMINOPHEN", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "TYLENOL", "company": "Johnson & Johnson", "category": "Pain Relief"},
    {"brand_name": "IBUPROFEN", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "ADVIL", "company": "Pfizer", "category": "Pain Relief"},
    {"brand_name": "MOTRIN", "company": "Johnson & Johnson", "category": "Pain Relief"},
    {"brand_name": "NAPROXEN", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "ALEVE", "company": "Bayer", "category": "Pain Relief"},
    {"brand_name": "NAPROSYN", "company": "Roche", "category": "Pain Relief"},
    {"brand_name": "CELECOXIB", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "CELEBREX", "company": "Pfizer", "category": "Pain Relief"},
    {"brand_name": "MELOXICAM", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "MOBICOX", "company": "Boehringer", "category": "Pain Relief"},
    {"brand_name": "DICLOFENAC", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "VOLTAREN", "company": "Novartis", "category": "Pain Relief"},
    {"brand_name": "INDOMETHACIN", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "INDOCID", "company": "Merck", "category": "Pain Relief"},
    {"brand_name": "KETOROLAC", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "TORADOL", "company": "Roche", "category": "Pain Relief"},

    # Opioids
    {"brand_name": "TRAMADOL", "company": "Various", "category": "Pain Relief"},
    {"brand_name": "TRAMACET", "company": "Janssen", "category": "Pain Relief"},
    {"brand_name": "CODEINE", "company": "Various", "category": "Opioid"},
    {"brand_name": "TYLENOL #3", "company": "Janssen", "category": "Opioid"},
    {"brand_name": "OXYCODONE", "company": "Various", "category": "Opioid"},
    {"brand_name": "PERCOCET", "company": "Endo", "category": "Opioid"},
    {"brand_name": "OXYCONTIN", "company": "Purdue", "category": "Opioid"},
    {"brand_name": "HYDROMORPHONE", "company": "Various", "category": "Opioid"},
    {"brand_name": "DILAUDID", "company": "Purdue", "category": "Opioid"},
    {"brand_name": "MORPHINE", "company": "Various", "category": "Opioid"},
    {"brand_name": "MS CONTIN", "company": "Purdue", "category": "Opioid"},
    {"brand_name": "FENTANYL", "company": "Various", "category": "Opioid"},
    {"brand_name": "DURAGESIC", "company": "Janssen", "category": "Opioid"},
    {"brand_name": "BUPRENORPHINE", "company": "Various", "category": "Opioid"},
    {"brand_name": "SUBOXONE", "company": "Indivior", "category": "Opioid"},
    {"brand_name": "METHADONE", "company": "Various", "category": "Opioid"},

    # Nerve Pain
    {"brand_name": "GABAPENTIN", "company": "Various", "category": "Nerve Pain"},
    {"brand_name": "NEURONTIN", "company": "Pfizer", "category": "Nerve Pain"},
    {"brand_name": "PREGABALIN", "company": "Various", "category": "Nerve Pain"},
    {"brand_name": "LYRICA", "company": "Pfizer", "category": "Nerve Pain"},

    # Muscle Relaxants
    {"brand_name": "CYCLOBENZAPRINE", "company": "Various", "category": "Muscle Relaxant"},
    {"brand_name": "FLEXERIL", "company": "Janssen", "category": "Muscle Relaxant"},
    {"brand_name": "BACLOFEN", "company": "Various", "category": "Muscle Relaxant"},
    {"brand_name": "LIORESAL", "company": "Novartis", "category": "Muscle Relaxant"},
    {"brand_name": "METHOCARBAMOL", "company": "Various", "category": "Muscle Relaxant"},
    {"brand_name": "ROBAXIN", "company": "Pfizer", "category": "Muscle Relaxant"},
    {"brand_name": "TIZANIDINE", "company": "Various", "category": "Muscle Relaxant"},
    {"brand_name": "ZANAFLEX", "company": "Acorda", "category": "Muscle Relaxant"},

    # =========================================================================
    # GASTROINTESTINAL
    # =========================================================================
    {"brand_name": "OMEPRAZOLE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "LOSEC", "company": "AstraZeneca", "category": "Stomach/GERD"},
    {"brand_name": "PANTOPRAZOLE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "PANTOLOC", "company": "Takeda", "category": "Stomach/GERD"},
    {"brand_name": "ESOMEPRAZOLE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "NEXIUM", "company": "AstraZeneca", "category": "Stomach/GERD"},
    {"brand_name": "LANSOPRAZOLE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "PREVACID", "company": "Takeda", "category": "Stomach/GERD"},
    {"brand_name": "RABEPRAZOLE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "PARIET", "company": "Janssen", "category": "Stomach/GERD"},
    {"brand_name": "DEXLANSOPRAZOLE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "DEXILANT", "company": "Takeda", "category": "Stomach/GERD"},
    {"brand_name": "FAMOTIDINE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "PEPCID", "company": "Johnson & Johnson", "category": "Stomach/GERD"},
    {"brand_name": "RANITIDINE", "company": "Various", "category": "Stomach/GERD"},
    {"brand_name": "ONDANSETRON", "company": "Various", "category": "Nausea"},
    {"brand_name": "ZOFRAN", "company": "GSK", "category": "Nausea"},
    {"brand_name": "METOCLOPRAMIDE", "company": "Various", "category": "Nausea"},
    {"brand_name": "MAXERAN", "company": "Sanofi", "category": "Nausea"},
    {"brand_name": "DOMPERIDONE", "company": "Various", "category": "Nausea"},
    {"brand_name": "MOTILIUM", "company": "Janssen", "category": "Nausea"},
    {"brand_name": "DIMENHYDRINATE", "company": "Various", "category": "Nausea"},
    {"brand_name": "GRAVOL", "company": "Church & Dwight", "category": "Nausea"},
    {"brand_name": "PROCHLORPERAZINE", "company": "Various", "category": "Nausea"},
    {"brand_name": "STEMETIL", "company": "Sanofi", "category": "Nausea"},

    # Laxatives & GI
    {"brand_name": "DOCUSATE", "company": "Various", "category": "Laxative"},
    {"brand_name": "COLACE", "company": "Purdue", "category": "Laxative"},
    {"brand_name": "SENNOSIDES", "company": "Various", "category": "Laxative"},
    {"brand_name": "SENOKOT", "company": "Purdue", "category": "Laxative"},
    {"brand_name": "POLYETHYLENE GLYCOL", "company": "Various", "category": "Laxative"},
    {"brand_name": "RESTORALAX", "company": "Bayer", "category": "Laxative"},
    {"brand_name": "MIRALAX", "company": "Bayer", "category": "Laxative"},
    {"brand_name": "LACTULOSE", "company": "Various", "category": "Laxative"},
    {"brand_name": "LOPERAMIDE", "company": "Various", "category": "Anti-Diarrheal"},
    {"brand_name": "IMODIUM", "company": "Johnson & Johnson", "category": "Anti-Diarrheal"},
    {"brand_name": "LINACLOTIDE", "company": "Various", "category": "IBS"},
    {"brand_name": "LINZESS", "company": "Allergan", "category": "IBS"},
    {"brand_name": "CONSTELLA", "company": "Allergan", "category": "IBS"},

    # IBD Medications
    {"brand_name": "MESALAMINE", "company": "Various", "category": "IBD"},
    {"brand_name": "ASACOL", "company": "Warner Chilcott", "category": "IBD"},
    {"brand_name": "PENTASA", "company": "Shire", "category": "IBD"},
    {"brand_name": "SALOFALK", "company": "Dr. Falk", "category": "IBD"},
    {"brand_name": "MEZAVANT", "company": "Shire", "category": "IBD"},
    {"brand_name": "SULFASALAZINE", "company": "Various", "category": "IBD"},

    # =========================================================================
    # RESPIRATORY / ALLERGY
    # =========================================================================
    {"brand_name": "ALBUTEROL", "company": "Various", "category": "Asthma"},
    {"brand_name": "FLUTICASONE", "company": "Various", "category": "Asthma"},
    {"brand_name": "FLOVENT", "company": "GSK", "category": "Asthma"},
    {"brand_name": "BUDESONIDE", "company": "Various", "category": "Asthma"},
    {"brand_name": "PULMICORT", "company": "AstraZeneca", "category": "Asthma"},
    {"brand_name": "FLUTICASONE-SALMETEROL", "company": "Various", "category": "Asthma"},
    {"brand_name": "ADVAIR", "company": "GSK", "category": "Asthma"},
    {"brand_name": "BUDESONIDE-FORMOTEROL", "company": "Various", "category": "Asthma"},
    {"brand_name": "SYMBICORT", "company": "AstraZeneca", "category": "Asthma"},
    {"brand_name": "MONTELUKAST", "company": "Various", "category": "Asthma"},
    {"brand_name": "SINGULAIR", "company": "Merck", "category": "Asthma"},
    {"brand_name": "TIOTROPIUM", "company": "Various", "category": "COPD"},
    {"brand_name": "SPIRIVA", "company": "Boehringer", "category": "COPD"},
    {"brand_name": "IPRATROPIUM", "company": "Various", "category": "COPD"},
    {"brand_name": "ATROVENT", "company": "Boehringer", "category": "COPD"},
    {"brand_name": "UMECLIDINIUM", "company": "Various", "category": "COPD"},
    {"brand_name": "INCRUSE", "company": "GSK", "category": "COPD"},
    {"brand_name": "GLYCOPYRROLATE", "company": "Various", "category": "COPD"},
    {"brand_name": "TRELEGY", "company": "GSK", "category": "COPD"},
    {"brand_name": "BREO", "company": "GSK", "category": "COPD"},

    # Allergy
    {"brand_name": "CETIRIZINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "REACTINE", "company": "Johnson & Johnson", "category": "Allergy"},
    {"brand_name": "ZYRTEC", "company": "Johnson & Johnson", "category": "Allergy"},
    {"brand_name": "LORATADINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "CLARITIN", "company": "Bayer", "category": "Allergy"},
    {"brand_name": "FEXOFENADINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "ALLEGRA", "company": "Sanofi", "category": "Allergy"},
    {"brand_name": "DESLORATADINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "AERIUS", "company": "Merck", "category": "Allergy"},
    {"brand_name": "DIPHENHYDRAMINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "BENADRYL", "company": "Johnson & Johnson", "category": "Allergy"},
    {"brand_name": "HYDROXYZINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "ATARAX", "company": "Pfizer", "category": "Allergy"},

    # Nasal
    {"brand_name": "FLUTICASONE NASAL", "company": "Various", "category": "Nasal Spray"},
    {"brand_name": "FLONASE", "company": "GSK", "category": "Nasal Spray"},
    {"brand_name": "NASONEX", "company": "Merck", "category": "Nasal Spray"},
    {"brand_name": "MOMETASONE NASAL", "company": "Various", "category": "Nasal Spray"},
    {"brand_name": "RHINOCORT", "company": "AstraZeneca", "category": "Nasal Spray"},
    {"brand_name": "NASACORT", "company": "Sanofi", "category": "Nasal Spray"},
    {"brand_name": "AZELASTINE", "company": "Various", "category": "Nasal Spray"},
    {"brand_name": "ASTELIN", "company": "Valeant", "category": "Nasal Spray"},
    {"brand_name": "DYMISTA", "company": "Valeant", "category": "Nasal Spray"},

    # =========================================================================
    # ANTIBIOTICS
    # =========================================================================
    {"brand_name": "AMOXICILLIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "AMOXIL", "company": "GSK", "category": "Antibiotic"},
    {"brand_name": "AMOXICILLIN-CLAVULANATE", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "AUGMENTIN", "company": "GSK", "category": "Antibiotic"},
    {"brand_name": "CLAVULIN", "company": "GSK", "category": "Antibiotic"},
    {"brand_name": "AZITHROMYCIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "ZITHROMAX", "company": "Pfizer", "category": "Antibiotic"},
    {"brand_name": "CIPROFLOXACIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "CIPRO", "company": "Bayer", "category": "Antibiotic"},
    {"brand_name": "LEVOFLOXACIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "LEVAQUIN", "company": "Janssen", "category": "Antibiotic"},
    {"brand_name": "MOXIFLOXACIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "AVELOX", "company": "Bayer", "category": "Antibiotic"},
    {"brand_name": "DOXYCYCLINE", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "VIBRAMYCIN", "company": "Pfizer", "category": "Antibiotic"},
    {"brand_name": "CEPHALEXIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "KEFLEX", "company": "Shionogi", "category": "Antibiotic"},
    {"brand_name": "CEFUROXIME", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "CEFTIN", "company": "GSK", "category": "Antibiotic"},
    {"brand_name": "CEFIXIME", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "SUPRAX", "company": "Lupin", "category": "Antibiotic"},
    {"brand_name": "METRONIDAZOLE", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "FLAGYL", "company": "Pfizer", "category": "Antibiotic"},
    {"brand_name": "CLINDAMYCIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "DALACIN", "company": "Pfizer", "category": "Antibiotic"},
    {"brand_name": "NITROFURANTOIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "MACROBID", "company": "Procter & Gamble", "category": "Antibiotic"},
    {"brand_name": "SULFAMETHOXAZOLE-TRIMETHOPRIM", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "SEPTRA", "company": "Aspen", "category": "Antibiotic"},
    {"brand_name": "BACTRIM", "company": "Roche", "category": "Antibiotic"},
    {"brand_name": "PENICILLIN V", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "ERYTHROMYCIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "CLARITHROMYCIN", "company": "Various", "category": "Antibiotic"},
    {"brand_name": "BIAXIN", "company": "AbbVie", "category": "Antibiotic"},

    # Antifungals
    {"brand_name": "FLUCONAZOLE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "DIFLUCAN", "company": "Pfizer", "category": "Antifungal"},
    {"brand_name": "NYSTATIN", "company": "Various", "category": "Antifungal"},
    {"brand_name": "TERBINAFINE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "LAMISIL", "company": "Novartis", "category": "Antifungal"},
    {"brand_name": "CLOTRIMAZOLE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "CANESTEN", "company": "Bayer", "category": "Antifungal"},
    {"brand_name": "KETOCONAZOLE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "NIZORAL", "company": "Janssen", "category": "Antifungal"},

    # Antivirals
    {"brand_name": "ACYCLOVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "ZOVIRAX", "company": "GSK", "category": "Antiviral"},
    {"brand_name": "VALACYCLOVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "VALTREX", "company": "GSK", "category": "Antiviral"},
    {"brand_name": "FAMCICLOVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "FAMVIR", "company": "Novartis", "category": "Antiviral"},
    {"brand_name": "OSELTAMIVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "TAMIFLU", "company": "Roche", "category": "Antiviral"},
    {"brand_name": "PAXLOVID", "company": "Pfizer", "category": "Antiviral"},

    # =========================================================================
    # NEUROLOGICAL / SEIZURE
    # =========================================================================
    {"brand_name": "LEVETIRACETAM", "company": "Various", "category": "Seizure"},
    {"brand_name": "KEPPRA", "company": "UCB", "category": "Seizure"},
    {"brand_name": "LAMOTRIGINE", "company": "Various", "category": "Seizure"},
    {"brand_name": "LAMICTAL", "company": "GSK", "category": "Seizure"},
    {"brand_name": "TOPIRAMATE", "company": "Various", "category": "Seizure"},
    {"brand_name": "TOPAMAX", "company": "Janssen", "category": "Seizure"},
    {"brand_name": "VALPROIC ACID", "company": "Various", "category": "Seizure"},
    {"brand_name": "DEPAKOTE", "company": "AbbVie", "category": "Seizure"},
    {"brand_name": "EPIVAL", "company": "AbbVie", "category": "Seizure"},
    {"brand_name": "CARBAMAZEPINE", "company": "Various", "category": "Seizure"},
    {"brand_name": "TEGRETOL", "company": "Novartis", "category": "Seizure"},
    {"brand_name": "OXCARBAZEPINE", "company": "Various", "category": "Seizure"},
    {"brand_name": "TRILEPTAL", "company": "Novartis", "category": "Seizure"},
    {"brand_name": "PHENYTOIN", "company": "Various", "category": "Seizure"},
    {"brand_name": "DILANTIN", "company": "Pfizer", "category": "Seizure"},
    {"brand_name": "CLOBAZAM", "company": "Various", "category": "Seizure"},
    {"brand_name": "FRISIUM", "company": "Lundbeck", "category": "Seizure"},
    {"brand_name": "LACOSAMIDE", "company": "Various", "category": "Seizure"},
    {"brand_name": "VIMPAT", "company": "UCB", "category": "Seizure"},
    {"brand_name": "BRIVARACETAM", "company": "Various", "category": "Seizure"},
    {"brand_name": "BRIVLERA", "company": "UCB", "category": "Seizure"},

    # Parkinson's
    {"brand_name": "LEVODOPA-CARBIDOPA", "company": "Various", "category": "Parkinson's"},
    {"brand_name": "SINEMET", "company": "Merck", "category": "Parkinson's"},
    {"brand_name": "PRAMIPEXOLE", "company": "Various", "category": "Parkinson's"},
    {"brand_name": "MIRAPEX", "company": "Boehringer", "category": "Parkinson's"},
    {"brand_name": "ROPINIROLE", "company": "Various", "category": "Parkinson's"},
    {"brand_name": "REQUIP", "company": "GSK", "category": "Parkinson's"},
    {"brand_name": "RASAGILINE", "company": "Various", "category": "Parkinson's"},
    {"brand_name": "AZILECT", "company": "Teva", "category": "Parkinson's"},

    # Dementia
    {"brand_name": "DONEPEZIL", "company": "Various", "category": "Dementia"},
    {"brand_name": "ARICEPT", "company": "Eisai", "category": "Dementia"},
    {"brand_name": "MEMANTINE", "company": "Various", "category": "Dementia"},
    {"brand_name": "EBIXA", "company": "Lundbeck", "category": "Dementia"},
    {"brand_name": "RIVASTIGMINE", "company": "Various", "category": "Dementia"},
    {"brand_name": "EXELON", "company": "Novartis", "category": "Dementia"},
    {"brand_name": "GALANTAMINE", "company": "Various", "category": "Dementia"},
    {"brand_name": "REMINYL", "company": "Janssen", "category": "Dementia"},

    # Migraine
    {"brand_name": "SUMATRIPTAN", "company": "Various", "category": "Migraine"},
    {"brand_name": "IMITREX", "company": "GSK", "category": "Migraine"},
    {"brand_name": "RIZATRIPTAN", "company": "Various", "category": "Migraine"},
    {"brand_name": "MAXALT", "company": "Merck", "category": "Migraine"},
    {"brand_name": "ZOLMITRIPTAN", "company": "Various", "category": "Migraine"},
    {"brand_name": "ZOMIG", "company": "AstraZeneca", "category": "Migraine"},
    {"brand_name": "ERENUMAB", "company": "Various", "category": "Migraine Prevention"},
    {"brand_name": "AIMOVIG", "company": "Amgen", "category": "Migraine Prevention"},
    {"brand_name": "FREMANEZUMAB", "company": "Various", "category": "Migraine Prevention"},
    {"brand_name": "AJOVY", "company": "Teva", "category": "Migraine Prevention"},
    {"brand_name": "GALCANEZUMAB", "company": "Various", "category": "Migraine Prevention"},
    {"brand_name": "EMGALITY", "company": "Eli Lilly", "category": "Migraine Prevention"},

    # =========================================================================
    # ADHD MEDICATIONS
    # =========================================================================
    {"brand_name": "METHYLPHENIDATE", "company": "Various", "category": "ADHD"},
    {"brand_name": "RITALIN", "company": "Novartis", "category": "ADHD"},
    {"brand_name": "CONCERTA", "company": "Janssen", "category": "ADHD"},
    {"brand_name": "BIPHENTIN", "company": "Purdue", "category": "ADHD"},
    {"brand_name": "AMPHETAMINE SALTS", "company": "Various", "category": "ADHD"},
    {"brand_name": "ADDERALL", "company": "Teva", "category": "ADHD"},
    {"brand_name": "DEXTROAMPHETAMINE", "company": "Various", "category": "ADHD"},
    {"brand_name": "DEXEDRINE", "company": "Paladin", "category": "ADHD"},
    {"brand_name": "ATOMOXETINE", "company": "Various", "category": "ADHD"},
    {"brand_name": "STRATTERA", "company": "Eli Lilly", "category": "ADHD"},
    {"brand_name": "GUANFACINE", "company": "Various", "category": "ADHD"},
    {"brand_name": "INTUNIV", "company": "Takeda", "category": "ADHD"},
    {"brand_name": "CLONIDINE", "company": "Various", "category": "ADHD"},

    # =========================================================================
    # STEROIDS / ANTI-INFLAMMATORY
    # =========================================================================
    {"brand_name": "PREDNISONE", "company": "Various", "category": "Steroid"},
    {"brand_name": "PREDNISOLONE", "company": "Various", "category": "Steroid"},
    {"brand_name": "METHYLPREDNISOLONE", "company": "Various", "category": "Steroid"},
    {"brand_name": "MEDROL", "company": "Pfizer", "category": "Steroid"},
    {"brand_name": "DEXAMETHASONE", "company": "Various", "category": "Steroid"},
    {"brand_name": "DECADRON", "company": "Merck", "category": "Steroid"},
    {"brand_name": "HYDROCORTISONE", "company": "Various", "category": "Steroid"},
    {"brand_name": "CORTEF", "company": "Pfizer", "category": "Steroid"},
    {"brand_name": "BUDESONIDE ORAL", "company": "Various", "category": "Steroid"},
    {"brand_name": "ENTOCORT", "company": "AstraZeneca", "category": "Steroid"},

    # =========================================================================
    # BIOLOGICS & SPECIALTY
    # =========================================================================
    {"brand_name": "DUPIXENT", "company": "Sanofi/Regeneron", "category": "Biologic"},
    {"brand_name": "DUPILUMAB", "company": "Sanofi/Regeneron", "category": "Biologic"},
    {"brand_name": "HUMIRA", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "ADALIMUMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "ENBREL", "company": "Amgen", "category": "Biologic"},
    {"brand_name": "ETANERCEPT", "company": "Various", "category": "Biologic"},
    {"brand_name": "REMICADE", "company": "Janssen", "category": "Biologic"},
    {"brand_name": "INFLIXIMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "STELARA", "company": "Janssen", "category": "Biologic"},
    {"brand_name": "USTEKINUMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "COSENTYX", "company": "Novartis", "category": "Biologic"},
    {"brand_name": "SECUKINUMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "TALTZ", "company": "Eli Lilly", "category": "Biologic"},
    {"brand_name": "IXEKIZUMAB", "company": "Eli Lilly", "category": "Biologic"},
    {"brand_name": "SKYRIZI", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "RISANKIZUMAB", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "TREMFYA", "company": "Janssen", "category": "Biologic"},
    {"brand_name": "GUSELKUMAB", "company": "Janssen", "category": "Biologic"},
    {"brand_name": "RINVOQ", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "UPADACITINIB", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "XELJANZ", "company": "Pfizer", "category": "Biologic"},
    {"brand_name": "TOFACITINIB", "company": "Various", "category": "Biologic"},
    {"brand_name": "OTEZLA", "company": "Amgen", "category": "Biologic"},
    {"brand_name": "APREMILAST", "company": "Amgen", "category": "Biologic"},
    {"brand_name": "OLUMIANT", "company": "Eli Lilly", "category": "Biologic"},
    {"brand_name": "BARICITINIB", "company": "Eli Lilly", "category": "Biologic"},
    {"brand_name": "NUCALA", "company": "GSK", "category": "Biologic"},
    {"brand_name": "MEPOLIZUMAB", "company": "GSK", "category": "Biologic"},
    {"brand_name": "FASENRA", "company": "AstraZeneca", "category": "Biologic"},
    {"brand_name": "BENRALIZUMAB", "company": "AstraZeneca", "category": "Biologic"},
    {"brand_name": "XOLAIR", "company": "Novartis", "category": "Biologic"},
    {"brand_name": "OMALIZUMAB", "company": "Novartis", "category": "Biologic"},

    # =========================================================================
    # UROLOGY
    # =========================================================================
    {"brand_name": "TAMSULOSIN", "company": "Various", "category": "Urology"},
    {"brand_name": "FLOMAX", "company": "Boehringer", "category": "Urology"},
    {"brand_name": "SILODOSIN", "company": "Various", "category": "Urology"},
    {"brand_name": "RAPAFLO", "company": "Watson", "category": "Urology"},
    {"brand_name": "ALFUZOSIN", "company": "Various", "category": "Urology"},
    {"brand_name": "XATRAL", "company": "Sanofi", "category": "Urology"},
    {"brand_name": "FINASTERIDE", "company": "Various", "category": "Urology"},
    {"brand_name": "PROSCAR", "company": "Merck", "category": "Urology"},
    {"brand_name": "PROPECIA", "company": "Merck", "category": "Hair Loss"},
    {"brand_name": "DUTASTERIDE", "company": "Various", "category": "Urology"},
    {"brand_name": "AVODART", "company": "GSK", "category": "Urology"},
    {"brand_name": "OXYBUTYNIN", "company": "Various", "category": "Bladder"},
    {"brand_name": "DITROPAN", "company": "Janssen", "category": "Bladder"},
    {"brand_name": "TOLTERODINE", "company": "Various", "category": "Bladder"},
    {"brand_name": "DETROL", "company": "Pfizer", "category": "Bladder"},
    {"brand_name": "SOLIFENACIN", "company": "Various", "category": "Bladder"},
    {"brand_name": "VESICARE", "company": "Astellas", "category": "Bladder"},
    {"brand_name": "MIRABEGRON", "company": "Various", "category": "Bladder"},
    {"brand_name": "MYRBETRIQ", "company": "Astellas", "category": "Bladder"},
    {"brand_name": "SILDENAFIL", "company": "Various", "category": "ED"},
    {"brand_name": "VIAGRA", "company": "Pfizer", "category": "ED"},
    {"brand_name": "TADALAFIL", "company": "Various", "category": "ED"},
    {"brand_name": "CIALIS", "company": "Eli Lilly", "category": "ED"},

    # =========================================================================
    # EYE MEDICATIONS
    # =========================================================================
    {"brand_name": "LATANOPROST", "company": "Various", "category": "Glaucoma"},
    {"brand_name": "XALATAN", "company": "Pfizer", "category": "Glaucoma"},
    {"brand_name": "BIMATOPROST", "company": "Various", "category": "Glaucoma"},
    {"brand_name": "LUMIGAN", "company": "Allergan", "category": "Glaucoma"},
    {"brand_name": "TRAVOPROST", "company": "Various", "category": "Glaucoma"},
    {"brand_name": "TRAVATAN", "company": "Novartis", "category": "Glaucoma"},
    {"brand_name": "TIMOLOL", "company": "Various", "category": "Glaucoma"},
    {"brand_name": "TIMOPTIC", "company": "Merck", "category": "Glaucoma"},
    {"brand_name": "BRIMONIDINE", "company": "Various", "category": "Glaucoma"},
    {"brand_name": "ALPHAGAN", "company": "Allergan", "category": "Glaucoma"},
    {"brand_name": "DORZOLAMIDE", "company": "Various", "category": "Glaucoma"},
    {"brand_name": "TRUSOPT", "company": "Merck", "category": "Glaucoma"},
    {"brand_name": "DORZOLAMIDE-TIMOLOL", "company": "Various", "category": "Glaucoma"},
    {"brand_name": "COSOPT", "company": "Merck", "category": "Glaucoma"},
    {"brand_name": "CYCLOSPORINE EYE DROPS", "company": "Various", "category": "Dry Eye"},
    {"brand_name": "RESTASIS", "company": "Allergan", "category": "Dry Eye"},
    {"brand_name": "LIFITEGRAST", "company": "Various", "category": "Dry Eye"},
    {"brand_name": "XIIDRA", "company": "Novartis", "category": "Dry Eye"},

    # =========================================================================
    # OSTEOPOROSIS
    # =========================================================================
    {"brand_name": "ALENDRONATE", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "FOSAMAX", "company": "Merck", "category": "Osteoporosis"},
    {"brand_name": "RISEDRONATE", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "ACTONEL", "company": "Warner Chilcott", "category": "Osteoporosis"},
    {"brand_name": "DENOSUMAB", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "PROLIA", "company": "Amgen", "category": "Osteoporosis"},
    {"brand_name": "TERIPARATIDE", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "FORTEO", "company": "Eli Lilly", "category": "Osteoporosis"},
    {"brand_name": "ZOLEDRONIC ACID", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "ACLASTA", "company": "Novartis", "category": "Osteoporosis"},

    # =========================================================================
    # GOUT
    # =========================================================================
    {"brand_name": "ALLOPURINOL", "company": "Various", "category": "Gout"},
    {"brand_name": "ZYLOPRIM", "company": "Various", "category": "Gout"},
    {"brand_name": "FEBUXOSTAT", "company": "Various", "category": "Gout"},
    {"brand_name": "ULORIC", "company": "Takeda", "category": "Gout"},
    {"brand_name": "COLCHICINE", "company": "Various", "category": "Gout"},

    # =========================================================================
    # AUTOIMMUNE / RHEUMATOLOGY
    # =========================================================================
    {"brand_name": "METHOTREXATE", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "HYDROXYCHLOROQUINE", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "PLAQUENIL", "company": "Sanofi", "category": "Immunosuppressant"},
    {"brand_name": "LEFLUNOMIDE", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "ARAVA", "company": "Sanofi", "category": "Immunosuppressant"},
    {"brand_name": "AZATHIOPRINE", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "IMURAN", "company": "Paladin", "category": "Immunosuppressant"},
    {"brand_name": "MYCOPHENOLATE", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "CELLCEPT", "company": "Roche", "category": "Immunosuppressant"},
    {"brand_name": "TACROLIMUS", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "PROGRAF", "company": "Astellas", "category": "Immunosuppressant"},
    {"brand_name": "CYCLOSPORINE", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "NEORAL", "company": "Novartis", "category": "Immunosuppressant"},

    # =========================================================================
    # SUPPLEMENTS / VITAMINS
    # =========================================================================
    {"brand_name": "VITAMIN D", "company": "Various", "category": "Supplement"},
    {"brand_name": "VITAMIN D3", "company": "Various", "category": "Supplement"},
    {"brand_name": "CHOLECALCIFEROL", "company": "Various", "category": "Supplement"},
    {"brand_name": "D-TABS", "company": "Various", "category": "Supplement"},
    {"brand_name": "VITAMIN B12", "company": "Various", "category": "Supplement"},
    {"brand_name": "CYANOCOBALAMIN", "company": "Various", "category": "Supplement"},
    {"brand_name": "FOLIC ACID", "company": "Various", "category": "Supplement"},
    {"brand_name": "FOLATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "IRON", "company": "Various", "category": "Supplement"},
    {"brand_name": "FERROUS SULFATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "FERROUS GLUCONATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "FERROUS FUMARATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "CALCIUM", "company": "Various", "category": "Supplement"},
    {"brand_name": "CALCIUM CARBONATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "CALCIUM CITRATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "MAGNESIUM", "company": "Various", "category": "Supplement"},
    {"brand_name": "POTASSIUM CHLORIDE", "company": "Various", "category": "Supplement"},
    {"brand_name": "K-DUR", "company": "Various", "category": "Supplement"},
    {"brand_name": "SLOW-K", "company": "Various", "category": "Supplement"},
    {"brand_name": "OMEGA-3", "company": "Various", "category": "Supplement"},
    {"brand_name": "FISH OIL", "company": "Various", "category": "Supplement"},

    # =========================================================================
    # HORMONES
    # =========================================================================
    {"brand_name": "ESTRADIOL", "company": "Various", "category": "Hormone"},
    {"brand_name": "ESTRACE", "company": "Warner Chilcott", "category": "Hormone"},
    {"brand_name": "PREMARIN", "company": "Pfizer", "category": "Hormone"},
    {"brand_name": "PROGESTERONE", "company": "Various", "category": "Hormone"},
    {"brand_name": "PROMETRIUM", "company": "AbbVie", "category": "Hormone"},
    {"brand_name": "MEDROXYPROGESTERONE", "company": "Various", "category": "Hormone"},
    {"brand_name": "PROVERA", "company": "Pfizer", "category": "Hormone"},
    {"brand_name": "TESTOSTERONE", "company": "Various", "category": "Hormone"},
    {"brand_name": "ANDROGEL", "company": "AbbVie", "category": "Hormone"},

    # Contraceptives
    {"brand_name": "ALESSE", "company": "Pfizer", "category": "Birth Control"},
    {"brand_name": "YASMIN", "company": "Bayer", "category": "Birth Control"},
    {"brand_name": "YAZ", "company": "Bayer", "category": "Birth Control"},
    {"brand_name": "MARVELON", "company": "Organon", "category": "Birth Control"},
    {"brand_name": "TRI-CYCLEN", "company": "Janssen", "category": "Birth Control"},
    {"brand_name": "DIANE-35", "company": "Bayer", "category": "Birth Control"},
    {"brand_name": "LOLO", "company": "Allergan", "category": "Birth Control"},
    {"brand_name": "MIRENA", "company": "Bayer", "category": "Birth Control"},
    {"brand_name": "KYLEENA", "company": "Bayer", "category": "Birth Control"},
    {"brand_name": "NUVARING", "company": "Organon", "category": "Birth Control"},
    {"brand_name": "DEPO-PROVERA", "company": "Pfizer", "category": "Birth Control"},

    # =========================================================================
    # DERMATOLOGY
    # =========================================================================
    {"brand_name": "BETAMETHASONE", "company": "Various", "category": "Skin Steroid"},
    {"brand_name": "DIPROSONE", "company": "Merck", "category": "Skin Steroid"},
    {"brand_name": "CLOBETASOL", "company": "Various", "category": "Skin Steroid"},
    {"brand_name": "DERMOVATE", "company": "GSK", "category": "Skin Steroid"},
    {"brand_name": "TRIAMCINOLONE", "company": "Various", "category": "Skin Steroid"},
    {"brand_name": "KENALOG", "company": "Bristol-Myers", "category": "Skin Steroid"},
    {"brand_name": "HYDROCORTISONE CREAM", "company": "Various", "category": "Skin Steroid"},
    {"brand_name": "MOMETASONE", "company": "Various", "category": "Skin Steroid"},
    {"brand_name": "ELOCOM", "company": "Merck", "category": "Skin Steroid"},
    {"brand_name": "TACROLIMUS OINTMENT", "company": "Various", "category": "Skin"},
    {"brand_name": "PROTOPIC", "company": "LEO Pharma", "category": "Skin"},
    {"brand_name": "PIMECROLIMUS", "company": "Various", "category": "Skin"},
    {"brand_name": "ELIDEL", "company": "Valeant", "category": "Skin"},
    {"brand_name": "TRETINOIN", "company": "Various", "category": "Acne"},
    {"brand_name": "RETIN-A", "company": "Valeant", "category": "Acne"},
    {"brand_name": "ADAPALENE", "company": "Various", "category": "Acne"},
    {"brand_name": "DIFFERIN", "company": "Galderma", "category": "Acne"},
    {"brand_name": "BENZOYL PEROXIDE", "company": "Various", "category": "Acne"},
    {"brand_name": "ISOTRETINOIN", "company": "Various", "category": "Acne"},
    {"brand_name": "ACCUTANE", "company": "Roche", "category": "Acne"},
    {"brand_name": "CLINDAMYCIN GEL", "company": "Various", "category": "Acne"},
    {"brand_name": "CALCIPOTRIOL", "company": "Various", "category": "Psoriasis"},
    {"brand_name": "DOVONEX", "company": "LEO Pharma", "category": "Psoriasis"},
    {"brand_name": "DOVOBET", "company": "LEO Pharma", "category": "Psoriasis"},
    {"brand_name": "ENSTILAR", "company": "LEO Pharma", "category": "Psoriasis"},
]

    # Cardiovascular
    {"brand_name": "LIPITOR", "company": "Pfizer", "category": "Cardiovascular"},
    {"brand_name": "ATORVASTATIN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "CRESTOR", "company": "AstraZeneca", "category": "Cardiovascular"},
    {"brand_name": "ROSUVASTATIN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "ZOCOR", "company": "Merck", "category": "Cardiovascular"},
    {"brand_name": "SIMVASTATIN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "PRAVACHOL", "company": "Bristol-Myers Squibb", "category": "Cardiovascular"},
    {"brand_name": "RAMIPRIL", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "ALTACE", "company": "Sanofi", "category": "Cardiovascular"},
    {"brand_name": "LISINOPRIL", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "ENALAPRIL", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "LOSARTAN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "COZAAR", "company": "Merck", "category": "Cardiovascular"},
    {"brand_name": "VALSARTAN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "DIOVAN", "company": "Novartis", "category": "Cardiovascular"},
    {"brand_name": "AMLODIPINE", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "NORVASC", "company": "Pfizer", "category": "Cardiovascular"},
    {"brand_name": "METOPROLOL", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "LOPRESSOR", "company": "Novartis", "category": "Cardiovascular"},
    {"brand_name": "ATENOLOL", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "BISOPROLOL", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "CARVEDILOL", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "HYDROCHLOROTHIAZIDE", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "FUROSEMIDE", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "LASIX", "company": "Sanofi", "category": "Cardiovascular"},
    {"brand_name": "SPIRONOLACTONE", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "WARFARIN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "COUMADIN", "company": "Bristol-Myers Squibb", "category": "Cardiovascular"},
    {"brand_name": "ELIQUIS", "company": "Bristol-Myers Squibb", "category": "Cardiovascular"},
    {"brand_name": "APIXABAN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "XARELTO", "company": "Bayer", "category": "Cardiovascular"},
    {"brand_name": "RIVAROXABAN", "company": "Various", "category": "Cardiovascular"},
    {"brand_name": "PRADAXA", "company": "Boehringer Ingelheim", "category": "Cardiovascular"},
    {"brand_name": "PLAVIX", "company": "Sanofi", "category": "Cardiovascular"},
    {"brand_name": "CLOPIDOGREL", "company": "Various", "category": "Cardiovascular"},

    # Diabetes
    {"brand_name": "METFORMIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "GLUCOPHAGE", "company": "Bristol-Myers Squibb", "category": "Diabetes"},
    {"brand_name": "JANUVIA", "company": "Merck", "category": "Diabetes"},
    {"brand_name": "SITAGLIPTIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "JARDIANCE", "company": "Boehringer Ingelheim", "category": "Diabetes"},
    {"brand_name": "EMPAGLIFLOZIN", "company": "Various", "category": "Diabetes"},
    {"brand_name": "FORXIGA", "company": "AstraZeneca", "category": "Diabetes"},
    {"brand_name": "INVOKANA", "company": "Janssen", "category": "Diabetes"},
    {"brand_name": "OZEMPIC", "company": "Novo Nordisk", "category": "Diabetes"},
    {"brand_name": "SEMAGLUTIDE", "company": "Novo Nordisk", "category": "Diabetes"},
    {"brand_name": "TRULICITY", "company": "Eli Lilly", "category": "Diabetes"},
    {"brand_name": "VICTOZA", "company": "Novo Nordisk", "category": "Diabetes"},
    {"brand_name": "GLYBURIDE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "GLICLAZIDE", "company": "Various", "category": "Diabetes"},
    {"brand_name": "DIAMICRON", "company": "Servier", "category": "Diabetes"},
    {"brand_name": "INSULIN GLARGINE", "company": "Sanofi", "category": "Diabetes"},
    {"brand_name": "LANTUS", "company": "Sanofi", "category": "Diabetes"},
    {"brand_name": "HUMALOG", "company": "Eli Lilly", "category": "Diabetes"},
    {"brand_name": "NOVOLOG", "company": "Novo Nordisk", "category": "Diabetes"},
    {"brand_name": "NOVORAPID", "company": "Novo Nordisk", "category": "Diabetes"},

    # Thyroid
    {"brand_name": "SYNTHROID", "company": "AbbVie", "category": "Thyroid"},
    {"brand_name": "LEVOTHYROXINE", "company": "Various", "category": "Thyroid"},
    {"brand_name": "ELTROXIN", "company": "Aspen", "category": "Thyroid"},
    {"brand_name": "CYTOMEL", "company": "Pfizer", "category": "Thyroid"},

    # Gastrointestinal
    {"brand_name": "OMEPRAZOLE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "LOSEC", "company": "AstraZeneca", "category": "Gastrointestinal"},
    {"brand_name": "PRILOSEC", "company": "AstraZeneca", "category": "Gastrointestinal"},
    {"brand_name": "PANTOPRAZOLE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "PANTOLOC", "company": "Takeda", "category": "Gastrointestinal"},
    {"brand_name": "NEXIUM", "company": "AstraZeneca", "category": "Gastrointestinal"},
    {"brand_name": "ESOMEPRAZOLE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "PREVACID", "company": "Takeda", "category": "Gastrointestinal"},
    {"brand_name": "LANSOPRAZOLE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "ZANTAC", "company": "GSK", "category": "Gastrointestinal"},
    {"brand_name": "RANITIDINE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "PEPCID", "company": "Johnson & Johnson", "category": "Gastrointestinal"},
    {"brand_name": "FAMOTIDINE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "DOMPERIDONE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "METOCLOPRAMIDE", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "ONDANSETRON", "company": "Various", "category": "Gastrointestinal"},
    {"brand_name": "ZOFRAN", "company": "GSK", "category": "Gastrointestinal"},

    # Mental Health
    {"brand_name": "SERTRALINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "ZOLOFT", "company": "Pfizer", "category": "Mental Health"},
    {"brand_name": "ESCITALOPRAM", "company": "Various", "category": "Mental Health"},
    {"brand_name": "CIPRALEX", "company": "Lundbeck", "category": "Mental Health"},
    {"brand_name": "LEXAPRO", "company": "Forest Labs", "category": "Mental Health"},
    {"brand_name": "CITALOPRAM", "company": "Various", "category": "Mental Health"},
    {"brand_name": "CELEXA", "company": "Forest Labs", "category": "Mental Health"},
    {"brand_name": "FLUOXETINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "PROZAC", "company": "Eli Lilly", "category": "Mental Health"},
    {"brand_name": "PAROXETINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "PAXIL", "company": "GSK", "category": "Mental Health"},
    {"brand_name": "VENLAFAXINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "EFFEXOR", "company": "Pfizer", "category": "Mental Health"},
    {"brand_name": "DULOXETINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "CYMBALTA", "company": "Eli Lilly", "category": "Mental Health"},
    {"brand_name": "BUPROPION", "company": "Various", "category": "Mental Health"},
    {"brand_name": "WELLBUTRIN", "company": "GSK", "category": "Mental Health"},
    {"brand_name": "MIRTAZAPINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "REMERON", "company": "Organon", "category": "Mental Health"},
    {"brand_name": "TRAZODONE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "AMITRIPTYLINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "NORTRIPTYLINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "QUETIAPINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "SEROQUEL", "company": "AstraZeneca", "category": "Mental Health"},
    {"brand_name": "OLANZAPINE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "ZYPREXA", "company": "Eli Lilly", "category": "Mental Health"},
    {"brand_name": "RISPERIDONE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "RISPERDAL", "company": "Janssen", "category": "Mental Health"},
    {"brand_name": "ARIPIPRAZOLE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "ABILIFY", "company": "Bristol-Myers Squibb", "category": "Mental Health"},
    {"brand_name": "LORAZEPAM", "company": "Various", "category": "Mental Health"},
    {"brand_name": "ATIVAN", "company": "Pfizer", "category": "Mental Health"},
    {"brand_name": "CLONAZEPAM", "company": "Various", "category": "Mental Health"},
    {"brand_name": "RIVOTRIL", "company": "Roche", "category": "Mental Health"},
    {"brand_name": "DIAZEPAM", "company": "Various", "category": "Mental Health"},
    {"brand_name": "VALIUM", "company": "Roche", "category": "Mental Health"},
    {"brand_name": "ALPRAZOLAM", "company": "Various", "category": "Mental Health"},
    {"brand_name": "XANAX", "company": "Pfizer", "category": "Mental Health"},
    {"brand_name": "ZOPICLONE", "company": "Various", "category": "Mental Health"},
    {"brand_name": "IMOVANE", "company": "Sanofi", "category": "Mental Health"},
    {"brand_name": "ZOLPIDEM", "company": "Various", "category": "Mental Health"},

    # Neurological
    {"brand_name": "GABAPENTIN", "company": "Various", "category": "Neurological"},
    {"brand_name": "NEURONTIN", "company": "Pfizer", "category": "Neurological"},
    {"brand_name": "PREGABALIN", "company": "Various", "category": "Neurological"},
    {"brand_name": "LYRICA", "company": "Pfizer", "category": "Neurological"},
    {"brand_name": "TOPIRAMATE", "company": "Various", "category": "Neurological"},
    {"brand_name": "TOPAMAX", "company": "Janssen", "category": "Neurological"},
    {"brand_name": "LEVETIRACETAM", "company": "Various", "category": "Neurological"},
    {"brand_name": "KEPPRA", "company": "UCB", "category": "Neurological"},
    {"brand_name": "CARBAMAZEPINE", "company": "Various", "category": "Neurological"},
    {"brand_name": "TEGRETOL", "company": "Novartis", "category": "Neurological"},
    {"brand_name": "VALPROIC ACID", "company": "Various", "category": "Neurological"},
    {"brand_name": "DEPAKOTE", "company": "AbbVie", "category": "Neurological"},
    {"brand_name": "LAMOTRIGINE", "company": "Various", "category": "Neurological"},
    {"brand_name": "LAMICTAL", "company": "GSK", "category": "Neurological"},
    {"brand_name": "SUMATRIPTAN", "company": "Various", "category": "Neurological"},
    {"brand_name": "IMITREX", "company": "GSK", "category": "Neurological"},

    # Respiratory
    {"brand_name": "SALBUTAMOL", "company": "Various", "category": "Respiratory"},
    {"brand_name": "VENTOLIN", "company": "GSK", "category": "Respiratory"},
    {"brand_name": "ALBUTEROL", "company": "Various", "category": "Respiratory"},
    {"brand_name": "FLUTICASONE", "company": "Various", "category": "Respiratory"},
    {"brand_name": "FLOVENT", "company": "GSK", "category": "Respiratory"},
    {"brand_name": "ADVAIR", "company": "GSK", "category": "Respiratory"},
    {"brand_name": "SYMBICORT", "company": "AstraZeneca", "category": "Respiratory"},
    {"brand_name": "BUDESONIDE", "company": "Various", "category": "Respiratory"},
    {"brand_name": "PULMICORT", "company": "AstraZeneca", "category": "Respiratory"},
    {"brand_name": "MONTELUKAST", "company": "Various", "category": "Respiratory"},
    {"brand_name": "SINGULAIR", "company": "Merck", "category": "Respiratory"},
    {"brand_name": "TIOTROPIUM", "company": "Boehringer Ingelheim", "category": "Respiratory"},
    {"brand_name": "SPIRIVA", "company": "Boehringer Ingelheim", "category": "Respiratory"},
    {"brand_name": "IPRATROPIUM", "company": "Various", "category": "Respiratory"},
    {"brand_name": "ATROVENT", "company": "Boehringer Ingelheim", "category": "Respiratory"},

    # Antibiotics
    {"brand_name": "AMOXICILLIN", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "AMOXIL", "company": "GSK", "category": "Antibiotics"},
    {"brand_name": "AMOXICILLIN-CLAVULANATE", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "AUGMENTIN", "company": "GSK", "category": "Antibiotics"},
    {"brand_name": "CLAVULIN", "company": "GSK", "category": "Antibiotics"},
    {"brand_name": "AZITHROMYCIN", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "ZITHROMAX", "company": "Pfizer", "category": "Antibiotics"},
    {"brand_name": "CIPROFLOXACIN", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "CIPRO", "company": "Bayer", "category": "Antibiotics"},
    {"brand_name": "LEVOFLOXACIN", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "LEVAQUIN", "company": "Janssen", "category": "Antibiotics"},
    {"brand_name": "METRONIDAZOLE", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "FLAGYL", "company": "Pfizer", "category": "Antibiotics"},
    {"brand_name": "CLINDAMYCIN", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "DOXYCYCLINE", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "CEPHALEXIN", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "KEFLEX", "company": "Shionogi", "category": "Antibiotics"},
    {"brand_name": "NITROFURANTOIN", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "MACROBID", "company": "Procter & Gamble", "category": "Antibiotics"},
    {"brand_name": "SULFAMETHOXAZOLE-TRIMETHOPRIM", "company": "Various", "category": "Antibiotics"},
    {"brand_name": "SEPTRA", "company": "Aspen", "category": "Antibiotics"},
    {"brand_name": "BACTRIM", "company": "Roche", "category": "Antibiotics"},

    # Allergy
    {"brand_name": "CETIRIZINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "REACTINE", "company": "Johnson & Johnson", "category": "Allergy"},
    {"brand_name": "ZYRTEC", "company": "Johnson & Johnson", "category": "Allergy"},
    {"brand_name": "LORATADINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "CLARITIN", "company": "Bayer", "category": "Allergy"},
    {"brand_name": "FEXOFENADINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "ALLEGRA", "company": "Sanofi", "category": "Allergy"},
    {"brand_name": "DIPHENHYDRAMINE", "company": "Various", "category": "Allergy"},
    {"brand_name": "BENADRYL", "company": "Johnson & Johnson", "category": "Allergy"},
    {"brand_name": "HYDROXYZINE", "company": "Various", "category": "Allergy"},

    # Steroids
    {"brand_name": "PREDNISONE", "company": "Various", "category": "Steroids"},
    {"brand_name": "PREDNISOLONE", "company": "Various", "category": "Steroids"},
    {"brand_name": "DEXAMETHASONE", "company": "Various", "category": "Steroids"},
    {"brand_name": "METHYLPREDNISOLONE", "company": "Various", "category": "Steroids"},
    {"brand_name": "MEDROL", "company": "Pfizer", "category": "Steroids"},
    {"brand_name": "HYDROCORTISONE", "company": "Various", "category": "Steroids"},

    # Other Common Medications
    {"brand_name": "ALLOPURINOL", "company": "Various", "category": "Gout"},
    {"brand_name": "ZYLOPRIM", "company": "Prometheus", "category": "Gout"},
    {"brand_name": "COLCHICINE", "company": "Various", "category": "Gout"},
    {"brand_name": "METHOTREXATE", "company": "Various", "category": "Immunosuppressant"},
    {"brand_name": "FINASTERIDE", "company": "Various", "category": "Urology"},
    {"brand_name": "PROSCAR", "company": "Merck", "category": "Urology"},
    {"brand_name": "TAMSULOSIN", "company": "Various", "category": "Urology"},
    {"brand_name": "FLOMAX", "company": "Boehringer Ingelheim", "category": "Urology"},
    {"brand_name": "SILDENAFIL", "company": "Various", "category": "Urology"},
    {"brand_name": "VIAGRA", "company": "Pfizer", "category": "Urology"},
    {"brand_name": "TADALAFIL", "company": "Various", "category": "Urology"},
    {"brand_name": "CIALIS", "company": "Eli Lilly", "category": "Urology"},
    {"brand_name": "CYCLOBENZAPRINE", "company": "Various", "category": "Muscle Relaxant"},
    {"brand_name": "FLEXERIL", "company": "Janssen", "category": "Muscle Relaxant"},
    {"brand_name": "BACLOFEN", "company": "Various", "category": "Muscle Relaxant"},
    {"brand_name": "METHOCARBAMOL", "company": "Various", "category": "Muscle Relaxant"},
    {"brand_name": "ROBAXIN", "company": "Pfizer", "category": "Muscle Relaxant"},

    # Biologics & Specialty Medications
    {"brand_name": "DUPIXENT", "company": "Sanofi/Regeneron", "category": "Biologic"},
    {"brand_name": "DUPILUMAB", "company": "Sanofi/Regeneron", "category": "Biologic"},
    {"brand_name": "HUMIRA", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "ADALIMUMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "ENBREL", "company": "Amgen", "category": "Biologic"},
    {"brand_name": "ETANERCEPT", "company": "Various", "category": "Biologic"},
    {"brand_name": "REMICADE", "company": "Janssen", "category": "Biologic"},
    {"brand_name": "INFLIXIMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "STELARA", "company": "Janssen", "category": "Biologic"},
    {"brand_name": "USTEKINUMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "COSENTYX", "company": "Novartis", "category": "Biologic"},
    {"brand_name": "SECUKINUMAB", "company": "Various", "category": "Biologic"},
    {"brand_name": "TALTZ", "company": "Eli Lilly", "category": "Biologic"},
    {"brand_name": "SKYRIZI", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "RISANKIZUMAB", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "TREMFYA", "company": "Janssen", "category": "Biologic"},
    {"brand_name": "RINVOQ", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "UPADACITINIB", "company": "AbbVie", "category": "Biologic"},
    {"brand_name": "XELJANZ", "company": "Pfizer", "category": "Biologic"},
    {"brand_name": "TOFACITINIB", "company": "Various", "category": "Biologic"},
    {"brand_name": "OTEZLA", "company": "Amgen", "category": "Biologic"},
    {"brand_name": "APREMILAST", "company": "Various", "category": "Biologic"},
    {"brand_name": "KEYTRUDA", "company": "Merck", "category": "Oncology"},
    {"brand_name": "PEMBROLIZUMAB", "company": "Merck", "category": "Oncology"},
    {"brand_name": "OPDIVO", "company": "Bristol-Myers Squibb", "category": "Oncology"},
    {"brand_name": "NIVOLUMAB", "company": "Various", "category": "Oncology"},
    {"brand_name": "HERCEPTIN", "company": "Roche", "category": "Oncology"},
    {"brand_name": "TRASTUZUMAB", "company": "Various", "category": "Oncology"},
    {"brand_name": "AVASTIN", "company": "Roche", "category": "Oncology"},
    {"brand_name": "RITUXAN", "company": "Roche", "category": "Oncology"},
    {"brand_name": "RITUXIMAB", "company": "Various", "category": "Oncology"},

    # Dermatology
    {"brand_name": "EUCRISA", "company": "Pfizer", "category": "Dermatology"},
    {"brand_name": "CRISABOROLE", "company": "Pfizer", "category": "Dermatology"},
    {"brand_name": "ELIDEL", "company": "Valeant", "category": "Dermatology"},
    {"brand_name": "PIMECROLIMUS", "company": "Various", "category": "Dermatology"},
    {"brand_name": "PROTOPIC", "company": "LEO Pharma", "category": "Dermatology"},
    {"brand_name": "TACROLIMUS", "company": "Various", "category": "Dermatology"},
    {"brand_name": "BETAMETHASONE", "company": "Various", "category": "Dermatology"},
    {"brand_name": "CLOBETASOL", "company": "Various", "category": "Dermatology"},
    {"brand_name": "TRIAMCINOLONE", "company": "Various", "category": "Dermatology"},
    {"brand_name": "MOMETASONE", "company": "Various", "category": "Dermatology"},
    {"brand_name": "NASONEX", "company": "Merck", "category": "Dermatology"},
    {"brand_name": "DOVONEX", "company": "LEO Pharma", "category": "Dermatology"},
    {"brand_name": "CALCIPOTRIOL", "company": "Various", "category": "Dermatology"},
    {"brand_name": "ADAPALENE", "company": "Various", "category": "Dermatology"},
    {"brand_name": "DIFFERIN", "company": "Galderma", "category": "Dermatology"},
    {"brand_name": "TRETINOIN", "company": "Various", "category": "Dermatology"},
    {"brand_name": "RETIN-A", "company": "Valeant", "category": "Dermatology"},
    {"brand_name": "BENZOYL PEROXIDE", "company": "Various", "category": "Dermatology"},
    {"brand_name": "CLINDAMYCIN GEL", "company": "Various", "category": "Dermatology"},
    {"brand_name": "ACCUTANE", "company": "Roche", "category": "Dermatology"},
    {"brand_name": "ISOTRETINOIN", "company": "Various", "category": "Dermatology"},
    {"brand_name": "KETOCONAZOLE", "company": "Various", "category": "Dermatology"},
    {"brand_name": "NIZORAL", "company": "Janssen", "category": "Dermatology"},
    {"brand_name": "TERBINAFINE", "company": "Various", "category": "Dermatology"},
    {"brand_name": "LAMISIL", "company": "Novartis", "category": "Dermatology"},

    # Eye Medications
    {"brand_name": "LATANOPROST", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "XALATAN", "company": "Pfizer", "category": "Ophthalmology"},
    {"brand_name": "LUMIGAN", "company": "Allergan", "category": "Ophthalmology"},
    {"brand_name": "BIMATOPROST", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "TRAVATAN", "company": "Novartis", "category": "Ophthalmology"},
    {"brand_name": "TIMOLOL", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "BRIMONIDINE", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "ALPHAGAN", "company": "Allergan", "category": "Ophthalmology"},
    {"brand_name": "DORZOLAMIDE", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "COSOPT", "company": "Merck", "category": "Ophthalmology"},
    {"brand_name": "RESTASIS", "company": "Allergan", "category": "Ophthalmology"},
    {"brand_name": "CYCLOSPORINE EYE", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "XIIDRA", "company": "Novartis", "category": "Ophthalmology"},
    {"brand_name": "LIFITEGRAST", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "TOBRAMYCIN EYE", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "TOBREX", "company": "Novartis", "category": "Ophthalmology"},
    {"brand_name": "VIGAMOX", "company": "Novartis", "category": "Ophthalmology"},
    {"brand_name": "MOXIFLOXACIN EYE", "company": "Various", "category": "Ophthalmology"},
    {"brand_name": "PRED FORTE", "company": "Allergan", "category": "Ophthalmology"},
    {"brand_name": "PREDNISOLONE EYE", "company": "Various", "category": "Ophthalmology"},

    # Osteoporosis
    {"brand_name": "ALENDRONATE", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "FOSAMAX", "company": "Merck", "category": "Osteoporosis"},
    {"brand_name": "RISEDRONATE", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "ACTONEL", "company": "Warner Chilcott", "category": "Osteoporosis"},
    {"brand_name": "PROLIA", "company": "Amgen", "category": "Osteoporosis"},
    {"brand_name": "DENOSUMAB", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "FORTEO", "company": "Eli Lilly", "category": "Osteoporosis"},
    {"brand_name": "TERIPARATIDE", "company": "Various", "category": "Osteoporosis"},
    {"brand_name": "EVENITY", "company": "Amgen", "category": "Osteoporosis"},
    {"brand_name": "CALCIUM CARBONATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "VITAMIN D", "company": "Various", "category": "Supplement"},
    {"brand_name": "VITAMIN D3", "company": "Various", "category": "Supplement"},
    {"brand_name": "VITAMIN B12", "company": "Various", "category": "Supplement"},
    {"brand_name": "FOLIC ACID", "company": "Various", "category": "Supplement"},
    {"brand_name": "IRON SUPPLEMENT", "company": "Various", "category": "Supplement"},
    {"brand_name": "FERROUS SULFATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "FERROUS GLUCONATE", "company": "Various", "category": "Supplement"},
    {"brand_name": "MAGNESIUM", "company": "Various", "category": "Supplement"},
    {"brand_name": "POTASSIUM CHLORIDE", "company": "Various", "category": "Supplement"},
    {"brand_name": "K-DUR", "company": "Various", "category": "Supplement"},

    # Hormones & Reproductive
    {"brand_name": "ESTRADIOL", "company": "Various", "category": "Hormone"},
    {"brand_name": "ESTRACE", "company": "Warner Chilcott", "category": "Hormone"},
    {"brand_name": "PREMARIN", "company": "Pfizer", "category": "Hormone"},
    {"brand_name": "PROGESTERONE", "company": "Various", "category": "Hormone"},
    {"brand_name": "PROMETRIUM", "company": "AbbVie", "category": "Hormone"},
    {"brand_name": "TESTOSTERONE", "company": "Various", "category": "Hormone"},
    {"brand_name": "ANDROGEL", "company": "AbbVie", "category": "Hormone"},
    {"brand_name": "BIRTH CONTROL PILL", "company": "Various", "category": "Contraceptive"},
    {"brand_name": "ALESSE", "company": "Pfizer", "category": "Contraceptive"},
    {"brand_name": "YASMIN", "company": "Bayer", "category": "Contraceptive"},
    {"brand_name": "MARVELON", "company": "Organon", "category": "Contraceptive"},
    {"brand_name": "TRI-CYCLEN", "company": "Janssen", "category": "Contraceptive"},
    {"brand_name": "NUVARING", "company": "Organon", "category": "Contraceptive"},
    {"brand_name": "MIRENA", "company": "Bayer", "category": "Contraceptive"},
    {"brand_name": "CLOMID", "company": "Sanofi", "category": "Fertility"},
    {"brand_name": "CLOMIPHENE", "company": "Various", "category": "Fertility"},
    {"brand_name": "LETROZOLE", "company": "Various", "category": "Fertility"},
    {"brand_name": "FEMARA", "company": "Novartis", "category": "Fertility"},

    # ADHD & Stimulants
    {"brand_name": "ADDERALL", "company": "Teva", "category": "ADHD"},
    {"brand_name": "AMPHETAMINE", "company": "Various", "category": "ADHD"},
    {"brand_name": "VYVANSE", "company": "Takeda", "category": "ADHD"},
    {"brand_name": "LISDEXAMFETAMINE", "company": "Various", "category": "ADHD"},
    {"brand_name": "RITALIN", "company": "Novartis", "category": "ADHD"},
    {"brand_name": "METHYLPHENIDATE", "company": "Various", "category": "ADHD"},
    {"brand_name": "CONCERTA", "company": "Janssen", "category": "ADHD"},
    {"brand_name": "BIPHENTIN", "company": "Purdue", "category": "ADHD"},
    {"brand_name": "STRATTERA", "company": "Eli Lilly", "category": "ADHD"},
    {"brand_name": "ATOMOXETINE", "company": "Various", "category": "ADHD"},
    {"brand_name": "INTUNIV", "company": "Takeda", "category": "ADHD"},
    {"brand_name": "GUANFACINE", "company": "Various", "category": "ADHD"},
    {"brand_name": "MODAFINIL", "company": "Various", "category": "Wakefulness"},
    {"brand_name": "ALERTEC", "company": "Shire", "category": "Wakefulness"},
    {"brand_name": "PROVIGIL", "company": "Teva", "category": "Wakefulness"},

    # Migraine
    {"brand_name": "SUMATRIPTAN", "company": "Various", "category": "Migraine"},
    {"brand_name": "IMITREX", "company": "GSK", "category": "Migraine"},
    {"brand_name": "RIZATRIPTAN", "company": "Various", "category": "Migraine"},
    {"brand_name": "MAXALT", "company": "Merck", "category": "Migraine"},
    {"brand_name": "ZOLMITRIPTAN", "company": "Various", "category": "Migraine"},
    {"brand_name": "ZOMIG", "company": "AstraZeneca", "category": "Migraine"},
    {"brand_name": "AIMOVIG", "company": "Amgen", "category": "Migraine"},
    {"brand_name": "ERENUMAB", "company": "Various", "category": "Migraine"},
    {"brand_name": "AJOVY", "company": "Teva", "category": "Migraine"},
    {"brand_name": "FREMANEZUMAB", "company": "Various", "category": "Migraine"},
    {"brand_name": "EMGALITY", "company": "Eli Lilly", "category": "Migraine"},
    {"brand_name": "GALCANEZUMAB", "company": "Various", "category": "Migraine"},
    {"brand_name": "NURTEC", "company": "Biohaven", "category": "Migraine"},
    {"brand_name": "RIMEGEPANT", "company": "Various", "category": "Migraine"},
    {"brand_name": "UBRELVY", "company": "AbbVie", "category": "Migraine"},

    # Antifungals
    {"brand_name": "FLUCONAZOLE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "DIFLUCAN", "company": "Pfizer", "category": "Antifungal"},
    {"brand_name": "ITRACONAZOLE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "SPORANOX", "company": "Janssen", "category": "Antifungal"},
    {"brand_name": "NYSTATIN", "company": "Various", "category": "Antifungal"},
    {"brand_name": "CLOTRIMAZOLE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "CANESTEN", "company": "Bayer", "category": "Antifungal"},
    {"brand_name": "MICONAZOLE", "company": "Various", "category": "Antifungal"},
    {"brand_name": "MONISTAT", "company": "Johnson & Johnson", "category": "Antifungal"},

    # Antivirals
    {"brand_name": "ACYCLOVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "ZOVIRAX", "company": "GSK", "category": "Antiviral"},
    {"brand_name": "VALACYCLOVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "VALTREX", "company": "GSK", "category": "Antiviral"},
    {"brand_name": "FAMCICLOVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "FAMVIR", "company": "Novartis", "category": "Antiviral"},
    {"brand_name": "OSELTAMIVIR", "company": "Various", "category": "Antiviral"},
    {"brand_name": "TAMIFLU", "company": "Roche", "category": "Antiviral"},
    {"brand_name": "PAXLOVID", "company": "Pfizer", "category": "Antiviral"},
    {"brand_name": "NIRMATRELVIR", "company": "Pfizer", "category": "Antiviral"},
    {"brand_name": "TRUVADA", "company": "Gilead", "category": "Antiviral"},
    {"brand_name": "DESCOVY", "company": "Gilead", "category": "Antiviral"},
    {"brand_name": "BIKTARVY", "company": "Gilead", "category": "Antiviral"},
    {"brand_name": "HARVONI", "company": "Gilead", "category": "Antiviral"},
    {"brand_name": "EPCLUSA", "company": "Gilead", "category": "Antiviral"},
    {"brand_name": "MAVYRET", "company": "AbbVie", "category": "Antiviral"},

    # GI Specialty
    {"brand_name": "MESALAMINE", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "ASACOL", "company": "Warner Chilcott", "category": "GI Specialty"},
    {"brand_name": "PENTASA", "company": "Shire", "category": "GI Specialty"},
    {"brand_name": "SALOFALK", "company": "Dr. Falk", "category": "GI Specialty"},
    {"brand_name": "SULFASALAZINE", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "AZULFIDINE", "company": "Pfizer", "category": "GI Specialty"},
    {"brand_name": "BUDESONIDE", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "ENTOCORT", "company": "AstraZeneca", "category": "GI Specialty"},
    {"brand_name": "LOPERAMIDE", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "IMODIUM", "company": "Johnson & Johnson", "category": "GI Specialty"},
    {"brand_name": "LACTULOSE", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "POLYETHYLENE GLYCOL", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "MIRALAX", "company": "Bayer", "category": "GI Specialty"},
    {"brand_name": "RESTORALAX", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "SENOKOT", "company": "Purdue", "category": "GI Specialty"},
    {"brand_name": "SENNA", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "DOCUSATE", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "COLACE", "company": "Purdue", "category": "GI Specialty"},
    {"brand_name": "LINZESS", "company": "Allergan", "category": "GI Specialty"},
    {"brand_name": "LINACLOTIDE", "company": "Various", "category": "GI Specialty"},
    {"brand_name": "TRULANCE", "company": "Takeda", "category": "GI Specialty"},

    # Additional Common Medications
    {"brand_name": "METOCLOPRAMIDE", "company": "Various", "category": "Antiemetic"},
    {"brand_name": "REGLAN", "company": "Various", "category": "Antiemetic"},
    {"brand_name": "PROCHLORPERAZINE", "company": "Various", "category": "Antiemetic"},
    {"brand_name": "GRAVOL", "company": "Church & Dwight", "category": "Antiemetic"},
    {"brand_name": "DIMENHYDRINATE", "company": "Various", "category": "Antiemetic"},
    {"brand_name": "DEXAMETHASONE", "company": "Various", "category": "Corticosteroid"},
    {"brand_name": "DECADRON", "company": "Merck", "category": "Corticosteroid"},
    {"brand_name": "BUDESONIDE NASAL", "company": "Various", "category": "Nasal"},
    {"brand_name": "RHINOCORT", "company": "AstraZeneca", "category": "Nasal"},
    {"brand_name": "FLONASE", "company": "GSK", "category": "Nasal"},
    {"brand_name": "FLUTICASONE NASAL", "company": "Various", "category": "Nasal"},
    {"brand_name": "NASACORT", "company": "Sanofi", "category": "Nasal"},
    {"brand_name": "TRIAMCINOLONE NASAL", "company": "Various", "category": "Nasal"},
    {"brand_name": "AZELASTINE", "company": "Various", "category": "Nasal"},
    {"brand_name": "ASTELIN", "company": "Valeant", "category": "Nasal"},
    {"brand_name": "DYMISTA", "company": "Valeant", "category": "Nasal"},
    {"brand_name": "OXYMETAZOLINE", "company": "Various", "category": "Nasal"},
    {"brand_name": "DRISTAN", "company": "Bayer", "category": "Nasal"},
    {"brand_name": "OTRIVIN", "company": "Novartis", "category": "Nasal"},
    {"brand_name": "XYLOMETAZOLINE", "company": "Various", "category": "Nasal"},
]


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'med_list' not in st.session_state:
    st.session_state.med_list = []

if 'verification_states' not in st.session_state:
    st.session_state.verification_states = {}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def search_medications(query):
    """Search local medication database - instant results."""
    if not query or len(query) < 1:
        return []

    query_upper = query.upper()
    results = []

    for med in MEDICATION_DATABASE:
        if query_upper in med['brand_name']:
            results.append({
                'brand_name': med['brand_name'],
                'company': med['company'],
                'category': med['category'],
                'source': 'RxFlow Database'
            })

    # Sort by how well it matches (starts with query first)
    results.sort(key=lambda x: (not x['brand_name'].startswith(query_upper), x['brand_name']))

    return results[:20]


def search_health_canada_api(query):
    """Search Health Canada's full drug database API."""
    if not query or len(query) < 2:
        return []

    try:
        import json

        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        url = "https://health-products.canada.ca/api/drug/drugproduct/"
        params = {
            'brandname': clean_query,
            'lang': 'en',
            'type': 'json'
        }

        # Use streaming to limit data downloaded
        response = requests.get(url, params=params, timeout=8, stream=True)

        if response.status_code == 200:
            # Read only first 200KB to avoid memory issues
            content = ""
            bytes_read = 0
            max_bytes = 200000

            for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                if chunk:
                    content += chunk
                    bytes_read += len(chunk)
                    if bytes_read >= max_bytes:
                        break

            response.close()

            # Try to fix truncated JSON
            try:
                # Find last complete object
                last_complete = content.rfind('},')
                if last_complete > 0:
                    content = content[:last_complete + 1] + ']'
                data = json.loads(content)
            except json.JSONDecodeError:
                # If JSON is broken, try to find valid portion
                try:
                    first_bracket = content.find('[')
                    last_bracket = content.rfind('}')
                    if first_bracket >= 0 and last_bracket > first_bracket:
                        content = content[first_bracket:last_bracket + 1] + ']'
                        data = json.loads(content)
                    else:
                        return []
                except:
                    return []

            results = []
            seen_names = set()

            for item in data[:100]:
                brand_name = item.get('brand_name', '').strip()
                company = item.get('company_name', '').strip()

                if brand_name and brand_name.upper() not in seen_names:
                    seen_names.add(brand_name.upper())
                    results.append({
                        'brand_name': brand_name,
                        'company': company if company else 'Health Canada DPD',
                        'category': 'Health Canada',
                        'source': 'Health Canada API'
                    })

            return results[:30]
        return []

    except requests.exceptions.Timeout:
        return []
    except Exception as e:
        return []


def reset_all_verifications():
    """Reset all verification checkboxes when a new medication is added."""
    st.session_state.verification_states = {
        idx: False for idx in range(len(st.session_state.med_list))
    }


def check_all_verified():
    """Check if all medications in the list are verified."""
    if not st.session_state.med_list:
        return False

    for idx in range(len(st.session_state.med_list)):
        if not st.session_state.verification_states.get(idx, False):
            return False
    return True


def generate_calendar_html(med_list):
    """Generate an HTML calendar view of the medication schedule."""
    if not med_list:
        return "<p>No medications to display.</p>"

    today = datetime.now()
    days = [(today + timedelta(days=i)) for i in range(7)]
    day_names = [d.strftime("%a %m/%d") for d in days]

    time_slots = ['Morning', 'Noon', 'Evening', 'Bedtime']
    time_labels = {
        'Morning': 'Morning<br>(6-9 AM)',
        'Noon': 'Noon<br>(11AM-1PM)',
        'Evening': 'Evening<br>(5-7 PM)',
        'Bedtime': 'Bedtime<br>(9-11 PM)'
    }

    html = '<div class="calendar-container"><table class="calendar-table">'
    html += '<tr><th>Time</th>'
    for day_name in day_names:
        html += f'<th>{day_name}</th>'
    html += '</tr>'

    for slot in time_slots:
        html += f'<tr><td class="time-header">{time_labels[slot]}</td>'
        for _ in days:
            html += '<td>'
            for med in med_list:
                if slot in med['time_slots']:
                    card_class = 'calendar-med manual' if med['source'] == 'manual' else 'calendar-med'
                    html += f'''
                    <div class="{card_class}">
                        <div class="med-title">{med['name']}</div>
                        <div class="med-dose">{med['strength_value']} {med['strength_unit']}</div>
                    </div>
                    '''
            html += '</td>'
        html += '</tr>'

    html += '</table></div>'
    return html


def generate_preview_html(med_list):
    """Generate an HTML preview of the PDF schedule."""
    if not med_list:
        return ""

    time_slots = ['Morning', 'Noon', 'Evening', 'Bedtime']

    html = '''
    <div class="preview-container">
        <div class="preview-header">PDF Preview - Medication Schedule</div>
        <table style="width:100%; border-collapse: collapse; margin-top: 10px;">
            <tr style="background-color: #1976d2; color: white;">
                <th style="padding: 10px; border: 1px solid #1565c0; text-align: left;">Medication</th>
                <th style="padding: 10px; border: 1px solid #1565c0; text-align: center;">Morning</th>
                <th style="padding: 10px; border: 1px solid #1565c0; text-align: center;">Noon</th>
                <th style="padding: 10px; border: 1px solid #1565c0; text-align: center;">Evening</th>
                <th style="padding: 10px; border: 1px solid #1565c0; text-align: center;">Bedtime</th>
            </tr>
    '''

    for med in med_list:
        bg_color = '#fff3e0' if med['source'] == 'manual' else '#e8f5e9'
        source_label = ' (Manual)' if med['source'] == 'manual' else ''

        html += f'''
            <tr style="background-color: {bg_color};">
                <td style="padding: 10px; border: 1px solid #e0e0e0;">
                    <strong>{med['name']}</strong>{source_label}<br>
                    <span style="color: #616161;">{med['strength_value']} {med['strength_unit']}</span>
                </td>
        '''

        for slot in time_slots:
            if slot in med['time_slots']:
                html += f'''
                    <td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center; background-color: #c8e6c9;">
                        <strong>X</strong><br>
                        <span style="font-size: 0.8rem;">{med['strength_value']} {med['strength_unit']}</span>
                    </td>
                '''
            else:
                html += '<td style="padding: 10px; border: 1px solid #e0e0e0; text-align: center; color: #bdbdbd;">-</td>'

        html += '</tr>'

    html += f'''
        </table>
        <div style="margin-top: 15px; padding: 10px; background-color: #fff8e1; border-radius: 4px; font-size: 0.85rem;">
            <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}<br>
            <em>DISCLAIMER: This schedule is for personal reference only. Always consult a pharmacist or healthcare provider.</em>
        </div>
    </div>
    '''
    return html


def generate_pdf(med_list):
    """Generate a landscape PDF with medication schedule grid."""
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(25, 118, 210)
    pdf.cell(0, 12, 'RxFlow Canada - Medication Schedule', ln=True, align='C')

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    pdf.ln(8)

    pdf.set_fill_color(25, 118, 210)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 10)

    col_widths = [90, 35, 35, 35, 35]
    headers = ['Medication Details', 'Morning', 'Noon', 'Evening', 'Bedtime']

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    time_slots = ['Morning', 'Noon', 'Evening', 'Bedtime']

    for med in med_list:
        med_text = f"{med['name']}\n{med['strength_value']} {med['strength_unit']}"
        if med['source'] == 'manual':
            med_text += "\n(Manual Entry)"

        row_height = 14

        if med['source'] == 'manual':
            pdf.set_fill_color(255, 243, 224)
        else:
            pdf.set_fill_color(232, 245, 233)

        pdf.set_font('Helvetica', 'B', 9)
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        pdf.multi_cell(col_widths[0], row_height/2, med_text, border=1, align='L', fill=True)
        pdf.set_xy(x_start + col_widths[0], y_start)

        for i, slot in enumerate(time_slots):
            if slot in med['time_slots']:
                mark = f"X\n({med['strength_value']} {med['strength_unit']})"
                pdf.set_font('Helvetica', 'B', 9)
            else:
                mark = "-"
                pdf.set_font('Helvetica', '', 9)

            pdf.multi_cell(col_widths[i+1], row_height/2, mark, border=1, align='C', fill=True)
            if i < 3:
                pdf.set_xy(x_start + col_widths[0] + sum(col_widths[1:i+2]), y_start)

        pdf.ln(0)

    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(100, 100, 100)
    footer_text = (
        f"Generated by RxFlow Canada. User verified on {datetime.now().strftime('%Y-%m-%d')}.\n"
        "IMPORTANT: This schedule is for personal reference only. Always consult a pharmacist or healthcare provider."
    )
    pdf.multi_cell(0, 5, footer_text, align='C')

    pdf.ln(5)
    pdf.set_fill_color(255, 235, 238)
    pdf.set_text_color(198, 40, 40)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.multi_cell(0, 5,
        "DISCLAIMER: This tool does not provide medical advice. "
        "Verify all medications and dosages with a licensed healthcare professional.",
        align='C', fill=True)

    return pdf.output(dest='S').encode('latin-1')


# =============================================================================
# MAIN APPLICATION UI
# =============================================================================

st.markdown("""
<div class="app-header">
    <p class="app-title">RxFlow Canada</p>
    <p class="app-subtitle">Safety-Critical Medication Schedule Builder</p>
</div>
""", unsafe_allow_html=True)

med_count = len(st.session_state.med_list)
verified_count = sum(1 for idx in range(med_count) if st.session_state.verification_states.get(idx, False))

if med_count == 0:
    status_text = "No medications added yet"
elif verified_count == med_count:
    status_text = f"[OK] {med_count} medication(s) - All verified - Ready to download"
else:
    status_text = f"[!] {med_count} medication(s) - {verified_count}/{med_count} verified"

st.markdown(f'<div class="status-bar">{status_text}</div>', unsafe_allow_html=True)


# =============================================================================
# ADD MEDICATION SECTION
# =============================================================================

with st.expander("Add Medication", expanded=True):

    manual_mode = st.toggle(
        "Medication Not Found? (Manual Entry)",
        value=False,
        help="Enable this if you cannot find your medication in the list"
    )

    if manual_mode:
        st.markdown("""
        <div class="manual-warning">
            WARNING: MANUAL ENTRY MODE - Double-check spelling and dosage carefully!
        </div>
        """, unsafe_allow_html=True)

    # MODE A: Database Search
    if not manual_mode:
        st.markdown("##### Search Medication Database")
        st.caption("Type in the box below to filter medications instantly")

        # Initialize session state for API results
        if 'api_search_results' not in st.session_state:
            st.session_state.api_search_results = []
        if 'api_search_query' not in st.session_state:
            st.session_state.api_search_query = ""

        # Create searchable options list from local DB + any API results
        local_options = [
            f"{med['brand_name']} - {med['company']} ({med['category']})"
            for med in MEDICATION_DATABASE
        ]

        api_options = [
            f"{med['brand_name']} - {med['company']} ({med['category']})"
            for med in st.session_state.api_search_results
        ]

        # Combine and deduplicate
        all_options = ["-- Select a medication --"] + sorted(set(local_options + api_options))

        selected_option = st.selectbox(
            "Search and select medication",
            options=all_options,
            index=0,
            placeholder="Type to search...",
            key="med_search_selectbox"
        )

        medication_name = None
        source_type = None

        if selected_option and selected_option != "-- Select a medication --":
            # Extract the brand name from the selection
            brand_name = selected_option.split(" - ")[0]
            medication_name = brand_name
            source_type = 'database'

            # Find the category for display
            found = False
            for med in MEDICATION_DATABASE:
                if med['brand_name'] == brand_name:
                    st.info(f"**Selected:** {med['brand_name']} ({med['category']})")
                    found = True
                    break

            if not found:
                for med in st.session_state.api_search_results:
                    if med['brand_name'] == brand_name:
                        st.info(f"**Selected:** {med['brand_name']} (from Health Canada)")
                        source_type = 'health_canada'
                        break

        # Health Canada API Search Section
        st.markdown("---")
        st.markdown("###### Can't find your medication?")
        st.caption("Search Health Canada's complete database (47,000+ products)")

        api_col1, api_col2 = st.columns([3, 1])

        with api_col1:
            api_query = st.text_input(
                "Search Health Canada",
                placeholder="Enter medication name and click Search...",
                key="hc_api_search",
                label_visibility="collapsed"
            )

        with api_col2:
            search_hc_clicked = st.button("Search HC", type="secondary", use_container_width=True)

        if search_hc_clicked and api_query:
            with st.spinner("Searching Health Canada database..."):
                api_results = search_health_canada_api(api_query)

                if api_results:
                    st.session_state.api_search_results = api_results
                    st.session_state.api_search_query = api_query
                    st.success(f"Found {len(api_results)} result(s) from Health Canada! Select from dropdown above.")
                    st.rerun()
                else:
                    st.warning("No results found. Try different spelling or use Manual Entry.")

        if st.session_state.api_search_results:
            st.caption(f"Health Canada results for '{st.session_state.api_search_query}' added to dropdown above")

    # MODE B: Manual Entry
    else:
        st.markdown("##### Enter Medication Name")
        medication_name = st.text_input(
            "Medication name (check spelling carefully)",
            placeholder="Enter exact medication name...",
            help="Double-check the spelling before proceeding"
        )
        source_type = 'manual'

    st.divider()

    # STRENGTH INPUT
    st.markdown("##### Dosage Strength")
    st.caption("Enter the strength per dose (check your medication label)")

    strength_col1, strength_col2 = st.columns([2, 1])

    with strength_col1:
        strength_value = st.number_input(
            "Strength Value",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            step=0.5,
            format="%.1f",
            help="Enter the numeric strength value only"
        )

    with strength_col2:
        strength_unit = st.selectbox(
            "Unit",
            options=["mg", "mcg", "g", "mL", "units", "puffs", "tablet"],
            index=0,
            help="Select the appropriate unit"
        )

    st.divider()

    # TIME SLOTS
    st.markdown("##### Schedule (Select all that apply)")
    st.caption("Check each time of day this medication should be taken")

    time_col1, time_col2 = st.columns(2)

    with time_col1:
        morning = st.checkbox("Morning (6-9 AM)", key="time_morning")
        noon = st.checkbox("Noon (11 AM-1 PM)", key="time_noon")

    with time_col2:
        evening = st.checkbox("Evening (5-7 PM)", key="time_evening")
        bedtime = st.checkbox("Bedtime (9-11 PM)", key="time_bedtime")

    selected_times = []
    if morning: selected_times.append("Morning")
    if noon: selected_times.append("Noon")
    if evening: selected_times.append("Evening")
    if bedtime: selected_times.append("Bedtime")

    st.divider()

    # VALIDATION
    validation_errors = []

    if not medication_name:
        validation_errors.append("Select or enter a medication name")
    if strength_value <= 0:
        validation_errors.append("Enter a valid strength value (> 0)")
    if not selected_times:
        validation_errors.append("Select at least one time slot")

    if validation_errors:
        st.warning("**Complete the following to add medication:**\n- " + "\n- ".join(validation_errors))

    add_disabled = len(validation_errors) > 0

    if st.button(
        "Add Medication to Schedule",
        type="primary",
        disabled=add_disabled,
        use_container_width=True
    ):
        new_med = {
            'name': medication_name,
            'strength_value': strength_value,
            'strength_unit': strength_unit,
            'time_slots': selected_times,
            'source': source_type,
            'added_at': datetime.now().isoformat()
        }

        st.session_state.med_list.append(new_med)
        reset_all_verifications()
        st.toast(f"'{medication_name}' added to schedule!")
        st.rerun()


# =============================================================================
# CALENDAR VIEW SECTION
# =============================================================================

if st.session_state.med_list:
    st.markdown("---")
    st.markdown("### Weekly Calendar View")
    st.caption("Your medication schedule for the next 7 days")
    calendar_html = generate_calendar_html(st.session_state.med_list)
    st.markdown(calendar_html, unsafe_allow_html=True)


# =============================================================================
# REVIEW LIST SECTION
# =============================================================================

st.markdown("---")
st.markdown("### Current Medication List")

if not st.session_state.med_list:
    st.info("No medications added yet. Use the form above to add medications to your schedule.")
else:
    st.caption("**IMPORTANT:** Verify each medication entry before downloading the PDF.")

    for idx, med in enumerate(st.session_state.med_list):
        card_class = "manual-card" if med['source'] == 'manual' else "verified-card"
        badge_class = "manual-badge" if med['source'] == 'manual' else "verified-badge"
        badge_text = "MANUAL ENTRY" if med['source'] == 'manual' else "DATABASE"

        time_slots_html = "".join([f'<span class="time-slot">{slot}</span>' for slot in med['time_slots']])

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div class="med-name">{med['name']}</div>
                <span class="{badge_class}">{badge_text}</span>
            </div>
            <div class="med-details">
                <strong>Dosage:</strong> {med['strength_value']} {med['strength_unit']}
            </div>
            <div class="time-slots">{time_slots_html}</div>
        </div>
        """, unsafe_allow_html=True)

        verify_col, remove_col = st.columns([3, 1])

        with verify_col:
            st.markdown('<div class="verify-section">', unsafe_allow_html=True)
            verified = st.checkbox(
                f"I verify '{med['name']}' entry is correct",
                key=f"verify_{idx}",
                value=st.session_state.verification_states.get(idx, False)
            )
            st.session_state.verification_states[idx] = verified
            st.markdown('</div>', unsafe_allow_html=True)

        with remove_col:
            if st.button("Remove", key=f"remove_{idx}", use_container_width=True):
                st.session_state.med_list.pop(idx)
                reset_all_verifications()
                st.toast("Medication removed")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# PDF PREVIEW & DOWNLOAD SECTION
# =============================================================================

st.markdown("---")
st.markdown("### Generate Schedule PDF")

all_verified = check_all_verified()
has_medications = len(st.session_state.med_list) > 0

if not has_medications:
    st.warning("**Cannot generate PDF:** Add at least one medication to the schedule.")
elif not all_verified:
    unverified_count = len(st.session_state.med_list) - verified_count
    st.warning(f"**Cannot generate PDF:** {unverified_count} medication(s) still need verification. Check the boxes above.")
else:
    st.success("All medications verified! Review the preview below, then download your PDF.")
    st.markdown("#### Preview")
    preview_html = generate_preview_html(st.session_state.med_list)
    st.markdown(preview_html, unsafe_allow_html=True)

if st.button(
    "Download Schedule PDF",
    type="primary",
    disabled=not (has_medications and all_verified),
    use_container_width=True
):
    with st.spinner("Generating PDF..."):
        pdf_bytes = generate_pdf(st.session_state.med_list)
        st.download_button(
            label="Click to Save PDF",
            data=pdf_bytes,
            file_name=f"RxFlow_Schedule_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        st.toast("PDF generated successfully!")


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #9e9e9e; font-size: 0.8rem; padding: 1rem 0;">
    <strong>RxFlow Canada</strong> | For personal reference only<br>
    Database includes 200+ common Canadian medications<br>
    Always consult a pharmacist or healthcare provider
</div>
""", unsafe_allow_html=True)
