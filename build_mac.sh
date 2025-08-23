#!/bin/bash
python3 -m PyInstaller Bin/Main.py \
    --noconsole \
    --noconfirm \
    --hidden-import=PyQt6 \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --add-data "Data:Data" \
    --add-data "Bin:Bin" \
    --add-data "Achievement Icons:Achievement Icons" \
    --add-data "DLC:DLC"
