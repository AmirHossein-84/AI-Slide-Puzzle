# Implementation Steps: Web App & 43-Slot Transformation

## Phase 1: 43-Slot Engine & Graph Parity Refactor
- [x] **Step 1.1**: Update `src/environment/puzzle_state.py` to support 43 board positions (42 tiles $1\dots42$ in $6\times7$ grid + bottom-left pocket $(7, 0)$ as blank $0$).
- [x] **Step 1.2**: Update mathematical parity solvability invariant for 43-slot graph.
- [x] **Step 1.3**: Update `src/environment/puzzle_env.py` for 43 positions.
- [x] **Step 1.4**: Update unit tests in `tests/test_puzzle_state.py` and `tests/test_puzzle_env.py` (100% pass rate).

## Phase 2: 43-Slot Multi-Solver Suite Refactor
- [x] **Step 2.1**: Update `src/solvers/astar_solver.py` and `src/solvers/idastar_solver.py` for 43-slot state.
- [x] **Step 2.2**: Update `src/solvers/hierarchical_solver.py` to solve 43-slot board (solves rows $0\dots5$, columns $1\dots5$, and parks blank in pocket $(7, 0)$ in $< 0.2\text{s}$).
- [x] **Step 2.3**: Update `src/models/heuristic_net.py` and `src/solvers/neural_solver.py`.
- [x] **Step 2.4**: Run pytest on solver test suite (`tests/test_solvers.py`, `tests/test_neural_solver.py` passing 100%).

## Phase 3: FastAPI & WebSocket AI Server
- [x] **Step 3.1**: Add `fastapi`, `uvicorn`, `websockets` to `requirements.txt` and install in `.venv`.
- [x] **Step 3.2**: Implement `src/server/schemas.py` (Pydantic data contracts).
- [x] **Step 3.3**: Implement `src/server/app.py` (REST endpoints `/api/state`, `/api/scramble`, `/api/solve` and WebSocket `/ws/solve` for live streaming).
- [x] **Step 3.4**: Test FastAPI server endpoints (`tests/test_server.py` passing 100%).

## Phase 4: React + Vite + Tailwind + Framer Motion Frontend
- [x] **Step 4.1**: Initialize React + TypeScript + Vite project under `web/`.
- [x] **Step 4.2**: Install `tailwindcss`, `framer-motion`, `lucide-react`, `canvas-confetti`.
- [x] **Step 4.3**: Copy 42 tile sprites into `web/public/tiles/`.
- [x] **Step 4.4**: Implement `Board43.tsx` with retro Digimon casing, 42 grid tiles, and the bottom-left parking pocket with fluid animations.
- [x] **Step 4.5**: Implement `Controls.tsx`, `Telemetry.tsx`, and `App.tsx` (Production bundle built cleanly in `dist/`).

## Phase 5: One-Command Launcher & End-to-End Verification
- [x] **Step 5.1**: Implement `run_web.py` (single-command launcher that boots FastAPI on port 8000 and Vite on port 5173).
- [x] **Step 5.2**: Test browser loading and live auto-solving.
- [x] **Step 5.3**: Update `README.md` and `walkthrough.md` with complete web instructions and troubleshooting.
