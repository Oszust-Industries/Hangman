@echo off
python -m PyInstaller Bin/Main.py ^
    --noconsole ^
    --noconfirm ^
    --icon="Data/exeIcon.ico" ^
    --add-data "Data;Data" ^
    --add-data "Bin;Bin" ^
    --add-data "Achievement Icons;Achievement Icons" ^
    --add-data "DLC;DLC" ^