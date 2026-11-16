@echo off
cd /d "%~dp0"

echo Opening WiFi Wireless Mouse and Keyboard Server...
uv run python main.py
