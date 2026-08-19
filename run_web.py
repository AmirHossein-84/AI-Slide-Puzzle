#!/usr/bin/env python3
"""Unified One-Command Launcher for Digimon Sliding Puzzle Web App & AI Server."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def wait_for_port(port: int = 8000, host: str = "127.0.0.1", timeout: float = 6.0) -> bool:
    """Waits until the backend server is accepting TCP connections."""
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.2):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)
    return False


def main() -> int:
    """Launches both FastAPI AI Server and React Vite Frontend concurrently."""
    project_root = Path(__file__).parent.resolve()
    web_dir = project_root / "web"
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = Path(sys.executable)

    print("\n" + "=" * 65)
    print("  🧩 DIGIMON 43-SLOT SLIDING PUZZLE - WEB & AI SERVER LAUNCHER")
    print("=" * 65)
    print(f"[*] Project Root  : {project_root}")
    print(f"[*] Python Engine : {venv_python}")
    print(f"[*] Web Client Dir: {web_dir}")
    print("=" * 65 + "\n")

    # 1. Start FastAPI Backend (Port 8000)
    print("[*] Starting Python FastAPI & WebSocket AI Server on port 8000...")
    backend_cmd = [
        str(venv_python),
        "-m",
        "uvicorn",
        "src.server.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--log-level",
        "warning",
    ]

    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(project_root),
        shell=False,
    )

    # Wait for backend to be ready
    wait_for_port(port=8000, timeout=8.0)

    # 2. Start Vite Frontend (Port 5173)
    print("[*] Starting React + Vite Frontend on port 5173...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(web_dir),
        shell=True,
    )

    time.sleep(1.5)
    frontend_url = "http://localhost:5173"
    print("\n" + "-" * 65)
    print(f"[+] Web Application running at: {frontend_url}")
    print(f"[+] Python FastAPI AI Backend : http://127.0.0.1:8000/docs")
    print("-" * 65)
    print("[*] Press Ctrl+C at any time to stop both servers.\n")

    try:
        webbrowser.open(frontend_url)
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down servers...")
        frontend_proc.terminate()
        backend_proc.terminate()
        print("[+] Goodbye!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
