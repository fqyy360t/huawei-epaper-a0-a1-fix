@echo off
chcp 936 >nul
title MF-INK Flash
echo.
echo  ============================================
echo   MF-INK V1.0.4  yi jian shua ji
echo  ============================================
echo.
echo   Qing ba banzi USB cha hao, ran hou an ren yi jian kai shi...
pause >nul
echo.
"C:/Users/fqyy3/.workbuddy/binaries/python/versions/3.13.12/python.exe" "F:/git/huawei-epaper-a0-a1-fix/scripts/flash_mfink.py"
echo.
echo  Sha ji jie shu, an ren yi jian guan bi chuang kou.
pause >nul