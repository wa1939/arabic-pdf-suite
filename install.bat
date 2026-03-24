@echo off
set APP_DIR=arabic-pdf-suite
if not exist %APP_DIR% (
  git clone https://github.com/wa1939/arabic-pdf-suite.git %APP_DIR%
)
cd %APP_DIR%
py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 3000
