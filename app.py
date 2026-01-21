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
import calendar
from med_data import MEDICATION_DATABASE

# =============================================================================
# SHARED UI COMPONENTS
# =============================================================================

def AppButton(label, key=None, type="secondary", on_click=None, help=None, disabled=False, use_container_width=True, args=None, kwargs=None):
    """
    Shared button component with consistent styling.
    Defaults to full width (use_container_width=True).
    Styles: h-12, rounded-2xl, flex centered, no wrap.
    """
    return st.button(
        label,
        key=key,
        type=type,
        on_click=on_click,
        args=args,
        kwargs=kwargs,
        help=help,
        disabled=disabled,
        use_container_width=use_container_width
    )

def AppInput(label, value="", key=None, placeholder="", type="default", on_change=None, disabled=False, label_visibility="visible", **kwargs):
    """
    Shared input component with consistent styling.
    Styles: h-12, rounded-2xl, px-4, text-base, py-0.
    """
    return st.text_input(
        label,
        value=value,
        key=key,
        placeholder=placeholder,
        type=type,
        on_change=on_change,
        disabled=disabled,
        label_visibility=label_visibility,
        **kwargs
    )

def AppSelect(label, options, index=0, key=None, on_change=None, disabled=False, label_visibility="visible", **kwargs):
    """
    Shared select component.
    """
    return st.selectbox(
        label,
        options,
        index=index,
        key=key,
        on_change=on_change,
        disabled=disabled,
        label_visibility=label_visibility,
        **kwargs
    )

def AppNumberInput(label, min_value=None, max_value=None, value=None, step=None, format=None, key=None, label_visibility="visible", **kwargs):
    """
    Shared number input component.
    """
    return st.number_input(
        label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        format=format,
        key=key,
        label_visibility=label_visibility,
        **kwargs
    )



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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    :root {
        /* Branding */
        --font-display: 'Space Grotesk', 'Segoe UI', sans-serif;
        --font-body: 'IBM Plex Sans', 'Segoe UI', sans-serif;

        /* Colors */
        --primary: #ff5a1f;
        --primary-dark: #c2410c;
        --primary-light: #ffd7bf;
        --accent: #0ea5a4;
        --accent-dark: #0f766e;
        --success: #0f766e;
        --success-light: #ccfbf1;
        --warning: #f59e0b;
        --warning-light: #fef3c7;
        --danger: #ef4444;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-400: #94a3b8;
        --gray-500: #64748b;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-900: #0f172a;

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
        --height-control: 48px;
        --radius-control: 16px;
        
        --input-height: var(--height-control);
        --button-height: var(--height-control);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: var(--radius-control);

        /* Shadows */
        --shadow-card: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-elevated: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* Page Wrapper (centered, max-w-640px) */
    .stApp {
        background:
            radial-gradient(900px 520px at 6% -8%, rgba(255, 90, 31, 0.18), transparent 60%),
            radial-gradient(900px 520px at 95% 0%, rgba(14, 165, 164, 0.16), transparent 58%),
            linear-gradient(180deg, #fef7f1 0%, #f8fafc 40%, #eef2f7 100%);
        display: flex;
        justify-content: center;
    }

    .block-container {
        padding-top: var(--space-6) !important;
        padding-bottom: var(--space-6) !important;
        padding-left: var(--space-4) !important;
        padding-right: var(--space-4) !important;
        max-width: 640px !important;
        width: 100% !important;
        margin: 0 auto;
    }
    
    /* Ensure content stack has consistent spacing */
    .stVerticalBlock {
        gap: var(--space-5) !important;
    }

    /* Global typography */
    * {
        font-family: var(--font-body);
    }

    @keyframes riseIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ===== APP BAR ===== */
    .app-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 56px;
        padding: 0 var(--space-4);
        background: transparent;
        border-bottom: none;
        margin: 0 calc(-1 * var(--space-4)) var(--space-3);
    }
    .app-bar-left {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }
    .app-bar-icon {
        width: 36px;
        height: 36px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .app-bar-title {
        font-size: var(--text-xl);
        font-weight: 700;
        color: white;
        font-family: var(--font-display);
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
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

    /* ===== WARNING BANNER (Floating Card) ===== */
    .warning-banner {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: #fff4e6;
        border-radius: var(--radius-md);
        font-size: var(--text-sm);
        color: #9a3412;
        margin-bottom: var(--space-3);
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }
    .warning-banner-icon {
        flex-shrink: 0;
        font-size: 12px;
    }
    .warning-banner-text {
        flex: 1;
    }
    .warning-banner-link {
        color: var(--warning);
        font-weight: 500;
        cursor: pointer;
    }

    /* ===== COMPACT LINK BUTTONS ===== */
    .compact-links {
        display: flex;
        gap: var(--space-3);
        margin-top: var(--space-2);
        margin-bottom: var(--space-2);
    }
    .compact-link {
        font-size: var(--text-xs);
        color: var(--primary);
        cursor: pointer;
        padding: var(--space-1) 0;
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .compact-link:hover {
        text-decoration: underline;
    }

    /* ===== CARD (single style) ===== */
    .card {
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        box-shadow: var(--shadow-card);
        margin-bottom: var(--space-4);
    }

    /* ===== CARD (st.container styling) ===== */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        box-shadow: var(--shadow-card);
        border: none; /* User requested removal of shadows/borders if needed, but styling allows shadow */
        margin-bottom: var(--space-4);
    }
    
    /* Remove default Streamlit border padding if needed */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        /* gap between elements inside card */
    }

    /* ===== HEADER CARD (Title + Warning) ===== */
    .header-card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-card);
        overflow: hidden;
        margin-bottom: var(--space-4);
        animation: riseIn 0.45s ease both;
    }
    .header-card-top {
        background: linear-gradient(135deg, #ff5a1f 0%, #ff7a45 40%, #0ea5a4 100%);
        padding: var(--space-3) var(--space-4);
    }
    .header-card-body {
        padding: var(--space-3) var(--space-4);
    }

    /* ===== SECTION HEADERS ===== */
    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--space-3);
        margin-top: var(--space-5);
        padding: 0 var(--space-1);
    }
    .section-title {
        font-size: var(--text-sm);
        font-weight: 600;
        letter-spacing: 0.025em;
        text-transform: uppercase;
        color: var(--gray-500);
        font-family: var(--font-display);
    }

    /* ===== EMPTY STATE ===== */
    .empty-state {
        background: white;
        border-radius: var(--radius-lg);
        border: 1px solid var(--gray-200);
        padding: var(--space-6);
        text-align: center;
        color: var(--gray-500);
    }
    .empty-state-icon {
        font-size: 32px;
        margin-bottom: var(--space-2);
        opacity: 0.7;
    }

    /* Legacy list-card for backward compatibility */
    .list-card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1), 0 1px 4px rgba(0, 0, 0, 0.06);
        margin-bottom: var(--space-6);
        padding: var(--space-4);
    }
    .list-card .med-list-header {
        margin-top: 0;
    }
    .list-card .app-footer {
        padding: var(--space-3) 0 0 0;
        padding-bottom: 0;
    }

    /* ===== ADD MEDICATION SECTION (cyan tint) ===== */
    .add-med-section {
        background: #ecfeff;
        margin: 0 calc(-1 * var(--space-4)) var(--space-3);
        padding: var(--space-2) var(--space-4) var(--space-4);
        border-bottom: 2px solid #a5f3fc;
    }
    .add-med-section .app-bar {
        background: transparent;
        border-bottom: none;
        margin-bottom: var(--space-2);
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
    .mini-label {
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--gray-600);
        margin: 0 0 6px 2px;
    }

    /* ===== INPUTS & SELECTS ===== */
    .stTextInput > div > div, .stSelectbox > div > div {
        border-radius: var(--radius-lg) !important;
        height: var(--input-height) !important;
        min-height: var(--input-height) !important;
        font-size: var(--text-base);
        background-color: white !important;
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-card);
        padding: 0 var(--space-4) !important;
        display: flex;
        align-items: center;
        box-sizing: border-box;
        overflow: visible;
    }
    .stNumberInput > div > div {
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    .stTextInput > div > div:focus-within, .stSelectbox > div > div:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(8, 145, 178, 0.15);
    }
    .stTextInput input, .stNumberInput input {
        font-size: var(--text-base);
        line-height: normal;
        background: transparent !important;
        height: 100%;
        padding: 0 !important;
        margin: 0;
        display: block;
        transform: none;
    }
    .stNumberInput input {
        padding-left: var(--space-4) !important;
        padding-right: var(--space-2) !important;
    }
    .stNumberInput input:focus,
    .stTextInput input:focus {
        outline: none;
        box-shadow: none;
    }
    .stTextInput input {
        height: var(--input-height) !important;
        line-height: var(--input-height) !important;
    }
    /* Compact height for the medication search input */
    div[data-testid="stTextInput"][data-key="med_search_input"] > div > div {
        height: 36px !important;
        min-height: 36px !important;
    }
    div[data-testid="stTextInput"][data-key="med_search_input"] div[data-baseweb="input"],
    div[data-testid="stTextInput"][data-key="med_search_input"] div[data-baseweb="base-input"] {
        height: 36px !important;
        min-height: 36px !important;
    }
    div[data-testid="stTextInput"][data-key="med_search_input"] input {
        height: 36px !important;
        line-height: 36px !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    .stTextInput div[data-baseweb="input"],
    .stTextInput div[data-baseweb="base-input"] {
        height: var(--input-height);
        align-items: center;
        border-radius: var(--radius-lg);
        overflow: hidden;
    }
    .stTextInput div[data-baseweb="input"] > div,
    .stTextInput div[data-baseweb="base-input"] > div {
        height: var(--input-height);
        display: flex;
        align-items: center;
    }
    .stNumberInput input {
        height: var(--input-height) !important;
        line-height: var(--input-height) !important;
        padding: 0 var(--space-4) !important;
        transform: none;
    }

    /* Number inputs (clean, no steppers) */
    .stNumberInput div[data-baseweb="input"] {
        border-radius: var(--radius-lg);
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow-card);
        background: white;
        height: var(--input-height);
        align-items: center;
        padding: 0 !important;
        overflow: hidden;
    }
    .stNumberInput div[data-baseweb="input"]:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(255, 90, 31, 0.2);
    }
    .stNumberInput div[data-baseweb="input"] > div {
        height: var(--input-height);
        display: flex;
        align-items: center;
        padding: 0 !important;
    }
    .stNumberInput div[data-baseweb="input"] button {
        display: none !important; /* Hide native steppers */
    }
    .stNumberInput input {
        height: var(--input-height) !important;
        line-height: var(--input-height) !important;
        padding: 0 var(--space-4) !important;
        background: transparent !important;
        width: 100%;
    }
    .stSelectbox div[data-baseweb="select"] {
        height: var(--input-height) !important;
        min-height: var(--input-height) !important;
        border-radius: var(--radius-lg) !important;
        overflow: hidden;
        padding: 0 !important;
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] [role="button"] {
        height: var(--input-height) !important;
        min-height: var(--input-height) !important;
        display: flex;
        align-items: center;
        padding: 0 var(--space-4) !important;
        box-sizing: border-box;
    }

    /* Forced White Background for inner containers */
    div[data-baseweb="input"], div[data-baseweb="base-input"] {
        background-color: white !important;
    }
    /* Hide the helper text/label space if unused */
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label {
        display: none; 
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        font-family: var(--font-display);
        font-weight: 500;
        box-sizing: border-box;
        height: var(--button-height) !important;
        min-height: var(--button-height) !important;
        font-size: var(--text-base) !important;
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--gray-200);
        transition: all 0.15s ease;
        background: white;
        color: var(--gray-700);
        box-shadow: 0 10px 20px rgba(15, 23, 42, 0.08);
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: var(--space-2);
        padding: 0 var(--space-4) !important;
        line-height: 1; 
        white-space: nowrap !important;
        width: 100%;
    }
    .stButton > button span,
    .stButton > button p {
        color: var(--gray-700) !important;
    }
    .stButton > button * {
        color: inherit !important;
        opacity: 1 !important;
    }
    .stButton > button[aria-label="+"],
    .stButton > button[aria-label="-"] {
        padding: 0 !important;
        min-width: 40px;
        width: 40px;
        font-size: 18px !important;
        font-weight: 700;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        background: #fff7ed;
        border-color: #fdba74;
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    /* Preview/Primary buttons */
    .stButton > button p {
        font-size: 16px;
        font-weight: 500;
        margin: 0;
    }

    /* ===== SELECTED MEDICATION CHIP ===== */
    .selected-chip {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: #f0fdfa;
        border-radius: var(--radius-md);
        margin-bottom: var(--space-4);
        border: 1px solid #99f6e4;
    }
    .selected-chip.compact {
        margin-bottom: 0;
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
        background: linear-gradient(135deg, #fff1e6 0%, #ffe4d6 100%);
        border-color: #fdba74;
        color: #9a3412;
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

    /* ===== MEDICATION LIST ITEMS ===== */
    .med-item {
        display: flex;
        align-items: center;
        padding: var(--space-4);
        background: linear-gradient(180deg, #ffffff 0%, #fff7ed 120%);
        border-radius: var(--radius-lg);
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        margin-bottom: var(--space-3);
        border: 1px solid #fed7aa;
        border-left: 4px solid var(--primary);
        animation: riseIn 0.4s ease both;
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
        margin-top: 4px;
    }
    
    /* Removed duplicative empty-state and med-list-header styles here.
       They are now handled by the specific class definitions added earlier. */
        border: 1px dashed var(--gray-300);
    }
    .empty-state-icon {
        font-size: 24px;
        margin-bottom: var(--space-1);
        opacity: 0.5;
    }
    .empty-state-title {
        font-size: var(--text-sm);
        font-weight: 500;
        color: var(--gray-600);
        margin-bottom: 0;
    }
    .empty-state-text {
        font-size: var(--text-xs);
        color: var(--gray-500);
        display: none;
    }

    /* ===== SEARCH RESULTS (Floating Dropdown) ===== */
    .search-container-wrapper {
        position: relative;
    }
    
    .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        z-index: 99999;
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-md);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        max-height: 300px;
        overflow-y: auto;
        margin-top: 4px;
    }
    .search-result {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--space-3) var(--space-4);
        background: white;
        border-bottom: 1px solid var(--gray-50);
        cursor: pointer;
        transition: all 0.15s;
        min-height: 50px;
    }
    .search-result:last-child {
        border-bottom: none;
    }
    .search-result:hover {
        background: #fff7ed;
        padding-left: var(--space-5); /* Slight movement effect */
    }
    .search-result-info {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .search-result-name {
        font-size: var(--text-base);
        font-weight: 600;
        color: var(--gray-900);
    }
    .search-result-cat {
        font-size: var(--text-xs);
        color: var(--gray-500);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }
    .search-result-add {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #ff5a1f 0%, #ff7a45 100%);
        color: white;
        border-radius: 50%;
        font-size: 18px;
        font-weight: 600;
        flex-shrink: 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .search-result:hover .search-result-add {
        transform: scale(1.1);
        background: linear-gradient(135deg, #ff7a45 0%, #ff5a1f 100%);
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
        font-family: var(--font-display);
    }

    /* ===== DIVIDER (Compact) ===== */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #fed7aa 40%, #99f6e4 60%, transparent 100%);
        margin: var(--space-2) 0;
    }

    /* ===== PREVIEW CARD ===== */
    .preview-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        box-shadow: var(--shadow-elevated);
        margin-bottom: var(--space-4);
        border: 2px solid #fdba74;
        animation: riseIn 0.5s ease both;
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
        font-family: var(--font-display);
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
        return [], None

    try:
        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        url = "https://health-products.canada.ca/api/drug/drugproduct/"
        params = {
            'brandname': clean_query,
            'lang': 'en',
            'type': 'json'
        }
        headers = {
            'User-Agent': 'Medication Schedule Builder/1.0'
        }

        try:
            response = requests.get(url, params=params, timeout=(5, 60), headers=headers)
        except requests.exceptions.ReadTimeout:
            response = requests.get(url, params=params, timeout=(5, 90), headers=headers)
        if response.status_code != 200:
            return [], f"Health Canada API error ({response.status_code})."

        data = response.json()

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

        return results[:30], None

    except requests.exceptions.Timeout:
        return [], "Health Canada API timed out. Please try again or check your network."
    except Exception as e:
        return [], "Health Canada API request failed."


def run_health_canada_search():
    """Fetch Health Canada results for the current search field."""
    query = st.session_state.get("hc_search", "").strip()
    if len(query) < 2:
        st.session_state.api_search_results = []
        st.session_state.hc_search_ran = False
        st.session_state.hc_search_last = ""
        st.session_state.hc_search_error = ""
        return
    st.session_state.hc_search_ran = True
    st.session_state.hc_search_last = query
    st.session_state.hc_search_error = ""
    with st.spinner("Searching Health Canada..."):
        api_results, api_error = search_health_canada_api(query)
    if api_results:
        st.session_state.api_search_results = api_results
    else:
        st.session_state.api_search_results = []
        if api_error:
            st.session_state.hc_search_error = api_error
            st.warning(api_error)
        else:
            st.warning("No results.")


def generate_dose_schedule(start_dose, target_dose, step_amount, days_per_step):
    """
    Generates a list of dates and doses.
    """
    schedule = []
    current_dose = start_dose
    current_date = datetime.now().date()

    if start_dose > target_dose:
        direction = -1  # Taper
    else:
        direction = 1  # Increase

    keep_calculating = True
    while keep_calculating:
        schedule.append({
            "date": current_date,
            "dose": current_dose,
            "duration_days": days_per_step
        })

        next_dose = current_dose + (step_amount * direction)

        if (direction == -1 and next_dose <= target_dose) or \
           (direction == 1 and next_dose >= target_dose):
            current_dose = target_dose
            keep_calculating = False
            schedule.append({
                "date": current_date + timedelta(days=days_per_step),
                "dose": current_dose,
                "note": "Target Reached"
            })
        else:
            current_dose = next_dose
            current_date = current_date + timedelta(days=days_per_step)

    return schedule


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
            <em>Experimental tool - not medical advice. Verify medication name, dose, route, and schedule against the patient's prescription. Must be reviewed by a licensed professional. Developer assumes no liability for errors, omissions, misuse, or outcomes.</em>
        </div>
    </div>
    '''
    return html


def generate_pdf(med_list):
    """Generate a landscape PDF with monthly calendar view."""
        # import calendar moved to top

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

                    # Medications for this day (skip past dates in current month)
                    if not (month == today.month and year == today.year and day_offset < 0):
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
                            day_dose = get_dose_for_day(med, day_offset)
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
        "Experimental tool - not medical advice. Verify medication name, dose, route, and schedule against the patient's prescription. Must be reviewed by a licensed professional. Developer assumes no liability for errors, omissions, misuse, or outcomes.",
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
if 'final_ack_check' not in st.session_state:
    st.session_state.final_ack_check = False

# =============================================================================
# CARD 1: ACTIONS PANEL (Title, Warning)
# =============================================================================

# Card 1 - Header section with gradient and warning
st.markdown('''
<div class="header-card">
    <div class="header-card-top">
        <div class="app-bar">
            <div class="app-bar-left">
                <div class="app-bar-icon">💊</div>
                <span class="app-bar-title">Medication Schedule</span>
            </div>
        </div>
    </div>
    <div class="header-card-body">
        <div class="warning-banner">
            <span class="warning-banner-icon">⚠️</span>
            <span class="warning-banner-text">Experimental tool - not medical advice. Use at your own risk. Always verify medication name, dose, route, and schedule against the patient's prescription. Must be reviewed by a licensed professional. Developer assumes no liability for errors, omissions, misuse, or outcomes.</span>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)


# =============================================================================
# ADD MEDICATION CARD (Tools Area)
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
if 'hc_search_ran' not in st.session_state:
    st.session_state.hc_search_ran = False
if 'hc_search_last' not in st.session_state:
    st.session_state.hc_search_last = ""
if 'hc_search_error' not in st.session_state:
    st.session_state.hc_search_error = ""

# Tools Card: Search + Buttons (Card 2)
# Using st.container(border=True) to create the card visual
with st.container(border=True):

    # === MEDICATION SELECTION ===
    if st.session_state.selected_medication:
        # Show selected medication chip + change button in one row
        med = st.session_state.selected_medication
        med_name = med.get('brand_name', med.get('name', 'Unknown'))
        chip_col, btn_col = st.columns([4, 1])
        with chip_col:
            st.markdown(f'''
                <div class="selected-chip compact">
                    <span class="selected-chip-name">{med_name}</span>
                </div>
            ''', unsafe_allow_html=True)
        with btn_col:
            if AppButton("Change", type="secondary", key="change_med"):
                st.session_state.selected_medication = None
                st.session_state.dose_value = 0.0
                st.session_state.selected_times = []
                st.session_state.manual_entry_mode = False
                st.rerun()

    elif st.session_state.manual_entry_mode:
        # Manual entry mode
        st.markdown('<p class="section-label">Medication name</p>', unsafe_allow_html=True)
        manual_name = AppInput(
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

        if AppButton("← Back to search", type="secondary"):
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

        # Calculate matches immediately (Dynamic Filtering)
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
                # Use a bordered container to mimic a dropdown list
                with st.container(border=True):
                    for i, med in enumerate(all_matches):
                        cat = med.get('category', '')
                        if AppButton(f"➕ {med['brand_name']} — {cat}", key=f"med_result_{i}"):
                            st.session_state.selected_medication = {
                                **med,
                                'source': 'health_canada' if med in st.session_state.api_search_results else 'database'
                            }
                            st.rerun()
            else:
                st.caption("No matches found.")

        # Equal-width buttons row (Buttons moved below results to allow expansion)
        if 'show_hc_search' not in st.session_state:
            st.session_state.show_hc_search = False

        btn_col1, btn_col2 = st.columns(2, gap="small")
        with btn_col1:
            if AppButton("✏️ Add manually", key="manual_entry_btn", type="secondary"):
                st.session_state.manual_entry_mode = True
                st.rerun()
        with btn_col2:
            if AppButton("🔍 Browse meds", key="hc_toggle_btn", type="secondary"):
                st.session_state.show_hc_search = not st.session_state.show_hc_search
                st.rerun()

        # Health Canada search (collapsible)
        if st.session_state.show_hc_search:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            hc_col1, hc_col2 = st.columns([6, 1], gap="small")
            with hc_col1:
                hc_query = AppInput(
                    "",
                    placeholder="Search 47K+ products...",
                    key="hc_search",
                    label_visibility="collapsed"
                )
            with hc_col2:
                if AppButton("Go", key="hc_search_btn"):
                    run_health_canada_search()

            if (
                st.session_state.hc_search_ran
                and st.session_state.hc_search_last == (hc_query or "").strip()
            ):
                if st.session_state.hc_search_error:
                    hc_query_clean = re.sub(r'[^\w\s]', '', st.session_state.hc_search_last).strip()
                    hc_url = (
                        "https://health-products.canada.ca/api/drug/drugproduct/"
                        f"?brandname={hc_query_clean}&lang=en&type=json"
                    )
                    st.markdown(
                        f'Can\'t reach the API? <a href="{hc_url}" target="_blank" rel="noopener noreferrer">Open results in your browser</a>.',
                        unsafe_allow_html=True
                    )
                if st.session_state.api_search_results:
                    with st.container(border=True):
                        for i, med in enumerate(st.session_state.api_search_results[:10]):
                            cat = med.get('category', 'Health Canada')
                            if AppButton(f"➕ {med['brand_name']} — {cat}", key=f"hc_result_{i}"):
                                st.session_state.selected_medication = {
                                    **med,
                                    'source': 'health_canada'
                                }
                                st.rerun()
                else:
                    st.caption("No Health Canada results found.")

# =============================================================================
# DOSE SECTION (shown after medication selected)
# =============================================================================

if st.session_state.selected_medication:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Dose</p>', unsafe_allow_html=True)

    dose_col1, dose_col2 = st.columns([2, 1])
    with dose_col1:
        dose_val = AppNumberInput(
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
        dose_unit = AppSelect(
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

                g_col1, g_col2 = st.columns(2, gap="small")
                with g_col1:
                    st.markdown('<p class="mini-label">Start dose</p>', unsafe_allow_html=True)
                    start_dose = AppNumberInput("Start", min_value=0.0, value=st.session_state.dose_value, step=0.5, format="%.1f", key="grad_start", label_visibility="collapsed")
                with g_col2:
                    st.markdown('<p class="mini-label">Target dose</p>', unsafe_allow_html=True)
                    end_dose = AppNumberInput("End", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="grad_end", label_visibility="collapsed")

                g_col3, g_col4 = st.columns(2, gap="small")
                with g_col3:
                    st.markdown('<p class="mini-label">Change by</p>', unsafe_allow_html=True)
                    change_amt = AppNumberInput("Change by", min_value=0.1, value=5.0, step=0.5, format="%.1f", key="grad_change", label_visibility="collapsed")
                with g_col4:
                    st.markdown('<p class="mini-label">Every X days</p>', unsafe_allow_html=True)
                    change_days = AppNumberInput("Every X days", min_value=1, value=7, step=1, key="grad_days", label_visibility="collapsed")

                # Validate inputs before building schedule
                input_errors = []
                if change_amt <= 0:
                    input_errors.append("Change by must be > 0")
                if int(change_days) < 1:
                    input_errors.append("Every X days must be >= 1")

                is_taper = "Taper" in direction
                if is_taper and start_dose <= end_dose:
                    input_errors.append("Start dose must be greater than target dose for taper")
                if (not is_taper) and start_dose >= end_dose:
                    input_errors.append("Target dose must be greater than start dose for increase")

                if input_errors:
                    st.warning("Fix: " + "; ".join(input_errors))
                    doses = []
                else:
                    # Calculate schedule using date-based steps
                    schedule = generate_dose_schedule(start_dose, end_dose, change_amt, int(change_days))

                    # Convert date-based schedule to day offsets for existing logic
                    today_date = datetime.now().date()
                    doses = []
                    for item in schedule:
                        day_offset = (item["date"] - today_date).days
                        doses.append({"day": day_offset, "dose": item["dose"]})

                    if doses:
                        preview = " -> ".join([f"Day {d['day']+1}: {d['dose']}" for d in doses[:4]])
                        if len(doses) > 4:
                            preview += f" ... ({len(doses)} steps)"
                        st.caption(preview)

                dose_schedule = {
                    "type": "gradual",
                    "direction": "taper" if is_taper else "increase",
                    "start_dose": start_dose,
                    "end_dose": end_dose,
                    "change_amount": change_amt,
                    "change_days": int(change_days),
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
                        if AppButton("✕", key=f"rm_cd_{i}"):
                            st.session_state.custom_doses.pop(i)
                            st.rerun()

                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    cd_start = AppNumberInput("From", min_value=1, value=1, key="cd_from")
                with cc2:
                    cd_end = AppNumberInput("To", min_value=1, value=7, key="cd_to")
                with cc3:
                    cd_dose = AppNumberInput("Dose", min_value=0.0, value=st.session_state.dose_value, step=0.5, format="%.1f", key="cd_dose")

                if AppButton("Add range", key="add_cd_range"):
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

    # Time chip buttons in 2x2 grid (compact)
    time_options = [
        ("Morning", "☀️ AM"),
        ("Noon", "🕛 Noon"),
        ("Evening", "🌙 PM"),
        ("Bedtime", "🛏️ Bed")
    ]

    chip_cols = st.columns(4)
    for i, (key, label) in enumerate(time_options):
        with chip_cols[i]:
            is_selected = key in st.session_state.selected_times
            btn_type = "primary" if is_selected else "secondary"
            display_label = f"✓ {label}" if is_selected else label

            if AppButton(display_label, key=f"time_chip_{key}", type=btn_type):
                if is_selected:
                    st.session_state.selected_times.remove(key)
                else:
                    st.session_state.selected_times.append(key)
                st.rerun()

    # =========================================================================
    # INLINE ADD BUTTON (appears only when medication is being configured)
    # =========================================================================

    # Determine medication name and source
    medication_name = st.session_state.selected_medication.get('brand_name', st.session_state.selected_medication.get('name'))
    source_type = st.session_state.selected_medication.get('source', 'database')

    # Validation
    can_add = st.session_state.dose_value > 0 and len(st.session_state.selected_times) > 0

    # Compact summary + Add button in single row
    if can_add:
        times_str = ", ".join(st.session_state.selected_times)
        st.markdown(f'''
        <div style="background: var(--success-light); padding: var(--space-2) var(--space-3); border-radius: var(--radius-md); margin-top: var(--space-2); display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: var(--text-sm); color: var(--gray-700);">
                <strong>{medication_name}</strong> • {st.session_state.dose_value} {st.session_state.dose_unit} • {times_str}
            </span>
        </div>
        ''', unsafe_allow_html=True)

        # Add to list button
        if AppButton("✓ Add to List", type="primary", key="add_med_btn"):
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
    else:
        # Show what's missing
        missing = []
        if st.session_state.dose_value <= 0:
            missing.append("dose")
        if not st.session_state.selected_times:
            missing.append("time")
        st.caption(f"Enter {' and '.join(missing)} to add")




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

    # Final acknowledgement before print/download
    final_ack_check = st.checkbox(
        "I understand this is an experimental tool, not medical advice, and I am responsible for verifying medication name, dose, route, and schedule with a licensed professional.",
        key="final_ack_check"
    )

    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3, gap="small")

    with btn_col1:
        view_pdf_enabled = final_ack_check
        view_pdf_href = f"data:application/pdf;base64,{pdf_base64}" if view_pdf_enabled else "#"
        view_pdf_style = (
            "display: flex; align-items: center; justify-content: center; "
            "width: 100%; height: 50px; background-color: var(--primary); color: white; "
            "text-decoration: none; border-radius: var(--radius-md); font-weight: 600; "
            "font-size: var(--text-base); border: 1px solid rgba(255,255,255,0.2); "
            "box-shadow: 0 1px 2px rgba(0,0,0,0.05); transition: all 0.2s;"
            if view_pdf_enabled else
            "display: flex; align-items: center; justify-content: center; "
            "width: 100%; height: 50px; background-color: #e2e8f0; color: #94a3b8; "
            "text-decoration: none; border-radius: var(--radius-md); font-weight: 600; "
            "font-size: var(--text-base); border: 1px solid #e2e8f0;"
        )
        # "View PDF" button (Styled EXACTLY like a primary button)
        # Using a full-width div wrapper to simulate use_container_width=True behavior
        st.markdown(f'''
            <a href="{view_pdf_href}"
               target="_blank"
               title="Open PDF in new tab"
               style="{view_pdf_style}">
                📄 View PDF
            </a>
        ''', unsafe_allow_html=True)

    with btn_col2:
        st.download_button(
            label="💾 Download",
            data=pdf_bytes,
            file_name=f"Medication_Calendar_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            disabled=not final_ack_check
        )

    with btn_col3:
        if AppButton("✕ Close", key="close_preview", type="secondary", use_container_width=True):
            st.session_state.show_preview_modal = False
            st.rerun()

    st.markdown('<div style="margin-bottom: var(--space-4);"></div>', unsafe_allow_html=True)


# =============================================================================
# CARD 2: LIST PANEL (Patient Medications, Preview, Footer)
# =============================================================================

# Card 2 - List Panel (Renamed to Section Header)
st.markdown('''
<div class="section-header">
    <span class="section-title">Patient Medications</span>
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
            if AppButton("🗑️", key=f"remove_{idx}", help="Remove"):
                st.session_state.med_list.pop(idx)
                reset_all_verifications()
                st.toast("Removed")
                st.rerun()

# =============================================================================
# PREVIEW SCHEDULE BUTTON (after medication list)
# =============================================================================

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

has_meds = len(st.session_state.med_list) > 0
all_verified = check_all_verified() if has_meds else False

if has_meds and all_verified:
    if AppButton("📄 Preview Schedule", key="preview_schedule_btn", type="primary"):
        st.session_state.final_ack_check = False
        st.session_state.show_preview_modal = True
        st.rerun()
elif has_meds:
    AppButton("📄 Preview Schedule", key="preview_schedule_btn", disabled=True)
    st.markdown('<p style="text-align: center; font-size: 12px; color: #6b7280;">✓ Verify all medications above to enable preview</p>', unsafe_allow_html=True)
else:
    AppButton("📄 Preview Schedule", key="preview_schedule_btn", disabled=True)
    st.markdown('<p style="text-align: center; font-size: 12px; color: #6b7280;">Add medications above to generate schedule</p>', unsafe_allow_html=True)


# =============================================================================
# FOOTER
# =============================================================================

st.markdown("""
<div class="app-footer">
    <p style="margin: 0; line-height: 1.6;">
        For pharmacy use<br>        Experimental tool - not medical advice; verify medication name, dose, route, and schedule<br>
        Must be reviewed by a licensed professional; developer assumes no liability
    </p>
</div>
""", unsafe_allow_html=True)
