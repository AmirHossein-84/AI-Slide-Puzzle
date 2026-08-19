import React from 'react';
import {
  Brain,
  FastForward,
  Flame,
  Pause,
  Play,
  RotateCcw,
  Shuffle,
  SkipForward,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { SolverName } from '../types/puzzle';
import { sounds } from '../utils/audio';

interface ControlsProps {
  onScramble: (steps: number) => void;
  onSolve: (solver: SolverName) => void;
  onReset: () => void;
  isPlaying: boolean;
  onTogglePlay: () => void;
  onStepForward: () => void;
  playbackSpeed: number;
  onSpeedChange: (speed: number) => void;
  scrambleDepth: number;
  onScrambleDepthChange: (depth: number) => void;
  selectedSolver: SolverName;
  onSolverChange: (solver: SolverName) => void;
  showNumbers: boolean;
  onToggleNumbers: () => void;
  useProcedural: boolean;
  onToggleProcedural: () => void;
  isSolving: boolean;
  hasSolution: boolean;
}

export const Controls: React.FC<ControlsProps> = ({
  onScramble,
  onSolve,
  onReset,
  isPlaying,
  onTogglePlay,
  onStepForward,
  playbackSpeed,
  onSpeedChange,
  scrambleDepth,
  onScrambleDepthChange,
  selectedSolver,
  onSolverChange,
  showNumbers,
  onToggleNumbers,
  useProcedural,
  onToggleProcedural,
  isSolving,
  hasSolution,
}) => {
  const [soundMuted, setSoundMuted] = React.useState(false);

  const toggleSound = () => {
    const next = !soundMuted;
    setSoundMuted(next);
    sounds.enabled = !next;
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-5 shadow-2xl backdrop-blur-md flex flex-col space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="font-arcade text-sm font-bold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          <Brain className="w-4 h-4 text-emerald-400" />
          AI &amp; Game Controls
        </h3>
        <button
          onClick={toggleSound}
          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          title={soundMuted ? 'Unmute Sound' : 'Mute Sound'}
        >
          {soundMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-emerald-400" />}
        </button>
      </div>

      {/* Scramble Section */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Scramble Depth</span>
          <span className="font-mono text-emerald-400 font-bold">{scrambleDepth} steps</span>
        </div>
        <input
          type="range"
          min={5}
          max={200}
          step={5}
          value={scrambleDepth}
          onChange={(e) => onScrambleDepthChange(Number(e.target.value))}
          className="w-full accent-emerald-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
        />

        {/* Quick Depth Presets */}
        <div className="grid grid-cols-4 gap-1 pt-0.5">
          {[20, 50, 100, 200].map((d) => (
            <button
              key={d}
              onClick={() => onScrambleDepthChange(d)}
              className={`py-1 px-1.5 rounded text-[10px] font-mono font-bold transition ${
                scrambleDepth === d
                  ? 'bg-emerald-600 text-white shadow'
                  : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {d === 200 ? '200 MAX' : `${d} moves`}
            </button>
          ))}
        </div>

        <button
          onClick={() => onScramble(scrambleDepth)}
          disabled={isSolving}
          className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-arcade font-bold text-sm flex items-center justify-center gap-2 shadow-lg hover:shadow-blue-500/20 active:scale-[0.98] transition disabled:opacity-50"
        >
          <Shuffle className="w-4 h-4" />
          Scramble Board
        </button>
      </div>

      {/* Solver Select */}
      <div className="space-y-2">
        <label className="text-xs text-slate-400 font-medium block">
          Select AI Solver Engine
        </label>
        <select
          value={selectedSolver}
          onChange={(e) => onSolverChange(e.target.value as SolverName)}
          disabled={isSolving}
          className="w-full bg-slate-800/90 border border-slate-700 text-slate-100 rounded-xl px-3 py-2.5 text-sm font-medium focus:ring-2 focus:ring-emerald-500 focus:outline-none cursor-pointer"
        >
          <option value="Hierarchical Subgoal Solver">Hierarchical Subgoal Solver (&lt; 50ms)</option>
          <option value="Neural AI (PyTorch)">Neural AI (PyTorch Deep RL)</option>
          <option value="A* Search (Linear Conflict)">A* Search (Linear Conflict Heuristic)</option>
          <option value="IDA* Search">IDA* Search (Transposition-Bounded)</option>
        </select>
        <button
          onClick={() => onSolve(selectedSolver)}
          disabled={isSolving}
          className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-arcade font-bold text-sm flex items-center justify-center gap-2 shadow-lg hover:shadow-emerald-500/25 active:scale-[0.98] transition disabled:opacity-50"
        >
          <Brain className={`w-4 h-4 ${isSolving ? 'animate-spin' : ''}`} />
          {isSolving ? 'Solving Puzzle...' : 'Solve with AI'}
        </button>
      </div>

      {/* Playback Controls & Ultra-Speed */}
      <div className="space-y-2 pt-2 border-t border-slate-800">
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={onTogglePlay}
            disabled={!hasSolution}
            className={`py-2 px-3 rounded-xl font-arcade text-xs font-bold flex items-center justify-center gap-1.5 transition ${
              isPlaying
                ? 'bg-amber-600 text-white hover:bg-amber-500'
                : 'bg-slate-800 text-slate-200 hover:bg-slate-700 disabled:opacity-40'
            }`}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            {isPlaying ? 'Pause' : 'Play'}
          </button>
          <button
            onClick={onStepForward}
            disabled={!hasSolution || isPlaying}
            className="py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-arcade text-xs font-bold flex items-center justify-center gap-1.5 transition disabled:opacity-40"
          >
            <SkipForward className="w-3.5 h-3.5" />
            Step
          </button>
          <button
            onClick={onReset}
            className="py-2 px-3 rounded-xl bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 border border-rose-800/40 font-arcade text-xs font-bold flex items-center justify-center gap-1.5 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset
          </button>
        </div>

        {/* Speed Slider (1 to 200 moves/sec) */}
        <div className="pt-2">
          <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
            <span className="flex items-center gap-1.5">
              <FastForward className="w-3.5 h-3.5 text-cyan-400" />
              Playback Speed
            </span>
            <span className="font-mono text-cyan-400 font-bold flex items-center gap-1">
              {playbackSpeed > 50 && <Flame className="w-3 h-3 text-amber-400 animate-pulse" />}
              {playbackSpeed} moves/sec
            </span>
          </div>
          <input
            type="range"
            min={1}
            max={200}
            value={playbackSpeed}
            onChange={(e) => onSpeedChange(Number(e.target.value))}
            className="w-full accent-cyan-400 bg-slate-800 h-2 rounded-lg cursor-pointer"
          />

          {/* Quick Speed Presets */}
          <div className="grid grid-cols-4 gap-1 pt-1">
            {[10, 50, 100, 200].map((spd) => (
              <button
                key={spd}
                onClick={() => onSpeedChange(spd)}
                className={`py-1 px-1 rounded text-[10px] font-mono font-bold transition ${
                  playbackSpeed === spd
                    ? 'bg-cyan-600 text-white shadow'
                    : 'bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {spd === 200 ? '⚡ 200 MAX' : `${spd}x`}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Visual Toggles */}
      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800 text-xs">
        <button
          onClick={onToggleNumbers}
          className={`py-2 px-3 rounded-xl font-medium transition ${
            showNumbers
              ? 'bg-emerald-950/70 border border-emerald-500/40 text-emerald-300'
              : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
          }`}
        >
          🔢 Numbers: {showNumbers ? 'ON' : 'OFF'}
        </button>
        <button
          onClick={onToggleProcedural}
          className={`py-2 px-3 rounded-xl font-medium transition ${
            useProcedural
              ? 'bg-blue-950/70 border border-blue-500/40 text-blue-300'
              : 'bg-slate-800/60 text-slate-400 hover:bg-slate-800'
          }`}
        >
          🎨 {useProcedural ? 'Retro Style' : 'Digimon Art'}
        </button>
      </div>
    </div>
  );
};
