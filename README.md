# 🧩 Digimon 43-Slot Web Sliding Puzzle & AI Multi-Solver Suite

An advanced, high-performance **Web-based Sliding Tile Puzzle Game & AI/ML Solving Suite** written in **React 18 + Vite + Tailwind CSS + Framer Motion** (Frontend) and **Python FastAPI + WebSockets + PyTorch** (Backend).

Modeled directly after the real-world handheld **Digimon 42-Tile Sliding Puzzle with an Extra Parking Pocket (43 total positions)**!

---

## 🌟 Key Features

- **🌐 Modern Web Application (`web/`)**:
  - **Authentic 90s Handheld Toy Casing**: Retro green plastic frame with molded logo, power indicator lamps, and tactile click sounds via Web Audio API.
  - **Exact 43-Slot Geometry**: All 42 Digimon tiles ($1 \dots 42$) fill the $6 \times 7$ grid, and a dedicated **bottom-left parking pocket $(7, 0)$** holds the empty space ($0$) in the solved state!
  - **Framer Motion Fluid Physics**: Smooth animated sliding transitions for tiles moving across the grid and into/out of the parking pocket.
  - **Live WebSocket Auto-Solving**: Real-time step-by-step streaming with variable playback speeds ($1\times$ to $25\times$), step navigation, and victory confetti.
  - **Full Human Play Mode**: Interactive click-to-slide and keyboard arrow key controls.
- **🧠 Multi-Solver AI Suite**:
  1. **Hierarchical Subgoal Solver**: Systematic row-by-row reduction solving the massive $3 \times 10^{52}$ 43-slot state space in **under 0.2 seconds**!
  2. **A\* Search (Linear Conflict)**: Admissible Manhattan Distance + Linear Conflict heuristic pathfinding.
  3. **IDA\* (Iterative Deepening A\*)**: Memory-efficient optimal search.
  4. **Neural AI (PyTorch DeepCubeA)**: Deep Residual ConvNet trained via Autodidactic Iteration (ADI) to estimate cost-to-go.
- **⚡ High-Performance Mathematical Engine**:
  - **Exact Inversion Parity Solvability Invariant** tailored for the 43-slot topology.
  - **185,000+ state transitions/sec** throughput.
- **🚀 One-Command Launcher (`python run_web.py`)**:
  - Single command boots both the FastAPI AI server on port 8000 and the Vite web client on port 5173, then automatically opens your browser.

---

## 🚀 Quick Start Guide

### 1. Launch the Web Game with One Command
Open your terminal (PowerShell) in the project directory:
```powershell
.\.venv\Scripts\python run_web.py
```
*(Automatically starts the FastAPI backend, the React frontend, and opens `http://localhost:5173` in your default web browser)*

---

### 2. How to Play & Control the Web Game

- **Slide Tiles**: Click on any tile adjacent to the blank space, or use the **Arrow Keys** on your keyboard.
- **Scramble Board**: Select your desired scramble depth on the slider and click **🔀 Scramble Board** (guaranteed 100% solvable).
- **Solve with AI**:
  1. Pick a solver from the dropdown menu (e.g. **Hierarchical Solver (< 0.2s)** or **Neural AI**).
  2. Click **🧠 Solve with AI**.
  3. Watch the AI solve the board live with animated step streaming!
  4. Use **⏸ Pause / ▶ Play** and the **Playback Speed** slider to inspect individual moves.
- **Visual Toggles**:
  - Click **🔢 Numbers** to toggle number badge overlays on/off.
  - Click **🎨 Style** to switch between authentic Digimon character artwork and retro procedural blue tiles.

---

### 3. Train the PyTorch Deep Learning Model
Train your own neural cost-to-go model using Autodidactic Iteration (ADI) on your RTX 3050 GPU:

```powershell
# Fast training verification on 3x3 boards (~15 seconds):
.\.venv\Scripts\python train.py --rows 3 --cols 3 --epochs 20 --batch-size 256

# Train on the full 43-slot Digimon board:
.\.venv\Scripts\python train.py --rows 7 --cols 6 --epochs 50 --batch-size 1024 --max-depth 30 --save-model "models/digimon_ai.pt"
```

---

### 4. Run Multi-Solver Benchmarks
```powershell
.\.venv\Scripts\python benchmark.py --rows 3 --cols 3 --num-puzzles 20 --depth 15
```

---

### 5. Run Automated Tests
```powershell
.\.venv\Scripts\pytest tests/ -v
```
*(28 passing automated tests verifying state math, pocket mechanics, parity solvability, Gymnasium API, solvers, and FastAPI server endpoints)*

---

## 🏛️ System Architecture

```
puzzle-ai-game/
├── web/                                # Modern React 18 + Vite + Tailwind Frontend
│   ├── public/
│   │   └── tiles/                      # 42 Sliced Digimon Sprites (tile_01 to tile_42)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Board43.tsx             # 42-Tile + Parking Pocket Framer Motion Board
│   │   │   ├── Controls.tsx            # Scramble, Solve, Playback & Speed Sliders
│   │   │   └── Telemetry.tsx           # Live Metrics & Diagnostics HUD
│   │   ├── types/
│   │   │   └── puzzle.ts               # Data transfer contracts
│   │   ├── utils/
│   │   │   └── audio.ts                # Web Audio API procedural synthesizer
│   │   ├── App.tsx                     # Main Dashboard Application
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── src/
│   ├── environment/
│   │   ├── puzzle_state.py             # 43-Slot NumPy Engine & Parity Solvability
│   │   └── puzzle_env.py               # Gymnasium RL Environment
│   ├── solvers/
│   │   ├── base_solver.py              # Solver Interface & Results
│   │   ├── hierarchical_solver.py      # 43-Slot Subgoal Reduction Solver (< 0.2s)
│   │   ├── astar_solver.py             # A* Search (Manhattan + Linear Conflicts)
│   │   ├── idastar_solver.py           # Iterative Deepening A* Search
│   │   └── neural_solver.py            # PyTorch Neural A* Search
│   ├── models/
│   │   └── heuristic_net.py            # PyTorch Deep Residual ConvNet
│   ├── server/
│   │   ├── app.py                      # FastAPI REST & WebSocket Server
│   │   └── schemas.py                  # Pydantic Schemas
│   └── utils/
│       ├── image_slicer.py             # Asset Slicer & Procedural Generator
│       └── benchmark_runner.py         # Multi-Solver Benchmark Engine
├── tests/                              # Pytest Test Suite (28 Tests)
├── run_web.py                          # Unified One-Click Launcher (FastAPI + Vite)
├── train.py                            # PyTorch ADI Training Pipeline
├── benchmark.py                        # Benchmark Tournament CLI
├── preprocess.py                       # Asset Slicing CLI
├── requirements.txt                    # Python Dependencies
├── plan.md                             # Architectural Design Document
└── steps.md                            # Milestone Checklist
```

---

## 💡 How the 43-Slot Mechanics Work

```
      Col 0    Col 1    Col 2    Col 3    Col 4    Col 5
Row 0 [  1  ]  [  2  ]  [  3  ]  [  4  ]  [  5  ]  [  6  ]
Row 1 [  7  ]  [  8  ]  [  9  ]  [ 10  ]  [ 11  ]  [ 12  ]
Row 2 [ 13  ]  [ 14  ]  [ 15  ]  [ 16  ]  [ 17  ]  [ 18  ]
Row 3 [ 19  ]  [ 20  ]  [ 21  ]  [ 22  ]  [ 23  ]  [ 24  ]
Row 4 [ 25  ]  [ 26  ]  [ 27  ]  [ 28  ]  [ 29  ]  [ 30  ]
Row 5 [ 31  ]  [ 32  ]  [ 33  ]  [ 34  ]  [ 35  ]  [ 36  ]
Row 6 [ 37  ]  [ 38  ]  [ 39  ]  [ 40  ]  [ 41  ]  [ 42  ]
        |
Row 7 [  0  ] (Empty Parking Pocket in Solved State)
```

1. **Solved Goal State**:
   - Tiles $1 \dots 42$ occupy all 42 positions on the $6 \times 7$ grid.
   - The parking pocket $(7, 0)$ holds the empty space ($0$).
2. **Gameplay Physics**:
   - When a tile at $(6, 0)$ (e.g. tile 37) slides DOWN into the pocket $(7, 0)$, space opens up on the main grid at $(6, 0)$.
   - The empty space can then move across all 42 slots in the main grid in 4 directions to rearrange tiles.
3. **Solving & Parking**:
   - The Hierarchical Solver arranges tiles $1 \dots 36$ in rows $0 \dots 5$, then positions tiles $38 \dots 42$ in row 6.
   - The blank is brought to $(6, 0)$ and slides DOWN into pocket $(7, 0)$, pulling tile 37 up into $(6, 0)$ and leaving the pocket empty.
   - Victory fanfare and celebration confetti trigger automatically!
