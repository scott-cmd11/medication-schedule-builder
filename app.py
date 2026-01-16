# -*- coding: utf-8 -*-
"""
Medication Schedule Builder
A mobile-first Streamlit application with strict "Checks & Balances"
"""

import streamlit as st
import requests
import pandas as pd
from fpdf import FPDF
from datetime import datetime, timedelta
import re
import base64

# =============================================================================
# PAGE CONFIG & CUSTOM CSS
# =============================================================================

st.set_page_config(
    page_title="Medication Schedule Builder",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        /* Colors */
        --primary: #0891b2;
        --primary-dark: #0e7490;
        --primary-light: #22d3ee;
        --success: #059669;
        --success-light: #d1fae5;
        --warning: #d97706;
        --warning-light: #fef3c7;
        --danger: #dc2626;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-900: #111827;

        /* Spacing */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 20px;
        --space-6: 24px;

        /* Typography */
        --text-xs: 12px;
        --text-sm: 14px;
        --text-base: 16px;
        --text-lg: 18px;
        --text-xl: 20px;

        /* Sizes */
        --input-height: 48px;
        --button-height: 48px;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;

        /* Shadows */
        --shadow-card: 0 1px 3px rgba(0,0,0,0.08);
        --shadow-elevated: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* Neutral background */
    .stApp {
        background: #f8f9fa;
    }

    /* Container */
    .block-container {
        padding: 0 var(--space-4) var(--space-4);
        max-width: 420px !important;
        margin: 0 auto;
    }
    .stMainBlockContainer {
        max-width: 420px !important;
        margin: 0 auto;
    }

    /* Global typography */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ===== APP BAR ===== */
    .app-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 56px;
        padding: 0 var(--space-4);
        background: white;
        border-bottom: 1px solid var(--gray-200);
        margin: 0 calc(-1 * var(--space-4)) var(--space-4);
    }
    .app-bar-left {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }
    .app-bar-icon {
        width: 32px;
        height: 32px;
        background: var(--primary);
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    .app-bar-title {
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--gray-900);
    }
    .app-bar-btn {
        display: flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-2) var(--space-3);
        background: var(--gray-100);
        border-radius: var(--radius-sm);
        font-size: var(--text-sm);
        font-weight: 500;
        color: var(--gray-700);
        cursor: pointer;
        transition: background 0.15s;
    }
    .app-bar-btn:hover {
        background: var(--gray-200);
    }
    .app-bar-btn.disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .app-bar-actions {
        position: absolute;
        top: 0;
        right: var(--space-4);
        height: 56px;
        display: flex;
        align-items: center;
    }
    /* Style the preview button row to overlap with app bar */
    .preview-btn-row {
        margin-top: -48px;
        margin-bottom: var(--space-3);
        display: flex;
        justify-content: flex-end;
    }
    .preview-btn-row .stButton > button {
        min-height: 36px;
        padding: var(--space-2) var(--space-3);
        font-size: var(--text-sm);
        background: var(--gray-100);
        color: var(--gray-700);
    }
    .preview-btn-row .stButton > button:hover:not(:disabled) {
        background: var(--gray-200);
    }
    .preview-btn-row .stButton > button:disabled {
        opacity: 0.5;
    }

    /* ===== WARNING BANNER ===== */
    .warning-banner {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: #fffbeb;
        border-radius: var(--radius-sm);
        font-size: var(--text-sm);
        color: #92400e;
        margin-bottom: var(--space-4);
    }
    .warning-banner-icon {
        flex-shrink: 0;
    }
    .warning-banner-text {
        flex: 1;
    }
    .warning-banner-link {
        color: var(--warning);
        font-weight: 500;
        cursor: pointer;
    }

    /* ===== CARD (single style) ===== */
    .card {
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        box-shadow: var(--shadow-card);
        margin-bottom: var(--space-4);
    }
    .card-header {
        margin-bottom: var(--space-4);
    }
    .card-title {
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--gray-900);
        margin: 0;
    }
    .card-subtitle {
        font-size: var(--text-sm);
        color: var(--gray-500);
        margin-top: var(--space-1);
    }

    /* ===== SECTION LABEL ===== */
    .section-label {
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--gray-700);
        margin-bottom: var(--space-2);
    }
    .section-helper {
        font-size: var(--text-xs);
        color: var(--gray-500);
        margin-bottom: var(--space-2);
    }

    /* ===== INPUTS ===== */
    .stTextInput > div > div {
        border-radius: var(--radius-md);
        min-height: var(--input-height);
        font-size: var(--text-base);
    }
    .stTextInput > div > div > input {
        font-size: var(--text-base);
    }
    .stNumberInput > div > div {
        border-radius: var(--radius-md);
        min-height: var(--input-height);
    }
    .stSelectbox > div > div {
        border-radius: var(--radius-md);
        min-height: var(--input-height);
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        min-height: var(--button-height);
        font-size: var(--text-base);
        border-radius: var(--radius-md);
        border: none;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-elevated);
    }
    .stButton > button[kind="primary"] {
        background: var(--primary);
    }
    .stButton > button[kind="secondary"] {
        background: var(--gray-100);
        color: var(--gray-700);
    }

    /* ===== SELECTED MEDICATION CHIP ===== */
    .selected-chip {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: var(--success-light);
        border-radius: var(--radius-md);
        margin-bottom: var(--space-4);
    }
    .selected-chip-icon {
        color: var(--success);
    }
    .selected-chip-name {
        font-weight: 600;
        color: var(--gray-900);
    }
    .selected-chip-change {
        font-size: var(--text-sm);
        color: var(--primary);
        cursor: pointer;
        margin-left: var(--space-2);
    }

    /* ===== TIME CHIPS ===== */
    .time-chips {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--space-2);
    }
    .time-chip {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        min-height: 44px;
        padding: var(--space-3);
        background: white;
        border: 2px solid var(--gray-200);
        border-radius: var(--radius-md);
        font-size: var(--text-sm);
        font-weight: 500;
        color: var(--gray-700);
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .time-chip:hover {
        border-color: var(--primary);
    }
    .time-chip.selected {
        background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%);
        border-color: var(--primary);
        color: var(--primary-dark);
    }
    .time-chip-check {
        display: none;
    }
    .time-chip.selected .time-chip-check {
        display: inline;
        color: var(--primary);
    }

    /* ===== STICKY ACTION BAR ===== */
    .sticky-action-bar {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 420px;
        background: white;
        border-top: 1px solid var(--gray-200);
        padding: var(--space-3) var(--space-4);
        padding-bottom: calc(var(--space-3) + env(safe-area-inset-bottom, 0));
        box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    .sticky-bar-summary {
        font-size: var(--text-sm);
        color: var(--gray-500);
        margin-bottom: var(--space-2);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sticky-bar-error {
        font-size: var(--text-xs);
        color: var(--danger);
        margin-bottom: var(--space-2);
    }

    /* ===== MEDICATION LIST ===== */
    .med-list-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--space-3);
    }
    .med-list-title {
        font-size: var(--text-base);
        font-weight: 600;
        color: var(--gray-900);
    }
    .med-item {
        display: flex;
        align-items: center;
        padding: var(--space-3) var(--space-4);
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-card);
        margin-bottom: var(--space-2);
    }
    .med-item-info {
        flex: 1;
        min-width: 0;
    }
    .med-item-name {
        font-size: var(--text-base);
        font-weight: 600;
        color: var(--gray-900);
    }
    .med-item-details {
        font-size: var(--text-sm);
        color: var(--gray-500);
        margin-top: 2px;
    }
    .med-item-actions {
        display: flex;
        gap: var(--space-2);
    }
    .med-item-btn {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--gray-100);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: background 0.15s;
    }
    .med-item-btn:hover {
        background: var(--gray-200);
    }

    /* ===== EMPTY STATE ===== */
    .empty-state {
        text-align: center;
        padding: var(--space-6) var(--space-4);
    }
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: var(--space-3);
        opacity: 0.4;
    }
    .empty-state-title {
        font-size: var(--text-base);
        font-weight: 500;
        color: var(--gray-700);
        margin-bottom: var(--space-1);
    }
    .empty-state-text {
        font-size: var(--text-sm);
        color: var(--gray-500);
    }

    /* ===== SEARCH RESULTS ===== */
    .search-results {
        margin-top: var(--space-2);
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-md);
        overflow: hidden;
    }
    .search-result {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--space-3);
        background: white;
        border-bottom: 1px solid var(--gray-100);
        cursor: pointer;
        transition: background 0.1s;
    }
    .search-result:last-child {
        border-bottom: none;
    }
    .search-result:hover {
        background: var(--gray-50);
    }
    .search-result-name {
        font-size: var(--text-base);
        font-weight: 500;
        color: var(--gray-900);
    }
    .search-result-cat {
        font-size: var(--text-sm);
        color: var(--gray-500);
    }

    /* ===== LINK BUTTON ===== */
    .link-btn {
        font-size: var(--text-sm);
        color: var(--primary);
        cursor: pointer;
        padding: var(--space-2) 0;
    }
    .link-btn:hover {
        text-decoration: underline;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        font-size: var(--text-sm);
        font-weight: 500;
        color: var(--gray-600);
        background: var(--gray-50);
        border-radius: var(--radius-sm);
    }

    /* ===== CHECKBOX ===== */
    .stCheckbox > label {
        font-size: var(--text-sm);
        min-height: 40px;
        display: flex;
        align-items: center;
        color: var(--gray-700);
    }

    /* ===== FOOTER ===== */
    .app-footer {
        text-align: center;
        padding: var(--space-4);
        padding-bottom: calc(var(--space-4) + 80px);
        color: var(--gray-500);
        font-size: var(--text-xs);
    }

    /* ===== DIVIDER ===== */
    .divider {
        height: 1px;
        background: var(--gray-200);
        margin: var(--space-4) 0;
    }

    /* ===== PREVIEW CARD ===== */
    .preview-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        box-shadow: var(--shadow-elevated);
        margin-bottom: var(--space-4);
        border: 2px solid var(--primary);
    }
    .preview-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--space-3);
    }
    .preview-card-title {
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--gray-900);
    }
    .preview-iframe {
        width: 100%;
        height: 400px;
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-sm);
        margin-bottom: var(--space-3);
    }

    /* Legacy support - keeping for PDF generation */
    .med-name { font-weight: 600; color: var(--gray-900); }
    .med-details { font-size: var(--text-sm); color: var(--gray-500); }
    .time-slot {
        background: var(--primary);
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: var(--text-xs);
        font-weight: 500;
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
                'source': 'Local Database'
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


def get_dose_for_day(med, day_offset):
    """Get the dose for a medication on a specific day (0 = today, 1 = tomorrow, etc.)."""
    if not med.get('variable_dosing') or not med.get('dose_schedule'):
        return med['strength_value']

    schedule = med['dose_schedule']

    if schedule['type'] == 'gradual':
        # Find which step we're on based on day offset
        steps = schedule.get('steps', [])
        if not steps:
            return med['strength_value']

        # Find the appropriate step for this day
        current_dose = steps[0]['dose']
        for step in steps:
            if day_offset >= step['day']:
                current_dose = step['dose']
            else:
                break
        return current_dose

    elif schedule['type'] == 'custom':
        # Check custom date ranges (day 1 = today, so offset 0 = day 1)
        day_num = day_offset + 1
        ranges = schedule.get('ranges', [])
        for r in ranges:
            if r['start_day'] <= day_num <= r['end_day']:
                return r['dose']
        # If no range matches, return the base strength
        return med['strength_value']

    return med['strength_value']


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
        for day_idx, _ in enumerate(days):
            html += '<td>'
            for med in med_list:
                if slot in med['time_slots']:
                    card_class = 'calendar-med manual' if med['source'] == 'manual' else 'calendar-med'
                    # Get dose for this specific day (supports variable dosing)
                    day_dose = get_dose_for_day(med, day_idx)
                    # Add indicator if dose is changing
                    dose_indicator = ""
                    if med.get('variable_dosing') and med.get('dose_schedule'):
                        prev_dose = get_dose_for_day(med, day_idx - 1) if day_idx > 0 else day_dose
                        if day_dose < prev_dose:
                            dose_indicator = " ↓"
                        elif day_dose > prev_dose:
                            dose_indicator = " ↑"
                    html += f'''
                    <div class="{card_class}">
                        <div class="med-title">{med['name']}</div>
                        <div class="med-dose">{day_dose} {med['strength_unit']}{dose_indicator}</div>
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
            <em>Please verify all medication details with the patient's prescription.</em>
        </div>
    </div>
    '''
    return html


def generate_pdf(med_list):
    """Generate a landscape PDF with monthly calendar view."""
    import calendar

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)

    today = datetime.now()
    current_month = today.month
    current_year = today.year

    # Generate calendar for current month and next month
    for month_offset in range(2):
        month = current_month + month_offset
        year = current_year
        if month > 12:
            month = month - 12
            year += 1

        pdf.add_page()

        # Page dimensions (A4 landscape: 297 x 210 mm)
        page_width = 297
        page_height = 210
        margin = 10

        # Title
        pdf.set_font('Helvetica', 'B', 20)
        pdf.set_text_color(25, 118, 210)
        month_name = calendar.month_name[month]
        pdf.cell(0, 12, f'{month_name} {year}', ln=True, align='C')

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, 'Medication Schedule', ln=True, align='C')
        pdf.ln(3)

        # Calendar grid setup
        col_width = (page_width - 2 * margin) / 7
        header_height = 8
        row_height = 28

        # Day headers
        days_of_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        pdf.set_fill_color(25, 118, 210)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 10)

        for day_name in days_of_week:
            pdf.cell(col_width, header_height, day_name, border=1, align='C', fill=True)
        pdf.ln()

        # Get calendar data
        cal = calendar.Calendar(firstweekday=6)  # Sunday first
        month_days = cal.monthdayscalendar(year, month)

        # Draw calendar grid
        for week in month_days:
            y_row_start = pdf.get_y()

            for day_idx, day in enumerate(week):
                x_cell = margin + (day_idx * col_width)

                # Cell background
                if day == 0:
                    pdf.set_fill_color(245, 245, 245)  # Gray for empty
                elif day == today.day and month == today.month and year == today.year:
                    pdf.set_fill_color(255, 253, 231)  # Yellow for today
                else:
                    pdf.set_fill_color(255, 255, 255)  # White

                pdf.rect(x_cell, y_row_start, col_width, row_height, 'DF')
                pdf.set_draw_color(200, 200, 200)
                pdf.rect(x_cell, y_row_start, col_width, row_height, 'D')

                if day != 0:
                    # Day number
                    pdf.set_xy(x_cell + 1, y_row_start + 1)
                    pdf.set_font('Helvetica', 'B', 9)
                    pdf.set_text_color(50, 50, 50)
                    pdf.cell(col_width - 2, 5, str(day), align='L')

                    # Calculate day offset from today for variable dosing
                    cell_date = datetime(year, month, day)
                    day_offset = (cell_date - today.replace(hour=0, minute=0, second=0, microsecond=0)).days

                    # Medications for this day
                    y_offset = y_row_start + 7
                    for med in med_list:
                        if y_offset + 5 > y_row_start + row_height - 1:
                            # Show overflow indicator
                            pdf.set_xy(x_cell + 1, y_row_start + row_height - 4)
                            pdf.set_font('Helvetica', '', 5)
                            pdf.set_text_color(150, 150, 150)
                            pdf.cell(col_width - 2, 3, '...more', align='R')
                            break

                        # Med pill/badge
                        if med['source'] == 'manual':
                            pdf.set_fill_color(255, 224, 178)  # Orange
                        else:
                            pdf.set_fill_color(200, 230, 201)  # Green

                        pdf.rect(x_cell + 1, y_offset, col_width - 2, 5, 'F')

                        # Med name (truncated) with variable dosing support
                        pdf.set_xy(x_cell + 2, y_offset + 0.5)
                        pdf.set_font('Helvetica', '', 5)
                        pdf.set_text_color(30, 30, 30)

                        # Get dose for this day (supports variable dosing)
                        day_dose = get_dose_for_day(med, max(0, day_offset))
                        med_label = f"{med['name'][:8]} {day_dose}{med['strength_unit']}"
                        pdf.cell(col_width - 4, 4, med_label, align='L')

                        y_offset += 6

            pdf.set_y(y_row_start + row_height)

        # Legend
        pdf.ln(3)
        pdf.set_font('Helvetica', '', 7)
        pdf.set_text_color(100, 100, 100)

        # Legend items
        legend_y = pdf.get_y()
        pdf.set_fill_color(200, 230, 201)
        pdf.rect(margin, legend_y, 4, 4, 'F')
        pdf.set_xy(margin + 5, legend_y)
        pdf.cell(30, 4, 'Database verified', align='L')

        pdf.set_fill_color(255, 224, 178)
        pdf.rect(margin + 40, legend_y, 4, 4, 'F')
        pdf.set_xy(margin + 45, legend_y)
        pdf.cell(30, 4, 'Manual entry', align='L')

        pdf.set_fill_color(255, 253, 231)
        pdf.rect(margin + 80, legend_y, 4, 4, 'F')
        pdf.set_xy(margin + 85, legend_y)
        pdf.cell(20, 4, 'Today', align='L')

        # Medication list summary on right side of legend
        pdf.set_xy(margin + 120, legend_y)
        pdf.set_font('Helvetica', 'B', 7)
        pdf.cell(0, 4, 'Medications: ', align='L')
        pdf.set_font('Helvetica', '', 7)
        med_summary = ', '.join([f"{m['name']} ({m['strength_value']}{m['strength_unit']})" for m in med_list[:4]])
        if len(med_list) > 4:
            med_summary += f' +{len(med_list) - 4} more'
        pdf.set_xy(margin + 145, legend_y)
        pdf.cell(0, 4, med_summary, align='L')

    # Final page - detailed schedule
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(25, 118, 210)
    pdf.cell(0, 10, 'Daily Medication Schedule', ln=True, align='C')
    pdf.ln(5)

    # Time-based schedule table
    time_slots = ['Morning (6-9 AM)', 'Noon (11AM-1PM)', 'Evening (5-7 PM)', 'Bedtime (9-11 PM)']
    slot_keys = ['Morning', 'Noon', 'Evening', 'Bedtime']

    pdf.set_fill_color(25, 118, 210)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(70, 10, 'Time', border=1, align='C', fill=True)
    pdf.cell(0, 10, 'Medications', border=1, align='C', fill=True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    for i, slot_label in enumerate(time_slots):
        slot_key = slot_keys[i]
        meds_in_slot = [m for m in med_list if slot_key in m['time_slots']]

        pdf.set_fill_color(245, 245, 245)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(70, 12, slot_label, border=1, align='C', fill=True)

        pdf.set_fill_color(255, 255, 255)
        pdf.set_font('Helvetica', '', 9)
        if meds_in_slot:
            med_text = ', '.join([f"{m['name']} {m['strength_value']} {m['strength_unit']}" for m in meds_in_slot])
        else:
            med_text = '-'
        pdf.cell(0, 12, med_text, border=1, align='L', fill=True)
        pdf.ln()

    # Footer/disclaimer
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')

    pdf.ln(3)
    pdf.set_fill_color(255, 235, 238)
    pdf.set_text_color(198, 40, 40)
    pdf.set_font('Helvetica', 'B', 7)
    pdf.multi_cell(0, 4,
        "Please verify all medication details match the patient's prescription before use.",
        align='C', fill=True)

    return pdf.output(dest='S').encode('latin-1')


# =============================================================================
# MAIN APPLICATION UI
# =============================================================================

med_count = len(st.session_state.med_list)
has_meds = med_count > 0
all_meds_verified = check_all_verified() if has_meds else False
preview_btn_class = "app-bar-btn" if (has_meds and all_meds_verified) else "app-bar-btn disabled"

# Initialize preview modal state
if 'show_preview_modal' not in st.session_state:
    st.session_state.show_preview_modal = False

# Compact App Bar with Preview button integrated
st.markdown(f'''
<div class="app-bar">
    <div class="app-bar-left">
        <div class="app-bar-icon">💊</div>
        <span class="app-bar-title">Medication Schedule</span>
    </div>
</div>
''', unsafe_allow_html=True)

# Preview button positioned to align with app bar
st.markdown('<div class="preview-btn-row">', unsafe_allow_html=True)
preview_col1, preview_col2 = st.columns([2.5, 1])
with preview_col2:
    preview_disabled = not (has_meds and all_meds_verified)
    if st.button("📄 Preview", key="app_bar_preview", disabled=preview_disabled, use_container_width=True):
        st.session_state.show_preview_modal = True
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Slim warning banner
st.markdown('''
<div class="warning-banner">
    <span class="warning-banner-icon">⚠️</span>
    <span class="warning-banner-text">Verify against patient's prescription before printing.</span>
</div>
''', unsafe_allow_html=True)


# =============================================================================
# ADD MEDICATION CARD
# =============================================================================

# Initialize session states
if 'api_search_results' not in st.session_state:
    st.session_state.api_search_results = []
if 'selected_medication' not in st.session_state:
    st.session_state.selected_medication = None
if 'manual_entry_mode' not in st.session_state:
    st.session_state.manual_entry_mode = False
if 'dose_value' not in st.session_state:
    st.session_state.dose_value = 0.0
if 'dose_unit' not in st.session_state:
    st.session_state.dose_unit = "mg"
if 'selected_times' not in st.session_state:
    st.session_state.selected_times = []
if 'custom_doses' not in st.session_state:
    st.session_state.custom_doses = []

# Card container
st.markdown('''
<div class="card">
    <div class="card-header">
        <h2 class="card-title">Add medication</h2>
        <p class="card-subtitle">Search and add dosing schedule</p>
    </div>
</div>
''', unsafe_allow_html=True)

# Using a container for the card content
with st.container():

    # === MEDICATION SELECTION ===
    if st.session_state.selected_medication:
        # Show selected medication chip
        med = st.session_state.selected_medication
        med_name = med.get('brand_name', med.get('name', 'Unknown'))
        st.markdown(f'''
            <div class="selected-chip">
                <span class="selected-chip-icon">✓</span>
                <span class="selected-chip-name">{med_name}</span>
            </div>
        ''', unsafe_allow_html=True)

        change_col1, change_col2 = st.columns([3, 1])
        with change_col2:
            if st.button("Change", type="secondary", key="change_med", use_container_width=True):
                st.session_state.selected_medication = None
                st.session_state.dose_value = 0.0
                st.session_state.selected_times = []
                st.session_state.manual_entry_mode = False
                st.rerun()

    elif st.session_state.manual_entry_mode:
        # Manual entry mode
        st.markdown('<p class="section-label">Medication name</p>', unsafe_allow_html=True)
        manual_name = st.text_input(
            "Medication name",
            placeholder="Enter medication name...",
            key="manual_med_input",
            label_visibility="collapsed"
        )
        if manual_name:
            st.session_state.selected_medication = {
                'brand_name': manual_name,
                'name': manual_name,
                'category': 'Manual Entry',
                'source': 'manual'
            }
            st.rerun()

        if st.button("← Back to search", type="secondary"):
            st.session_state.manual_entry_mode = False
            st.rerun()

    else:
        # Search mode (default)
        search_query = st.text_input(
            "Search medication",
            placeholder="Search medication...",
            key="med_search_input",
            label_visibility="collapsed"
        )

        # Show filtered results when typing (min 2 chars)
        if search_query and len(search_query) >= 2:
            query_lower = search_query.lower()
            local_matches = [
                med for med in MEDICATION_DATABASE
                if query_lower in med['brand_name'].lower()
            ][:6]

            api_matches = [
                med for med in st.session_state.api_search_results
                if query_lower in med['brand_name'].lower()
            ][:4]

            all_matches = local_matches + api_matches

            if all_matches:
                st.markdown('<div class="search-results">', unsafe_allow_html=True)
                for i, med in enumerate(all_matches):
                    cat = med.get('category', '')
                    if st.button(
                        f"{med['brand_name']} — {cat}",
                        key=f"med_result_{i}",
                        use_container_width=True
                    ):
                        st.session_state.selected_medication = {
                            **med,
                            'source': 'health_canada' if med in st.session_state.api_search_results else 'database'
                        }
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption("No matches found.")

        # Links row
        link_col1, link_col2 = st.columns(2)
        with link_col1:
            if st.button("Not found? Add manually", key="manual_entry_btn"):
                st.session_state.manual_entry_mode = True
                st.rerun()
        with link_col2:
            with st.expander("Search Health Canada", expanded=False):
                hc_query = st.text_input("", placeholder="Search 47K+ products...", key="hc_search", label_visibility="collapsed")
                if st.button("Search", key="hc_search_btn", use_container_width=True):
                    if hc_query:
                        with st.spinner("Searching..."):
                            api_results = search_health_canada_api(hc_query)
                            if api_results:
                                st.session_state.api_search_results = api_results
                                st.rerun()
                            else:
                                st.warning("No results.")

# =============================================================================
# DOSE SECTION (shown after medication selected)
# =============================================================================

if st.session_state.selected_medication:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Dose</p>', unsafe_allow_html=True)

    dose_col1, dose_col2 = st.columns([2, 1])
    with dose_col1:
        dose_val = st.number_input(
            "Amount",
            min_value=0.0,
            max_value=10000.0,
            value=st.session_state.dose_value,
            step=1.0,
            format="%.1f",
            key="dose_amount_input",
            label_visibility="collapsed",
            placeholder="Amount"
        )
        if dose_val != st.session_state.dose_value:
            st.session_state.dose_value = dose_val

    with dose_col2:
        unit_options = ["mg", "mcg", "g", "mL", "units", "puffs", "tablet"]
        current_idx = unit_options.index(st.session_state.dose_unit) if st.session_state.dose_unit in unit_options else 0
        dose_unit = st.selectbox(
            "Unit",
            options=unit_options,
            index=current_idx,
            key="dose_unit_select",
            label_visibility="collapsed"
        )
        if dose_unit != st.session_state.dose_unit:
            st.session_state.dose_unit = dose_unit

    # Advanced options (tapering) in expander
    dose_schedule = None
    variable_dosing = False

    with st.expander("Advanced: Variable dosing", expanded=False):
        variable_dosing = st.checkbox("Enable variable/tapering dose", key="var_dose_check")

        if variable_dosing:
            dosing_mode = st.radio(
                "Mode",
                options=["Gradual change", "Custom dates"],
                horizontal=True,
                key="dosing_mode_radio"
            )

            if dosing_mode == "Gradual change":
                direction = st.radio(
                    "Direction",
                    options=["Taper (decrease)", "Increase"],
                    horizontal=True,
                    key="direction_radio"
                )

                g_col1, g_col2 = st.columns(2)
                with g_col1:
                    start_dose = st.number_input("Start", min_value=0.0, value=st.session_state.dose_value, step=0.5, format="%.1f", key="grad_start")
                with g_col2:
                    end_dose = st.number_input("End", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="grad_end")

                g_col3, g_col4 = st.columns(2)
                with g_col3:
                    change_amt = st.number_input("Change by", min_value=0.1, value=5.0, step=0.5, format="%.1f", key="grad_change")
                with g_col4:
                    change_days = st.number_input("Every X days", min_value=1, value=7, step=1, key="grad_days")

                # Calculate schedule
                is_taper = "Taper" in direction
                doses = []
                current = start_dose
                day = 0
                if is_taper:
                    while current > end_dose and len(doses) < 50:
                        doses.append({"day": day, "dose": current})
                        current = max(end_dose, current - change_amt)
                        day += change_days
                    if current == end_dose:
                        doses.append({"day": day, "dose": end_dose})
                else:
                    while current < end_dose and len(doses) < 50:
                        doses.append({"day": day, "dose": current})
                        current = min(end_dose, current + change_amt)
                        day += change_days
                    if current == end_dose:
                        doses.append({"day": day, "dose": end_dose})

                if doses:
                    preview = " → ".join([f"Day {d['day']+1}: {d['dose']}" for d in doses[:4]])
                    if len(doses) > 4:
                        preview += f" ... ({len(doses)} steps)"
                    st.caption(preview)

                dose_schedule = {
                    "type": "gradual",
                    "direction": "taper" if is_taper else "increase",
                    "start_dose": start_dose,
                    "end_dose": end_dose,
                    "change_amount": change_amt,
                    "change_days": change_days,
                    "steps": doses
                }

            else:  # Custom dates
                for i, cd in enumerate(st.session_state.custom_doses):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1:
                        st.text(f"Day {cd['start_day']}-{cd['end_day']}")
                    with c2:
                        st.text(f"{cd['dose']} {st.session_state.dose_unit}")
                    with c3:
                        if st.button("✕", key=f"rm_cd_{i}"):
                            st.session_state.custom_doses.pop(i)
                            st.rerun()

                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    cd_start = st.number_input("From", min_value=1, value=1, key="cd_from")
                with cc2:
                    cd_end = st.number_input("To", min_value=1, value=7, key="cd_to")
                with cc3:
                    cd_dose = st.number_input("Dose", min_value=0.0, value=st.session_state.dose_value, step=0.5, format="%.1f", key="cd_dose")

                if st.button("Add range", use_container_width=True, key="add_cd_range"):
                    st.session_state.custom_doses.append({"start_day": cd_start, "end_day": cd_end, "dose": cd_dose})
                    st.rerun()

                if st.session_state.custom_doses:
                    dose_schedule = {"type": "custom", "ranges": st.session_state.custom_doses.copy()}

# =============================================================================
# TIMES SECTION (shown after medication selected)
# =============================================================================

if st.session_state.selected_medication:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Times</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-helper">Tap to select</p>', unsafe_allow_html=True)

    # Time chip buttons in 2x2 grid
    time_options = [
        ("Morning", "☀️ Morning"),
        ("Noon", "🕛 Noon"),
        ("Evening", "🌙 Evening"),
        ("Bedtime", "🛏️ Bedtime")
    ]

    chip_cols = st.columns(2)
    for i, (key, label) in enumerate(time_options):
        with chip_cols[i % 2]:
            is_selected = key in st.session_state.selected_times
            btn_type = "primary" if is_selected else "secondary"
            display_label = f"✓ {label}" if is_selected else label

            if st.button(display_label, key=f"time_chip_{key}", use_container_width=True, type=btn_type):
                if is_selected:
                    st.session_state.selected_times.remove(key)
                else:
                    st.session_state.selected_times.append(key)
                st.rerun()

# =============================================================================
# STICKY CTA BAR
# =============================================================================

# Determine medication name and source
medication_name = None
source_type = None
if st.session_state.selected_medication:
    medication_name = st.session_state.selected_medication.get('brand_name', st.session_state.selected_medication.get('name'))
    source_type = st.session_state.selected_medication.get('source', 'database')

# Validation
validation_errors = []
if not medication_name:
    validation_errors.append("Select a medication")
if st.session_state.dose_value <= 0:
    validation_errors.append("Enter dose amount")
if not st.session_state.selected_times:
    validation_errors.append("Select at least one time")

add_disabled = len(validation_errors) > 0

# Build summary
if medication_name:
    times_str = ", ".join(st.session_state.selected_times) if st.session_state.selected_times else "No times"
    summary = f"{medication_name} • {st.session_state.dose_value} {st.session_state.dose_unit} • {times_str}"
else:
    summary = "Select a medication to continue"

# Show error if needed
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if validation_errors and medication_name:
    error_text = " · ".join(validation_errors)
    st.markdown(f'<p class="sticky-bar-error">{error_text}</p>', unsafe_allow_html=True)

# Summary line
st.markdown(f'<p class="sticky-bar-summary">{summary}</p>', unsafe_allow_html=True)

# Add button
if st.button(
    "Add Medication",
    type="primary",
    disabled=add_disabled,
    use_container_width=True,
    key="add_med_btn"
):
    # Build dose schedule if variable dosing was used
    final_dose_schedule = None
    final_variable_dosing = False
    if 'var_dose_check' in st.session_state and st.session_state.var_dose_check:
        final_variable_dosing = True
        if 'dose_schedule' in dir() and dose_schedule:
            final_dose_schedule = dose_schedule

    new_med = {
        'name': medication_name,
        'strength_value': st.session_state.dose_value,
        'strength_unit': st.session_state.dose_unit,
        'time_slots': st.session_state.selected_times.copy(),
        'source': source_type,
        'added_at': datetime.now().isoformat(),
        'variable_dosing': final_variable_dosing,
        'dose_schedule': final_dose_schedule
    }

    st.session_state.med_list.append(new_med)

    # Reset form state
    st.session_state.selected_medication = None
    st.session_state.dose_value = 0.0
    st.session_state.selected_times = []
    st.session_state.custom_doses = []
    st.session_state.manual_entry_mode = False

    reset_all_verifications()
    st.toast(f"'{medication_name}' added!")
    st.rerun()


# =============================================================================
# PREVIEW CARD (shown when preview button is clicked)
# =============================================================================

if st.session_state.show_preview_modal and has_meds and all_meds_verified:
    # Generate PDF
    pdf_bytes = generate_pdf(st.session_state.med_list)
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    # Preview card header
    st.markdown('''
    <div class="preview-card">
        <div class="preview-card-header">
            <span class="preview-card-title">📄 Schedule Preview</span>
        </div>
    ''', unsafe_allow_html=True)

    # Embedded PDF viewer
    st.markdown(f'''
        <iframe
            src="data:application/pdf;base64,{pdf_base64}"
            class="preview-iframe"
            title="PDF Preview">
        </iframe>
    </div>
    ''', unsafe_allow_html=True)

    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        # Print button - opens PDF in new tab
        st.markdown(f'''
            <a href="data:application/pdf;base64,{pdf_base64}"
               target="_blank"
               style="display: inline-flex; align-items: center; justify-content: center;
                      width: 100%; padding: 0.75rem 1rem;
                      background-color: var(--primary); color: white;
                      text-decoration: none; border-radius: var(--radius-md);
                      font-weight: 500; font-size: var(--text-sm);">
                🖨️ Print
            </a>
        ''', unsafe_allow_html=True)

    with btn_col2:
        st.download_button(
            label="💾 Download",
            data=pdf_bytes,
            file_name=f"Medication_Calendar_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with btn_col3:
        if st.button("✕ Close", key="close_preview", use_container_width=True):
            st.session_state.show_preview_modal = False
            st.rerun()

    st.markdown('<div style="margin-bottom: var(--space-4);"></div>', unsafe_allow_html=True)


# =============================================================================
# PATIENT MEDICATIONS LIST
# =============================================================================

# List header
st.markdown('''
<div class="med-list-header">
    <span class="med-list-title">Patient medications</span>
</div>
''', unsafe_allow_html=True)

if not st.session_state.med_list:
    # Empty state (only here, not elsewhere)
    st.markdown('''
    <div class="empty-state">
        <div class="empty-state-icon">💊</div>
        <div class="empty-state-title">No medications yet</div>
        <div class="empty-state-text">Add one above to generate the schedule</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    for idx, med in enumerate(st.session_state.med_list):
        # Build dose display
        if med.get('variable_dosing') and med.get('dose_schedule'):
            schedule = med['dose_schedule']
            if schedule['type'] == 'gradual':
                direction = "↓" if schedule['direction'] == 'taper' else "↑"
                dose_str = f"{schedule['start_dose']}→{schedule['end_dose']} {med['strength_unit']} {direction}"
            else:
                dose_str = f"Variable ({len(schedule.get('ranges', []))} ranges)"
        else:
            dose_str = f"{med['strength_value']} {med['strength_unit']}"

        # Build times string
        times_str = " · ".join(med.get('time_slots', []))

        # Render medication item card
        st.markdown(f'''
        <div class="med-item">
            <div class="med-item-info">
                <div class="med-item-name">{med['name']}</div>
                <div class="med-item-details">{dose_str} · {times_str}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Actions row
        action_col1, action_col2 = st.columns([4, 1])

        with action_col1:
            verified = st.checkbox(
                f"Verified",
                key=f"verify_{idx}",
                value=st.session_state.verification_states.get(idx, False)
            )
            st.session_state.verification_states[idx] = verified

        with action_col2:
            if st.button("🗑️", key=f"remove_{idx}", help="Remove"):
                st.session_state.med_list.pop(idx)
                reset_all_verifications()
                st.toast("Removed")
                st.rerun()


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div class="app-footer">
    <p style="margin: 0; line-height: 1.6;">
        For pharmacy use<br>
        Always verify against patient prescription
    </p>
</div>
""", unsafe_allow_html=True)
