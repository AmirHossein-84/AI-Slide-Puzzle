# Digimon 43-Slot Web Sliding Tile Puzzle: Architecture & Design Plan

## 1. Project Overview & Refactored Objective
This project implements a complete, modern **Web-based Sliding Tile Puzzle Game & AI/ML Solving Suite** with:
- **Exact Physical Geometry**: 42 numbered tiles ($1 \dots 42$) in a $6 \times 7$ grid + **1 dedicated bottom-left parking pocket** at position $(7, 0)$ (total **43 board positions**).
- **Frontend**: Modern **React + Vite + Tailwind CSS + Framer Motion** with retro 90s Digimon green toy casing, fluid tile slide physics, audio feedback, and celebration effects.
- **Backend & AI Server**: **Python FastAPI + WebSockets** connected directly to the multi-solver AI suite (Hierarchical Subgoal Solver, A*, IDA*, PyTorch Neural Network).
- **One-Command Bootstrapper**: `python run_web.py` launches both the FastAPI AI server and React Vite client.

```
+-------------------------------------------------------------------------------+
|                    REACT + VITE + TAILWIND + FRAMER MOTION                    |
|  - Retro Green Digimon Toy Casing                                             |
|  - 42 Digimon Art Tiles in 6x7 Grid + Bottom-Left Parking Pocket (43 slots)   |
|  - Fluid Drag/Click Sliding & Keyboard Arrows                                 |
|  - Live WebSocket Solution Streaming & Playback Speed Controls                |
|  - Web Training Dashboard (Live loss charts & solve rate)                     |
+---------------------------------------+---------------------------------------+
                                        | (WebSocket + REST API)
                                        v
+-------------------------------------------------------------------------------+
|                      PYTHON FASTAPI + WEBSOCKET BACKEND                       |
|  - Real-time Solution & Step Streaming                                        |
|  - Background PyTorch Autodidactic Training Runner                            |
|  - Multi-Solver Performance Benchmarking API                                  |
+---------------------------------------+---------------------------------------+
                                        |
+---------------------------------------+---------------------------------------+
|                 43-SLOT PUZZLE ENGINE & MULTI-SOLVER SUITE                    |
|  - PuzzleState43 (42 tiles + 1 pocket graph adjacency)                        |
|  - Exact Graph Inversion Parity Solvability                                   |
|  - Hierarchical Subgoal Solver (Solves 43-slot board in < 0.2s)               |
|  - Classical A* & IDA* (Manhattan + Linear Conflicts)                         |
|  - PyTorch DeepCubeA Neural Heuristic Network                                 |
+-------------------------------------------------------------------------------+
```

---

## 2. 43-Slot Board Topography & Movement Graph

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

- **Solved Goal State**:
  - Positions $(0, 0) \dots (6, 5)$ contain tiles $1 \dots 42$.
  - Position $(7, 0)$ contains tile $0$ (the empty space).
- **Adjacency**:
  - Main grid $(r, c) \in [0, 6] \times [0, 5]$: 4-directional moves (Up, Down, Left, Right).
  - Slot $(6, 0)$ is also adjacent to Pocket $(7, 0)$ (Down move enters pocket).
  - Pocket $(7, 0)$ is only adjacent to $(6, 0)$ (Up move enters main grid).

---

## 3. Web Tech Stack & Directory Structure

```
puzzle-ai-game/
├── web/                        # Modern React + Vite Frontend
│   ├── public/
│   │   ├── tiles/              # 42 Sliced Digimon Tile Sprites
│   │   └── sounds/             # Tile slide click audio
│   ├── src/
│   │   ├── components/
│   │   │   ├── Board43.tsx     # 42-Tile + Pocket Framer Motion Board
│   │   │   ├── Controls.tsx    # Scramble, Solve, Playback sliders
│   │   │   ├── Telemetry.tsx   # Moves, Time, Nodes, FPS HUD
│   │   │   └── TrainingModal.tsx # Web Training Dashboard
│   │   ├── App.tsx             # Main Web Application
│   │   ├── index.css           # Tailwind styles & retro toy frame
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── src/
│   ├── environment/
│   │   ├── puzzle_state.py     # 43-slot state graph & solvability engine
│   │   └── puzzle_env.py       # Gymnasium Environment
│   ├── solvers/
│   │   ├── hierarchical_solver.py # 43-slot Subgoal Solver
│   │   ├── astar_solver.py     # 43-slot A* Solver
│   │   ├── idastar_solver.py   # 43-slot IDA* Solver
│   │   └── neural_solver.py    # PyTorch Neural A*
│   ├── models/
│   │   └── heuristic_net.py    # PyTorch ResNet for 43-slot topology
│   └── server/
│       ├── app.py              # FastAPI REST & WebSocket Server
│       └── schemas.py          # Pydantic request/response models
├── run_web.py                  # One-click unified runner (FastAPI + Vite)
├── train.py                    # PyTorch ADI Training CLI
├── benchmark.py                # Multi-Solver Benchmark CLI
└── README.md
```
