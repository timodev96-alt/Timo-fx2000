import subprocess
import sys
import os
import platform
import shutil

APP_NAME    = "Timof(x)2000"
ENTRY_POINT = "main.py"
ICON_WIN    = "icon.ico"
ICON_MAC    = "icon.icns"

HIDDEN_IMPORTS = [
    "numpy",
    "numpy.core._multiarray_umath",
    "numpy.core._multiarray_tests",
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "matplotlib.figure",
    "matplotlib.pyplot",
    "tkinter",
    "tkinter.ttk",
    "PIL",
]

def run(cmd: list[str]):
    print("\n▶  " + " ".join(cmd) + "\n")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\nCommand failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def ensure_pyinstaller():
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} found.")
    except ImportError:
        print("PyInstaller not found — installing...")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def clean_previous():
    for folder in ("build", "dist", f"{APP_NAME}.spec"):
        if os.path.exists(folder):
            print(f"Removing old {folder}/")
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            else:
                os.remove(folder)

def build():
    os_name = platform.system()   # "Windows" | "Darwin" | "Linux"
    print(f"\n🖥   Detected OS: {os_name}")

    ensure_pyinstaller()
    clean_previous()
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name", APP_NAME,
        "--windowed",
        *sum([["--hidden-import", h] for h in HIDDEN_IMPORTS], []),

        "--add-data", f"ui{os.pathsep}ui",

        "--collect-all", "numpy",
        "--collect-all", "matplotlib",
    ]

    if os_name == "Windows" and os.path.exists(ICON_WIN):
        cmd += ["--icon", ICON_WIN]
    elif os_name == "Darwin" and os.path.exists(ICON_MAC):
        cmd += ["--icon", ICON_MAC]
    cmd += ["--onefile"]

    cmd.append(ENTRY_POINT)
    run(cmd)

    dist_path = os.path.join("dist", APP_NAME)
    if os_name == "Windows":
        exe_path = dist_path + ".exe" if os.path.exists(dist_path + ".exe") else dist_path
    else:
        exe_path = dist_path

    print(f"Build complete!")
    print(f"utput folder : dist/{APP_NAME}/")
    if os_name == "Windows":
        print(f"Launch with   : dist\\{APP_NAME}\\{APP_NAME}.exe")
    elif os_name == "Darwin":
        print(f"Launch with   : open dist/{APP_NAME}/{APP_NAME}.app")
    else:
        print(f"Launch with   : ./dist/{APP_NAME}/{APP_NAME}")

if __name__ == "__main__":
    build()
