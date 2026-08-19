import React from 'react';
import { Activity, Clock, Cpu, Move, Target, Zap } from 'lucide-react';
import { PuzzleStateData } from '../types/puzzle';

interface TelemetryProps {
  state: PuzzleStateData;
  moveCount: number;
  solveDurationMs: number;
  nodesExpanded: number;
  statusMessage: string;
  activePhase?: string;
}

export const Telemetry: React.FC<TelemetryProps> = ({
  state,
  moveCount,
  solveDurationMs,
  nodesExpanded,
  statusMessage,
  activePhase,
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-2xl p-5 shadow-2xl backdrop-blur-md flex flex-col space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="font-arcade text-sm font-bold tracking-wider text-slate-200 uppercase flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          Live Telemetry &amp; Diagnostics
        </h3>
        {activePhase && (
          <span className="text-[11px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 px-2.5 py-0.5 rounded-full flex items-center gap-1.5 animate-pulse">
            <Target className="w-3.5 h-3.5 text-indigo-400" />
            {activePhase}
          </span>
        )}
      </div>

      {/* Grid of Key Metrics */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-800/70 p-3 rounded-xl border border-slate-700/50">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5 mb-1">
            <Move className="w-3.5 h-3.5 text-blue-400" />
            Moves Made
          </span>
          <p className="font-mono text-xl font-bold text-white">{moveCount}</p>
        </div>

        <div className="bg-slate-800/70 p-3 rounded-xl border border-slate-700/50">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5 mb-1">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            Manhattan Dist
          </span>
          <p className="font-mono text-xl font-bold text-amber-300">
            {state.manhattan}
          </p>
        </div>

        <div className="bg-slate-800/70 p-3 rounded-xl border border-slate-700/50">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5 mb-1">
            <Clock className="w-3.5 h-3.5 text-emerald-400" />
            AI Solve Time
          </span>
          <p className="font-mono text-xl font-bold text-emerald-400">
            {solveDurationMs > 0 ? `${solveDurationMs.toFixed(1)} ms` : '--'}
          </p>
        </div>

        <div className="bg-slate-800/70 p-3 rounded-xl border border-slate-700/50">
          <span className="text-[11px] text-slate-400 font-medium flex items-center gap-1.5 mb-1">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            Nodes Expanded
          </span>
          <p className="font-mono text-xl font-bold text-indigo-300">
            {nodesExpanded > 0 ? nodesExpanded.toLocaleString() : '--'}
          </p>
        </div>
      </div>

      {/* Real-time Status Notice */}
      <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex items-center space-x-3">
        <span
          className={`w-2 h-2 rounded-full flex-shrink-0 ${
            state.is_solved ? 'bg-emerald-400 animate-ping' : 'bg-blue-400'
          }`}
        />
        <p className="text-xs text-slate-300 font-mono truncate">
          {statusMessage}
        </p>
      </div>
    </div>
  );
};
