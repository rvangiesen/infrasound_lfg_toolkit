"""
Laptop Setup & Dependency Installer for Infrasound & LGF Toolkit
Automates installation of Python dependencies, Dracal utilities, and launcher scripts.
"""

import sys
import os
import subprocess
import shutil

# Ensure UTF-8 output encoding for Windows CLI stdout
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_PATH = os.path.join(PROJECT_DIR, "requirements.txt")
DRACAL_INSTALLER = os.path.join(PROJECT_DIR, "DracalUtilities-3.7.0.exe")

STANDARD_DRACAL_PATHS = [
    r"C:\Program Files\Dracal\Cmd\dracal-usb-get.exe",
    r"C:\Program Files (x86)\Dracal\Cmd\dracal-usb-get.exe",
    r"C:\Program Files\Dracal\DracalView.exe",
    r"C:\Program Files (x86)\Dracal\DracalView.exe"
]

def check_dracal_installed():
    for p in STANDARD_DRACAL_PATHS:
        if os.path.exists(p):
            return True, p
    return False, ""

def install_python_requirements():
    print("=== [1/3] Checking & Installing Python Dependencies ===")
    if not os.path.exists(REQUIREMENTS_PATH):
        print(f"Error: {REQUIREMENTS_PATH} not found.")
        return False
    
    cmd = [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_PATH]
    try:
        res = subprocess.run(cmd, check=True)
        print("[OK] Python dependencies successfully installed/verified.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install Python dependencies: {e}")
        return False

def check_and_install_dracal(interactive=True):
    print("\n=== [2/3] Checking Dracal Sensor Software ===")
    installed, found_path = check_dracal_installed()
    if installed:
        print(f"[OK] Dracal software detected at: {found_path}")
        return True
    
    print("[WARNING] Dracal software (dracal-usb-get.exe / DracalView) not found in standard program files.")
    if os.path.exists(DRACAL_INSTALLER):
        print(f"[INFO] Found offline installer: {os.path.basename(DRACAL_INSTALLER)}")
        if interactive:
            print("Launching Dracal Utilities installer...")
            try:
                subprocess.Popen([DRACAL_INSTALLER])
                print("[INFO] Please complete the Dracal installer wizard on screen.")
            except Exception as e:
                print(f"[ERROR] Could not launch Dracal installer: {e}")
    else:
        print("[WARNING] Installer DracalUtilities-3.7.0.exe not found in project directory.")
    return False

def create_launcher_scripts():
    print("\n=== [3/3] Creating 1-Click Launchers ===")
    bat_content = f"""@echo off
TITLE Infrasound & LGF Toolkit Launcher
echo Starting Infrasound & LGF Meetstation...
cd /d "{PROJECT_DIR}"
"{sys.executable}" -m streamlit run app.py
pause
"""
    bat_path = os.path.join(PROJECT_DIR, "start_app.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)
    print(f"[OK] Created launcher script: {bat_path}")

    # Also create desktop shortcut script if on Windows
    desktop_bat = os.path.join(os.path.expanduser("~"), "Desktop", "Start_Infrasound_Toolkit.bat")
    try:
        with open(desktop_bat, "w", encoding="utf-8") as f:
            f.write(bat_content)
        print(f"[OK] Created Desktop shortcut: {desktop_bat}")
    except Exception as e:
        print(f"[NOTE] Could not write Desktop shortcut ({e}), launcher script available in project directory.")

def main():
    print("=" * 60)
    print(" INFRASOUND & LFG TOOLKIT LAPTOP AUTOMATED SETUP")
    print("=" * 60)
    
    success = install_python_requirements()
    check_and_install_dracal(interactive=True)
    create_launcher_scripts()
    
    print("\n=" * 60)
    if success:
        print(" SETUP COMPLETE! You can now start the application by running:")
        print("   start_app.bat  (or running 'streamlit run app.py')")
    else:
        print("[WARNING] Setup completed with some warnings. Check logs above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
