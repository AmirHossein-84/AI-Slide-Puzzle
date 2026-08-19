import React, { useEffect, useRef, useState } from 'react';
import confetti from 'canvas-confetti';
import { Sparkles, Gamepad2, Brain } from 'lucide-react';
import { Board43 } from './components/Board43';
import { Controls } from './components/Controls';
import { Telemetry } from './components/Telemetry';
import { TrainingStudio } from './components/TrainingStudio';
import { ActionType, PuzzleStateData, SolverName } from './types/puzzle';
import { sounds } from './utils/audio';

// Default initial solved 43-slot state
const initialGoalBoard = Array.from({ length: 42 }, (_, i) => i + 1).concat([0]);

const defaultState: PuzzleStateData = {
  board: initialGoalBoard,
  rows: 7,
  cols: 6,
  has_pocket: true,
  blank_pos: [7, 0],
  is_solved: true,
  is_solvable: true,
  manhattan: 0,
  linear_conflicts: 0,
};

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'game' | 'training'>('game');

  const [state, setState] = useState<PuzzleStateData>(defaultState);
  const [selectedSolver, setSelectedSolver] = useState<SolverName>('Hierarchical Subgoal Solver');
  const [scrambleDepth, setScrambleDepth] = useState<number>(20);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(8);
  const [showNumbers, setShowNumbers] = useState<boolean>(true);
  const [useProcedural, setUseProcedural] = useState<boolean>(false);

  // Solving & playback states
  const [isSolving, setIsSolving] = useState<boolean>(false);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [solutionSteps, setSolutionSteps] = useState<number[]>([]);
  const [moveCount, setMoveCount] = useState<number>(0);
  const [solveDurationMs, setSolveDurationMs] = useState<number>(0);
  const [nodesExpanded, setNodesExpanded] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('Welcome! Slide tiles or choose an AI solver.');
  const [activePhase, setActivePhase] = useState<string>('');

  const wsRef = useRef<WebSocket | null>(null);

  // Fetch initial state on mount
  useEffect(() => {
    fetch('/api/state')
      .then((res) => res.json())
      .then((data: PuzzleStateData) => setState(data))
      .catch(() => {
        setState(defaultState);
      });
  }, []);

  // Keyboard navigation (active in Game tab)
  useEffect(() => {
    if (activeTab !== 'game') return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (isSolving || isPlaying) return;
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
        e.preventDefault();
        let act: ActionType | null = null;
        if (e.key === 'ArrowUp') act = 1; // DOWN (moves blank down)
        if (e.key === 'ArrowDown') act = 0; // UP
        if (e.key === 'ArrowLeft') act = 3; // RIGHT
        if (e.key === 'ArrowRight') act = 2; // LEFT

        if (act !== null) {
          handleMove(act);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [state, isSolving, isPlaying, activeTab]);

  // Trigger celebration on solve
  useEffect(() => {
    if (state.is_solved && moveCount > 0 && activeTab === 'game') {
      sounds.playVictory();
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#10b981', '#3b82f6', '#f59e0b', '#ec4899'],
      });
    }
  }, [state.is_solved, moveCount, activeTab]);

  // Execute Move
  const handleMove = async (action: ActionType) => {
    try {
      const res = await fetch('/api/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, board: state.board }),
      });

      if (res.ok) {
        const nextState = await res.json();
        setState(nextState);
        setMoveCount((prev) => prev + 1);
        sounds.playSlide();
      }
    } catch {
      // Ignore network hiccup
    }
  };

  // Scramble
  const handleScramble = async (steps: number) => {
    setIsPlaying(false);
    setSolutionSteps([]);
    try {
      const res = await fetch('/api/scramble', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ steps }),
      });
      if (res.ok) {
        const nextState = await res.json();
        setState(nextState);
        setMoveCount(0);
        setStatusMessage(`Scrambled ${steps} steps. Solvable and ready!`);
      }
    } catch {
      setStatusMessage('Backend offline: start server with python run_web.py');
    }
  };

  // Reset
  const handleReset = async () => {
    setIsPlaying(false);
    setSolutionSteps([]);
    try {
      const res = await fetch('/api/reset', { method: 'POST' });
      if (res.ok) {
        const nextState = await res.json();
        setState(nextState);
        setMoveCount(0);
        setStatusMessage('Reset to solved goal state.');
      }
    } catch {
      setState(defaultState);
    }
  };

  // AI Solve via WebSocket
  const handleSolve = (solver: SolverName) => {
    if (state.is_solved) {
      setStatusMessage('Board is already solved!');
      return;
    }

    setIsSolving(true);
    setIsPlaying(true);
    setStatusMessage(`Solving with ${solver}...`);

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/solve`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          board: state.board,
          solver,
          step_delay: 1.0 / Math.max(1, playbackSpeed),
        })
      );
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'step') {
        setState((prev) => ({
          ...prev,
          board: msg.board,
          blank_pos: msg.blank_pos,
          is_solved: msg.is_solved,
        }));
        setMoveCount((prev) => prev + 1);
        sounds.playSlide();
        if (msg.phase_name) {
          setActivePhase(msg.phase_name);
        }
        setStatusMessage(`AI Step ${msg.step_index}/${msg.total_steps} (${msg.action_name})`);
      } else if (msg.type === 'complete') {
        setIsSolving(false);
        setIsPlaying(false);
        setSolveDurationMs(msg.duration_ms);
        setNodesExpanded(msg.nodes_expanded);
        setActivePhase('🎉 Puzzle Solved!');
        setStatusMessage(`Solved in ${msg.duration_ms.toFixed(1)}ms (${msg.total_steps} moves)!`);
      } else if (msg.type === 'error') {
        setIsSolving(false);
        setIsPlaying(false);
        setActivePhase('');
        setStatusMessage(`Solver Error: ${msg.message}`);
      }
    };

    ws.onerror = () => {
      setIsSolving(false);
      setIsPlaying(false);
      setStatusMessage('WebSocket connection error.');
    };
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-between p-4 sm:p-6 selection:bg-emerald-500">
      {/* Top Header Bar & Navigation */}
      <header className="w-full max-w-6xl flex flex-col sm:flex-row items-center justify-between py-3 border-b border-slate-800/80 mb-6 gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-lg">
            <Gamepad2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-arcade text-xl sm:text-2xl font-bold tracking-wider text-white flex items-center gap-2">
              DIGIMON PUZZLE AI <Sparkles className="w-4 h-4 text-emerald-400" />
            </h1>
            <p className="text-xs text-slate-400 font-medium">
              43-Slot Handheld Geometry &bull; PyTorch ADI Training &bull; Multi-Solver AI Suite
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-2xl border border-slate-800">
          <button
            onClick={() => setActiveTab('game')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'game'
                ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Gamepad2 className="w-4 h-4" />
            <span>Play &amp; Solve</span>
          </button>

          <button
            onClick={() => setActiveTab('training')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'training'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Brain className="w-4 h-4 text-indigo-300" />
            <span>Live AI Training Studio</span>
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          </button>
        </div>
      </header>

      {/* Dynamic View: Game Mode and Training Studio kept mounted in DOM */}
      <main
        className={`w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-8 items-start ${
          activeTab === 'game' ? 'grid' : 'hidden'
        }`}
      >
        {/* Left Column: Handheld Toy Board (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col items-center justify-center">
          <Board43
            state={state}
            onMove={handleMove}
            showNumbers={showNumbers}
            useProcedural={useProcedural}
            disabled={isSolving}
          />
        </div>

        {/* Right Column: Controls & Telemetry Dashboard (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-6 w-full">
          <Controls
            onScramble={handleScramble}
            onSolve={handleSolve}
            onReset={handleReset}
            isPlaying={isPlaying}
            onTogglePlay={() => setIsPlaying(!isPlaying)}
            onStepForward={() => {}}
            playbackSpeed={playbackSpeed}
            onSpeedChange={setPlaybackSpeed}
            scrambleDepth={scrambleDepth}
            onScrambleDepthChange={setScrambleDepth}
            selectedSolver={selectedSolver}
            onSolverChange={setSelectedSolver}
            showNumbers={showNumbers}
            onToggleNumbers={() => setShowNumbers(!showNumbers)}
            useProcedural={useProcedural}
            onToggleProcedural={() => setUseProcedural(!useProcedural)}
            isSolving={isSolving}
            hasSolution={solutionSteps.length > 0}
          />

          <Telemetry
            state={state}
            moveCount={moveCount}
            solveDurationMs={solveDurationMs}
            nodesExpanded={nodesExpanded}
            statusMessage={statusMessage}
            activePhase={activePhase}
          />
        </div>
      </main>

      <main className={`w-full max-w-6xl ${activeTab === 'training' ? 'block' : 'hidden'}`}>
        <TrainingStudio />
      </main>

      {/* Footer */}
      <footer className="w-full max-w-6xl mt-8 pt-4 border-t border-slate-800/60 text-center text-xs text-slate-500 font-mono">
        Digimon 43-Slot Sliding Puzzle &bull; PyTorch DeepCubeA &amp; Hierarchical Subgoal Reduction AI
      </footer>
    </div>
  );
};
