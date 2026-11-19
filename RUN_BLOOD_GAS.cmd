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
if not exist "%~dp0app\dist\index.html" (
  echo Falta compilar la interfaz local en app\dist.
  exit /b 1
)
echo EMERGENCY T05 - CLINICALLY_PENDING - SOLO DATOS SINTETICOS
echo Abra en el navegador la URL local que aparece debajo.
echo Mantenga esta ventana abierta. Para terminar, pulse Ctrl+C.
"%BG_PYTHON%" -X utf8 clinical\scripts\blood_gas_local.py
set "BG_EXIT=%ERRORLEVEL%"
pause
exit /b %BG_EXIT%
