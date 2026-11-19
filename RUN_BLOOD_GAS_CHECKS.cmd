@echo off
setlocal
cd /d "%~dp0"
if not defined BG_PYTHON set "BG_PYTHON=python"
if not defined BG_OCR_MODEL set "BG_OCR_MODEL=%~dp0tools\blood-gas-ocr\models\eng.traineddata"
set "NODE_PATH=%~dp0tools\blood-gas-ocr\node_modules"
set "PYTHONUTF8=1"
set "PYTHONDONTWRITEBYTECODE=1"
if not exist "%BG_OCR_MODEL%" (
  echo Falta el modelo OCR verificado. Consulte docs\BLOOD_GAS_LOCAL.md.
  exit /b 1
)
if not exist "%NODE_PATH%\tesseract.js\package.json" (
  echo Instale las dependencias OCR fijadas con npm ci --ignore-scripts --prefix tools\blood-gas-ocr.
  exit /b 1
)
echo Pruebas locales con datos sinteticos. No crean commits ni publican.
"%BG_PYTHON%" -X utf8 -m unittest discover -s clinical\tests -p "test_blood_gas_*.py" -v
if errorlevel 1 exit /b 1
"%BG_PYTHON%" -X utf8 -m unittest discover -s clinical\tests -p "test_acid_base_review.py" -v
set "BG_EXIT=%ERRORLEVEL%"
pause
exit /b %BG_EXIT%
