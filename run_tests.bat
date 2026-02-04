@echo off
cd /d D:\Projet_streamlit\assistant_matanne
echo Running tests/core/...
python -m pytest tests/core/ -v --tb=no -q 2>&1 > test_core_output.txt
type test_core_output.txt | findstr /r "passed failed skipped"

echo.
echo Running tests/services/...
python -m pytest tests/services/ -v --tb=no -q 2>&1 > test_services_output.txt
type test_services_output.txt | findstr /r "passed failed skipped"

echo.
echo Done. Check test_*_output.txt files for details.
