@echo off
chcp 65001 > NUL
echo ========================================================
echo   씨제이씨협동조합 AI 블로그 마케팅 자동화 시스템 (Windows)
echo ========================================================
echo.
echo 가상환경 활성화 및 로컬 웹 서버(http://localhost:8501)를 구동합니다...
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [알림] 가상환경(venv)을 탐색 중입니다...
)

streamlit run app.py

pause
