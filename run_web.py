#!/usr/bin/env python3
"""Unified One-Command Launcher for Digimon Sliding Puzzle Web App & AI Server."""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import List


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Checks if a TCP port can be bound without Windows access permission errors."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except (OSError, PermissionError):
            return False


def find_free_port(preferred_ports: List[int] | None = None, host: str = "127.0.0.1") -> int:
    """Finds an available TCP port, checking preferred candidates before falling back to system allocation."""
    if preferred_ports is None:
        preferred_ports = [8100, 8080, 8888, 8000, 8088]

    for port in preferred_ports:
        if is_port_available(port, host=host):
            return port

    # Fallback to ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def wait_for_port(port: int, host: str = "127.0.0.1", timeout: float = 6.0) -> bool:
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
    parser = argparse.ArgumentParser(description="Digimon Sliding Puzzle Web & AI Server Launcher")
    parser.add_argument("--port", type=int, default=None, help="Custom port for Python AI backend")
    args = parser.parse_args()

    project_root = Path(__file__).parent.resolve()
    web_dir = project_root / "web"
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = Path(sys.executable)

    # 1. Determine safe backend port (avoiding Windows Hyper-V / WSL excluded port ranges)
    if args.port and is_port_available(args.port):
        backend_port = args.port
    else:
        backend_port = find_free_port(preferred_ports=[8100, 8080, 8888, 8000, 8088])

    print("\n" + "=" * 65)
    print("  🧩 DIGIMON 43-SLOT SLIDING PUZZLE - WEB & AI SERVER LAUNCHER")
    print("=" * 65)
    print(f"[*] Project Root  : {project_root}")
    print(f"[*] Python Engine : {venv_python}")
    print(f"[*] AI Backend Port: {backend_port}")
    print(f"[*] Web Client Dir: {web_dir}")
    print("=" * 65 + "\n")

    # 2. Start FastAPI Backend
    print(f"[*] Starting Python FastAPI & WebSocket AI Server on port {backend_port}...")
    backend_cmd = [
        str(venv_python),
        "-m",
        "uvicorn",
        "src.server.app:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(backend_port),
        "--log-level",
        "warning",
    ]

    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(project_root),
        shell=False,
    )

    # Wait for backend to be ready
    is_ready = wait_for_port(port=backend_port, timeout=8.0)
    if not is_ready:
        print(f"[!] Warning: Backend server on port {backend_port} took longer than expected to initialize.")

    # 3. Start Vite Frontend with dynamic backend port
    print("[*] Starting React + Vite Frontend on port 5173...")
    env = os.environ.copy()
    env["VITE_BACKEND_PORT"] = str(backend_port)

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(web_dir),
        env=env,
        shell=True,
    )

    time.sleep(1.5)
    frontend_url = "http://localhost:5173"
    print("\n" + "-" * 65)
    print(f"[+] Web Application running at: {frontend_url}")
    print(f"[+] Python FastAPI AI Backend : http://127.0.0.1:{backend_port}/docs")
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
