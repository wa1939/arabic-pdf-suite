@echo off
if not exist .venv (
  py -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py --server.port 3000 --server.address 0.0.0.0
pause
