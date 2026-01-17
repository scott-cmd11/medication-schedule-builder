# Medication Schedule Builder (RxFlow Canada)

Mobile-first Streamlit app for building patient medication schedules with guardrails, verification, and PDF export.

## Features
- Add medications by search or manual entry
- Dose and unit selection with optional variable/tapering schedules
- Time-of-day selection chips
- Verification checklist before preview
- PDF schedule preview and download

## Requirements
- Python 3.9+
- Packages listed in `requirements.txt`

## Quick start
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Notes
- The app stores state in Streamlit session state during use.
- PDF output is generated client-side from the current medication list.

## Project structure
- `app.py` - Streamlit application and UI styles
- `requirements.txt` - Python dependencies
