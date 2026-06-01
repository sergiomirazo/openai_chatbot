"""Build script for creating Windows .exe using PyInstaller.

Usage:
    python build_exe.py
"""

import subprocess
import sys
from pathlib import Path


def main():
    root = Path(__file__).parent
    main_script = root / "main.py"
    dist_dir = root / "dist"
    build_dir = root / "build"
    name = "ChatBotAI"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", name,
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
        "--add-data", f"src{';'}src",
        "--hidden-import", "kivy_deps.sdl2",
        "--hidden-import", "kivy_deps.glew",
        "--hidden-import", "kivy_deps.angle",
        "--hidden-import", "kivy_deps.gstreamer",
        "--hidden-import", "openai",
        "--hidden-import", "keyring",
        "--hidden-import", "platformdirs",
        "--collect-all", "kivy",
        str(main_script),
    ]

    print(f"Building {name}.exe...")
    result = subprocess.run(cmd, cwd=str(root))
    if result.returncode == 0:
        print(f"Build successful! Output: {dist_dir / name}.exe")
    else:
        print("Build failed.", file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
