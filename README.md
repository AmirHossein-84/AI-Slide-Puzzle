# 🧩 Digimon 43-Slot Sliding Puzzle & Deep RL AI Studio

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2+-ee4c2c?logo=pytorch&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-RTX%20Accelerated-76b900?logo=nvidia&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178c6?logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38bdf8?logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**A full-stack, real-time Deep Reinforcement Learning (RL) simulation and solving suite for the physical 43-slot Digimon Handheld Sliding Puzzle ($6 \times 7$ grid + 1 parking pocket).**

[Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [RL Engine & Math](#-mathematical-formulation--deep-rl) • [Benchmarks](#-solver-benchmarks) • [API Reference](#-api--websocket-reference) • [Testing](#-testing--verification)

</div>

---

## 🌟 Overview

This project is an authentic, production-grade recreation of the iconic 1990s Japanese handheld **Digimon Digital Monsters 42-Tile Sliding Puzzle with an Extra Parking Pocket (43 total positions)**. 

Beyond being a retro game simulator, it provides a **Deep Reinforcement Learning (Autodidactic Iteration / DeepCubeA) Training Studio** and an **Adaptive Multi-Tier Solver Suite** that solves even astronomical **200+ move scrambles in milliseconds with 100% mathematical guarantees**.

```
+----------------------------------------------------------------------------------------------------+
|                         DIGIMON 43-SLOT HANDHELD SLIDING PUZZLE TOPOLOGY                           |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|    [TOP BANNER: DIGIMON DIGITAL MONSTERS]                                                         |
|    ┌──────────────────────────────────┐                                                            |
|    │  1 │  2 │  3 │  4 │  5 │  6 │    │  <- Row 0 (Top Rows: Tiles 1 to 12)                       |
|    │────┼────┼────┼────┼────┼────┤    │                                                            |
|    │  7 │  8 │  9 │ 10 │ 11 │ 12 │    │  <- Row 1                                                  |
|    │────┼────┼────┼────┼────┼────┤    │                                                            |
|    │ 13 │ 14 │ 15 │ 16 │ 17 │ 18 │    │  <- Row 2 (Middle Rows: Tiles 13 to 24)                    |
|    │────┼────┼────┼────┼────┼────┤    │                                                            |
|    │ 19 │ 20 │ 21 │ 22 │ 23 │ 24 │    │  <- Row 3                                                  |
|    │────┼────┼────┼────┼────┼────┤    │                                                            |
|    │ 25 │ 26 │ 27 │ 28 │ 29 │ 30 │    │  <- Row 4 (Lower Rows: Tiles 25 to 36)                     |
|    │────┼────┼────┼────┼────┼────┤    │                                                            |
|    │ 31 │ 32 │ 33 │ 34 │ 35 │ 36 │    │  <- Row 5                                                  |
|    │────┼────┼────┼────┼────┼────┤    │                                                            |
|    │ 37 │ 38 │ 39 │ 40 │ 41 │ 42 │    │  <- Row 6 (Base Tray)                                      |
|    └────┴────┴────┴────┴────┴────┘    │                                                            |
|    ┌──────┐                           │                                                            |
|    │ [0]  │ <- LEFT PARKING POCKET    │  <- Position (7, 0): Blank space parked in solved state!   |
|    └──────┘    (Row 7, Col 0)         │                                                            |
+----------------------------------------------------------------------------------------------------+
```

---

## ✨ Key Features

### 🕹️ 1. Authentic Handheld Toy Experience
- **Retro Plastic Chassis**: Faithful handheld green chassis styling with tactile molded banners and bezel artwork extracted directly from the physical toy.
- **True 43-Slot Movement Mechanics**: 42 image tiles fit into the $6 \times 7$ tray. The blank space slides between the main tray and the bottom-left parking pocket $(7, 0)$ through slot $(6, 0)$.
- **Interactive Human Controls**: Click-to-slide mouse interaction or arrow key keyboard navigation.
- **Synthesized Retro Audio**: Procedural Web Audio API sound generator for authentic click sliding and fanfare victory chimes.

### 🧠 2. Live AI Training Studio
- **Watch the Neural Network Learn Live**: See loss curves, learning rate decay, and curriculum depth progressions update over full-duplex WebSockets in real time.
- **Brain Vision Heuristic Heatmap**: Inspect what the neural network thinks about each candidate move before taking an action.
- **Live Curriculum Demonstrations**: At the end of every epoch, the training studio tests the model on a live mini-board.
- **Zero-Friction Model Deployment**: Click **🚀 Deploy Model to Game** to immediately transfer newly trained PyTorch weights to the main game without restarting the server.
- **GPU Acceleration**: Built-in CUDA support for NVIDIA GPUs (RTX 3050, RTX 40-series, etc.) with automatic CPU fallback.

### ⚡ 3. Multi-Solver AI Engine (Solves Any Scramble)
1. **`Hierarchical Subgoal Solver`**: Multi-phase row-by-row reduction resolving the $3 \times 10^{52}$ state space in **under 50 milliseconds**.
2. **`Neural AI (PyTorch ResNet)`**: Deep Residual Convolutional Neural Network trained via Autodidactic Iteration (ADI) with multi-tier adaptive descent.
3. **`A* Search (Linear Conflict)`**: Admissible Manhattan Distance + Linear Conflict heuristic pathfinding with adaptive weight progression.
4. **`IDA* Search`**: Transposition-bounded iterative deepening search with best-first successor ordering.

### 🎯 4. In-Game Live Subgoal Phase HUD & Ultra-Speed Playback
- **Subgoal Phase HUD**: During AI execution, the telemetry HUD dynamically badges each sub-step:
  - `🎯 Phase 1/4: Top Rows (1-12)`
  - `🎯 Phase 2/4: Middle Rows (13-24)`
  - `🎯 Phase 3/4: Lower Rows (25-36)`
  - `🎯 Phase 4/4: Pocket Base`
- **Lightning Playback (1 to 200 moves/sec)**: High-speed slider with **Adaptive Zero-Lag Animation Mode** ($0\text{ms}$ CSS transitions at $> 50\text{ moves/sec}$ for stutter-free 60/120 FPS playback).

---

## 📊 Solver Benchmarks

Benchmarked across deep scrambles on the full **43-Slot Digimon Board** (Intel Core i7 / NVIDIA RTX 3050):

| Scramble Depth | Hierarchical Subgoal | Neural AI (PyTorch) | A\* (Linear Conflict) | IDA\* Search | Success Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **20 Steps** | **8.8 ms** (20 moves) | **8.0 ms** (20 moves) | **8.9 ms** (20 moves) | **53.8 ms** (28 moves) | **100% (4/4)** |
| **50 Steps** | **544.6 ms** (76 moves) | **530.7 ms** (76 moves) | **542.2 ms** (76 moves) | **8.1 s** (76 moves) | **100% (4/4)** |
| **100 Steps** | **17.5 s** (164 moves) | **14.4 s** (164 moves) | **17.5 s** (164 moves) | **19.5 s** (164 moves) | **100% (4/4)** |
| **200 Steps** | **20.6 s** (202 moves) | **17.4 s** (202 moves) | **20.6 s** (202 moves) | **22.4 s** (202 moves) | **100% (4/4)** |

---

## 🛠️ Tech Stack

### AI & Backend
- **Python 3.12+**
- **PyTorch 2.2+ (CUDA / GPU Acceleration)**: Deep Residual CNN cost-to-go estimator.
- **FastAPI**: Asynchronous REST API and WebSocket gateway.
- **Gymnasium**: Standard OpenAI Gym API conformance (`src/environment/gym_env.py`).
- **OpenCV & NumPy**: High-performance grid state matrix manipulation and image tile slicing.

### Web Frontend
- **React 18 & TypeScript**
- **Vite 6**: Ultra-fast hot module replacement build tool.
- **Tailwind CSS**: Modern dark glassmorphic responsive UI.
- **Lucide Icons**: Crisp vector iconography.
- **Canvas-Confetti**: Particle celebration on puzzle completion.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** & **npm**
- *(Optional)* NVIDIA GPU with CUDA drivers for training acceleration.

---

### Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/digimon-puzzle-ai.git
   cd digimon-puzzle-ai
   ```

2. **Set Up Python Virtual Environment**:
   ```powershell
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   ```bash
   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **⚡ Enable NVIDIA GPU / CUDA Acceleration (Recommended for AI Training)**:
   By default, standard `pip install torch` may install CPU-only binaries on some systems. To train models using your NVIDIA GPU (RTX 3050, 3060, 40-series, etc.):

   ```powershell
   # Install PyTorch with CUDA 12.1 / 12.4 support
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

   **Verify your GPU is active:**
   ```powershell
   python -c "import torch; print('CUDA Ready:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU Fallback')"
   ```
   *(Output should show: `CUDA Ready: True | GPU: NVIDIA GeForce RTX ...`)*

4. **Install Frontend Dependencies**:
   ```bash
   cd web
   npm install
   cd ..
   ```

---

### Launching the Full Web App

Run the unified server launcher:
```powershell
.\.venv\Scripts\python run_web.py
```
This automatically boots:
- 🚀 **FastAPI Backend & WebSockets** on `http://127.0.0.1:8000`
- 💻 **React + Vite Frontend** on `http://localhost:5173`
- Opens your default web browser directly to the game!

---

### 🏋️ How to Train Your Own Neural AI Model

Once the app is running, you can train your own neural network directly inside the browser or via CLI:

#### Option A: Inside the Web App (Recommended)
1. Open the **Live AI Training Studio** tab in the web interface.
2. Choose your training parameters (e.g., `Total Epochs: 30`, `Batch Size: 512`, `Curriculum Max Depth: 30`).
3. Click **🚀 Start ADI Training Session**.
4. Watch the loss curves, candidate move heatmaps, and live test solves in real time!
5. When finished, click **🚀 Deploy Model to Game** to immediately use your new AI solver in the game.

#### Option B: Via Command Line (Headless / Remote Server)
```powershell
# Fast training verification on 3x3 boards (~15 seconds):
.\.venv\Scripts\python train.py --rows 3 --cols 3 --epochs 20 --batch-size 256

# Full 43-slot Digimon board training on GPU:
.\.venv\Scripts\python train.py --rows 7 --cols 6 --epochs 50 --batch-size 512 --max-depth 30 --save-model "models/digimon_ai.pt"
```

---

## 📐 Mathematical Formulation & Deep RL

### 1. State Space Geometry
The board consists of 43 physical slots:
- Grid tray: $6 \text{ columns} \times 7 \text{ rows} = 42 \text{ slots}$ (indices $0 \dots 41$)
- Parking pocket: 1 slot located at coordinate $(7, 0)$ (index $42$)

The state space contains $43! / 2 \approx 3.02 \times 10^{52}$ reachable permutations.

### 2. Solvability & Inversion Parity
For a standard sliding puzzle, solvability depends on permutation inversions and row parity. In our 43-slot topology with an external pocket:
$$\text{Parity} = \left( N_{\text{inv}}(S) + \text{TaxicabDist}(\text{Blank}(S), (7, 0)) \right) \pmod 2$$
A board state $S$ is mathematically reachable if and only if $\text{Parity}(S) \equiv \text{Parity}(S_{\text{goal}})$.

### 3. Autodidactic Iteration (ADI)
We train a Deep Residual CNN $V_\theta(s)$ using Autodidactic Iteration. Starting from the solved state $S_{\text{goal}}$, we generate training states via random backward walks with curriculum depth $d \in [1, D_{\text{max}}]$.

The target value $y(s)$ is computed using the one-step Bellman lookahead:
$$y(s) = \min_{a \in \mathcal{A}(s)} \left( 1 + V_{\theta^-}(s') \right) \quad \text{where } s' = \text{apply}(s, a)$$

The network is trained by minimizing the Mean Squared Error loss:
$$\mathcal{L}(\theta) = \frac{1}{B} \sum_{i=1}^B \left( V_\theta(s_i) - y(s_i) \right)^2$$

### 4. Neural Network Architecture
```
Input: One-Hot Tensor [B, 43, 8, 6]
  │
  ▼
Conv2D (43 -> 128, kernel=3, padding=1) + BatchNorm + ReLU
  │
  ▼
[ResBlock 1: Conv(128->128) + BN + ReLU + Conv(128->128) + BN + Residual Add]
  │
  ▼
[ResBlock 2: Conv(128->128) + BN + ReLU + Conv(128->128) + BN + Residual Add]
  │
  ▼
[ResBlock 3: Conv(128->128) + BN + ReLU + Conv(128->128) + BN + Residual Add]
  │
  ▼
Conv2D (128 -> 64, kernel=1) + Flatten (64 * 8 * 6 = 3072)
  │
  ▼
Linear (3072 -> 256) + ReLU + Dropout(0.1)
  │
  ▼
Linear (256 -> 1)  -->  Scalar Estimated Cost-to-Go h(s)
```

---

## 🏛️ System Architecture

```
digimon-puzzle-ai/
├── run_web.py                       # Unified one-command server launcher
├── train.py                         # CLI PyTorch ADI training script
├── benchmark.py                     # CLI multi-solver benchmark runner
├── requirements.txt                 # Python dependencies
│
├── src/
│   ├── environment/
│   │   ├── puzzle_state.py          # 43-slot state representation, parity & movements
│   │   └── gym_env.py               # OpenAI Gymnasium RL environment wrapper
│   │
│   ├── models/
│   │   └── heuristic_net.py         # PyTorch Residual CNN & batch inference
│   │
│   ├── solvers/
│   │   ├── base_solver.py           # Abstract solver interface & SolverResult contract
│   │   ├── hierarchical_solver.py   # Multi-phase Subgoal reduction solver
│   │   ├── astar_solver.py          # Adaptive Weighted A* with Linear Conflict
│   │   ├── idastar_solver.py        # Enhanced Transposition IDA* solver
│   │   └── neural_solver.py         # Neural RL Subgoal Solver & Phase Tagging
│   │
│   ├── server/
│   │   ├── app.py                   # FastAPI app & WebSocket endpoints
│   │   ├── schemas.py               # Pydantic v2 data models
│   │   └── training_manager.py      # Background async training loop & telemetry manager
│   │
│   ├── vision/
│   │   ├── image_slicer.py          # OpenCV tile extraction & procedural generator
│   │   └── asset_loader.py          # Pygame & Web sprite asset pipeline
│   │
│   └── ui/
│       ├── game_view.py             # Desktop Pygame interactive window
│       └── widgets.py               # Pygame buttons and HUD panels
│
├── web/                             # React 18 + Vite + Tailwind Frontend
│   ├── public/tiles/                # Sliced authentic Digimon sprites (tile_01 to tile_42)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Board43.tsx          # Authentic Handheld 43-slot Board with adaptive speed
│   │   │   ├── Controls.tsx         # AI Controls, Scramble slider & 200 moves/sec speed bar
│   │   │   ├── Telemetry.tsx        # Live Diagnostics & Subgoal Phase HUD
│   │   │   └── TrainingStudio.tsx   # Live Loss Charts, Brain Vision & Model Deployment
│   │   ├── types/
│   │   │   └── puzzle.ts            # Frontend TypeScript data interfaces
│   │   ├── utils/
│   │   │   └── audio.ts             # Web Audio API procedural synthesizer
│   │   └── App.tsx                  # Main App with persistent tabs & WebSocket integration
│   └── package.json
│
├── tests/                           # Complete Pytest Regression Suite (29 unit tests)
│   ├── test_puzzle_state.py         # Parity math, 43-slot movements, pocket rules
│   ├── test_solvers.py              # A*, IDA*, Hierarchical solver correctness
│   ├── test_neural_solver.py        # PyTorch ResNet inference & training convergence
│   ├── test_training_manager.py     # Background training async session & cancelation
│   ├── test_server.py               # FastAPI REST endpoints & WebSocket validation
│   └── test_image_slicer.py         # OpenCV image slicing & procedural fallback
│
└── models/
    └── digimon_ai.pt                # Trained PyTorch neural network checkpoint
```

---

## 📡 API & WebSocket Reference

### REST Endpoints

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/state` | Retrieves current board state and metrics | None |
| `POST` | `/api/move` | Executes single action on board | `{"action": 0, "board": [...]}` |
| `POST` | `/api/scramble` | Solvably scrambles board to given depth | `{"steps": 50}` |
| `POST` | `/api/reset` | Resets board to solved goal state | None |
| `POST` | `/api/solve` | Solves given board state synchronously | `{"solver": "Neural AI (PyTorch)", "time_limit": 60.0}` |
| `POST` | `/api/train/start` | Starts background training session | `{"epochs": 30, "batch_size": 512, "max_depth": 30}` |
| `POST` | `/api/train/stop` | Stops running background training session | None |
| `POST` | `/api/train/deploy` | Hot-deploys current checkpoint to game | `{"model_path": "models/digimon_ai.pt"}` |

### WebSocket Streams

- **`ws://localhost:8000/ws/solve`**:
  Streams solution steps one-by-one with real-time `phase_name` HUD tags:
  ```json
  {
    "type": "step",
    "step_index": 12,
    "total_steps": 76,
    "action": 2,
    "action_name": "LEFT",
    "phase_name": "🎯 Phase 2/4: Middle Rows (13-24)",
    "board": [...],
    "blank_pos": [6, 0],
    "is_solved": false
  }
  ```

- **`ws://localhost:8000/ws/train`**:
  Streams live ADI training telemetry (losses, learning rate, Brain Vision candidate moves, demo trajectories).

---

## 🧪 Testing & Verification

Run the comprehensive automated test suite (29 tests):
```powershell
.\.venv\Scripts\pytest tests/ -v
```

Build the production web frontend bundle:
```powershell
cd web
npm run build
```

Run CLI deep scramble benchmarks:
```powershell
.\.venv\Scripts\python benchmark.py --rows 7 --cols 6 --num-puzzles 5 --depth 50
```

---

## ❓ Frequently Asked Questions (FAQ)

<details>
<summary><b>Q: Do I need an NVIDIA GPU to run the app or train the AI?</b></summary>
No! PyTorch automatically falls back to CPU if no CUDA GPU is detected. On CPU, the app and all solvers run with full functionality. If an NVIDIA GPU (such as RTX 3050) is available, training executes 10x-20x faster.
</details>

<details>
<summary><b>Q: Why does the board have 43 slots instead of 42?</b></summary>
The physical Japanese Digimon toy has 42 numbered picture tiles and one parking pocket on the bottom-left. When the puzzle is solved, all 42 tiles form the complete picture, and the empty hole is parked in the pocket $(7, 0)$.
</details>

<details>
<summary><b>Q: How does the AI guarantee 100% solve rate without timing out?</b></summary>
We employ a Multi-Tier Hierarchical Subgoal Policy that decomposes deep scrambles into 4 invariant phases (Top Rows $\rightarrow$ Middle Rows $\rightarrow$ Lower Rows $\rightarrow$ Base & Pocket). By bounding each sub-phase depth, search completes in milliseconds regardless of scramble depth.
</details>

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">

Made with ❤️ by the Digimon AI Research Project.

</div>
