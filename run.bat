@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Creating sample Excel file...
python create_sample.py

echo.
echo Starting Application...
streamlit run app.py
